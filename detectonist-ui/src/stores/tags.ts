// stores/tags.ts
import { defineStore } from "pinia";
import { ref } from "vue";

export const useTagsStore = defineStore("tags", () => {
    const tags = ref<string[]>([]);

    // Fetch tags from API
    const fetchTags = async () => {
        try {
            const res = await fetch("/api/tags");
            const data = await res.json();
            tags.value = data.tags || [];
        } catch (error) {
            console.error("Error fetching tags:", error);
        }
    };

    // Add a new tag
    const addTag = async (tag: string) => {
        if (!tag.trim()) return;
        try {
            await fetch(`/api/tags/add/${encodeURIComponent(tag)}`, { method: "POST" });
            await fetchTags(); // Refresh tags after adding
        } catch (error) {
            console.error("Error adding tag:", error);
        }
    };

    // Delete a tag
    const deleteTag = async (tag: string) => {
        try {
            await fetch(`/api/tags/del/${encodeURIComponent(tag)}`, { method: "POST" });
            await fetchTags(); // Refresh tags after deleting
        } catch (error) {
            console.error("Error deleting tag:", error);
        }
    };

    return { tags, fetchTags, addTag, deleteTag };
});