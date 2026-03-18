# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from google.adk.apps import App

from agents.flights_search.prompt import system_instruction
from agents.flights_search.schema import FlightsSearchInput, FlightsSearchOutput

from utils.logging import setup_logging

logger = setup_logging(name=__name__)

APP_NAME = "agents"

# Create the agent
flights_search = Agent(
    model=Gemini(model="gemini-2.5-flash", use_interactions_api=False),
    name="flights_search",
    description="""The Flight Search Agent: An expert flight search simulator. 
    This agent generates a list of flights based on the user's input.""",
    instruction=system_instruction,
    input_schema=FlightsSearchInput,
    output_schema=FlightsSearchOutput,
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
    root_agent=flights_search,
)