# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from google.adk.apps import App
from google.adk.tools import google_search

from agents.filter_smart.prompt import system_instruction
from agents.filter_smart.schema import FilterSmartInput, FilterSmartOutput

from utils.logging import setup_logging

logger = setup_logging(name=__name__)

APP_NAME = "agents"

# Create the agent
filter_smart = Agent(
    model=Gemini(model="gemini-2.5-flash", use_interactions_api=False),
    name="filter_smart_agent",
    description="""The Filter Smart Agent: An expert at filtering the results of the flights search agent that are not based on existing filters.""",
    instruction=system_instruction,
    tools=[google_search],
    input_schema=FilterSmartInput,
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
    root_agent=filter_smart,
)