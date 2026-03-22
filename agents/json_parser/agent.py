# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

from google.adk.agents.llm_agent import Agent
from google.adk.models.google_llm import Gemini
from google.adk.planners import BuiltInPlanner
from google.genai.types import ThinkingConfig
from google.adk.apps import App

from agents.json_parser.prompt import system_instruction
from agents.json_parser.schema import JSONParserInput, JSONParserOutput

from utils.logging import setup_logging

logger = setup_logging(name=__name__)

APP_NAME = "agents"

# Create the agent
json_parser = Agent(
    model=Gemini(model="gemini-2.5-flash", use_interactions_api=False),
    name="json_parser_agent",
    description="""The JSON Parser Agent: An expert at parsing the results into JSON format.""",
    instruction=system_instruction,
    input_schema=JSONParserInput,
    output_schema=JSONParserOutput,
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
    root_agent=json_parser,
)