"""
This file defines the database models
"""

from pydal.validators import *

from .common import Field, db, auth

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#

# Ingredients table
db.define_table("ingredients", 
                Field("name", "string", unique=True, requires=IS_NOT_EMPTY()), #change to is not empty
                Field("unit", "string", default=""),
                Field("calories_per_unit", "integer", default=0),
                Field("description", "text", default=""),
                auth.signature,)

# Recipes table
db.define_table("recipes",
                Field("name", "string", default=""),
                Field("type", "string", default=""),
                Field("description", "text", default=""),
                Field("image", "upload"),
                Field("author", "reference auth_user"),
                Field("instruction_steps", "text", default=""), #change to text
                Field("servings", "integer", default=1),
                auth.signature,)

# Linking table
db.define_table("linking",
    Field("recipe_id", "reference recipes"),
    Field("ingredient_id", "reference ingredients"),
    Field("quantity_per_serving", "double", default=0),
)

# Commit 
db.commit()