# Cravely: Discover recipes worth every bite

> **Disclaimer:** This app is strictly for food lovers. Calorie counts aren't super accurate — food is meant to be enjoyed!
---

## Recipe Manager - Py4Web Project

A web-based recipe management system built with the Py4Web framework.

---

## Description

Cravely is a full-stack web application that allows users to:

- Create, view, and delete recipes.
- Manage ingredients and quantities.
- Automatically calculate total recipe calories.
- Upload and display recipe images.
- Seamlessly search for recipes by name or type.
- Add new ingredients

---

## Setup Instructions

### Install Py4Web (First-Time Setup)

We recommend installing Py4Web inside a virtual environment:

```bash
# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install py4web
pip install py4web

# Clone this repo
Clone This Repository
git clone <repo-link>
cd <project-directory>

Run the Application
py4web run apps

```

## Features Overview (For a more detailed view visit: docs/documentation.md)

-> Add, edit, and delete recipes
-> Link recipes with ingredients and servings
-> Auto-calculate total calories per recipe
-> Ingredient management with search and unit management
-> TheMealDB API import with automatic ingredient linking
-> Admin pages to clear data, import data, and auto-fill calories
-> Public search API for recipes and ingredients


## App Navigation Guide

| **Page**              | **URL Path**                   | **Description**                        |
|-----------------------|--------------------------------|----------------------------------------|
| Landing Page          | `/Cravely/landing`             | Main landing page                      |
| Recipes Page          | `/Cravely/recipes`             | Browse, search, and manage recipes     |
| Add Recipe            | `/Cravely/upload`              | Upload new recipes                     |
| Ingredients           | `/Cravely/ingredients`         | Manage and add ingredients             |
| About Page            | `/Cravely/about`               | About the app                          |
| Admin: Import         | `/Cravely/importData`          | Import recipes from TheMealDB          |
| Admin: Clear All      | `/Cravely/clearAllData`        | Clear all recipes and ingredients      |
| Admin: Fill Calories  | `/Cravely/admin/fill_calories` | Auto-fill ingredient calories          |


## API Endpoints

### Public APIs

- `/Cravely/api/public/recipes?name=<name>`
- `/Cravely/api/public/ingredients?search=<term>`

### Private APIs (Authenticated)

- `/Cravely/api/recipes`
- `/Cravely/api/ingredients`

---

## Additional Documentation

For a super detailed explanation of all the features, how the app works, and screenshots of each page, please visit the `docs` folder in this repository.

Inside `docs/documentation.md` you will find:
- Full feature breakdown
- How each page works
- Detailed walkthroughs with screenshots

This document is designed to give a clear tour of the project from both a technical and user perspective.


## Creators of Cravely:
- Charles Phu
- Thomas Wong
- Uday Patel
- Kiaran Lau
- Giovanni Hernandez Barajas
- Robert Agnvall

## Acknowledgements

- [TheMealDB API](https://www.themealdb.com/api.php) — for recipe data
- [Py4Web](https://py4web.com/) — the web framework that powers this app
- [Tailwind CSS](https://tailwindcss.com/) — for beautiful styling
