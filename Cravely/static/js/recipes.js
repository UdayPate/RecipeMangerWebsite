"use strict";

const app = Vue.createApp({
  data() {
    return {
      recipes_list: [],
      search_bar: "",
      name_search: "",
      type_search: "",
      user_id: null,
      api_url: "/Cravely/api/recipes", // default to private
    };
  },
  methods: {
    async fetchUserId() {
      try {
        const res = await fetch("/Cravely/api/user");
        const data = await res.json();
        if (data?.id) {
          this.user_id = data.id;
          this.api_url = "/Cravely/api/recipes";
        } else {
          throw new Error("Not logged in");
        }
      } catch {
        this.user_id = null;
        this.api_url = "/Cravely/api/public/recipes";
      }
    },
    async load_data() {
      try {
        const params = new URLSearchParams();
        if (this.name_search.trim()) {
          params.append("name", this.name_search.trim());
        } else if (this.type_search.trim()) {
          params.append("type", this.type_search.trim());
        }

        const res = await fetch(`${this.api_url}?${params.toString()}`);
        const result = await res.json();

        if (result.success) {
          for (const recipe of result.recipes) {
            try {
              const calRes = await fetch(`/Cravely/api/recipes/${recipe.id}/calories`);
              const calData = await calRes.json();
              recipe.total_calories = calData.success ? calData.total_calories : "N/A";
            } catch {
              recipe.total_calories = "N/A";
            }
          }

          this.recipes_list = result.recipes;
        } else {
          console.error("Failed to load recipes:", result.errors);
        }
      } catch (error) {
        console.error("Fetch error:", error);
      }
    },

    async deleteRecipe(recipe_id) {
      if (!confirm("Are you sure you want to delete this recipe?")) return;

      try {
        const res = await fetch(`/Cravely/api/recipes/${recipe_id}`, {
          method: "DELETE",
        });
        const data = await res.json();
        if (data.success) {
          this.load_data();
        } else {
          alert("Failed to delete recipe.");
        }
      } catch (err) {
        console.error("Error deleting recipe:", err);
      }
    },

    editRecipe(recipe_id) {
      window.location.href = `/Cravely/upload?edit=${recipe_id}`;
    },
  },
  watch: {
    name_search() {
      this.load_data();
    },
    type_search() {
      this.load_data();
    },
  },
  async mounted() {
    await this.fetchUserId();
    this.load_data();
  },
});

app.mount("#myapp");
