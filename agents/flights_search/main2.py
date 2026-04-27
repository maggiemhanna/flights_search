# Copyright (c) 2024 Maggie Mhanna
# All rights reserved.

import json
import os
import asyncio
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

def get_location_ids(city_name: str, api_key: str) -> List[str]:
    try:
        search = GoogleSearch({
            "engine": "google_flights_autocomplete",
            "q": city_name,
            "api_key": api_key
        })
        results = search.get_dict()
        
        ids = []
        if "suggestions" in results:
            for suggestion in results["suggestions"]:
                if suggestion.get("type") == "airport":
                    ids.append(suggestion["id"])
                elif suggestion.get("type") == "city" and suggestion.get("airports"):
                    for airport in suggestion["airports"]:
                        ids.append(airport["id"])
                elif suggestion.get("id") and len(suggestion["id"]) == 3 and suggestion["id"].isupper():
                    ids.append(suggestion["id"])
        
        unique_ids = list(dict.fromkeys(ids))
        return unique_ids[:2]
    except Exception as e:
        logger.error(f"Error resolving location IDs for {city_name}: {e}")
    return []

async def fetch_google_flights(input_data: FlightsSearchInput) -> FlightsSearchOutput:
    api_key = os.environ.get("SERPAPI_API_KEY") or os.environ.get("SERPAPI_KEY")
    if not api_key:
        logger.error("SERPAPI_API_KEY environment variable not set.")
        raise HTTPException(status_code=500, detail="SERPAPI_API_KEY not configured")

    origin_ids = get_location_ids(input_data.origin, api_key)
    dest_ids = get_location_ids(input_data.destination, api_key)

    if not origin_ids or not dest_ids:
        logger.error(f"Could not resolve location IDs for {input_data.origin} or {input_data.destination}")
        raise HTTPException(status_code=400, detail="Could not resolve location IDs for cities provided")

    all_flights_pool = []
    
    import itertools
    for origin_id, dest_id in itertools.product(origin_ids, dest_ids):
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
        
        if input_data.filters.direct:
            search_params["stops"] = 1
        elif input_data.filters.max_stops is not None:
            if input_data.filters.max_stops == 0:
                search_params["stops"] = 1
            elif input_data.filters.max_stops == 1:
                search_params["stops"] = 2
            elif input_data.filters.max_stops == 2:
                search_params["stops"] = 3
                
        if input_data.filters.max_price is not None:
            search_params["max_price"] = input_data.filters.max_price
        try:
            search = GoogleSearch(search_params)
            results = search.get_dict()
            flights = results.get("best_flights", []) + results.get("other_flights", [])
            all_flights_pool.extend(flights)
        except Exception as e:
            logger.error(f"Error calling SerpApi for {origin_id}->{dest_id}: {e}")

    if not all_flights_pool:
        raise HTTPException(status_code=404, detail="No flights found for any airport combination")

    import random
    sample_size = min(15, len(all_flights_pool))
    sampled_flights = random.sample(all_flights_pool, sample_size)

    async def get_return_times(flight, origin_id, dest_id):
        if "departure_token" not in flight:
            return "N/A", "N/A"
        departure_token = flight["departure_token"]
        
        def call_serpapi():
            from serpapi import GoogleSearch
            search = GoogleSearch({
                "engine": "google_flights",
                "departure_token": departure_token,
                "departure_id": origin_id,
                "arrival_id": dest_id,
                "outbound_date": input_data.departure_date,
                "return_date": input_data.return_date,
                "api_key": api_key
            })
            return search.get_dict()
            
        try:
            results = await asyncio.to_thread(call_serpapi)
            options = results.get("best_flights", []) + results.get("other_flights", [])
            if options:
                best = options[0]
                legs = best.get("flights", [])
                if legs:
                    return legs[0].get("departure_airport", {}).get("time", "N/A"), legs[-1].get("arrival_airport", {}).get("time", "N/A")
        except Exception as e:
            logger.error(f"Error fetching return flights for {departure_token}: {e}")
        return "N/A", "N/A"

    tasks = []
    for flight in sampled_flights:
        outbound_legs = flight.get("flights", [])
        if outbound_legs:
            o_id = outbound_legs[0].get("departure_airport", {}).get("id")
            d_id = outbound_legs[-1].get("arrival_airport", {}).get("id")
            tasks.append(get_return_times(flight, o_id, d_id))
        else:
            tasks.append(asyncio.sleep(0, result=("N/A", "N/A")))
            
    return_data = await asyncio.gather(*tasks)

    flights_list = []
    for flight, (ret_time, ret_arr_time) in zip(sampled_flights, return_data):
        flights_array = flight.get("flights", [])
        if not flights_array:
            continue
            
        outbound_legs = flights_array
        price = str(flight.get("price", "N/A"))
        primary_leg = outbound_legs[0]
        airline = primary_leg.get("airline", "N/A")
        flight_number = primary_leg.get("flight_number", "N/A")
        
        stops = len(outbound_legs) - 1
        stopover_cities = [leg.get("arrival_airport", {}).get("name", "N/A") for leg in outbound_legs[:-1]] if stops > 0 else []
        
        departure_time = outbound_legs[0].get("departure_airport", {}).get("time", "N/A")
        arrival_time = outbound_legs[-1].get("arrival_airport", {}).get("time", "N/A")
        
        return_time = ret_time
        return_arrival_time = ret_arr_time

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
        results = await fetch_google_flights(user_input)
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
