#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/6/20 10:02
# @File  : tools.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  :
import os
from litellm import completion
from google.adk.tools import ToolContext
from google.adk.tools.agent_tool import AgentTool
from disease_data import disease_symptoms
import time
from datetime import datetime
import random
# import litellm
# litellm._turn_on_debug()

TOOL_MODEL_API_BASE = os.environ["TOOL_MODEL_API_BASE"]
TOOL_MODEL_API_KEY = os.environ["TOOL_MODEL_API_KEY"]
TOOL_MODEL_NAME = os.environ["TOOL_MODEL_NAME"]
TOOL_MODEL_PROVIDER = os.environ["TOOL_MODEL_PROVIDER"]
def query_deepseek(prompt):
    try:
        response = completion(provider=TOOL_MODEL_PROVIDER, model=TOOL_MODEL_NAME,
                                   messages=[{"content": prompt, "role": "user"}],
                                   api_base=TOOL_MODEL_API_BASE,
                                   api_key=TOOL_MODEL_API_KEY
                              )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

async def matchDiseaseBySymptoms(
    symptoms: list,
    tool_context: ToolContext,
):
    """
    根据疾病的症状搜索可能的疾病
    params:
    symptoms：症状的列表
    :return: 返回所有可能的疾病
    """
    # 需要使用疾病症状和数据库进行向量匹配，然后使用大模型进行判断，是否是一个或者多个疾病。返回给前端疾病名称和症状。
    # 这里进行简化，直接使用这些症状和疾病数据库让大模型进行匹配。
    agent_name = tool_context.agent_name
    print(f"Agent{agent_name}正在调用工具：matchDiseaseBySymptoms")
    #
    return result

async def getTreatmentAdvice(disease_name: str, tool_context: ToolContext):
    """
    获取疾病的治疗建议
    params:
    disease_name: 疾病名称
    """
    #查询真实的某个疾病的治疗建议数据库，得到专业建议，这里使用大模型模拟
    prompt = """
### 🩺 Prompt：疾病治疗建议助手

你是一位具有丰富临床经验的医学专家，擅长用**通俗易懂的语言**为患者提供**可靠的治疗建议**。你具备对医学文献的检索和整合能力，能够基于最新的循证医学和权威指南，提供针对特定疾病的治疗方案。

请根据用户提供的疾病名称，输出以下内容：

1. ✅ **简要介绍该疾病**（病因、常见症状等，简明扼要）
2. 💊 **常用治疗方法**（包括药物、手术、生活方式干预等）
3. ⚠️ **治疗过程中的注意事项**（如药物副作用、禁忌等）
4. 📚 **参考的权威指南或共识**（如《中国X疾病诊疗指南2023》或WHO指南）

请确保回答内容简洁明了，适合患者理解。如果该疾病属于罕见病或特需专科干预，请注明需就诊相关专科医生。

"""
    prompt += f"###  disease_name: {disease_name}"
    response = query_deepseek(prompt)
    return response


if __name__ == '__main__':
    result = matchDiseaseBySymptoms(symptoms=['失眠'])
    print(result)