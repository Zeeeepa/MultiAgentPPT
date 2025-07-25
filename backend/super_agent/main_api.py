import logging
import os

import click
import uvicorn

from adk_agent_executor import ADKAgentExecutor
from dotenv import load_dotenv
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from starlette.routing import Route
from google.adk.agents.run_config import RunConfig, StreamingMode
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from starlette.applications import Starlette
from agent import root_agent

# 加载环境变量
load_dotenv()

# 配置日志格式和级别
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

@click.command()
@click.option("--host", "host", default="localhost", help="服务器绑定的主机名（默认为 localhost,可以指定具体本机ip）")
@click.option("--port", "port", default=10012, help="服务器监听的端口号（默认为 10012）")
def main(host, port):
    """
    启动ppt Agent服务，支持流式和非流式输出。
    """
    streaming = os.environ.get("STREAMING") == "true"
    agent_card_name = "ppt Agent"
    agent_name = "ppt_agent"
    agent_description = "generate ppt outline and content"

    # 定义Agent技能
    skill = AgentSkill(
        id=agent_name,
        name=agent_card_name,
        description=agent_description,
        tags=["ppt"],
        examples=["ppt"],
    )

    # 构建Agent卡片信息
    agent_card = AgentCard(
        name=agent_card_name,
        description=agent_description,
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )

    logger.info("初始化Runner...")
    runner = Runner(
        app_name=agent_card.name,
        agent=root_agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    # 根据环境变量决定是否启用流式输出
    if streaming:
        logger.info("启用流式SSE模式")
        run_config = RunConfig(
            streaming_mode=StreamingMode.SSE,
            max_llm_calls=500
        )
    else:
        logger.info("启用非流式模式")
        run_config = RunConfig(
            streaming_mode=StreamingMode.NONE,
            max_llm_calls=500
        )

    # 初始化Agent执行器
    agent_executor = ADKAgentExecutor(runner, agent_card, run_config)

    # 初始化请求处理器
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor, task_store=InMemoryTaskStore()
    )

    # 构建A2A应用
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

    logger.info(f"服务启动中: http://{host}:{port}/")
    uvicorn.run(a2a_app.build(), host=host, port=port)

if __name__ == "__main__":
    main()
