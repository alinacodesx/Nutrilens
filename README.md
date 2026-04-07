# NutriLens — Personalized Food Health Analyzer

## Overview

NutriLens is a web-based application that analyzes packaged food ingredients and provides personalized health insights based on user conditions. It simplifies complex ingredient lists into clear, actionable decisions.

---

## Problem

* Food labels are difficult for most people to understand
* Harmful ingredients such as excess sugar, sodium, and additives often go unnoticed
* There is no simple system for personalized dietary guidance

---

## Solution

NutriLens uses a rule-based analysis system to evaluate ingredients and generate personalized health recommendations.

---

## How It Works

1. User selects a food item
2. Ingredient data is retrieved
3. The analysis engine processes the ingredients
4. Personalized suggestions are generated

---

## Features (Version 1)

* Predefined food dataset
* Health condition selection:

  * Diabetic
  * High Cholesterol
  * Weight Loss
* Ingredient-level analysis
* Clear and simple output

---

## Tech Stack

* Python
* Flask
* HTML
* CSS

---

## Architecture

User Input → Flask Route → Analysis Engine → Response

---

## Project Structure

```bash
NutriLens/
│── app.py
│── logic.py
│── data.py
│── templates/
│── static/
│── requirements.txt
│── README.md
```

---

## Run Locally
pip install -r requirements.txt
python app.py


---

## Screenshots
<img width="513" height="302" alt="image" src="https://github.com/user-attachments/assets/5b03a027-8b2b-4347-88a2-0d64f5e5213e" />
<img width="656" height="887" alt="image" src="https://github.com/user-attachments/assets/bdfb3574-cc4d-4a1f-95c0-3b12a5c0776c" />
<img width="643" height="887" alt="image" src="https://github.com/user-attachments/assets/43b1c9eb-0a1a-42fb-bda1-bdd3400ef56a" />
<img width="276" height="734" alt="image" src="https://github.com/user-attachments/assets/e1f9ca47-dc1b-4934-a5c0-c5a170ec7a1d" />



---

## Live Demo



---

## Future Improvements

* Real-time food search
* Database integration
* Improved UI/UX
* AI-based recommendations

---

## Version

V1: Rule-based ingredient analysis
V2 (Planned): AI-powered system

---

## Learning Goal

This project reflects my approach to learning backend by building real-world systems instead of only studying theory.
---

## Feedback

Open to suggestions and improvements.
