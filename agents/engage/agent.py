# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from google.adk.apps import App

from agents.engage.prompt import system_instruction
from agents.engage.schema import EngageInput, EngageOutput

from utils.logging import setup_logging

logger = setup_logging(name=__name__)

APP_NAME = "agents"

# Create the agent
engage = Agent(
    model=Gemini(model="gemini-2.5-flash", use_interactions_api=False),
    name="engage",
    description="""The Engage Agent: An expert at understanding user intent and extracting key information from their messages in order to decide which agent to use.""",
    instruction=system_instruction,
    input_schema=EngageInput,
    output_schema=EngageOutput,
    include_contents='none',
    planner=BuiltInPlanner(
        thinking_config=ThinkingConfig(
            include_thoughts=False,
            thinking_budget=0,
        )
    )
)

# Create the main App
app = App(
    name=APP_NAME,
    root_agent=engage,
)