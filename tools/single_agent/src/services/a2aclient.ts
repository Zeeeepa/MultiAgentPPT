// Converted version: Wraps main loop logic in a function that accepts input strings, and exposes helper functions
import { A2AClient } from "@a2a-js/sdk";

// --- ANSI Colors ---
const colors = {
  reset: "\x1b[0m",
  bright: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
  gray: "\x1b[90m",
};

function colorize(color, text) {
  return `${colors[color]}${text}${colors.reset}`;
}
function generateId() {
  return crypto.randomUUID();
}

export function createA2AClientHandler(serverUrl = "http://localhost:10002") {
  const client = new A2AClient(serverUrl);
  let agentName = "Agent";
  let currentTaskId;
  let currentContextId;

  async function fetchAgentCard() {
    const card = await client.getAgentCard();
    agentName = card.name || agentName;
    return card;
  }

  function printAgentEvent(event) {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = colorize("magenta", `\n${agentName} [${timestamp}]:`);
    if (event.kind === "status-update") {
      const state = event.status.state;
      let stateEmoji = "❓", stateColor = "yellow";
      if (state === "working") [stateEmoji, stateColor] = ["⏳", "blue"];
      else if (state === "input-required") [stateEmoji, stateColor] = ["🤔", "yellow"];
      else if (state === "completed") [stateEmoji, stateColor] = ["✅", "green"];
      else if (state === "canceled") [stateEmoji, stateColor] = ["⏹️", "gray"];
      else if (state === "failed") [stateEmoji, stateColor] = ["❌", "red"];
      else[stateEmoji, stateColor] = ["ℹ️", "dim"];

      console.log(`${prefix} ${stateEmoji} Status: ${colorize(stateColor, state)} (Task: ${event.taskId}, Context: ${event.contextId}) ${event.final ? colorize("bright", "[FINAL]") : ""}`);
      if (event.status.message) {
        printMessageContent(event.status.message);
      }
    } else if (event.kind === "artifact-update") {
      console.log(`${prefix} 📄 Artifact Received: ${event.artifact.name || "(unnamed)"}`);
      printMessageContent({
        messageId: generateId(),
        kind: "message",
        role: "agent",
        parts: event.artifact.parts,
        taskId: event.taskId,
        contextId: event.contextId,
      });
    }
  }

  function printMessageContent(message) {
    message.parts.forEach((part, index) => {
      const partPrefix = colorize("red", `Part ${index + 1}:`);
      if (part.kind === "text") {
        console.log(`${partPrefix} ${colorize("green", "📝 Text:")}`, part.text);
      } else if (part.kind === "file") {
        const file = part.file;
        console.log(`${partPrefix} ${colorize("blue", "📄 File:")} Name: ${file.name}, Type: ${file.mimeType}`);
      } else if (part.kind === "data") {
        console.log(`${partPrefix} ${colorize("yellow", "📊 Data:")}`, JSON.stringify(part.data, null, 2));
      }
    });
  }

  async function sendMessage(input) {
    const messageId = generateId();
    const message = {
      messageId,
      kind: "message",
      role: "user",
      parts: [{ kind: "text", text: input }],
      ...(currentTaskId && { taskId: currentTaskId }),
      ...(currentContextId && { contextId: currentContextId })
    };

    const params = { message };
    const stream = client.sendMessageStream(params);

    for await (const event of stream) {
      const timestamp = new Date().toLocaleTimeString();
      const prefix = colorize("magenta", `\n${agentName} [${timestamp}]:`);

      if (["status-update", "artifact-update"].includes(event.kind)) {
        printAgentEvent(event);
        if (event.kind === "status-update" && event.final && event.status.state !== "input-required") {
          currentTaskId = undefined;
        }
      } else if (event.kind === "message") {
        console.log(`${prefix} ${colorize("green", "✉️ Message Stream Event:")}`);
        printMessageContent(event);
        currentTaskId = event.taskId;
        currentContextId = event.contextId;
      } else if (event.kind === "task") {
        console.log(`${prefix} ${colorize("blue", "ℹ️ Task Stream Event:")} ID: ${event.id}`);
        currentTaskId = event.id;
        currentContextId = event.contextId;
        if (event.status.message) printMessageContent(event.status.message);
      }
    }
  }

  
  async function sendMessageStream(params, onMessage, onError, onClose) {
    try {
      const stream = client.sendMessageStream(params);
      for await (const event of stream) {
        onMessage(event);
      }
      if (onClose) onClose();
    } catch (err) {
      if (onError) onError(err);
    }
  }

  return {
    fetchAgentCard,
    sendMessage,
    sendMessageStream,
    getCurrentTaskId: () => currentTaskId,
    getCurrentContextId: () => currentContextId,
    resetSession: () => {
      currentTaskId = undefined;
      currentContextId = undefined;
    },
  };
}
