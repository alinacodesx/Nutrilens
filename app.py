from flask import Flask, render_template, request, session
from logic import get_product_data, get_health_verdict

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-this-later"  # needed for Flask to sign session cookies

@app.route("/")
def home():
    # Pre-fill the condition dropdown with whatever was chosen last time, if any
    saved_condition = session.get("condition")
    return render_template("index.html", saved_condition=saved_condition)

@app.route("/analyze", methods=["POST"])
def analyze_food():
    food_input = request.form["food"]
    condition = request.form["condition"]

    # Remember this condition for next time, so the user doesn't have to
    # re-select it on every single search.
    session["condition"] = condition

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