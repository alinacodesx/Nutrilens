"""
Standalone test of OpenFoodFacts API calls.
Run this directly (no Flask) to confirm the API works and to inspect
the real shape of the data before we build anything around it.
"""

import requests
HEADERS = {
    "User-Agent": "NutriLensV2/0.1 (Phase1 test script; contact: your-email@example.com)"
}

def get_product_by_barcode(barcode: str) -> dict | None:
    """Look up a single product by exact barcode. Returns None if not found."""
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()  # raises if the request itself failed (network, 500, etc.)
    data = resp.json()

    # OFF returns status=1 if found, status=0 if not found — even on a 200 OK.
    # This is a classic gotcha: HTTP success != product found.
    if data.get("status") != 1:
        return None

    return data["product"]


def search_products_by_name(name: str, limit: int = 5) -> list[dict]:
    """Search products by free-text name. Returns a list of raw product dicts."""
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "json": 1,
        "page_size": limit,
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("products", [])


if __name__ == "__main__":
    print("=== Barcode lookup test (Nutella, 3017620422003) ===")
    product = get_product_by_barcode("3017620422003")
    if product:
        print("Name:", product.get("product_name"))
        print("Nutriments keys:", list(product.get("nutriments", {}).keys())[:10])
        print("Ingredients text:", (product.get("ingredients_text") or "")[:150])
    else:
        print("Not found.")

    print("\n=== Name search test ('oats') ===")
    results = search_products_by_name("oats", limit=3)
    for p in results:
        print("-", p.get("product_name"), "|", p.get("code"))