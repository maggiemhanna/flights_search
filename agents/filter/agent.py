# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from google.adk.apps import App

from agents.filter.prompt import system_instruction
from agents.filter.schema import FilterInput, FilterOutput

from utils.logging import setup_logging

logger = setup_logging(name=__name__)

APP_NAME = "agents"

# Create the agent
filter = Agent(
    model=Gemini(model="gemini-2.5-flash", use_interactions_api=False),
    name="filter_agent",
    description="""The Filter Agent: An expert at filtering the results of the flights search agent based on existing filters.""",
    instruction=system_instruction,
    input_schema=FilterInput,
    output_schema=FilterOutput,
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
    root_agent=filter,
)