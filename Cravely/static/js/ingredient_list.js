"use strict";

const app = Vue.createApp({
  data() {
    return {
      ingredients: [],
      new_ingredient: {
        name: "",
        unit: "",
        calories_per_unit: 0,
        description: ""
      },
      searchTerm: "",
      error: "",
      success: ""
    };
  },
  methods: {
    async fetchIngredients(search = "") {
      try {
        const url = search ? `/Cravely/api/ingredients?search=${encodeURIComponent(search)}` : "/Cravely/api/ingredients";
        const res = await fetch(url);
        const data = await res.json();
        if (data.success) {
          this.ingredients = data.ingredients;
        }
      } catch (err) {
        this.error = "Failed to load ingredients.";
        console.error(err);
      }
    },
    async addIngredient() {
      this.error = "";
      this.success = "";
      if (!this.new_ingredient.name) {
        this.error = "Name is required.";
        return;
      }
      try {
        const res = await fetch("/Cravely/api/ingredients", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(this.new_ingredient)
        });
        const result = await res.json();
        if (result.success) {
          this.success = "Ingredient added successfully!";
          this.new_ingredient = { name: "", unit: "", calories_per_unit: 0, description: "" };
          this.fetchIngredients(); // reload
        } else {
          this.error = result.errors || "Failed to add ingredient.";
        }
      } catch (err) {
        this.error = "An error occurred.";
        console.error(err);
      }
    },
    searchIngredients() {
      this.fetchIngredients(this.searchTerm);
    }
  },
  mounted() {
    this.fetchIngredients();
  }
});

app.mount("#app");
