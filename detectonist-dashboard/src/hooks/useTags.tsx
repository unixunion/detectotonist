"use client";

import { useState, useEffect } from "react";

export function useTags() {
  const [tags, setTags] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");

  // Fetch tags from API
  const fetchTags = async () => {
    try {
      const res = await fetch("/api/tags");
      const data = await res.json();
      setTags(data.tags || []);
    } catch (error) {
      console.error("Error fetching tags:", error);
    }
  };

  useEffect(() => {
    fetchTags();
  }, []);

  // Toggle tag selection
  const toggleTag = (tag: string) => {
    setSelectedTags((prevTags) =>
      prevTags.includes(tag) ? prevTags.filter((t) => t !== tag) : [...prevTags, tag]
    );
  };

  // Clear selected tags
  const clearSelectedTags = () => {
    setSelectedTags([]);
  };

  // Add new tag
  const addTag = async () => {
    if (!newTag.trim()) return;
    try {
      await fetch(`/api/tags/add/${encodeURIComponent(newTag)}`, { method: "POST" });
      setNewTag(""); // Reset input field
      fetchTags(); // Refresh tag list
    } catch (error) {
      console.error("Error adding tag:", error);
    }
  };

  // Delete tag
  const deleteTag = async (tag: string) => {
    try {
      await fetch(`/api/tags/del/${encodeURIComponent(tag)}`, { method: "POST" });
      fetchTags(); // Refresh tag list
    } catch (error) {
      console.error("Error deleting tag:", error);
    }
  };

  return {
    tags,
    selectedTags,
    newTag,
    setNewTag,
    toggleTag,
    clearSelectedTags,
    addTag,
    deleteTag,
  };
}