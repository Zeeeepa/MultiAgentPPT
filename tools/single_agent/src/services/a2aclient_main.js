import { createA2AClientHandler } from './a2aclient.js';

const handler = createA2AClientHandler("http://localhost:10002");

await handler.fetchAgentCard();
await handler.sendMessage("Hello, What's Beijing Weather?");
