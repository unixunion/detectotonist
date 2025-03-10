"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useTags } from "@/hooks/useTags";

export default function TagManager() {
  const { tags, newTag, setNewTag, addTag, deleteTag } = useTags();

  return (
    <div className="space-y-4">
      <div className="flex space-x-2">
        <Input
          value={newTag}
          onChange={(e) => setNewTag(e.target.value)}
          placeholder="New tag..."
        />
        <Button onClick={addTag}>Add</Button>
      </div>

      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <div key={tag} className="flex items-center gap-2 border rounded p-2">
            <span>{tag}</span>
            <Button size="sm" variant="destructive" onClick={() => deleteTag(tag)}>
              ✕
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}