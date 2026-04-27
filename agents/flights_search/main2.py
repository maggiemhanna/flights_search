# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

import json
import os
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

import yaml
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents.flights_search.schema import FlightsSearchInput, FlightsSearchOutput, Flight
from utils.logging import setup_logging, format_dict_for_logs

# We need serpapi, let's try to import it
try:
    from serpapi import GoogleSearch
except ImportError:
    # Define a mock or just let it fail later
    pass

logger = setup_logging(name=__name__)

APP_NAME = "flights_search"
ENV_FILE_PATH = Path("agents/flights_search/env.yaml")

def load_env_variables(file_path: Path) -> None:
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

load_env_variables(ENV_FILE_PATH)

api = FastAPI(
    title="Flights Search Agent Service (SerpApi)",
    description="API for running the Flights Search Agent using SerpApi."
)

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    return {"message": "Flights Search Agent Service (SerpApi) is running."}

def get_location_id(city_name: str, api_key: str) -> str | None:
    try:
        search = GoogleSearch({
            "engine": "google_flights_autocomplete",
            "q": city_name,
            "api_key": api_key
        })
        results = search.get_dict()
        
        if "suggestions" in results:
            for suggestion in results["suggestions"]:
                if suggestion.get("type") == "airport":
                    return suggestion["id"]
                elif suggestion.get("type") == "city" and suggestion.get("airports"):
                    return suggestion["airports"][0]["id"]
                elif suggestion.get("id") and len(suggestion["id"]) == 3 and suggestion["id"].isupper():
                    return suggestion["id"]
    except Exception as e:
        logger.error(f"Error resolving location ID for {city_name}: {e}")
    return None

def fetch_google_flights(input_data: FlightsSearchInput) -> FlightsSearchOutput:
    api_key = os.environ.get("SERPAPI_API_KEY") or os.environ.get("SERPAPI_KEY")
    if not api_key:
        logger.error("SERPAPI_API_KEY environment variable not set.")
        raise HTTPException(status_code=500, detail="SERPAPI_API_KEY not configured")

    origin_id = get_location_id(input_data.origin, api_key)
    dest_id = get_location_id(input_data.destination, api_key)

    if not origin_id or not dest_id:
        logger.error(f"Could not resolve location IDs for {input_data.origin} or {input_data.destination}")
        raise HTTPException(status_code=400, detail="Could not resolve location IDs for cities provided")

    search_params = {
        "engine": "google_flights",
        "departure_id": origin_id,
        "arrival_id": dest_id,
        "outbound_date": input_data.departure_date,
        "return_date": input_data.return_date,
        "currency": "EUR",
        "hl": "en",
        "type": 1,
        "api_key": api_key
    }

    try:
        search = GoogleSearch(search_params)
        results = search.get_dict()
        logger.info(f"SerpApi top level keys: {list(results.keys())}")
        if "best_flights" in results and results["best_flights"]:
            first_flight = results["best_flights"][0]
            logger.info(f"First flight top level keys: {list(first_flight.keys())}")
            if "flights" in first_flight:
                logger.info(f"First flight segments count: {len(first_flight['flights'])}")
                for i, leg in enumerate(first_flight['flights']):
                    logger.info(f"Leg {i} times: dep={leg.get('departure_airport', {}).get('time')}, arr={leg.get('arrival_airport', {}).get('time')}")
    except Exception as e:
        logger.error(f"Error calling SerpApi: {e}")
        raise HTTPException(status_code=500, detail="Error fetching flights from provider")

    flights_list = []
    all_flights = results.get("best_flights", []) + results.get("other_flights", [])
    
    for index, flight in enumerate(all_flights[:3]):
        flights_array = flight.get("flights", [])
        if not flights_array:
            continue
            
        outbound_legs = flights_array
        
        # Defensive parsing
        price = str(flight.get("price", "N/A"))
        primary_leg = outbound_legs[0]
        airline = primary_leg.get("airline", "N/A")
        flight_number = primary_leg.get("flight_number", "N/A")
        
        stops = len(outbound_legs) - 1
        stopover_cities = [leg.get("arrival_airport", {}).get("name", "N/A") for leg in outbound_legs[:-1]] if stops > 0 else []
        
        # Extract times
        departure_time = outbound_legs[0].get("departure_airport", {}).get("time", "N/A")
        arrival_time = outbound_legs[-1].get("arrival_airport", {}).get("time", "N/A")
        
        return_time = "N/A"
        return_arrival_time = "N/A"
        
        # Fetch return flights for each option (makes extra API calls)
        if "departure_token" in flight:
            departure_token = flight["departure_token"]
            try:
                return_search = GoogleSearch({
                    "engine": "google_flights",
                    "departure_token": departure_token,
                    "departure_id": origin_id,
                    "arrival_id": dest_id,
                    "outbound_date": input_data.departure_date,
                    "return_date": input_data.return_date,
                    "api_key": api_key
                })
                return_results = return_search.get_dict()
                return_options = return_results.get("best_flights", []) + return_results.get("other_flights", [])
                logger.info(f"Return results keys: {list(return_results.keys())}")
                if "error" in return_results:
                    logger.error(f"SerpApi error for return flights: {return_results['error']}")
                if return_options:
                    logger.info(f"First return option keys: {list(return_options[0].keys())}")
                    if "flights" in return_options[0]:
                        logger.info(f"First return option segments count: {len(return_options[0]['flights'])}")
                        for i, leg in enumerate(return_options[0]['flights']):
                            logger.info(f"Return Leg {i} times: dep={leg.get('departure_airport', {}).get('time')}, arr={leg.get('arrival_airport', {}).get('time')}")
                    best_return = return_options[0]
                    return_legs = best_return.get("flights", [])
                    if return_legs:
                        return_time = return_legs[0].get("departure_airport", {}).get("time", "N/A")
                        return_arrival_time = return_legs[-1].get("arrival_airport", {}).get("time", "N/A")
            except Exception as e:
                logger.error(f"Error fetching return flights: {e}")

        origin_str = f"{input_data.origin} ({outbound_legs[0].get('departure_airport', {}).get('id', 'N/A')})"
        dest_str = f"{input_data.destination} ({outbound_legs[-1].get('arrival_airport', {}).get('id', 'N/A')})"
        
        flights_list.append(Flight(
            origin=origin_str,
            destination=dest_str,
            departure_date=input_data.departure_date,
            return_date=input_data.return_date,
            departure_time=departure_time,
            arrival_time=arrival_time,
            return_time=return_time,
            return_arrival_time=return_arrival_time,
            price=price,
            airline=airline,
            flight_number=flight_number,
            stops=stops,
            stopover_cities=stopover_cities
        ))

    return FlightsSearchOutput(flights=flights_list)

@api.post("/run-flights-search", response_model=Dict[str, Any], tags=["Agent"])
async def run_flights_search(user_input: FlightsSearchInput) -> Dict[str, Any]:
    logger.info(f"--- Raw User Input ---\n{format_dict_for_logs(user_input.model_dump())}")
    
    try:
        results = fetch_google_flights(user_input)
        return {
            "status": "success",
            "results": [results.model_dump()]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.exception("A critical error occurred while processing the request.")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal Server Error: {e}"
        )

if __name__ == "__main__":
    logger.info("Starting Uvicorn server for SerpApi Agent...")
    uvicorn.run(api, host="127.0.0.1", port=8006)
