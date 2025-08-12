"use client";

import { Wand2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { usePresentationState } from "@/states/presentation-state";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { PresentationInput } from "./PresentationInput";
import { PresentationControls } from "./PresentationControls";
import { PresentationTemplates } from "./PresentationTemplates";
import { RecentPresentations } from "./RecentPresentations";
import { PresentationExamples } from "./PresentationExamples";
import { PresentationsSidebar } from "./PresentationsSidebar";
import { useEffect } from "react";
import { PresentationHeader } from "./PresentationHeader";
import { createEmptyPresentation } from "@/app/_actions/presentation/presentationActions";

export function PresentationDashboard() {
  const router = useRouter();
  const {
    presentationInput,
    isGeneratingOutline,
    setCurrentPresentation,
    setIsGeneratingOutline,
    // We'll use these instead of directly calling startOutlineGeneration
    setShouldStartOutlineGeneration,
    language,
    numSlides,

  } = usePresentationState();

  useEffect(() => {
    setCurrentPresentation("", "");
    // Make sure to reset any generation flags when landing on dashboard
    setIsGeneratingOutline(false);
    setShouldStartOutlineGeneration(false);
  }, []);

  const handleGenerate = async () => {
    console.time("createEmptyPresentation");
    if (!presentationInput.trim()) {
      toast.error("Please enter a topic for your presentation");
      return;
    }
    setIsGeneratingOutline(true);
    console.log('language=>',language)
    console.log('numSlides=>',numSlides)

    try {
      const result = await createEmptyPresentation(
        presentationInput || "Untitled Presentation",
        "default",
        language,
        numSlides
      );
      console.timeEnd("createEmptyPresentation");
      if (result.success && result.presentation) {
        setCurrentPresentation(
          result.presentation.id,
          result.presentation.title
        );
        router.push(`/presentation/generate/${result.presentation.id}`);
      } else {
        setIsGeneratingOutline(false);
        toast.error(result.message || "Failed to create presentation");
      }
    } catch (error) {
      setIsGeneratingOutline(false);
      console.error("Error creating presentation:", error);
      toast.error("Failed to create presentation");
    }
  };

  const handleCreateBlank = async () => {
    try {
      setIsGeneratingOutline(true);
      const result = await createEmptyPresentation("Untitled Presentation", "default", language);
      if (result.success && result.presentation) {
        setCurrentPresentation(
          result.presentation.id,
          result.presentation.title
        );
        router.push(`/presentation/generate/${result.presentation.id}`);
      } else {
        setIsGeneratingOutline(false);
        toast.error(result.message || "Failed to create presentation");
      }
    } catch (error) {
      setIsGeneratingOutline(false);
      console.error("Error creating presentation:", error);
      toast.error("Failed to create presentation");
    }
  };

  return (
    <div className="notebook-section relative w-full">
      <PresentationsSidebar />

      <div className="mx-auto w-full max-w-4xl space-y-12 px-6 py-12">
        <PresentationHeader />


        <div className="space-y-8">
          <PresentationInput />

          <PresentationControls />
          <div className="flex items-center justify-end">
            <div className="flex items-center gap-2">
              <Button
                onClick={handleGenerate}
                disabled={!presentationInput.trim() || isGeneratingOutline}
                variant={isGeneratingOutline ? "loading" : "default"}
                className="gap-2"
              >
                <Wand2 className="h-4 w-4" />
               生成演示文稿
              </Button>
              <Button
                variant="outline"
                onClick={handleCreateBlank}
                className="gap-2"
              >
                <Plus className="h-4 w-4" />
                Create Blank
              </Button>
            </div>
          </div>
        </div>

        <PresentationExamples />
        <RecentPresentations />
        <PresentationTemplates />
      </div>
    </div>
  );
}
