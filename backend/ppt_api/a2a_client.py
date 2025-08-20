import uuid
import httpx
from a2a.client import A2AClient
import asyncio
from a2a.types import (MessageSendParams, SendMessageRequest, SendStreamingMessageRequest)

async def httpx_client():
    timeout = httpx.Timeout(30.0)  # 设置为 30 秒
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:
        # 初始化客户端（确保base_url包含协议头）
        client = await A2AClient.get_client_from_agent_card_url(
            httpx_client, 'http://localhost:10001'  # 确保此处是完整 URL
        )

        # 生成唯一请求ID
        request_id = uuid.uuid4().hex
        # 构造消息参数
        send_message_payload = {
            'message': {
                'role': 'user',
                'parts': [{'type': 'text', 'text': prompt}],
                'messageId': request_id
            }
        }
        print(f"发送message信息: {send_message_payload}")
        # 流式请求的示例
        streaming_request = SendStreamingMessageRequest(
            id=request_id,
            params=MessageSendParams(**send_message_payload)  # 同样的 payload 可以用于非流式请求
        )

        stream_response = client.send_message_streaming(streaming_request)
        async for chunk in stream_response:
            print(chunk.model_dump(mode='json', exclude_none=True))


async def send_outline_prompt_streaming(prompt: str, metadata={}, agent_card_url: str = 'http://localhost:10001'):
    """
    发送用户 prompt 给指定 A2A Agent，使用流式方式返回响应。
    # metadata =
    :param prompt: 用户输入的提示文本
    :param agent_card_url: agent card 的 URL，默认是本地地址
    """
    timeout = httpx.Timeout(30.0)  # 设置超时时间为 30 秒
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:
        try:
            # 初始化客户端
            client = await A2AClient.get_client_from_agent_card_url(httpx_client, agent_card_url)

            # 构造请求 ID 和请求 payload
            request_id = uuid.uuid4().hex
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [{'type': 'text', 'text': prompt}],
                    'messageId': request_id,
                    'metadata': metadata
                }
            }

            print(f"发送 message 信息: {send_message_payload}")

            # 创建流式消息请求
            streaming_request = SendStreamingMessageRequest(
                id=request_id,
                params=MessageSendParams(**send_message_payload)
            )

            # 处理流式响应
            stream_response = client.send_message_streaming(streaming_request)
            async for chunk in stream_response:
                chunk_data = chunk.model_dump(mode='json', exclude_none=True)
                yield {"type": "data", "text": chunk_data}
        except Exception as e:
            print(f"发送失败: {e}")
            yield {"type":"error", "text": f"发送失败: {e}"}
    yield {"type":"final", "text": "发送完成"}

async def send_ppt_outline_streaming(outline: str, metadata={}, agent_card_url: str = 'http://localhost:10011'):
    """
    发送用户 outline 给指定 A2A Agent，使用流式方式返回响应。

    :param outline: 用户输入的提示文本
    :param agent_card_url: agent card 的 URL，默认是本地地址
    """
    timeout = httpx.Timeout(30.0)  # 设置超时时间为 30 秒
    async with httpx.AsyncClient(timeout=timeout) as httpx_client:
        try:
            # 初始化客户端
            client = await A2AClient.get_client_from_agent_card_url(httpx_client, agent_card_url)

            # 构造请求 ID 和请求 payload
            request_id = uuid.uuid4().hex
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [{'type': 'text', 'text': outline}],
                    'messageId': request_id,
                    'metadata': metadata
                }
            }

            print(f"发送 message 信息: {send_message_payload}")

            # 创建流式消息请求
            streaming_request = SendStreamingMessageRequest(
                id=request_id,
                params=MessageSendParams(**send_message_payload)
            )

            # 处理流式响应
            stream_response = client.send_message_streaming(streaming_request)
            async for chunk in stream_response:
                chunk_data = chunk.model_dump(mode='json', exclude_none=True)
                yield {"type": "data", "text": chunk_data}
        except Exception as e:
            print(f"发送失败: {e}")
            yield {"type":"error", "text": f"发送失败: {e}"}
    yield {"type":"final", "text": "发送完成"}


async def send_ppt_outline_streaming_simulate(outline: str, metadata={}, agent_card_url: str = 'http://localhost:10011'):
    """
    发送用户 outline 给指定 A2A Agent，使用流式方式返回响应。

    :param outline: 用户输入的提示文本
    :param agent_card_url: agent card 的 URL，默认是本地地址
    """
    stream_response = ["1","2","3","4"]
    try:
        for chunk in stream_response:
            yield {"type": "data", "text": chunk}
    except Exception as e:
        print(f"发送失败: {e}")
        yield {"type":"error", "text": f"发送失败: {e}"}
    yield {"type":"final", "text": "发送完成"}

if __name__ == '__main__':
    # prompt = """特斯拉汽车"""
    asyncio.run(httpx_client())
