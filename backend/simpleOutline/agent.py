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

1. 用户输入身体不适或症状描述后，请立即执行以下操作：

2. **提取症状关键词**：如“头痛”“发热”“咳嗽”等；
   - 将当前提取的症状与对话历史中的症状合并为完整症状列表 `symptoms`。

3. **调用工具：匹配疾病**
   - 请立即调用工具 `matchDiseaseBySymptoms(symptoms)` 来获取可能的疾病列表，**不要自行猜测疾病名称**。

4. **根据匹配结果继续处理**：

   - **如果结果为唯一疾病**，请调用 `getTreatmentAdvice(disease_name)` 获取治疗建议，并以通俗易懂的语言向用户解释。
   - **如果有多个可能疾病**，请分析各疾病典型症状差异，向用户提出进一步确认问题，缩小范围。
     - 示例提问：”请问您还有发烧、流涕或咽痛等症状吗？”

---

### 🔧 工具说明：
- `matchDiseaseBySymptoms(symptoms: list[str]) -> list[str]`：根据症状返回可能疾病列表。
- `getTreatmentAdvice(disease_name: str) -> str`：根据疾病名称返回治疗建议文本。

---

### 🎯 其他要求：

- 回答语气温和，提问简洁明确；
- 所有医学术语用通俗语言解释；
- 若用户没有更多症状，也要基于当前信息给出可能疾病的排序和建议。

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
