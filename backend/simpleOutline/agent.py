import os
from google.adk.agents import SequentialAgent
from questionnaire import questionnaire_loop, summary_agent
from create_model import create_model
from dotenv import load_dotenv
load_dotenv()

model = create_model(model=os.environ["LLM_MODEL"], provider=os.environ["MODEL_PROVIDER"])

root_agent = SequentialAgent(
    name="questionnaire_root",
    sub_agents=[
        questionnaire_loop,
        summary_agent
    ]
)