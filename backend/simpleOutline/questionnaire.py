
from google.adk.agents import LoopAgent, LlmAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from typing import AsyncGenerator

# 1. Define Questions
QUESTIONS = [
    "What is your favorite programming language and why?",
    "What is your experience with building AI agents?",
    "What are you hoping to achieve with this questionnaire?"
]

# Initialize state
initial_state = {
    "current_question_index": 0,
    "answers": [],
    "user_input": ""
}

# 2. Agent to ask the current question
class AskQuestion(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        current_index = ctx.session.state.get("current_question_index", 0)
        if current_index < len(QUESTIONS):
            question = QUESTIONS[current_index]
            yield Event(author=self.name, actions=EventActions(notify=f"Question {current_index + 1}: {question}"))
        yield Event(author=self.name, actions=EventActions())

# 3. Agent to check the user's answer
answer_checker = LlmAgent(
    name="AnswerChecker",
    instruction="Evaluate the user's answer in state['user_input']. If the answer is substantive (not a skip or empty), output 'pass'. Otherwise, output 'fail'.",
    output_key="answer_status"
)

# 4. Agent to control the flow
class FlowController(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        status = ctx.session.state.get("answer_status", "fail")
        current_index = ctx.session.state.get("current_question_index", 0)
        
        if status == "pass":
            # Save the answer and move to the next question
            answers = ctx.session.state.get("answers", [])
            user_input = ctx.session.state.get("user_input", "")
            answers.append(user_input)
            ctx.session.state["answers"] = answers
            
            next_index = current_index + 1
            ctx.session.state["current_question_index"] = next_index
            
            if next_index >= len(QUESTIONS):
                # All questions answered, stop the loop
                yield Event(author=self.name, actions=EventActions(escalate=True))
            else:
                # Continue to the next question
                yield Event(author=self.name, actions=EventActions())
        else:
            # Repeat the current question
            yield Event(author=self.name, actions=EventActions(notify="Please provide a more detailed answer."))

# 5. The main loop for the questionnaire
questionnaire_loop = LoopAgent(
    name="QuestionnaireLoop",
    max_iterations=len(QUESTIONS) * 2,  # Allow for re-asking each question once
    sub_agents=[
        AskQuestion(name="Ask"),
        # Here you would typically get user input and put it into state['user_input']
        # For this example, we'll assume it's pre-filled for each iteration
        answer_checker,
        FlowController(name="Control")
    ]
)

# 6. Agent to provide the final summary
summary_agent = LlmAgent(
    name="SummaryAgent",
    instruction="Summarize the user's answers in state['answers'] and provide a concluding remark.",
    output_key="final_summary"
)

