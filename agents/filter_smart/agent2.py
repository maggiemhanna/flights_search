import os
import yaml
import json
from pathlib import Path
from typing import List, TypedDict, Any

from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, END
from langchain_core.tools import Tool
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_community import GoogleSearchAPIWrapper

from agents.filter_smart.schema import FilterSmartInput, FilterSmartOutput
from agents.filter_smart.prompt import system_instruction
from utils.logging import setup_logging

import re

def load_json_with_markdown(data):
    # Strip leading/trailing whitespace
    data = data.strip()
    
    # Regex to find content inside ```json ... ``` or ``` ... ```
    # Pattern explanation:
    # ```(?:json)? -> matches opening triple backticks and optional 'json' tag
    # \s*          -> matches any whitespace/newlines after the opening
    # (.*?)        -> non-greedy match of the actual JSON content
    # \s*```       -> matches trailing whitespace and closing backticks
    match = re.search(r"```(?:json|JSON)?\s*(.*?)\s*```", data, re.DOTALL)
    
    if match:
        data = match.group(1)
    
    return json.loads(data)

logger = setup_logging(name=__name__)

ENV_FILE_PATH = Path("agents/filter_smart/env.yaml")

def load_env_variables(file_path: Path) -> None:
    """Reads a YAML file and sets the key-value pairs as environment variables."""
    if not file_path.exists():
        logger.error(f"Environment file not found: {file_path}")
        return

    try:
        with file_path.open('r') as file:
            env_vars = yaml.safe_load(file) or {}
            for key, value in env_vars.items():
                os.environ[key] = str(value) 
                logger.info(f"Loaded {key} into environment.")
    except Exception as e:
        logger.error(f"Error loading environment variables from {file_path}: {e}")

# Load the environment variables before initializing the app
load_env_variables(ENV_FILE_PATH)

# This is the internal state of our Graph
class AgentState(TypedDict):
    user_message: str
    conversational_history: List[str]
    flights_input: List[dict]  # Dictionary format for LLM processing
    filter_response: str
    flights_output: List[dict]
    tool_calls: List[Any]

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    project="children-books-project",
    location="europe-west9",  
    temperature=1.0,  
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

search = GoogleSearchAPIWrapper()

def top5_results(query):
    return search.results(query, 5)

search_tool = Tool(
    name="GoogleSearch",
    description="Searches Google for recent results.",
    func=top5_results,
)
tools = [search_tool]
model_with_tools = model.bind_tools(tools)

# Use LLM model to process messages and generate responses, return responses with tool calls
def call_model(state: AgentState):
    logger.info(f"--- State ---\n{state}")
    logger.info(f"--- User Message ---\n{state['user_message']}")
    logger.info(f"--- Conversational History ---\n{state['conversational_history']}")
    logger.info(f"--- Flights Input ---\n{state['flights_input']}")

    system_message = system_instruction.format(
        user_message=state["user_message"],
        conversational_history=state["conversational_history"],
        flights_input=state["flights_input"],
    )
    
    messages = [SystemMessage(content=system_message)] + [HumanMessage(content=state["user_message"])]

    response = model_with_tools.invoke(messages)
    logger.info(f"--- Agent Response ---\n{response}")

    # Extract the response content
    response_content = response.content
    logger.info(f"--- Response Content ---\n{response_content}")

    response_tool_calls = response.tool_calls
    logger.info(f"--- Response Tool Calls ---\n{response_tool_calls}")
    
    if not response_tool_calls:
        response_json = load_json_with_markdown(response_content)
        logger.info(f"--- Response JSON ---\n{response_json}")
        return {"filter_response": response_json["filter_response"], "flights_output": response_json["flights_output"], "tool_calls": response_tool_calls}
    else:
        return {"tool_calls": response_tool_calls}

def call_tool_node(state: AgentState):
    tool_calls = state["tool_calls"]
    logger.info(f"--- Tool Calls ---\n{tool_calls}")
    for tool_call in tool_calls:
        logger.info(f"--- Tool Call ---\n{tool_call}")
        logger.info(f"--- Tool Call Result ---\n{search_tool.invoke(tool_call["args"])}")
    return 

# Define the conditional edge that determines whether to continue or not
def should_continue(state: AgentState):
    tool_calls = state["tool_calls"]
    # If the last message is not a tool call, then finish
    if not tool_calls:
        return "end"
    # default to continue
    return "continue"

# --- 4. Build the Graph ---

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("call_model", call_model)
workflow.add_node("call_tool_node", call_tool_node)

# Set Entry Point and Edges
workflow.set_entry_point("call_model")
workflow.add_conditional_edges(
    "call_model",
    should_continue,
    {
        "continue": "call_tool_node",
        "end": END,
    },
)
workflow.add_edge("call_tool_node", "call_model")

# Compile the Graph
app = workflow.compile()

if __name__ == "__main__":
    example_flights = [
        {"flight_number": "DL123", "airline": "Delta", "origin": "JFK", "destination": "LAX", "departure_time": "10:00 AM", "price": 450},
        {"flight_number": "NK99", "airline": "Spirit", "origin": "JFK", "destination": "LAX", "departure_time": "11:00 AM", "price": 200}
    ]
    
    inputs = {
        "user_message": "I want a flight with fast WiFi.",
        "conversational_history": [],
        "flights_input": example_flights
    }
    
    final_state = app.invoke(inputs)
    logger.info(f"--- Final State ---\n{final_state}")