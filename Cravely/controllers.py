from py4web import action, request, abort, redirect, response
from .common import db, auth, T
import json
import os

# -------------------------
# Page Routes
# -------------------------

@action("index")
def index():
    redirect("/Cravely/landing")
    return

# @action("index")
# @action.uses("index.html", auth, T)
# def index():
#     user = auth.get_user()
#     message = T("Hello {first_name}").format(**user) if user else T("Hello")
#     return dict(message=message)

# HTTP server from CSE 130
# Use syscall read to read binary
@action('uploads/<filename>',method=["GET"])
@action.uses(db)
def download(filename):
    path = os.path.join(os.path.dirname(__file__), 'uploads', filename)
    if os.path.exists(path) == False:
        abort(404)
    
    with open(path, 'rb') as f:
        data = f.read()
    
    if filename.lower().endswith('.jpeg'):
        content_type = 'image/jpeg'
    elif filename.lower().endswith('.png'):
        content_type = 'image/png'
    elif filename.lower().endswith('.jpg'):
        content_type = 'image/jpg'
    elif filename.lower().endswith('.gif'):
        content_type = 'image/gif'
    elif filename.lower().endswith('.raw'):
        content_type = 'image/raw'
    else:
        abort(405)

    response.headers['Content-Type'] = content_type
    response.headers['Content-Length'] = len(data)
    
    return data

@action("landing")
@action.uses("landing.html", db, auth, T)
def landing():
    return dict()

@action("upload")
@action.uses("upload.html", db, auth.user, T)
def upload():
    return dict()

@action("ingredients")
@action.uses("ingredient_list.html", db, auth, T)
def ingredients():
    return dict()

@action("recipes")
@action.uses("recipes.html",db,auth,T)
def recipes():
    return dict()

@action("about")
@action.uses("about.html", db, auth, T)
def about():
    return dict()

# ------------------------
# User API
# ------------------------
@action("api/user")
@action.uses(auth)
def get_user():
    user = auth.get_user()
    return dict(id=user["id"] if user else None)

# -------------------------
# Ingredient API
# -------------------------

@action("api/ingredients", method=["GET"])
@action.uses(db)
def get_ingredients():
    search = request.query.get("search", "").strip()
    if search:
        ingredients = db(db.ingredients.name.contains(search, case_sensitive=False)).select().as_list()
    else:
        ingredients = db(db.ingredients).select(orderby=db.ingredients.name).as_list()
    return {"success": True, "ingredients": ingredients}

#This is used to add the ingredients to the database
@action("api/ingredients", method=["POST"])
@action.uses(db, auth.user)
def post_ingredient():
    data = request.json
    if not data or not data.get("name"):
        return {"success": False, "errors": "Name is required"}

    data["name"] = data.get("name", "").strip().lower()  # Normalize

    existing = db(db.ingredients.name == data["name"]).select().first()
    if existing:
        return {"success": False, "errors": "Ingredient already exists"}

    result = db.ingredients.validate_and_insert(**data)
    if result.get("id"):
        return {"success": True, "id": result["id"]}
    else:
        return {"success": False, "errors": result.get("errors")}

# -------------------------
# Recipe API
# -------------------------

#This is used to get all the recipes from the database
# @action("api/recipes", method=["GET"])
# @action.uses(db)
# def get_recipes():
#     search_name = request.query.get("name", "").strip()
#     search_type = request.query.get("type", "").strip()

#     query = db.recipes.id > 0
#     if search_name:
#         query &= db.recipes.name.contains(search_name)
#     if search_type:
#         query &= db.recipes.type.contains(search_type)

#     recipes = db(query).select(orderby=db.recipes.name).as_list()
#     return {"success": True, "recipes": recipes}
@action("api/recipes", method=["GET"])
@action.uses(db)
def get_recipes():
    search_name = request.query.get("name", "").strip()
    search_type = request.query.get("type", "").strip()

    query = db.recipes.id > 0
    if search_name:
        query &= db.recipes.name.contains(search_name)
    if search_type:
        query &= db.recipes.type.contains(search_type)

    recipes = []
    for r in db(query).select(orderby=db.recipes.name):
        # Get linked ingredients
        links = db(db.linking.recipe_id == r.id).select()
        ingredients = []
        for link in links:
            ing = db.ingredients[link.ingredient_id]
            ingredients.append({
                "name": ing.name,
                "quantity_per_serving": link.quantity_per_serving,
                "unit": ing.unit
            })

        recipes.append({
            "id": r.id,
            "name": r.name,
            "type": r.type,
            "description": r.description,
            "instruction_steps": r.instruction_steps,
            "servings": r.servings,
            "author": r.author,
            "ingredients": ingredients,
            "image": r.image,
        })

    return {"success": True, "recipes": recipes}


@action("api/public/recipes", method=["GET"])
@action.uses(db)
def get_public_recipes():
    search_name = request.query.get("name", "").strip()
    search_type = request.query.get("type", "").strip()

    query = db.recipes.id > 0
    if search_name:
        query &= db.recipes.name.contains(search_name)
    if search_type:
        query &= db.recipes.type.contains(search_type)

    recipes = []
    for r in db(query).select(orderby=db.recipes.name):
        # Get linked ingredients
        links = db(db.linking.recipe_id == r.id).select()
        ingredients = []
        for link in links:
            ing = db.ingredients[link.ingredient_id]
            ingredients.append({
                "name": ing.name,
                "quantity_per_serving": link.quantity_per_serving,
                "unit": ing.unit
            })

        recipes.append({
            "id": r.id,
            "name": r.name,
            "type": r.type,
            "description": r.description,
            "instruction_steps": r.instruction_steps,
            "servings": r.servings,
            "author": r.author,
            "ingredients": ingredients,
            "image": r.image,
        })

    return {"success": True, "recipes": recipes}

#This function calls the link Cravely/api/recipes, its used to add new recipes to the database
@action("api/recipes", method=["POST"])
@action.uses(db, auth.user)
def post_recipe():
    data = request.json
    if request.content_type and "multipart/form-data" in request.content_type:
        recipe_json = request.POST.get("recipe")
        image_file = request.files.get("image")
        if not recipe_json:
            return {"success": False, "errors": "Missing recipe data"}
        data = json.loads(recipe_json)
    else:
        data = request.json
        image_file = None

    name = data.get("name", "").strip()
    recipe_type = data.get("type", "").strip()
    description = data.get("description", "").strip()
    instruction_steps = data.get("instruction_steps", "").strip()
    servings = data.get("servings", 1)
    ingredients = data.get("ingredients", [])

    if not name:
        return {"success": False, "errors": "Recipe name is required"}

    try:
        # Insert recipe and commit immediately
        recipe_id = db.recipes.insert(
            name=name,
            type=recipe_type,
            description=description,
            instruction_steps=instruction_steps,
            servings=servings,
            author=auth.user_id,
            image=image_file,
        )
        db.commit()  #Critical to satisfy FK constraints

        # Loop over ingredients, verify existence, and link
        for ing in ingredients:
            ing_name = ing.get("name", "").strip().lower()
            qty = ing.get("quantity_per_serving", 0)

            if not ing_name or qty <= 0:
                continue  # skip bad inputs

            ing_record = db(db.ingredients.name.lower() == ing_name).select().first()
            if not ing_record:
                return {"success": False, "errors": f"Ingredient '{ing_name}' does not exist"}

            db.linking.insert(
                recipe_id=recipe_id,
                ingredient_id=ing_record.id,
                quantity_per_serving=qty,
            )

        db.commit()
        return {"success": True, "id": recipe_id}

    except Exception as e:
        db.rollback()
        import traceback
        return {
            "success": False,
            "errors": str(e),
            "traceback": traceback.format_exc()  # Optional: for debugging in dev
        }


@action("api/recipes/<recipe_id:int>", method=["PUT"])
@action.uses(db, auth.user)
def put_recipe(recipe_id):
    recipe = db.recipes[recipe_id]
    if not recipe or recipe.author != auth.user_id:
        abort(403)

    recipe_json = request.POST.get("recipe")
    image_file = request.files.get("image")
    if not recipe_json:
        return {"success": False, "errors": "Missing recipe data"}
    data = json.loads(recipe_json)
    if not data:
        return {"success": False, "errors": "Missing data"}

    ingredients = data.pop("ingredients", [])

    update_data = {
        "name": data.get("name"),
        "type": data.get("type"),
        "description": data.get("description"),
        "instruction_steps": data.get("instruction_steps"),
        "servings": data.get("servings")
    }
    if image_file:
        update_data["image"] = image_file

    image_name = recipe = db(db.recipes.id == recipe_id).select().first().image

    if recipe and image_name:
        file_path = os.path.join(os.path.dirname(__file__), 'uploads', image_name)

        os.remove(file_path)

    db(db.recipes.id == recipe_id).update(**update_data)
    db(db.linking.recipe_id == recipe_id).delete()

    for ing in ingredients:
        ing_name = ing.get("name", "").strip()
        if not ing_name:
            continue
        ing_record = db(db.ingredients.name.like(ing_name, case_sensitive=False)).select().first()
        if not ing_record:
            return {"success": False, "errors": f"Ingredient '{ing_name}' does not exist"}

        db.linking.insert(
            recipe_id=recipe_id,
            ingredient_id=ing_record.id,
            quantity_per_serving=ing.get("quantity_per_serving", 0),
        )

    db.commit()
    return {"success": True}

#This lets you delete the recipe
@action("api/recipes/<recipe_id:int>", method=["DELETE"])
@action.uses(db, auth.user)
def delete_recipe(recipe_id):
    recipe = db.recipes[recipe_id]
    if not recipe or recipe.author != auth.user_id:
        abort(403)

    db(db.linking.recipe_id == recipe_id).delete()
    db(db.recipes.id == recipe_id).delete()
    db.commit()
    return {"success": True}

# -------------------------
# Calorie Calculation API
# -------------------------

@action("api/recipes/<recipe_id:int>/calories", method=["GET"])
@action.uses(db)
def get_total_calories(recipe_id):
    links = db(db.linking.recipe_id == recipe_id).select()
    total = 0
    for link in links:
        ingredient = db.ingredients[link.ingredient_id]
        total += ingredient.calories_per_unit * link.quantity_per_serving
    return {"success": True, "total_calories": total}


# -------------------------------
# import recipies and ingrediants
# -------------------------------

from .importData import import_themealdb

@action('importData')
@action.uses(db, auth.user)
def importData():
    result = import_themealdb(db)
    return dict(message=result)


# -------------------------------
# Clears the recipe and ingrediant data
# -------------------------------

@action('clearAllData')
@action.uses(db)
def clear_all_data():
    """WARNING: Deletes ALL recipes, ingredients, and linking data"""
    
    # Delete in order to avoid foreign key constraints
    db(db.linking.id > 0).delete()  # Delete all linking entries
    db(db.recipes.id > 0).delete()  # Delete all recipes  
    db(db.ingredients.id > 0).delete()  # Delete all ingredients
    
    # https://www.tutorialspoint.com/How-to-delete-all-files-in-a-directory-with-Python
    path = os.path.join(os.path.dirname(__file__), 'uploads')
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.remove(file_path)

    db.commit()
    
    return dict(message="Deleted ALL data from recipes, ingredients, and linking tables")


# ------------------------------
# Fetch full recipe for editing
# ------------------------------

@action("api/recipes/<recipe_id:int>", method=["GET"])
@action.uses(db, auth.user)
def get_recipe(recipe_id):
    recipe = db.recipes[recipe_id]
    if not recipe or recipe.author != auth.user_id:
        abort(403)

    ingredients = []
    links = db(db.linking.recipe_id == recipe_id).select()

    for link in links:
        ing = db.ingredients[link.ingredient_id]
        ingredients.append({
            "name": ing.name,
            "quantity_per_serving": link.quantity_per_serving
        })

    return {
        "success": True,
        "recipe": {
            "id": recipe.id,
            "name": recipe.name,
            "type": recipe.type,
            "description": recipe.description,
            "instruction_steps": recipe.instruction_steps,
            "servings": recipe.servings,
            "ingredients": ingredients
        }
    }


# -------------------------
# Public Ingredient Search API
# -------------------------

@action("api/public/ingredients", method=["GET"])
@action.uses(db)
def public_get_ingredients():
    search = request.query.get("search", "").strip()

    query = db.ingredients.id > 0
    if search:
        query &= db.ingredients.name.contains(search)

    ingredients = db(query).select(orderby=db.ingredients.name).as_list()

    return {
        "success": True,
        "ingredients": ingredients
    }

@action('admin/fill_calories')
@action.uses(db, auth.user)
def fill_calories():
    # The same calorie lookup dictionary we used before
    calorie_lookup = {
        "chicken": 239, "chicken thighs": 239, "chicken legs": 239,
        "beef": 250, "pork": 242, "salmon": 208, "cod": 105, "haddock": 90, "tuna": 132,
        "egg": 78, "eggs": 78, "egg white": 17, "bread": 265,
        "rice": 130, "basmati rice": 130, "sushi rice": 130,
        "butter": 717, "olive oil": 884, "extra virgin olive oil": 884, "vegetable oil": 884,
        "cream": 345, "cream cheese": 350, "milk": 42, "semi-skimmed milk": 42,
        "yogurt": 59, "greek yogurt": 59, "cheese": 402, "mozzarella": 300, "gruyere": 413,
        "potato": 77, "potatoes": 77, "carrot": 41, "carrots": 41,
        "onion": 40, "onions": 40, "spring onions": 32, "red onions": 40,
        "garlic": 149, "garlic clove": 149, "ginger": 80, "ginger paste": 80,
        "green chilli": 40, "chilli powder": 282, "turmeric powder": 312, "coriander": 23,
        "coriander seeds": 298, "cumin seeds": 375, "ground cumin": 375, "cumin": 375,
        "paprika": 282, "black pepper": 251, "salt": 0, "pepper": 251,
        "sugar": 387, "brown sugar": 387, "granulated sugar": 387, "caster sugar": 387,
        "honey": 304, "soy sauce": 53, "oyster sauce": 51, "lemon": 29, "lemons": 29,
        "lime": 30, "tomato": 18, "tomatoes": 18, "cherry tomatoes": 18,
        "baby plum tomatoes": 18, "tomato puree": 82, "tomato ketchup": 112, "tomato sauce": 29,
        "avocado": 160, "spinach": 23, "cucumber": 16, "broccoli": 34, "cabbage": 25,
        "mushrooms": 22, "peas": 81, "kidney beans": 127, "chickpeas": 164,
        "lentils": 116, "beans": 127, "pasta": 131, "farfalle": 131, "noodles": 138,
        "breadcrumbs": 350, "plain flour": 364, "flour": 364, "starch": 330,
        "potato starch": 330, "cornstarch": 330, "coconut milk": 230, "coconut cream": 330,
        "double cream": 345, "bay leaf": 314, "bay leaves": 314, "thyme": 276,
        "rosemary": 131, "basil": 22, "oregano": 265, "mint": 44, "nutmeg": 525,
        "allspice": 263, "star anise": 337, "cardamom": 311, "cloves": 274,
        "cinnamon stick": 247, "vanilla extract": 288, "vinegar": 20,
        "white wine vinegar": 20, "red wine vinegar": 20, "malt vinegar": 20,
        "maple syrup": 260, "molasses": 290
    }

    updated = 0

    for row in db(db.ingredients).select():
        name_lower = row.name.lower().strip()
        calories = calorie_lookup.get(name_lower)
        if calories and row.calories_per_unit == 0:
            db(db.ingredients.id == row.id).update(calories_per_unit=calories)
            updated += 1

    db.commit()
    return dict(message=f"Calories updated for {updated} ingredients")
