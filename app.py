from flask import Flask, render_template, request, send_from_directory
import random
from constraint import Problem
import os

app = Flask(__name__)

def calculate_bmr(gender, weight, height, age, activity_level, goal):
    gender = gender.lower()
    if gender in ["female", "f"]:
        bmr = (weight * 10) + (height * 6.25) - (age * 5) - 161
    elif gender in ["male", "m"]:
        bmr = (weight * 10) + (height * 6.25) - (age * 5) + 5
    else:
        return None
    
    if goal == 'cutting':
        bmr = bmr*0.8
    elif goal == 'maintenance':
        bmr = bmr*1
    elif goal == 'bulking':
        bmr = bmr*1.2

    if activity_level == 'sedentary':
        return int(bmr * 1.2)
    elif activity_level == 'lightly_active':
        return int(bmr * 1.375)
    elif activity_level == 'moderately_active':
        return int(bmr * 1.55)
    elif activity_level == 'very_active':
        return int(bmr * 1.725)
    elif activity_level == 'super_active':
        return int(bmr * 1.9)
    else:
        return None


food_dict_pagi = {
    "Nasi": {"Kalori": 200, "Protein": 2},
    "Sayur Asem": {"Kalori": 100, "Protein": 1},
    "Roti": {"Kalori": 150, "Protein": 6},
    "Telur": {"Kalori": 70, "Protein": 6},
    "Oatmeal": {"Kalori": 150, "Protein": 5},
    "WheyProtein": {"Kalori": 120, "Protein": 20},
    
}

food_dict_siang = {
    "Tahu": {"Kalori": 50, "Protein": 8},
    "Tempe": {"Kalori": 150, "Protein": 12},
    "Nasi": {"Kalori": 200, "Protein": 2},
    "Mie Goreng": {"Kalori": 200, "Protein": 8},
    "Dada Ayam Goreng": {"Kalori": 250, "Protein": 25},
    "Sandwich": {"Kalori": 180, "Protein": 7},
}

food_dict_malam = {
    "Nasi": {"Kalori": 200, "Protein": 2},
    "Ikan Bakar": {"Kalori": 250, "Protein": 22},
    "Sate Ayam": {"Kalori": 180, "Protein": 25},
    "Sup Ayam": {"Kalori": 150, "Protein": 15},
    "Quinoa": {"Kalori": 220, "Protein": 8},
    "Brokoli Rebus": {"Kalori": 50, "Protein": 3},
    
}


def food_recommendation(bmr, weight, food_dict_pagi, food_dict_siang, food_dict_malam):
    bmr_part = bmr // 3
    protein_need = weight * 1.5
    meals = ['Pagi', 'Siang', 'Malam']
    meal_plan = {}
    total_calories = 0
    total_protein = 0

    food_dicts = [food_dict_pagi, food_dict_siang, food_dict_malam]

    for meal, food_dict in zip(meals, food_dicts):
        total_calories_meal = 0
        total_protein_meal = 0

        problem = Problem()
        for food in food_dict:
            problem.addVariable(food, range(int(bmr_part / food_dict[food]["Kalori"]) + 1))

        problem.addConstraint(lambda *foods: sum(food * food_dict[food_name]["Kalori"] for food, food_name in zip(foods, food_dict)) <= bmr_part, food_dict.keys())
        problem.addConstraint(lambda *foods: sum(food * food_dict[food_name]["Kalori"] for food, food_name in zip(foods, food_dict)) >= bmr_part * 0.9, food_dict.keys())
        problem.addConstraint(lambda *foods: sum(food * food_dict[food_name]["Protein"] for food, food_name in zip(foods, food_dict)) >= protein_need, food_dict.keys())

        solutions = problem.getSolutions()

        if solutions:
            chosen_solution = random.choice(solutions)
            meal_plan[meal] = {food: quantity for food, quantity in chosen_solution.items()}
            total_calories_meal = sum(quantity * food_dict[food]["Kalori"] for food, quantity in chosen_solution.items())
            total_protein_meal = sum(quantity * food_dict[food]["Protein"] for food, quantity in chosen_solution.items())
        else:
            meal_plan[meal] = None

        total_calories += total_calories_meal
        total_protein += total_protein_meal

    return meal_plan, total_calories, total_protein




@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        gender = request.form["gender"]
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        age = int(request.form["age"])
        activity_level = request.form["activity_level"]
        goal = request.form["goal"]

        bmr = calculate_bmr(gender, weight, height, age, activity_level, goal)

        if bmr is not None:
            recommended_food, calories, protein = food_recommendation(bmr, weight, food_dict_pagi, food_dict_siang, food_dict_malam)
            if all(meal is not None for meal in recommended_food.values()):
                return render_template("result.html", bmr=bmr, recommended_food=recommended_food, calories=calories, protein=protein)
            else:
                return "Maaf, tidak ada rekomendasi yang tersedia."
        else:
            return "Jenis kelamin tidak valid."

    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)
