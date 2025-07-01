import os
import random

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import BaseTool
from typing import Dict, List, Any, AsyncGenerator, Optional, Union
from create_model import create_model
from tools import matchDiseaseBySymptoms,getTreatmentAdvice
from dotenv import load_dotenv
load_dotenv()

instruction = """
你是一位专业的**医学问诊Agent**，具备以下职责：
---

### ✅ 任务流程：

1. **接收用户输入**：用户描述当前的身体不适或症状表现。
2. **提取症状信息**：
   * 抽取本轮对话中的症状关键词（如：头痛、发热、咳嗽等）。
   * 将当前提取的症状与对话历史中国呢的症状一起累积，形成完整的症状集合。
   
3. **疾病初步匹配**：
   * 使用工具或函数接口（如：`matchDiseaseBySymptoms(symptoms)`）查询与症状集合相符的疾病。
   * 匹配结果可能是多个疾病（模糊匹配），也可能只有一个疾病（精确匹配）。
   
4. **结果处理逻辑**：

   * 如果只有一个疾病：
     * 使用工具或函数（如：`getTreatmentAdvice(disease_name)`）查询该疾病的治疗建议，并以通俗方式回复用户。
   * 如果有多个疾病候选：

     * 比较这些疾病的**典型症状差异**。
     * 向用户提出进一步问题，确认是否存在其他典型症状，以缩小诊断范围。

---

### 🎯 回答要求：

* 所有医学术语应使用**通俗易懂的语言**解释。
* 每一步都需保持与用户的**温和、耐心的问诊语气**。
* 提问要简洁明确，例如：“请问您是否还有发烧、出汗、咽喉痛等症状？”
* 如果用户没有更多症状，也要基于当前症状给出**可能性排序**，并推荐就医或下一步行动。

"""

model = create_model(model=os.environ["LLM_MODEL"], provider=os.environ["MODEL_PROVIDER"])

def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    # 1. 检查用户输入
    agent_name = callback_context.agent_name
    history_length = len(llm_request.contents)
    metadata = callback_context.state.get("metadata")
    print(f"调用了{agent_name}模型前的callback, 现在Agent共有{history_length}条历史记录,metadata数据为：{metadata}")
    #清空contents,不需要上一步的拆分topic的记录, 不能在这里清理，否则，每次调用工具都会清除记忆，白操作了
    # llm_request.contents.clear()
    # 返回 None，继续调用 LLM
    return None
def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    # 1. 检查用户输入
    agent_name = callback_context.agent_name
    response_data = len(llm_response.content.parts)
    metadata = callback_context.state.get("metadata")
    print(f"调用了{agent_name}模型后的callback, 这次模型回复{response_data}条信息,metadata数据为：{metadata}")
    #清空contents,不需要上一步的拆分topic的记录, 不能在这里清理，否则，每次调用工具都会清除记忆，白操作了
    # llm_request.contents.clear()
    # 返回 None，继续调用 LLM
    return None

def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:

  tool_name = tool.name
  print(f"调用了{tool_name}工具后的callback, tool_response数据为：{tool_response}")
  return None

root_agent = Agent(
    name="diagnosing_doctor",
    model=model,
    description=(
        "doctor"
    ),
    instruction=instruction,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    after_tool_callback=after_tool_callback,
    tools=[matchDiseaseBySymptoms,getTreatmentAdvice],
)
