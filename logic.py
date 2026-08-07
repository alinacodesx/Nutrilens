import requests
import json
import os
from google import genai

# Setup Gemini Client (API Key environment variable se lega)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def get_product_data(product_or_barcode):
    """Fetches real-time nutrition data from Open Food Facts API."""
    # 1. Check if input is a numeric Barcode
    if product_or_barcode.isdigit():
        url = f"https://world.openfoodfacts.org/api/v2/product/{product_or_barcode}.json"
    else:
        # 2. Search by product name if not a barcode
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={product_or_barcode}&search_simple=1&action=process&json=1"
        
    headers = {'User-Agent': 'NutriLensApp/2.0'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        
        if product_or_barcode.isdigit() and data.get("status") == 1:
            product = data.get("product", {})
        elif data.get("products"):
            product = data.get("products")[0]
        else:
            return None
            
        return {
            "name": product.get("product_name", product_or_barcode.title()),
            "category": product.get("categories", "General Food"),
            "processing_level": product.get("pnns_groups_1", "Processed"),
            "ingredients": product.get("ingredients_text", "Not specified"),
            "nutrition_per_100g": product.get("nutriments", {})
        }
    except Exception as e:
        print(f"API Error: {e}")
        return None


def analyze_with_gemini(product_data, condition):
    """Replaces V1 static rules with Gemini reasoning engine."""
    
    prompt = f"""
    You are the NutriLens Health Reasoning AI Engine.
    Analyze this food product for a user with the medical condition: '{condition}'.

    Product Information:
    - Name: {product_data['name']}
    - Ingredients: {product_data['ingredients']}
    - Nutrition Data: {product_data['nutrition_per_100g']}

    Return your response strictly as a JSON object matching this structure:
    {{
        "health_score": <number 1 to 10>,
        "risk_summary": "<brief 1-2 sentence risk analysis>",
        "warnings": ["<warning 1>", "<warning 2>"],
        "suggestions": ["<suggestion 1>", "<suggestion 2>"],
        "better_alternatives": ["<alternative 1>", "<alternative 2>", "<alternative 3>"],
        "recommended_frequency": "<e.g., Daily, Moderate, Occasional, Avoid>"
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                'response_mime_type': 'application/json'
            }
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini Error: {e}")
        # Fallback dictionary if AI fails
        return {
            "health_score": 5,
            "risk_summary": "Could not complete deep AI evaluation.",
            "warnings": ["Exercise caution with processed items."],
            "suggestions": ["Consult a nutritionist for personalized plans."],
            "better_alternatives": ["Fresh fruit", "Water"],
            "recommended_frequency": "Moderate"
        }