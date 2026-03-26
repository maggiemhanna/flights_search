import sys
import requests

# Import the custom logger from your project utilities
from utils.logging import setup_logging, format_dict_for_logs

logger = setup_logging(name=__name__)

BASE_URL = "https://engage-service-874751466618.europe-west9.run.app"

def test_root_endpoint():
    """Test the root health-check endpoint."""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}. Details: {response.text}"
    assert response.json() == {"message": "Engage Agent Service is running. Use the /run-engage endpoint via POST."}

def test_run_engage():
    """Test the engage endpoint and validate the exact JSON structure."""
    
    import os
    import json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tests = json.load(open(os.path.join(current_dir, "tests.json")))

    for test in tests:        

        payload = {
            "user_message": test["user_message"],
            "conversational_history": test["conversational_history"]
        }
        logger.info(f"Payload:\n{format_dict_for_logs(payload)}")

        # Issue the POST request to the deployed microservice endpoint
        response = requests.post(f"{BASE_URL}/run-engage", json=payload)
    
        # Verify HTTP status code
        assert response.status_code == 200, f"Expected 200, got {response.status_code}. Details: {response.text}"
    
        # Parse JSON
        data = response.json()
        assert data["status"] == "success"
    
        # Extract the actual agent results from the endpoint envelope
        results = data["results"][0]

        logger.info(f"Agent Response:\n{format_dict_for_logs(results)}")

        # --- User-Defined Assertions ---
    
        assert isinstance(results, dict), "Expected 'results' to be a dict"
        assert "agent_decision" in results, "Expected 'agent_decision' key in the first result"
        assert isinstance(results["agent_decision"], str), "Expected 'agent_decision' value to be a string."
        assert results["agent_decision"]==test["expected_agent_decision"], f"Expected 'agent_decision' value to be {test['expected_agent_decision']}, got {results['agent_decision']}"

        assert "agent_response" in results, "Missing 'agent_response'"
        assert isinstance(results["agent_response"], str), "Expected 'agent_response' value to be a string"


# --- Manual Execution Block ---
if __name__ == "__main__":
    logger.info(f"Running microservice tests against {BASE_URL}...")
    
    try:
        logger.info("Running test_root_endpoint...")
        test_root_endpoint()
        logger.info("✅ test_root_endpoint passed!")

        logger.info("Running test_run_engage...")
        # Note: If this hits a real LLM, it might take a few seconds to return.
        test_run_engage()
        logger.info("✅ test_run_engage passed!")

        logger.info("🎉 All tests completed successfully!")

    except AssertionError as e:
        logger.error(f"❌ Assertion Failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"❌ An unexpected error occurred: {e}")
        sys.exit(1)
