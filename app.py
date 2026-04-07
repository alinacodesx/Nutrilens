from flask import Flask, render_template, request
from data import foods
from logic import analyze

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze_food():
    food = request.form["food"]
    condition = request.form["condition"]

    food_data = foods[food]


    ingredients = [item["name"].lower() for item in food_data["ingredients"]]


    warnings, suggestions = analyze(ingredients, condition)
    health_percent = food_data["health_score"] * 10
    return render_template(
    "result.html",
    food_data=food_data,
    warnings=warnings,
    suggestions=suggestions,
    health_percent=health_percent
)

if __name__ == "__main__":
    app.run(debug=True)