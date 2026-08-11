import os
from flask import Flask, render_template, request, session
from logic import get_product_data, get_health_verdict

app = Flask(__name__)

# Reads FLASK_SECRET_KEY from environment if set (recommended for production --
# set this in Render's dashboard, same way as GEMINI_API_KEY). Falls back to a
# FIXED string, not os.urandom(), so sessions don't silently break every time
# the free-tier instance sleeps/restarts and regenerates a random key.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key-change-this-later")

@app.route("/")
def home():
    # Pre-fill the condition dropdown with whatever was chosen last time, if any
    saved_condition = session.get("condition")
    return render_template("index.html", saved_condition=saved_condition)

@app.route("/analyze", methods=["POST"])
def analyze_food():
    # .get() with a default avoids a crash if "food"/"condition" are ever missing
    # from the request (e.g. a direct API call, not just the HTML form).
    food_input = request.form.get("food", "").strip()
    condition = request.form.get("condition", "").strip()

    if not food_input:
        return render_template(
            "index.html",
            error="Please enter a food name or barcode.",
            saved_condition=session.get("condition"),
        )

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