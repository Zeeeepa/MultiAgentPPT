import os
import random

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from typing import Dict, List, Any, AsyncGenerator, Optional, Union
from create_model import create_model
from tools import DocumentSearch
from dotenv import load_dotenv
load_dotenv()

instruction = """
根据用户的描述生成大纲。仅生成大纲即可，无需多余说明。
输出示例格式如下：

# 第一部分主题
- 关于该主题的关键要点
- 另一个重要方面
- 简要结论或影响

# 第二部分主题
- 本部分的主要见解
- 支持性细节或示例
- 实际应用或收获
"""

model = create_model(model=os.environ["LLM_MODEL"], provider=os.environ["MODEL_PROVIDER"])

def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    # 1. 检查用户输入
    agent_name = callback_context.agent_name
    history_length = len(llm_request.contents)
    print(f"调用了{agent_name} research Agent的callback, 现在Agent共有{history_length}条历史记录")
    #清空contents,不需要上一步的拆分topic的记录, 不能在这里清理，否则，每次调用工具都会清除记忆，白操作了
    # llm_request.contents.clear()
    # 返回 None，继续调用 LLM
    return None

root_agent = Agent(
    name="outline_agent",
    model=model,
    description=(
        "generate outline"
    ),
    instruction=instruction,
    before_model_callback=before_model_callback,
    tools=[DocumentSearch],
)
