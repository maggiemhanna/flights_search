import sys
from fastapi.testclient import TestClient

# Import the custom logger from your project utilities
from utils.logging import setup_logging

logger = setup_logging(name=__name__)

# Import the FastAPI app from your main.py file.
try:
    from agents.flights_search.main import api 
except ImportError:
    logger.error("Could not import 'api' from 'main.py'")
    sys.exit(1)

# Initialize the TestClient
client = TestClient(api)

def test_root_endpoint():
    """Test the root health-check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Flights Search Agent Service is running. Use the /run-flights-search endpoint via POST."}

def test_run_flights_search():
    """Test the flights search endpoint and validate the exact JSON structure."""
    
    # You may need to adjust this payload to match your exact FlightsSearchInput schema
    payload = {
        "origin": "Paris",
        "destination": "New York",
        "departure_date": "2026-05-10",
        "return_date": "2026-05-20",
        "passengers": 1,
        "filters": {
            "max_price": 1000,
            "max_stops": 1
        }
    }

    # Issue the POST request to the endpoint
    response = client.post("/run-flights-search", json=payload)
    
    # Verify HTTP status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Details: {response.text}"
    
    # Parse JSON
    data = response.json()
    assert data["status"] == "success"
    
    # Extract the actual agent results from the endpoint envelope
    results = data["results"]

    # --- User-Defined Assertions ---
    
    assert isinstance(results, list), "Expected 'results' to be a list"
    assert len(results) > 0, "Expected 'results' to contain at least one item"
    assert "flights" in results[0], "Expected 'flights' key in the first result"
    assert isinstance(results[0]["flights"], list), "Expected 'flights' value to be a list"
    assert len(results[0]["flights"]) > 0, "Expected at least one flight in the 'flights' list"
    
    # Check a specific flight's structure
    first_flight = results[0]["flights"][0]
    assert "flight_number" in first_flight, "Missing 'flight_number'"
    assert "price" in first_flight, "Missing 'price'"
    assert "departure_time" in first_flight, "Missing 'departure_time'"
    assert "return_time" in first_flight, "Missing 'return_time'"

# --- Manual Execution Block ---
if __name__ == "__main__":
    logger.info("Running tests manually without pytest...")
    
    try:
        logger.info("Running test_root_endpoint...")
        test_root_endpoint()
        logger.info("✅ test_root_endpoint passed!")

        logger.info("Running test_run_flights_search...")
        # Note: If this hits a real LLM, it might take a few seconds to return.
        test_run_flights_search()
        logger.info("✅ test_run_flights_search passed!")

        logger.info("🎉 All tests completed successfully!")

    except AssertionError as e:
        logger.error(f"❌ Assertion Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)