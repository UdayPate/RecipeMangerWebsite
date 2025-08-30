"use strict";

const app = Vue.createApp({
  data() {
    return {
      recipe: {
        name: "",
        type: "",
        description: "",
        instruction_steps: "",
        servings: 1,
        ingredients: [],
      },
      new_ingredient: {
        name: "",
        quantity_per_serving: 0
      },
      editMode: false,
      editRecipeId: null,
      image: null,
    };
  },

  methods: {
    add_ingredient() {
      const name = this.new_ingredient.name.trim();
      const qty = this.new_ingredient.quantity_per_serving;

      if (name && qty > 0) {
        this.recipe.ingredients.push({ name, quantity_per_serving: qty });
        this.new_ingredient.name = "";
        this.new_ingredient.quantity_per_serving = 0;
      }
    },

    remove_ingredient(index) {
      this.recipe.ingredients.splice(index, 1);
    },

    uploadImage(event) {
      this.image = event.target.files[0];
    },

    async submit_recipe() {
      try {
        let response;
        if (this.editMode) {
          const formData = new FormData();
          formData.append("recipe", JSON.stringify(this.recipe));
          if (this.image) {
            formData.append("image", this.image);
          }
          // Update existing recipe
          response = await fetch(`/Cravely/api/recipes/${this.editRecipeId}`, {
            method: "PUT",
            // headers: { "Content-Type": "application/json" },
            body: formData
          });
        } else {
          // Create new recipe

          const formData = new FormData();
          formData.append("recipe", JSON.stringify(this.recipe));
          if (this.image) {
            formData.append("image", this.image);
          }

          response = await fetch("/Cravely/api/recipes", {
            method: "POST",
            // headers: { "Content-Type": "application/json" },
            body: formData
          });
        }

        const result = await response.json();
        if (result.success) {
          alert(this.editMode ? "Recipe updated!" : "Recipe submitted successfully!");
          window.location.href = "/Cravely/recipes";  // go back to recipe list after save
        } else {
          alert("Error: " + result.errors);
        }
      } catch (error) {
        console.error("Submission failed:", error);
        alert("Something went wrong.");
      }
    },

    async load_recipe_for_edit() {
      const urlParams = new URLSearchParams(window.location.search);
      const editId = urlParams.get("edit");
      if (!editId) return;

      this.editMode = true;
      this.editRecipeId = editId;

      try {
        const res = await fetch(`/Cravely/api/recipes/${editId}`);
        const data = await res.json();

        if (data.success) {
          const recipeData = data.recipe;
          this.recipe.name = recipeData.name;
          this.recipe.type = recipeData.type;
          this.recipe.description = recipeData.description;
          this.recipe.instruction_steps = recipeData.instruction_steps;
          this.recipe.servings = recipeData.servings;
          this.recipe.ingredients = recipeData.ingredients;
        } else {
          alert("Failed to load recipe.");
        }
      } catch (err) {
        console.error("Error loading recipe:", err);
        alert("Error loading recipe.");
      }
    }
  },

  async mounted() {
    await this.load_recipe_for_edit();
  }
});

app.mount("#app");

