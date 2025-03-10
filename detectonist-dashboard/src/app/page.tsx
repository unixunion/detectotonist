"use client";

import { useTags } from "@/hooks/useTags";
import TagManager from "@/components/ui/TagManager";
import { useVoiceRecognition } from "@/hooks/VoiceRecognition";

import Image from "next/image";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs"
import {Separator} from "@/components/ui/separator";

export default function Home() {
  const [filterData, setFilterData] = useState(null);
  const [classifyData, setClassifyData] = useState(null);
  const [goodBad, setGoodBad] = useState<"good" | "bad" | null>(null);
  const [samples, setSamples] = useState<{ files: string }[]>([]);
  const { tags, selectedTags, toggleTag, clearSelectedTags } = useTags();
  const [activeTab, setActiveTab] = useState("filter");
  // const [loadedTags, setLoadedTags] = useState<string[]>([]);

  const { isListening, start, stop } = useVoiceRecognition(
      handleVoiceCommand,
      true,
      tags,
      handleTagVoiceCommand
  ); //  activeTab === "filter"

  useEffect(() => {
    console.log("Tags loaded:", tags);
  }, [tags]);

  useEffect(() => {
    // console.log("Updated filterData:", filterData);
  }, [filterData]);

  useEffect(() => {
    console.log("Active tab changed:", activeTab);
    setTimeout(() => setActiveTab(activeTab), 0);
  }, [activeTab]);

  // auto invokes classify when bad/good is set.
  useEffect(() => {
    if (goodBad && classifyData) {
      console.log("Triggering classification after state update:", goodBad);
      handleClassify();
    }
  }, [goodBad]);

  // Submit classification to the api
  const handleClassify = async () => {
    if (!classifyData || !goodBad)
    {
      console.log("ClassifyData or goodBad not set!");
      return;
    }

    await fetch("/api/classify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: classifyData.filename,
        status: goodBad,
        tags: selectedTags,
      }),
    });

    // Refresh for the next file
    fetch("/api/next_classify_file")
      .then(res => res.json())
      .then(data => setClassifyData(data));

    // Reset state
    setGoodBad(null);
    clearSelectedTags();
  };

  // Function to fetch next file from Flask API
  const fetchFiles = async (type: "filter" | "classify" | "samples") => {
    try {
      const res = await fetch(`/api/next_${type}_file`);
      const data = await res.json();
      // console.log(`${type} data received:`, data);

      if (type === "filter") {
        setFilterData(data);
      } else if (type == "classify") {
        setClassifyData(data);
      } else {
        setSamples(data.files || []);
      }
    } catch (error) {
      console.error(`Error fetching ${type} file:`, error);
    }
  };

  // Poll every 5 seconds to check for new files
  useEffect(() => {
    fetchFiles("filter");
    fetchFiles("classify");
    fetchFiles("samples");

    const interval = setInterval(() => {
      fetchFiles("filter");
      fetchFiles("classify");
      fetchFiles("samples");
    }, 1000);

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, []);


  // Handle delete
  const handleDeleteSample = async (filename: string) => {
    await fetch(`/api/samples/delete/${filename}`, { method: "POST" });
    // setSamples(prevSamples => prevSamples.filter(sample => sample !== filename));
  };

  // Handle send back to classify
  const handleReclassifySample = async (filename: string) => {
    await fetch(`/api/samples/reclassify/${filename}`, { method: "POST" });
    // setSamples(prevSamples => prevSamples.filter(sample => sample !== filename));
  };


  const handleFilter = async (status: string) => {
    setFilterData((prevFilterData) => {
      if (!prevFilterData) {
        console.warn("No filterData available, skipping filter request.");
        return prevFilterData;
      }

      fetch("/api/filter", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename: prevFilterData.filename, status }),
      });

      fetch("/api/next_filter_file")
        .then(res => res.json())
        .then(data => setFilterData(data));

      return prevFilterData; // Ensure state update function is returned
    });
  };

  function handleVoiceCommand(command: string) {
    if (command === "accept") {
      console.log("handleFilter accept");
      setTimeout(() => handleFilter("accept"), 0);
    } else if (command === "reject") {
      console.log("handleFilter reject");
      setTimeout(() => handleFilter("reject"), 0);
    } else if (command === "classify") {
      console.log("Switching to classify tab");
      setTimeout(() => {setActiveTab("classify")}, 10);
    } else if (command === "filter") {
      console.log("Switching to filter tab");
      setTimeout(() => setActiveTab("filter"), 0);
    } else if (command === "good") {
      console.log("Setting classification to good");
      setGoodBad("good");
    } else if (command === "bad") {
      console.log("Setting classification to bad");
      setGoodBad("bad");
    } else if (command === "submit") {
      console.log("Submitting classification");
      handleClassify();
    }
  }

  function handleTagVoiceCommand(tag: string) {
    console.log(`Toggling tag from voice: ${tag}`);
    toggleTag(tag);
  }

  return (
    <Tabs value={activeTab} onValueChange={(val) => setActiveTab(val)} className="w-full max-w-3xl mx-auto">

      {/* Tabs */}
      <TabsList className="grid grid-cols-4 w-full">
        <TabsTrigger value="filter">Filter</TabsTrigger>
        <TabsTrigger value="classify">Classify</TabsTrigger>
        <TabsTrigger value="samples">Samples</TabsTrigger>
        <TabsTrigger value="settings">Settings</TabsTrigger>
      </TabsList>

      {/* FILTER TAB */}
      <TabsContent value="filter">
        {filterData && filterData.status === "ok" ? (
          <Card>
            <CardHeader>
              <CardTitle>Capturing Samples</CardTitle>
              <CardDescription>Click or Say: Accept or Reject</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Image src={filterData.spectrogram} width={500} height={500} alt="Spectrogram" />
              <audio controls>
                <source src={filterData.audio} type="audio/wav" />
              </audio>
              <div className="space-x-2">
                <Button onClick={() => handleFilter("accept")}>Accept</Button>
                <Button onClick={() => handleFilter("reject")} variant="destructive">
                  Reject
                </Button>
              </div>

            </CardContent>
            <Button onClick={isListening ? stop : start}>
              {isListening ? "🎤 Listening" : "Start Voice Recognition"}
            </Button>
          </Card>
        ) : (
            <Card>
              <CardContent>
                <p>No samples to filter</p>
              </CardContent>
              <Button onClick={isListening ? stop : start}>
                {isListening ? "🎤 Listening" : "Start Voice Recognition"}
              </Button>
            </Card>
        )}



      </TabsContent>

      {/* CLASSIFY TAB */}
      <TabsContent value="classify">
        {classifyData && classifyData.status === "ok" ? (
          <Card>
            <CardHeader>
              <CardTitle>Classify</CardTitle>
              <CardDescription>Classify the sample</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {/* Spectrogram Image */}
              <Image src={classifyData.spectrogram} width={500} height={500} alt="Spectrogram" />

              {/* Audio Player */}
              <audio controls>
                <source src={classifyData.audio} type="audio/wav" />
              </audio>



              {/* Tag Selection */}
              <div className="flex flex-wrap gap-2">
                {tags.map((tag) => (
                  <Button
                    key={tag}
                    variant={selectedTags.includes(tag) ? "default" : "outline"}
                    onClick={() => toggleTag(tag)}
                  >
                    {tag}
                  </Button>
                ))}
              </div>

              <Separator className="my-4" />

               {/* Good/Bad Selection */}
              <div className="flex space-x-4">
                <Button
                  variant={goodBad === "good" ? "default" : "outline"}
                  onClick={() => setGoodBad("good")}
                >
                  Good
                </Button>
                <Button
                  variant={goodBad === "bad" ? "destructive" : "outline"}
                  onClick={() => setGoodBad("bad")}
                >
                  Bad
                </Button>
              </div>

            </CardContent>

          </Card>
        ) : (
          <p>No files available</p>
        )}
      </TabsContent>

      {/* Samples Tab */}
      <TabsContent value="samples">
        <Card>
          <CardHeader>
            <CardTitle>Samples</CardTitle>
          </CardHeader>
          <CardContent>
            {samples.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Filename</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {samples.map((filename) => (
                    <TableRow key={filename}>
                      <TableCell>{filename}</TableCell>
                      <TableCell className="text-right space-x-2">
                        <Button onClick={() => handleReclassifySample(filename)} size="sm">
                          Reclassify
                        </Button>
                        <Button onClick={() => handleDeleteSample(filename)} size="sm" variant="destructive">
                          Delete
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p>No samples available</p>
            )}
          </CardContent>
        </Card>
      </TabsContent>


      <TabsContent value="settings">
        <Card>
          <CardHeader>
            <CardTitle>Settings</CardTitle>
            <CardDescription>Manage tags</CardDescription>
          </CardHeader>

          <CardContent className="space-y-2">
            {/* Tag Management */}
            <TagManager />
          </CardContent>

          <CardFooter>
            <Button>Shutdown</Button>
          </CardFooter>
        </Card>
      </TabsContent>
    </Tabs>
  );
}
