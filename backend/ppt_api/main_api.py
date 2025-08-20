#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 用于和rabbitMQ进行交互
import os
import logging
import random
import string
import time
import json
import asyncio
import traceback
from xml_convert_json import parse_trunk_data
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from mq_handler import start_consumer, MQHandler
from a2a_client import send_outline_prompt_streaming, send_ppt_outline_streaming, send_ppt_outline_streaming_simulate
from markdown_convert_json import markdown_to_json, data_to_markdown
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(module)s - %(funcName)s - %(message)s",
    handlers=[
        logging.FileHandler("mq.log", mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 创建一个线程池，定义线程池的大小10
executor = ThreadPoolExecutor(max_workers=20)


def handle_reasoning_stream_response(link_id, session_id, user_id, function_id, attachment, stream_response):
    """
    处理思维链流式响应
    """
    pass


def handle_outline_stream_response(link_id, session_id, user_id, function_id, attachment, stream_response):
    """
    大纲的生成
    """
    mq_handler = MQHandler(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, RABBITMQ_VIRTUAL_HOST,
                           QUEUE_NAME_ANSWER)
    # 如果发生错误，先处理错误：stream_response是字符串就是错误，应该默认是生成器
    def send_error_message(error_msg):
        """发送错误信息到消息队列"""
        mq_handler.send_message({
            "linkId": link_id,
            "sessionId": session_id,
            "userId": user_id,
            "functionId": function_id,
            "message": f'发生错误：{error_msg}',
            "reasoningMessage": "",
            "attachment": attachment,
            "type": 4,
        })
        time.sleep(0.01)
        mq_handler.send_message({
            "linkId": link_id,
            "sessionId": session_id,
            "userId": user_id,
            "functionId": function_id,
            "message": '[stop]',
            "reasoningMessage": "",
            "attachment": attachment,
            "type": 4,
        })

    if isinstance(stream_response, str):
        send_error_message(stream_response)
        mq_handler.close_connection()
        return
    # 生成大纲时的第一条进度消息提示，发送给前端
    PROCESS_STEPS = [
        {
            "id": 1,
            "mainHeading": "提取文献原文",
            "subheading": "根据相关文献提取对应的PDF全文内容"
        },
        {
            "id": 2,
            "mainHeading": "整理全文内容",
            "subheading": "阅读提取出的文献原文，结合PPT主题进行信息整理"
        },
        {
            "id": 3,
            "mainHeading": "生成章节大纲",
            "subheading": "完成PPT章节大纲的整理"
        }
    ]
    OUTLINE_PROCESS_MESSAGE = {
        "message": {
            "linkId": link_id,
            "pptUrl": None,
            "isEnd": 0,
            "progress": PROCESS_STEPS,
            "userId": user_id,
            "sessionId": link_id,
            "functionId": function_id,
            "type": "1"
        },
        "type": "0"
    }
    OUTLINE_PROCESS_MESSAGE["message"]["linkId"] = link_id
    OUTLINE_PROCESS_MESSAGE["message"]["sessionId"] = session_id
    OUTLINE_PROCESS_MESSAGE["message"]["functionId"] = function_id
    OUTLINE_PROCESS_MESSAGE["message"]["userId"] = user_id
    mq_handler.send_message(OUTLINE_PROCESS_MESSAGE)
    print(f"[Info] 发送状态数据完成(总步骤信息)：{OUTLINE_PROCESS_MESSAGE}")
    # 一条数据通知消息，通知大纲的生成进度
    OUTLINE_ONE_PROCESS = {
        "message": {
            "linkId": link_id,
            "pptUrl": None,
            "isEnd": 0,
            "progress": [
                {
                    "id": 1,
                    "mainHeading": "提取文献原文",
                    "subheading": "根据相关文献提取对应的PDF全文内容"
                }
            ],
            "userId": user_id,
            "sessionId": session_id,
            "functionId": function_id,
            "type": "2"
        },
        "type": "0"
    }
    # 目前的每一步的进度
    TOOL_NAME_STEPS = {
        "TranslateToEnglish": 0,
        "AbstractSearch": 1
    }
    finished_steps = []
    # 大纲的输出的结果的字段
    OUTLINE_RESULT = {
        "message": {
            "linkId": link_id,
            "responseMessage": {
                "data": [],
                "pmidList": []
            },
            "attachment": {
                "isRestock": 0,
                "selectType": "system",
                "type": "0"
            },
            "isEnd": 1,
            "progress": [
                {
                    "id": 3,
                    "mainHeading": "生成章节大纲",
                    "subheading": "完成PPT章节大纲的整理"
                }
            ],
            "sessionId": session_id,
            "userId": user_id,
            "functionId": function_id,
            "type": "2"
        },
        "type": "0"
    }
    OUTLINE_RESULT["message"]["linkId"] = link_id
    OUTLINE_RESULT["message"]["sessionId"] = session_id
    OUTLINE_RESULT["message"]["functionId"] = function_id
    OUTLINE_RESULT["message"]["userId"] = user_id

    async def consume():
        try:
            async for chunk in stream_response:
                try:
                    data_type = chunk.get("type")
                    if data_type == "final":
                        infoxmed20_answer_queue_message = {
                            "linkId": link_id,
                            "sessionId": session_id,
                            "userId": user_id,
                            "functionId": function_id,
                            "message": '[stop]',
                            "reasoningMessage": "",
                            "attachment": attachment,
                            "type": 4,
                        }
                    elif data_type == "error":
                        OUTLINE_RESULT["message"]["responseMessage"]["data"] = [{
                            "content": "发生了错误，请联系管理员",
                            "child": []
                        }]
                        infoxmed20_answer_queue_message = OUTLINE_RESULT
                    elif data_type == "data":
                        kind = chunk["text"]["result"]["kind"]
                        if kind == "status-update":
                            print(f"[Info] 状态更新：{chunk}")
                            chunk_status = chunk["text"]["result"]["status"]
                            if chunk_status.get("message"):
                                chunk_parts = chunk_status["message"]["parts"]
                                first_chunk = chunk_parts[0]
                                if first_chunk["kind"] == "data":
                                    chunk_data_type = first_chunk["data"]["type"]
                                    if chunk_data_type == "function_response":
                                        print(f"[Info] 收到data类型的数据")
                                        chunk_data_name = first_chunk["data"]["name"]
                                        current_step = TOOL_NAME_STEPS.get(chunk_data_name, 0)
                                        print(f"当前的进度步骤是：{current_step}")
                                        # 判断是否有比当前步骤更小的已经完成
                                        has_smaller_finished = any(step < current_step for step in finished_steps)

                                        # 如果没有比当前小的完成步骤，打印所有比自己小的步骤
                                        if not has_smaller_finished:
                                            print(f"Missing prerequisite steps: 已完成{finished_steps}，当前步骤是{current_step}，{chunk_data_name}")
                                            for tool, step in TOOL_NAME_STEPS.items():
                                                if step < current_step:
                                                    if step in finished_steps:
                                                        # 说明这个工具对应的step已经发送过通知给前端了，没必要继续通知了
                                                        continue
                                                    print(f"遗漏了比自己更小的Step，现在通知前端，已经完成了 {step}: {tool}")
                                                    OUTLINE_ONE_PROCESS["message"]["progress"] = [PROCESS_STEPS[step]]
                                                    print(f"[Info] 发送状态数据完成(补充发送步骤完成信息)：{OUTLINE_ONE_PROCESS}")
                                                    mq_handler.send_message(OUTLINE_ONE_PROCESS)
                                        if current_step in finished_steps:
                                            # 说明这个工具对应的step已经发送过通知给前端了，没必要继续通知了
                                            continue
                                        finished_steps.append(current_step)
                                        OUTLINE_ONE_PROCESS["message"]["progress"] = [PROCESS_STEPS[current_step]]
                                        infoxmed20_answer_queue_message = OUTLINE_ONE_PROCESS
                                    else:
                                        print(f"[Info] chunk_data_type不是function_response，跳过")
                                        continue
                                else:
                                    print(f"[Info] first_chunk的数据不是我们需要通知给前端的，跳过.")
                                    continue
                            else:
                                print(f"[Info] 收到的chunk中不包含message字段，跳过该数据.")
                                continue
                        elif kind == "artifact-update":
                            # 大纲的内容，
                            outline = chunk["text"]["result"]["artifact"]["parts"][0]["text"]
                            outline_json = markdown_to_json(outline)
                            outline_data = outline_json["data"]
                            OUTLINE_RESULT["message"]["responseMessage"]["data"] = outline_data
                            infoxmed20_answer_queue_message = OUTLINE_RESULT
                    else:
                        print(f"[警告] 未知的chunk类型：{data_type}，已跳过")
                        continue
                    mq_handler.send_message(infoxmed20_answer_queue_message)
                    print(f"[Info] 发送状态数据完成(逐个步骤完成信息或者大纲信息)：{infoxmed20_answer_queue_message}")
                except Exception as chunk_error:
                    print("[错误] 处理 chunk 时发生异常：", chunk_error)
                    traceback.print_exc()
                    send_error_message(f"处理数据块出错：{chunk_error}")
        except Exception as stream_error:
            print("[错误] 流消费失败：", stream_error)
            traceback.print_exc()
            send_error_message(f"处理流出错：{stream_error}")
        finally:
            mq_handler.close_connection()

    asyncio.run(consume())
def handle_ppt_stream_response(link_id, session_id, user_id, function_id, attachment, stream_response, title):
    """
    PPT的内容生成
    """
    mq_handler = MQHandler(RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USERNAME, RABBITMQ_PASSWORD, RABBITMQ_VIRTUAL_HOST,
                           QUEUE_NAME_ANSWER)
    # 如果发生错误，先处理错误：stream_response是字符串就是错误，应该默认是生成器
    def send_error_message(error_msg):
        """发送错误信息到消息队列"""
        mq_handler.send_message({
            "linkId": link_id,
            "sessionId": session_id,
            "userId": user_id,
            "functionId": function_id,
            "message": f'发生错误：{error_msg}',
            "reasoningMessage": "",
            "attachment": attachment,
            "type": 4,
        })
        time.sleep(0.01)
        mq_handler.send_message({
            "linkId": link_id,
            "sessionId": session_id,
            "userId": user_id,
            "functionId": function_id,
            "message": '[stop]',
            "reasoningMessage": "",
            "attachment": attachment,
            "type": 4,
        })

    if isinstance(stream_response, str):
        send_error_message(stream_response)
        mq_handler.close_connection()
        return
    # 生成大纲时的第一条进度消息提示，发送给前端
    # 目前的每一步的进度
    PROCESS_STEPS = [
            {
                "id": 1,
                "mainHeading": "阅读与总结文献",
                "subheading": "逐篇阅读文献并依据大纲提炼关键信息"
            },
            {
                "id": 2,
                "mainHeading": "图表资料提取",
                "subheading": "提取相关图表"
            },
            {
                "id": 3,
                "mainHeading": "撰写PPT",
                "subheading": "依据大纲整合素材并规划每页PPT内容"
            },
            {
                "id": 4,
                "mainHeading": "格式规范检查",
                "subheading": "统一检查文字、字体、段落与页面格式"
            },
            {
                "id": 5,
                "mainHeading": "PPT美化设计",
                "subheading": "优化排版并添加视觉元素提升美观度"
            },
            {
                "id": 6,
                "mainHeading": "生成PPT文件",
                "subheading": "整合内容并生成最终PPT文件"
            }
        ]
    PPT_PROCESS_MESSAGE = {
        "message": {
            "linkId": link_id,
            "pptUrl": "",
            "isEnd": 0,
            "progress": PROCESS_STEPS,
            "userId": user_id,
            "sessionId": session_id,
            "functionId": function_id,
            "type": 1,
        },
        "type": "1"
    }
    PPT_PROCESS_MESSAGE["message"]["linkId"] = link_id
    PPT_PROCESS_MESSAGE["message"]["sessionId"] = session_id
    PPT_PROCESS_MESSAGE["message"]["functionId"] = function_id
    PPT_PROCESS_MESSAGE["message"]["userId"] = user_id
    mq_handler.send_message(PPT_PROCESS_MESSAGE)
    logger.info(f"[Info] 发送状态数据完成(总步骤信息)：{PPT_PROCESS_MESSAGE}")
    # 一条数据通知消息，通知大纲的生成进度
    PPT_ONE_PROCESS = {
        "message": {
            "linkId": link_id,
            "pptUrl": None,
            "isEnd": 0,
            "progress": [
                {
                    "id": 1,
                    "mainHeading": "阅读与总结文献",
                    "subheading": "逐篇阅读文献并依据大纲提炼关键信息"
                }
            ],
            "userId": user_id,
            "sessionId": session_id,
            "functionId": function_id,
            "type": 2,
        },
        "type": "1"
    }
    AGENT_NAME_STEPS = {
        "SplitTopicAgent": 0,
        # 第一个研究Agent完成，我们对应着完成图表资料提取的步骤
        "research_agent_1": 1,
        "SummaryAgent": 2,
        "refineAgent": 3,
        "SlidesPlanner": 4,
    }
    finished_steps = []
    # PPT的最终结果字段
    PPT_RESULT = {
        "message": {
            "linkId": link_id,
            "pptUrl": "https://doc2.infox-med.com/ppt_multiple/CAR-T细胞疗法在实体瘤治疗中的挑战与进展_bb82edd23e614a6da579a5ec84727815.pptx",
            "isEnd": 1,
            "progress": [
                {
                    "id": 6,
                    "mainHeading": "生成PPT文件",
                    "subheading": "整合内容并生成最终PPT文件"
                }
            ],
            "userId": user_id,
            "sessionId": session_id,
            "functionId": function_id,
            "type": 2,
        },
        "type": "1"
    }
    PPT_RESULT["message"]["linkId"] = link_id
    PPT_RESULT["message"]["sessionId"] = session_id
    PPT_RESULT["message"]["functionId"] = function_id
    PPT_RESULT["message"]["userId"] = user_id
    async def consume():
        show_ppt_content = []
        references = []
        try:
            async for chunk in stream_response:
                try:
                    data_type = chunk.get("type")
                    if data_type == "final":
                        # 说明PPT的内容已经准备完成，准备下载ppt，然后返回最终的下载结果，并返回stop标识符
                        # 判断show_ppt_content是否不为空，如果不为空，那么使用xml_convert_json转换ppt内容为pdf，并提供下载链接
                        if show_ppt_content:
                            logger.info(f"*****************************************************************************************************************************************************************\n\n\n=================================================================================PPT转换阶段======================================================================\n\n\n*****************************************************************************************************************************************************************")
                            logger.info(f"需要转换成ppt文件的内容是: {show_ppt_content}  \nreferences: {references}  \ntitle: {title}")
                            logger.info(f"*****************************************************************************************************************************************************************\n\n\n=============================================================================PPT转换阶段完毕======================================================================\n\n\n*****************************************************************************************************************************************************************")
                            references = references[:30] #最大30个参考文献
                            ppt_url = parse_trunk_data(trunk_list=show_ppt_content, references=references, title=title)
                        else:
                            ppt_url = "https://infox-med.com/error"
                        infoxmed20_answer_queue_message = {
                            "message": {
                                "linkId": link_id,
                                "pptUrl": ppt_url,
                                "isEnd": 1,
                                "progress": [
                                    {
                                        "id": 6,
                                        "mainHeading": "生成PPT文件",
                                        "subheading": "整合内容并生成最终PPT文件"
                                    }
                                ],
                                "userId": user_id,
                                "sessionId": session_id,
                                "functionId": function_id,
                                "type": 2,
                            },
                            "type": "1"
                        }
                    elif data_type == "error":
                        infoxmed20_answer_queue_message = {
                            "message": {
                                "linkId": link_id,
                                "pptUrl": None,
                                "isEnd": 1,
                                "progress": [
                                    {
                                        "id": 6,
                                        "mainHeading": "生成PPT文件",
                                        "subheading": "出错啦，出现错误了，请联系管理员"
                                    }
                                ],
                                "userId": user_id,
                                "sessionId": session_id,
                                "functionId": function_id
                            },
                            "type": "1"
                        }
                    elif data_type == "data":
                        kind = chunk["text"]["result"]["kind"]
                        if kind == "status-update":
                            logger.info(f"[Info] 状态更新：{chunk}")
                            chunk_status = chunk["text"]["result"]["status"]
                            message = chunk_status.get("message", {})
                            metadata = message.get("metadata", {})
                            agent_name = metadata.get("author","unknown")
                            chunk_references = metadata.get("references",[])
                            if chunk_references:
                                # 更新引用，方便生成ppt文件时使用
                                references = chunk_references
                            show_ppt = metadata.get("show", False)
                            if show_ppt:
                                logger.info(f"收集到{agent_name}要显示的ppt的内容")
                                show_ppt_content.append(chunk)
                            continue
                        elif kind == "artifact-update":
                            #根据不同的Agent名称，判断当前是什么状态，需要收集metadata中的show为true的Agent的输出
                            metadata = chunk["text"]["result"]["artifact"].get("metadata", {})
                            # 哪个Agent的输出结果
                            agent_name = metadata.get("author","unknown")
                            if agent_name == "unknown": print(f"注意⚠️：返回的metada中的agent的name为unknown")
                            current_step = AGENT_NAME_STEPS.get(agent_name, 0)
                            print(f"当前的步骤是：{current_step}, 对应的Agent是: {agent_name}")
                            # 判断是否有比当前步骤更小的已经完成
                            has_smaller_finished = any(step < current_step for step in finished_steps)

                            # 如果没有比当前小的完成步骤，打印所有比自己小的步骤
                            if not has_smaller_finished:
                                print(f"Missing prerequisite steps: 已完成{finished_steps}，当前步骤是{current_step}，对应Agent名称：{agent_name}")
                                for tool, step in AGENT_NAME_STEPS.items():
                                    if step < current_step:
                                        if step in finished_steps:
                                            # 说明这个工具对应的step已经发送过通知给前端了，没必要继续通知了
                                            continue
                                        print(f"遗漏了比自己更小的Step，现在通知前端，已经完成了 {step}: {tool}")
                                        PPT_ONE_PROCESS["message"]["progress"] = [PROCESS_STEPS[step]]
                                        print(f"[Info] 发送状态数据完成(补充发送步骤完成信息)：{PPT_ONE_PROCESS}")
                                        mq_handler.send_message(PPT_ONE_PROCESS)
                            if current_step in finished_steps:
                                # 说明这个工具对应的step已经发送过通知给前端了，没必要继续通知了
                                continue
                            finished_steps.append(current_step)
                            PPT_ONE_PROCESS["message"]["progress"] = [PROCESS_STEPS[current_step]]
                            infoxmed20_answer_queue_message = PPT_ONE_PROCESS
                    else:
                        print(f"[警告] 未知的chunk类型：{data_type}，已跳过")
                        continue
                    mq_handler.send_message(infoxmed20_answer_queue_message)
                    logger.info(f"[Info] 发送状态数据完成(逐个步骤完成信息)：{infoxmed20_answer_queue_message}")
                except Exception as chunk_error:
                    print("[错误] 处理 chunk 时发生异常：", chunk_error)
                    traceback.print_exc()
                    send_error_message(f"处理数据块出错：{chunk_error}")
        except Exception as stream_error:
            print("[错误] 流消费失败：", stream_error)
            traceback.print_exc()
            send_error_message(f"处理流出错：{stream_error}")
        finally:
            mq_handler.close_connection()

    asyncio.run(consume())

def handle_infoxmed20_queue_message(infoxmed20_message):
    """
    处理从InfoXMed20队列接收到的消息
    """
    # 解析mq消息
    print(f"处理消息handle_infoxmed20_queue_message: {infoxmed20_message}")
    session_id = infoxmed20_message['message']['sessionId']
    user_id = infoxmed20_message['message']['userId']
    function_id = infoxmed20_message['message']['functionId']
    type = infoxmed20_message['type']
    prompt = infoxmed20_message['message']['prompt']
    # #输出语言
    # language = infoxmed20_message['message']['attachment']['language']
    # #文献选择时间
    # select_time= infoxmed20_message['message']['attachment']['select_time']    
    # 类型：type为0表示生成大纲, 1生成ppt
    infoxmed20_message_type = int(type)
    # 是否要调用function，默认调用，只有明确不掉用时才不调用
    # link_id:如果没有对应的key，默认为None
    link_id = infoxmed20_message['message']['linkId']
    attachment = infoxmed20_message['message']['attachment']
    # 调用GPT
    response = None
    stream_response = None
    reasoning_stream_response = None
    stream_response_dify = None
    if function_id == 5538134:
        agent_session_id = session_id + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if infoxmed20_message_type == 0:
            # 处理大纲内容
            attachment_doclist = attachment.get("docList", [])
            language = attachment.get("language", "chinese")
            select_time = attachment.get("time", [])
            # 添加language和select_time到metadata中
            if attachment_doclist:
                pmids = [doc["pmid"] for doc in attachment_doclist]
                metadata = {"pmids":pmids, "language":language, "select_time":select_time}
            else:
                metadata = {"language":language, "select_time":select_time}
            stream_response = send_outline_prompt_streaming(prompt=prompt,metadata=metadata, agent_card_url=os.environ["OUTLINE_URL"])
            handle_outline_stream_response(link_id, session_id, user_id, function_id, attachment, stream_response)
        elif infoxmed20_message_type == 1:
            # 处理ppt内容
            if isinstance(prompt, str):
                prompt_data = json.loads(prompt)
            else:
                prompt_data = prompt
            pmids = prompt_data.get("pmidList", [])
            outline = data_to_markdown(data=prompt_data["data"])
            title = prompt_data["data"][0]['content']
            language = attachment.get("language", "chinese")
            select_time = attachment.get("time", []) 
            stream_response = send_ppt_outline_streaming(outline=outline, metadata={"language":language, "numSlides": 12, "pmids":pmids,"select_time":select_time}, agent_card_url=os.environ["SLIDES_URL"])
            handle_ppt_stream_response(link_id, session_id, user_id, function_id, attachment, stream_response, title)
    else:
        print('不在进行处理这条消息，function_id NOT  : ' + str(function_id))
        return


def callback(ch, method, properties, body):
    """
    mq接收到消息后的回调函数，多线程处理
    """
    try:
        # 接收到mq的消息：转换成dict
        print(f"😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁😁 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        infoxmed20_message = json.loads(json.loads(body.decode('utf-8')))
        print(f" [🚚] 从mq接受到消息：{infoxmed20_message}")
        logger.info(f"[🚚] 从mq接受到消息：{infoxmed20_message}")
        # 提交任务到线程池
        executor.submit(handle_infoxmed20_queue_message, infoxmed20_message)
        # 手动发送消息确认
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"处理消息时出错: {e}")
        # 出错时拒绝消息并重新入队
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

if __name__ == '__main__':
    start_consumer(callback, auto_ack=False)