import { NextResponse } from "next/server";
// app/a2aexample/api/outline/route.ts
import { A2AClient, Message } from "@a2a-js/sdk";
import crypto from "node:crypto";
import {LangChainAdapter} from "ai"; // crypto is a built-in Node.js module

interface OutlineRequest {
    prompt: string;
    numberOfCards: number;
    language: string;
}

function generateId() {
  return crypto.randomUUID();
}
// A2A Agent 服务器的 URL。
// 在生产环境中，这应该从环境变量中读取。
const A2A_AGENT_SERVER_URL = process.env.A2A_AGENT_OUTLINE_URL ?? "http://localhost:10001";

console.log("A2A Agent Server URL:", A2A_AGENT_SERVER_URL);

/**
 * Creates an async generator that streams text content from the A2A agent.
 * @param {string} serverUrl - The URL of the A2A agent server.
 * @param {string} content - The user input (e.g., title for outline generation).
 * @yields {string} Each chunk of text received from the agent.
 */

function iteratorToStream(iterator: AsyncGenerator<string>): ReadableStream<string> {
  return new ReadableStream({
    async pull(controller) {
      const { value, done } = await iterator.next();
      if (done) {
        controller.close();
      } else {
        controller.enqueue(value);
      }
    },
  });
}

async function* generateOutlineStream(serverUrl: string, content: string, language: string) {
  const client = new A2AClient(serverUrl);

  const messageId = generateId();
  const message: Message = {
    messageId,
    kind: "message",
    role: "user",
    parts: [{ kind: "text", text: content }],
    metadata: { language: language}, // You can adjust the number of slides as needed
    // For a new outline, we typically start a new task/context.
    // If you need to continue a conversation, you'd pass taskId/contextId here.
  };

  try {
    const stream = client.sendMessageStream({ message });
    for await (const event of stream) {
      console.log("Received event:", event);
      // 处理 status-update 事件中嵌套的 message
      if (event.kind === "status-update" && event.status && event.status.message) {
        const nestedMessage = event.status.message;
        for (const part of nestedMessage.parts) {
          if (part.kind === "text") {
            console.log("Yielding text part (from status-update message):", part.text);
            //生成状态更新消息中包含的文本内容
            yield part.text; // Yield the text content
          }
        }
      }
      // --- 新增：处理 artifact-update 事件 ---
      else if (event.kind === "artifact-update" && event.artifact && event.artifact.parts) {
        console.log("Processing artifact-update event.");
        // 遍历 artifact 的 parts。Artifact 的 parts 也可能包含 text 或其他类型 (如 file)
        for (const part of event.artifact.parts) {
          if (part.kind === "text") {
            console.log("Yielding text part (from artifact):", part.text);
            //生成的artifact中包含的文本内容
            // yield part.text; // 将 Artifact 中的文本内容也输出
          }
        }
      }else {
        console.log("Received event (ignoring):", event);
      }
    }
  } catch (error) {
    console.error("Error communicating with A2A client:", error);
    // Rethrow or yield an error message to the consumer
    yield `Error: Failed to communicate with agent. ${error}`;
  }
}
export async function POST(request: Request) {
  try {
    const { prompt, numberOfCards, language } =
    (await request.json()) as OutlineRequest;

    if (!prompt || !numberOfCards || !language) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 },
      );
    }
    const stream = iteratorToStream(generateOutlineStream(A2A_AGENT_SERVER_URL, prompt, language));
    return LangChainAdapter.toDataStreamResponse(stream);
  } catch (error) {
    console.error("Error in presentation outline:", error);
    return NextResponse.json(
      { error: "Failed to generate presentation outline" },
      { status: 500 },
    );
  }
}
