"use client";

import { Button } from "@/components/ui/button";
import { useTags } from "@/hooks/useTags";

export default function TagSelector({ selectedTags, setSelectedTags }: {
  selectedTags: string[];
  setSelectedTags: (tags: string[]) => void;
}) {
  const { tags, toggleTag } = useTags();

  return (
    <div className="flex flex-wrap gap-2">
      {tags.map((tag) => (
        <Button
          key={tag}
          variant={selectedTags.includes(tag) ? "default" : "outline"}
          onClick={() => {
            const updatedTags = selectedTags.includes(tag)
              ? selectedTags.filter((t) => t !== tag)
              : [...selectedTags, tag];
            setSelectedTags(updatedTags);
          }}
        >
          {tag}
        </Button>
      ))}
    </div>
  );
}