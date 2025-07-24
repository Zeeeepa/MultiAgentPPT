// route.ts
import { NextResponse } from "next/server";
import { A2AClient, Message } from "@a2a-js/sdk";
import crypto from "node:crypto";
import { languages } from "prismjs";

interface SlidesRequest {
  title: string;
  outline: string[];
  language: string;
  tone: string;
  numSlides: number;
}

function generateId() {
  return crypto.randomUUID();
}

const A2A_AGENT_SERVER_URL = process.env.A2A_AGENT_SLIDES_URL ?? "http://localhost:10011";

async function* generateSlidesStream(
  serverUrl: string,
  slidesRequest: SlidesRequest,
): AsyncGenerator<string> {
  const client = new A2AClient(serverUrl);
  const messageId = generateId();
  const content = `Please generate a presentation with the following details:
Title: ${slidesRequest.title}
Language: ${slidesRequest.language}
Tone for images: ${slidesRequest.tone}

Outline:
${slidesRequest.outline.map((item, index) => `${index + 1}. ${item}`).join("\n")}
`;

  const message: Message = {
    messageId,
    kind: "message",
    role: "user",
    parts: [{ kind: "text", text: content }],
    metadata: {language: slidesRequest.language, tone: slidesRequest.tone, numSlides: slidesRequest.numSlides}
  };

  try {
    const stream = client.sendMessageStream({ message });
    for await (const event of stream) {
      console.log("收到后端的event", event)
      if (
        event.kind === "status-update" &&
        event.status?.message?.parts
      ) {
        for (const part of event.status.message.parts) {
          if (part.kind === "text") {
            const metadata = event.status.message.metadata ?? "";
            yield JSON.stringify({ type: "status-update", data: part.text, metadata }) + "\n";
          }
        }
      } else if (
        event.kind === "artifact-update" &&
        event.artifact?.parts
      ) {
        for (const part of event.artifact.parts) {
          if (part.kind === "text") {
            const metadata = event.artifact.metadata ?? "";
            yield JSON.stringify({ type: "artifact-update", data: part.text, metadata }) + "\n";
          }
        }
      }
    }
  } catch (error) {
    console.error("Error communicating with A2A client:", error);
    yield JSON.stringify({ type: "error", data: (error as Error).message }) + "\n";
  }
}

export async function POST(req: Request) {
  try {
    const { title, outline, language, tone, numSlides } = (await req.json()) as SlidesRequest;

    if (!title || !outline || !Array.isArray(outline) || !language) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
    }

    const stream = new ReadableStream({
      async start(controller) {
        const generator = generateSlidesStream(A2A_AGENT_SERVER_URL, {
          title,
          outline,
          language,
          tone,
          numSlides
        });

        for await (const chunk of generator) {
          controller.enqueue(new TextEncoder().encode(chunk));
        }
        controller.close();
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "application/json; charset=utf-8", // NDJSON but keep JSON-type
        "Transfer-Encoding": "chunked",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
      },
    });
  } catch (error) {
    console.error("Error in presentation generation:", error);
    return NextResponse.json({ error: "Failed to generate presentation slides" }, { status: 500 });
  }
}
