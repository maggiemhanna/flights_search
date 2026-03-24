# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from google.adk.apps import App

from agents.inspiration.prompt import system_instruction
from agents.inspiration.schema import InspirationInput, InspirationOutput

from utils.logging import setup_logging

logger = setup_logging(name=__name__)

APP_NAME = "agents"

# Create the agent
inspiration = Agent(
    model=Gemini(model="gemini-2.5-flash", use_interactions_api=False),
    name="inspiration",
    description="""The Inspiration Agent: An expert flight inspiration simulator. 
    Your goal is to generate a new destination, or dates based on user message.""",
    instruction=system_instruction,
    input_schema=InspirationInput,
    output_schema=InspirationOutput,
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
    root_agent=inspiration,
)