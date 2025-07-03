import asyncio
import functools
import logging
import os

import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from starlette.middleware.cors import CORSMiddleware
from google.adk.agents.run_config import RunConfig, StreamingMode
from adk_agent_executor import ADKAgentExecutor  # type: ignore[import-untyped]
from dotenv import load_dotenv


load_dotenv()

# 配置日志格式和级别
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def make_sync(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10008)
@click.option(
    '--calendar-agent', 'calendar_agent', default='http://localhost:10007'
)
def main(host: str, port: int, calendar_agent: str):
    skill = AgentSkill(
        id='plan_parties',
        name='Plan a Birthday Party',
        description='Plan a birthday party, including times, activities, and themes.',
        tags=['event-planning'],
        examples=[
            'My son is turning 3 on August 2nd! What should I do for his party?',
            'Can you add the details to my calendar?',
        ],
    )

    # 根据环境变量决定是否启用流式输出
    streaming = True
    if streaming:
        logger.info("使用 SSE 流式输出模式")
        run_config = RunConfig(
            streaming_mode=StreamingMode.SSE,
            max_llm_calls=500
        )
    else:
        logger.info("使用普通输出模式")
        run_config = RunConfig(
            streaming_mode=StreamingMode.NONE,
            max_llm_calls=500
        )

    # 初始化 agent 执行器
    agent_executor = ADKAgentExecutor(calendar_agent,run_config)
    agent_card = AgentCard(
        name='Birthday Planner',
        description='I can help you plan fun birthday parties.',
        url=f'http://{host}:{port}/',
        version='1.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=streaming),
        skills=[skill],
    )
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    # 构建 Starlette 应用
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    app = a2a_app.build()
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"服务启动中，监听地址: http://{host}:{port}")
    # 启动 uvicorn 服务器
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
