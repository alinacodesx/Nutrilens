"""
Standalone test of Gemini function-calling (tool-use).
Sends nutrition data + a health condition to Gemini, and forces the
response into a strict schema: verdict + reason. No free-text parsing.
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads .env and makes GEMINI_API_KEY available via os.getenv

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# This is the "schema" we discussed: the exact shape Gemini's response
# must follow. "enum" forces verdict to be one of these 4 values only —
# Gemini cannot invent a 5th option or free-text it.
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

tools = types.Tool(function_declarations=[analyze_food_function])
config = types.GenerateContentConfig(tools=[tools])


def get_health_verdict(product_name: str, nutriments: dict, condition: str) -> dict:
    """
    Calls Gemini with nutrition data + a health condition, and forces a
    structured verdict back via function-calling. Returns a dict with
    'verdict' and 'reason' keys.
    """
    # We deliberately hand Gemini ONLY the numbers we have — if a field is
    # missing, it's just absent from this dict, not filled with a guess.
    prompt = f"""
    Food: {product_name}
    Nutrition data (per 100g, where available): {nutriments}
    User health condition: {condition}

    Analyze whether this food is safe for someone with this condition.
    Base your verdict strictly on the nutrition data given.
    If critical fields are missing, use "insufficient_data" rather than guessing.
    Call the analyze_food_for_health function with your verdict.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=config,
    )

    # Gemini's function-calling response comes back as a "function_call" part,
    # not as plain text -- we pull the structured args out of it directly.
    part = response.candidates[0].content.parts[0]
    if part.function_call:
        return dict(part.function_call.args)
    else:
        # Fallback: model didn't call the function (shouldn't normally happen)
        return {"verdict": "insufficient_data", "reason": "Model did not return a structured verdict."}


if __name__ == "__main__":
    # Minimal fake nutrition data to test the loop end-to-end
    test_nutriments = {
        "sugars_100g": 56.3,
        "energy-kcal_100g": 539,
        "fat_100g": 30.9,
        "saturated-fat_100g": 10.6,
    }

    result = get_health_verdict("Nutella", test_nutriments, "diabetic")
    print("Verdict:", result.get("verdict"))
    print("Reason:", result.get("reason"))