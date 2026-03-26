import sys
import requests

# Import the custom logger from your project utilities
from utils.logging import setup_logging, format_dict_for_logs

logger = setup_logging(name=__name__)

BASE_URL = "https://inspiration-service-874751466618.europe-west9.run.app"

def test_root_endpoint():
    """Test the root health-check endpoint."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Details: {response.text}"
    assert response.json() == {"message": "Inspiration Agent Service is running. Use the /run-inspiration endpoint via POST."}

def test_run_inspiration():
    """Test the inspiration endpoint and validate the exact JSON structure."""
    
    payload = {
        "origin": "Paris",
        "destination": "New York",
        "departure_date": "2026-05-10",
        "return_date": "2026-05-20",
        "passengers": 1,
        "user_message": "I want to go to a city in Europe",
        "conversational_history": []
    }

    logger.info(f"Payload:\n{format_dict_for_logs(payload)}")

    # Issue the POST request to the deployed microservice endpoint
    response = requests.post(f"{BASE_URL}/run-inspiration", json=payload)
    
    # Verify HTTP status code
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Details: {response.text}"
    
    # Parse JSON
    data = response.json()
    assert data["status"] == "success"
    
    # Extract the actual agent results from the endpoint envelope
    results = data["results"]

    logger.info(f"Agent Response:\n{format_dict_for_logs(results)}")

    # --- User-Defined Assertions ---
    
    assert isinstance(results, list), "Expected 'results' to be a list"
    assert len(results) > 0, "Expected 'results' to contain at least one item"
    assert "origin" in results[0], "Expected 'origin' key in the first result"
    assert isinstance(results[0]["origin"], str), "Expected 'origin' value to be a string"
    
    assert "destination" in results[0], "Expected 'destination' key in the first result"
    assert isinstance(results[0]["destination"], str), "Expected 'destination' value to be a string"

# --- Manual Execution Block ---
if __name__ == "__main__":
    logger.info(f"Running microservice tests against {BASE_URL}...")
    
    try:
        logger.info("Running test_root_endpoint...")
        test_root_endpoint()
        logger.info("✅ test_root_endpoint passed!")

        logger.info("Running test_run_inspiration...")
        # Note: If this hits a real LLM, it might take a few seconds to return.
        test_run_inspiration()
        logger.info("✅ test_run_inspiration passed!")

        logger.info("🎉 All tests completed successfully!")

    except AssertionError as e:
        logger.error(f"❌ Assertion Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)
