"use client";

import { useEffect, useState, useRef } from "react";

export function useVoiceRecognition(
    onCommand: (command: string) => void,
    isActive: boolean,
    tags: string[],
    onTagDetected: (tag: string) => void
) {
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const tagsRef = useRef<string[]>(tags);

  // Sync updated tags whenever `tags` changes
  useEffect(() => {
    tagsRef.current = tags; // ✅ Always use the latest tags inside voice recognition
    console.log("Updating tags for voice recognition:", tags);
  }, [tags]);

  useEffect(() => {
    if (!("webkitSpeechRecognition" in window)) {
      console.warn("Speech recognition is not supported in this browser.");
      return;
    }

    if (!recognitionRef.current) {
      recognitionRef.current = new (window as any).webkitSpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = "en-US";

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
        console.log("Voice command detected:", transcript);

       if (["accept", "reject", "classify", "filter", "good", "bad", "submit"].includes(transcript)) {
         setTimeout(() => onCommand(transcript), 100);
       }

       console.log("Checking tag in updated tags:", tagsRef.current); // ✅ Always gets latest tags

        // Check if the command matches any available tag
        const detectedTag = tagsRef.current.find(tag => transcript.includes(tag.toLowerCase()));
        if (detectedTag) {
          console.log(`Tag detected from voice: ${detectedTag}`);
          onTagDetected(detectedTag);
        }

      };

      recognitionRef.current.onerror = (event: any) => {
        console.log("Speech recognition error:", event);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        console.log("Speech recognition ended.");
      };
    }

     // ✅ Prevent double start
    if (isActive && !isListening) {
      console.log("Starting speech recognition...");
      recognitionRef.current.start();
      setIsListening(true);
    } else if (!isActive && isListening) {
      console.log("Stopping speech recognition...");
      recognitionRef.current.stop();
      setIsListening(false);
    }

    return () => {
      recognitionRef.current?.stop();
    };
  }, [isActive, tags]);

  return {
    isListening,
    start: () => {
      recognitionRef.current?.start();
      setIsListening(true);
    },
    stop: () => {
      recognitionRef.current?.stop();
      setIsListening(false);
    },
  };
}