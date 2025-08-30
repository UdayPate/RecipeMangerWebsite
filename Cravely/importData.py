import requests
import re
from pydal import DAL
import uuid
import os

def import_themealdb(db):
    existing_recipes = db(db.recipes.name.contains("TheMealDB")).count()
    if existing_recipes > 0:
        return "Data already imported!"
    
    api_urls = [
        "https://www.themealdb.com/api/json/v1/1/search.php?s=chicken",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=pasta", 
        "https://www.themealdb.com/api/json/v1/1/search.php?s=beef",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=fish",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=rice",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=pizza",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=soup",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=salad",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=pork",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=vegetarian",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=dessert",
        "https://www.themealdb.com/api/json/v1/1/search.php?s=breakfast"
    ]
    
    imported_count = 0
    
    for url in api_urls:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                meals = data.get('meals', [])
                
                for meal in meals[:5]:
                    image_name = download_image(meal.get('strMealThumb',None))
                    if meal:
                        recipe_id = db.recipes.insert(
                            name=meal.get('strMeal', 'Unknown Recipe'),
                            type=meal.get('strCategory', 'Main Course'),
                            description=f"Imported from TheMealDB - {meal.get('strArea', 'International')} cuisine",
                            image=image_name,
                            author=6,
                            instruction_steps=meal.get('strInstructions', 'No instructions available'),
                            servings=4
                        )
                        
                        for i in range(1, 21):
                            ingredient_name = meal.get(f'strIngredient{i}', '').strip()
                            measure = meal.get(f'strMeasure{i}', '').strip()
                            
                            if ingredient_name:
                                existing_ingredient = db(db.ingredients.name == ingredient_name).select().first()
                                
                                if not existing_ingredient:
                                    ingredient_id = db.ingredients.insert(
                                        name=ingredient_name,
                                        unit=extract_unit(measure),
                                        calories_per_unit=0,
                                        description=f"Imported from TheMealDB"
                                    )
                                else:
                                    ingredient_id = existing_ingredient.id
                                
                                if measure:
                                    quantity = extract_quantity(measure)
                                    db.linking.insert(
                                        recipe_id=recipe_id,
                                        ingredient_id=ingredient_id,
                                        quantity_per_serving=quantity
                                    )
                        
                        imported_count += 1
                        
        except Exception as e:
            print(f"Error importing from {url}: {e}")
    
    db.commit()
    return f"Successfully imported {imported_count} recipes from TheMealDB!"

def extract_unit(measure_string):
    if not measure_string:
        return "piece"
    
    units = ['cup', 'cups', 'tbsp', 'tsp', 'oz', 'lb', 'lbs', 'ml', 'g', 'kg', 'clove', 'cloves']
    measure_lower = measure_string.lower()
    
    for unit in units:
        if unit in measure_lower:
            return unit
    
    return "piece"

def extract_quantity(measure_string):
    if not measure_string:
        return 1.0
    
    numbers = re.findall(r'\d+(?:\.\d+)?|\d+/\d+', measure_string)
    
    if numbers:
        try:
            if '/' in numbers[0]:
                parts = numbers[0].split('/')
                return float(parts[0]) / float(parts[1])
            else:
                return float(numbers[0])
        except:
            return 1.0
    
    return 1.0

# https://stackoverflow.com/questions/30229231/python-save-image-from-url
# https://www.geeksforgeeks.org/how-to-download-an-image-from-a-url-in-python/
def download_image(image_url):
    # print(image_url)
    if image_url == None:
        return None
    file_name = str(uuid.uuid4())
    data = requests.get(image_url).content
    real_file_name = file_name + '.jpg'
    real_file_name_with_path = os.path.join(os.path.dirname(__file__),"uploads",real_file_name)
    fd = open(real_file_name_with_path, 'wb')
    fd.write(data)
    fd.close()

    return real_file_name