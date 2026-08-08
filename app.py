from flask import Flask, render_template, request
from logic import get_product_data, get_health_verdict

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_food():
    food_input = request.form["food"]
    condition = request.form["condition"]

    # Step 1: fetch real nutrition data from OpenFoodFacts
    product_data = get_product_data(food_input)

    if product_data is None:
        # Product not found -- skip Gemini entirely (no data to reason over,
        # and no point spending an API call on it).
        return render_template(
            "result.html",
            not_found=True,
            searched_term=food_input,
        )

    # Step 2: send real data + condition to Gemini, get back a structured verdict
    result = get_health_verdict(product_data, condition)

    return render_template(
        "result.html",
        not_found=False,
        product_data=product_data,
        verdict=result.get("verdict"),
        reason=result.get("reason"),
    )

if __name__ == "__main__":
    app.run(debug=True)