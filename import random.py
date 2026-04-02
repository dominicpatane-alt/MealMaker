import random
import openpyxl
import tkinter as tk
from tkinter import messagebox

FILE_NAME = "meal_picker_starter.xlsx"
SHEET_NAME = "Foods"

foods = {
    "Grain": [],
    "Protein": [],
    "Sauce": [],
    "AddIn": []
}

current_meal = {
    "Grain": "",
    "Protein": "",
    "Sauce": "",
    "AddIn": ""
}


def load_foods():
    global foods
    foods = {
        "Grain": [],
        "Protein": [],
        "Sauce": [],
        "AddIn": []
    }

    try:
        workbook = openpyxl.load_workbook(FILE_NAME)
        sheet = workbook[SHEET_NAME]

        for row in sheet.iter_rows(min_row=2, values_only=True):
            name, category, enabled, notes = row

            if not name or not category:
                continue

            if str(enabled).strip().lower() != "yes":
                continue

            category = str(category).strip()

            if category in foods:
                foods[category].append(str(name).strip())

    except FileNotFoundError:
        messagebox.showerror("Error", f"Could not find {FILE_NAME}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load spreadsheet:\\n{e}")


def pick_random(category):
    items = foods.get(category, [])
    if not items:
        return "(none available)"
    return random.choice(items)


def generate_meal():
    current_meal["Grain"] = pick_random("Grain")
    current_meal["Protein"] = pick_random("Protein")
    current_meal["Sauce"] = pick_random("Sauce")

    addins = foods.get("AddIn", [])
    if addins and random.choice([True, False]):
        current_meal["AddIn"] = random.choice(addins)
    else:
        current_meal["AddIn"] = "(none)"

    update_labels()


def reroll_category(category):
    if category == "AddIn":
        addins = foods.get("AddIn", [])
        if addins and random.choice([True, False]):
            current_meal["AddIn"] = random.choice(addins)
        else:
            current_meal["AddIn"] = "(none)"
    else:
        current_meal[category] = pick_random(category)

    update_labels()


def update_labels():
    grain_value.config(text=current_meal["Grain"])
    protein_value.config(text=current_meal["Protein"])
    sauce_value.config(text=current_meal["Sauce"])
    addin_value.config(text=current_meal["AddIn"])

    final_text = f'{current_meal["Grain"]} + {current_meal["Protein"]} + {current_meal["Sauce"]}'
    if current_meal["AddIn"] != "(none)":
        final_text += f' + {current_meal["AddIn"]}'

    final_meal_value.config(text=final_text)


def refresh_data():
    load_foods()
    messagebox.showinfo("Refreshed", "Spreadsheet data reloaded.")


root = tk.Tk()
root.title("Meal Picker")
root.geometry("500x350")

title_label = tk.Label(root, text="What am I eating?", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

grain_label = tk.Label(root, text="Grain:", font=("Arial", 12, "bold"))
grain_label.pack()
grain_value = tk.Label(root, text="-", font=("Arial", 12))
grain_value.pack()

protein_label = tk.Label(root, text="Protein:", font=("Arial", 12, "bold"))
protein_label.pack()
protein_value = tk.Label(root, text="-", font=("Arial", 12))
protein_value.pack()

sauce_label = tk.Label(root, text="Sauce:", font=("Arial", 12, "bold"))
sauce_label.pack()
sauce_value = tk.Label(root, text="-", font=("Arial", 12))
sauce_value.pack()

addin_label = tk.Label(root, text="Add-In:", font=("Arial", 12, "bold"))
addin_label.pack()
addin_value = tk.Label(root, text="-", font=("Arial", 12))
addin_value.pack()

final_meal_label = tk.Label(root, text="Meal:", font=("Arial", 14, "bold"))
final_meal_label.pack(pady=(10, 0))
final_meal_value = tk.Label(root, text="-", font=("Arial", 13))
final_meal_value.pack(pady=(0, 10))

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Generate Meal", command=generate_meal).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Reroll Grain", command=lambda: reroll_category("Grain")).grid(row=0, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Reroll Protein", command=lambda: reroll_category("Protein")).grid(row=1, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Reroll Sauce", command=lambda: reroll_category("Sauce")).grid(row=1, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Reroll Add-In", command=lambda: reroll_category("AddIn")).grid(row=2, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Refresh Spreadsheet", command=refresh_data).grid(row=2, column=1, padx=5, pady=5)

load_foods()
generate_meal()

root.mainloop()