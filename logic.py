def analyze(ingredients, condition):
    warnings = []
    suggestions = []

    if condition == "diabetic":
        if any("sugar" in item for item in ingredients):
            warnings.append("High sugar - not recommended")
            suggestions.append("Avoid sugary foods")

    if condition == "cholesterol":
        if any("oil" in item or "fat" in item for item in ingredients):
            warnings.append("High fat content")
            suggestions.append("Choose low-fat alternatives")

    if condition == "weight loss":
        if any("oil" in item for item in ingredients):
            warnings.append("High calorie food")
            suggestions.append("Eat in moderation")

    return warnings, suggestions