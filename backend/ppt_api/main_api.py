#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import logging
import random
import string
import json
import asyncio
import traceback
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from a2a_client import send_outline_prompt_streaming, send_ppt_outline_streaming
from markdown_convert_json import markdown_to_json, data_to_markdown
from xml_convert_json import parse_trunk_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(module)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler("fastapi.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

executor = ThreadPoolExecutor(max_workers=20)
app = FastAPI(title="InfoXMed API", version="1.0")

# ==================================================
# 工具函数
# ==================================================
async def stream_outline(link_id, session_id, user_id, function_id, attachment, stream_response):
    """处理大纲流式响应"""
    try:
        async for chunk in stream_response:
            yield chunk
    except Exception as e:
        logger.error(f"[错误] 大纲流消费失败: {e}")
        traceback.print_exc()
        yield {"error": str(e)}

async def stream_ppt(link_id, session_id, user_id, function_id, attachment, stream_response, title):
    """处理PPT流式响应"""
    try:
        async for chunk in stream_response:
            yield chunk
    except Exception as e:
        logger.error(f"[错误] PPT流消费失败: {e}")
        traceback.print_exc()
        yield {"error": str(e)}

# ==================================================
# FastAPI 接口
# ==================================================

@app.post("/outline")
async def generate_outline(request: dict):
    """
    输入：和原先MQ message一致
    输出：生成大纲流
    """
    try:
        message = request["message"]
        session_id = message["sessionId"]
        user_id = message["userId"]
        prompt = message["prompt"]
        language = message.get("language", "chinese")
        metadata = {"language": language}

        stream_response = send_outline_prompt_streaming(
            prompt=prompt,
            metadata=metadata,
            agent_card_url=os.environ["OUTLINE_URL"]
        )

        return JSONResponse(content={"status": "started", "sessionId": session_id, "userId": user_id, "functionId": function_id})
    except Exception as e:
        logger.error(f"生成大纲出错: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/ppt")
async def generate_ppt(request: dict):
    """
    输入：大纲数据
    输出：生成PPT流
    """
    try:
        message = request["message"]
        session_id = message["sessionId"]
        user_id = message["userId"]
        prompt = message["prompt"]
        language = message.get("language", "chinese")
        numSlides = message.get("numSlides", 12)
        if isinstance(prompt, str):
            prompt_data = json.loads(prompt)
        else:
            prompt_data = prompt
        outline = data_to_markdown(data=prompt_data["data"])
        title = prompt_data["data"][0]['content']

        stream_response = send_ppt_outline_streaming(
            outline=outline,
            metadata={"language": language, "numSlides": numSlides},
            agent_card_url=os.environ["SLIDES_URL"]
        )

        return JSONResponse(content={"status": "started", "sessionId": session_id, "userId": user_id, "functionId": function_id})
    except Exception as e:
        logger.error(f"生成PPT出错: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == '__main__':
    # ==================================================
    # 启动命令:
    # uvicorn main_api:app --host 0.0.0.0 --port 6999 --reload
    # ==================================================
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6999)
