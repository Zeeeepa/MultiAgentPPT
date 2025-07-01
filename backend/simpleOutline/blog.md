# 追踪元数据之旅：深入解析A2A/ADK多智能体系统中的元数据流

在复杂的多智能体系统中，仅仅传递一个简单的提示（prompt）往往是不够的。为了构建健壮、有状态且具备上下文感知能力的应用，我们需要一种传递“关于数据的数据”——即**元数据（metadata）**——的方法。元数据可以包含任何信息，从用户ID和会话信息，到用于调试的追踪ID或改变智能体行为的自定义标志。

我们的MultiAgentPPT项目集成了A2A（Agent-to-Agent）和Google ADK（Agent Development Kit）框架，提供了一种强大的机制，可以在请求的整个生命周期中传播元数据。这确保了从最初的客户端调用到最终的响应，上下文永不丢失。

在这篇文章中，我们将一步步追踪一个`metadata`对象在系统中的完整旅程。

### 元数据的生命周期

元数据的流动被设计得天衣无缝，在流程中的特定接触点可以访问、读取甚至修改元数据。这使得动态和智能的代理交互成为可能。

#### 第一步：源头 - 客户端 (`a2a_client.py`)

一切都始于客户端。当一个请求被初始化时，客户端应用程序负责将初始的`metadata`对象附加到请求的载荷（payload）中。这是将在整个系统中传递的“事实之源”。

**`a2a_client.py` 中的概念性示例：**

```python
# 在 a2a_client.py 中，构造消息载荷时
send_message_payload = {
    "prompt": "创建一个关于电动汽车市场的演示文稿。",
    "metadata": {
        "user_data": "hello",
        "trace_id": "一个唯一的请求标识符",
        "target_audience": "investors"
    }
}

# 然后将此载荷发送到服务器
# client.send_message(send_message_payload)
```

#### 第二步：网关 - ADK Agent Executor (`adk_agent_executor.py`)

当后端收到请求时，`adk_agent_executor.py` 作为主入口点。

1.  **初始接收**：执行器首先直接从传入的消息上下文中访问元数据：`context.message.metadata`。
2.  **状态持久化**：至关重要的是，为了确保元数据在多轮对话和工具调用中保持不变，它会被立即保存到会话状态（session state）中。在创建会话时（`_upsert_session`），执行器会存储元数据，使其在任务的整个生命周期内都可用。

```python
# 在 adk_agent_executor.py 的 _process_request 方法中
metadata = context.message.metadata
# ...
await self._upsert_session(
    app_name=self.runner.app_name,
    user_id="self",
    session_id=session_id,
    state={"metadata": metadata}  # 将元数据持久化到会话中
)
```

#### 第三步：智能体感知 - 模型调用前 (`agent.py`)

在智能体查询语言模型之前，它有机会检查上下文。`agent.py` 中的 `before_model_callback` 回调函数会被触发，允许智能体从会话状态中访问持久化的元数据。这是一个强大的转折点，智能体可以利用元数据来修改其行为，例如，根据 `target_audience` 字段动态地改变发送给模型的提示。

```python
# 在 agent.py 中
def before_model_callback(callback_context):
    metadata = callback_context.state.get("metadata")
    if metadata:
        print(f"模型调用前发现元数据: {metadata}")
        # 示例：根据元数据修改提示
        # if metadata.get("target_audience") == "investors":
        #     callback_context.prompt += "
请侧重于财务预测。"
```

#### 第四步：中途修改 - 工具使用期间

智能体很少孤立工作；它们使用工具与外部世界互动。这些工具不仅可以*读取*当前的元数据，还可以用新信息*丰富*它。

例如，如果一个工具执行数据库查找并检索到一组文档ID，它可以将这些ID附加到元数据中。这使得工具调用的结果对流程中的所有后续步骤都可用。

```python
# 在一个假设的工具函数中
def my_database_tool(query: str, tool_context):
    # 1. 访问现有元数据
    metadata = tool_context.state.get("metadata", {})

    # 2. 执行操作并获取新信息
    document_ids = [0, 1, 2, 3] # 来自数据库查询的ID

    # 3. 丰富元数据
    metadata["tool_document_ids"] = document_ids

    # 4. 将更新后的元数据写回状态
    tool_context.state["metadata"] = metadata

    return "数据库查询成功。"
```

#### 第五步：后处理 - 模型调用后 (`agent.py`)

一旦模型做出响应并且任何工具都已运行，`agent.py` 中的 `after_model_callback` 就会被执行。在这里，智能体可以查看到完整的、演变后的`metadata`，其中现在包含了由工具添加的任何信息。这对于在形成响应之前进行日志记录、验证或最终处理非常有用。

```python
# 在 agent.py 中
def after_model_callback(callback_context):
    metadata = callback_context.state.get("metadata")
    if metadata:
        print(f"模型调用后（及工具调用后）的元数据: {metadata}")
        # 如果工具被调用，现在会包含 'tool_document_ids'
```

#### 第六步和第七步：最终交接并返回客户端

最后，回到 `adk_agent_executor.py`，当任务完成时（`event.is_final_response()`），执行器会检索最终的会话状态。此状态包含完全丰富的元数据对象。然后，该对象被打包到最终的工件（artifact）中，并通过SSE流发送回客户端。

客户端会收到一个最终的JSON对象，其中 `metadata` 字段反映了其完整的旅程，既包含初始数据，也包含在此过程中所做的所有修改。

**最终输出给客户端的示例：**

```json
{
  "id": "57071402-98d3-459d-a447-cbdf384e8323",
  "jsonrpc": "2.0",
  "result": {
    "artifact": {
      "artifactId": "156b98ac-3aa6-412c-97e2-6dff3148c46b",
      "metadata": {
        "user_data": "hello",
        "tool_document_ids": [0, 1, 2, 3]
      },
      "parts": [{
        "kind": "text",
        "text": "# 电动汽车全球市场概况..."
      }]
    },
    "contextId": "cdbf96d6-8a35-40e2-b3cd-e026c2c446f1",
    "kind": "artifact-update",
    "taskId": "3d5160e2-42ef-4244-872f-e23046b685f1"
  }
}
```

### 结论

A2A/ADK框架中的元数据流是状态和上下文管理的典范。通过在请求生命周期的每个阶段提供清晰的入口和出口点，它使得开发高度智能、可追踪和有状态的多智能体应用成为可能。这种架构确保了有价值的上下文不仅被传递，而且可以被动态地丰富，将一个简单的请求转变为用户、智能体及其工具之间充满数据的丰富对话。
