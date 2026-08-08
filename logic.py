import os
import time
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads .env locally; on Render/Railway, env vars are set directly in dashboard

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

HEADERS = {
    "User-Agent": "NutriLensV2/0.1 (Phase1; contact: your-email@example.com)"
}

# The forced-output schema for Gemini's verdict. "enum" guarantees verdict
# can only be one of these 4 values -- no free text, no hallucinated 5th option.
analyze_food_function = {
    "name": "analyze_food_for_health",
    "description": (
        "Return a health verdict for a food product given a specific "
        "health condition, based ONLY on the nutrition data provided."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "verdict": {
                "type": "string",
                "enum": ["safe", "caution", "avoid", "insufficient_data"],
                "description": (
                    "safe/caution/avoid based on the data given. "
                    "Use insufficient_data if key nutrition fields are missing "
                    "and you cannot make a responsible judgment."
                ),
            },
            "reason": {
                "type": "string",
                "description": "A short 1-2 sentence explanation for the verdict.",
            },
        },
        "required": ["verdict", "reason"],
    },
}

_tools = types.Tool(function_declarations=[analyze_food_function])
_config = types.GenerateContentConfig(tools=[_tools])


def get_product_data(product_or_barcode: str) -> dict | None:
    """
    Fetches nutrition data from OpenFoodFacts, by barcode (digits) or
    by name search. Returns None if nothing was found.
    """
    is_barcode = product_or_barcode.isdigit()

    if is_barcode:
        url = f"https://world.openfoodfacts.org/api/v2/product/{product_or_barcode}.json"
    else:
        url = "https://world.openfoodfacts.org/cgi/search.pl"

    # OFF's legacy search endpoint occasionally returns transient 503s
    # (it's rate-limited server-side). One quick retry smooths over that.
    for attempt in range(2):
        try:
            if is_barcode:
                params = {"lc": "en"}  # ask OFF to return English text fields where available
                res = requests.get(url, params=params, headers=HEADERS, timeout=10)
                data = res.json()
                if data.get("status") != 1:
                    return None
                product = data.get("product", {})
            else:
                params = {
                    "search_terms": product_or_barcode,
                    "search_simple": 1,
                    "json": 1,
                    "page_size": 5,  # fetch a few candidates instead of blindly trusting result #1
                    "lc": "en",
                }
                res = requests.get(url, params=params, headers=HEADERS, timeout=10)
                data = res.json()
                products = data.get("products", [])
                if not products:
                    return None
                product = _pick_best_match(products, product_or_barcode)

            return {
                "name": product.get("product_name") or product_or_barcode.title(),
                "ingredients": product.get("ingredients_text", "Not specified"),
                "nutriments": product.get("nutriments", {}),
            }
        except Exception as e:
            print(f"OpenFoodFacts API error (attempt {attempt + 1}): {e}")
            if attempt == 0:
                time.sleep(1.5)  # brief pause before the one retry
            else:
                return None


def _pick_best_match(products: list, search_term: str) -> dict:
    """
    Given a few candidate products, prefer the one whose name actually
    contains the search term -- rather than blindly trusting whichever
    result OFF's popularity-based sort put first (which can be an
    unrelated flavoring/variant product, as we saw with "maggi").
    Falls back to the first result if nothing matches cleanly.
    """
    term = search_term.lower()
    for product in products:
        name = (product.get("product_name") or "").lower()
        if term in name:
            return product
    return products[0]


def get_health_verdict(product_data: dict, condition: str) -> dict:
    """
    Calls Gemini with nutrition data + a health condition, and forces a
    structured verdict back via function-calling. Returns a dict with
    'verdict' and 'reason' keys.
    """
    prompt = f"""
    Food: {product_data['name']}
    Nutrition data (per 100g, where available): {product_data['nutriments']}
    User health condition: {condition}

    Analyze whether this food is safe for someone with this condition.
    Base your verdict strictly on the nutrition data given.
    If critical fields are missing, use "insufficient_data" rather than guessing.
    Call the analyze_food_for_health function with your verdict.
    """

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=_config,
        )
        part = response.candidates[0].content.parts[0]
        if part.function_call:
            return dict(part.function_call.args)
        return {"verdict": "insufficient_data", "reason": "Model did not return a structured verdict."}
    except Exception as e:
        print(f"Gemini API error: {e}")
        return {"verdict": "insufficient_data", "reason": "AI analysis is temporarily unavailable."}