from spam_scoring import calculate_spam_score
import pickle
import time
import requests
import subprocess
import os
import warnings

warnings.filterwarnings("ignore")

loaded_classifier = pickle.load(open("Assignment 4/naive_bayes_model.pkl", "rb"))


def test_spam_scoring_smoke_test():
    try:
        calculate_spam_score("Sample Text", loaded_classifier, 0.5)
    except Exception as e:
        raise AssertionError(f"calculate_spam_score function raised an exception: {e} (Smoke test failed)")

    assert type(calculate_spam_score("Sample Text", loaded_classifier,
                                     0.5)) == tuple, f"Expected 2 outputs, received 1 (Smoke test failed)"
    assert len(calculate_spam_score("Sample Text", loaded_classifier,
                                    0.5)) == 2, f"Expected 2 outputs, received {len(calculate_spam_score('Sample Text', loaded_classifier, 0.5))} (Smoke test failed)"


def test_spam_scoring_format_test():
    text = "Sample Text"
    threshold = 0.7
    prediction, probability = calculate_spam_score(text, loaded_classifier, threshold)
    assert type(prediction) == int

    try:
        float(probability)
    except Exception as e:
        raise AssertionError(f"calculate_spam_score function raised an exception: {e} (Format test failed)")


def test_spam_scoring_prediction_in_0_or_1():
    text = "Sample Text"
    threshold = 0.7
    prediction, _ = calculate_spam_score(text, loaded_classifier, threshold)
    assert prediction in (0, 1)


def test_spam_scoring_propensity_between_0_and_1():
    text = "Sample Text"
    threshold = 0.7
    _, propensity = calculate_spam_score(text, loaded_classifier, threshold)
    assert 0 <= propensity <= 1


def test_spam_scoring_threshold_0_prediction_always_1():
    text_1 = "Be there tonight"
    threshold = 0
    prediction, _ = calculate_spam_score(text_1, loaded_classifier, threshold)
    assert prediction == 1

    text_2 = "Get a chance to go on a vacation to Hawaii"
    threshold = 0
    prediction, _ = calculate_spam_score(text_2, loaded_classifier, threshold)
    assert prediction == 1


def test_spam_scoring_threshold_1_prediction_always_0():
    text_1 = "Be there tonight"
    threshold = 1
    prediction, _ = calculate_spam_score(text_1, loaded_classifier, threshold)
    assert prediction == 0

    text_2 = "Get a chance to go on a vacation to Hawaii"
    threshold = 1
    prediction, _ = calculate_spam_score(text_2, loaded_classifier, threshold)
    assert prediction == 0


def test_spam_scoring_obvious_spam_gives_prediction_1():
    text = '''Congratulations! You've been selected as the winner of our exclusive giveaway. 
              Claim your prize now and enjoy a luxurious vacation at one of our top-rated resorts.
              Hurry, this offer is only available for a limited time.'''
    threshold = 0.7
    prediction, _ = calculate_spam_score(text, loaded_classifier, threshold)
    assert prediction == 1


def test_spam_scoring_obvious_non_spam_gives_prediction_0():
    text = "Don't be late for tomorrow's meeting"
    threshold = 0.4
    prediction, _ = calculate_spam_score(text, loaded_classifier, threshold)
    assert prediction == 0


def test_flask_spam_classifier():
    process = subprocess.Popen(["python", "Assignment 4/spam_classifier_api.py"], stdout=subprocess.PIPE)

    time.sleep(2)

    payload = {"text": "Hello, congratulations! You have won a prize."}
    response = requests.post("http://localhost:5000/", data=payload)

    assert response.status_code == 200

    data = response.json()
    assert 'prediction' in data
    assert 'propensity' in data

    process.terminate()


def wait_for_spam_classifier_ready():
    max_retries = 10
    retry_delay = 5  # seconds

    for _ in range(max_retries):
        try:
            # Send a test request to the container to check if it's ready
            response = requests.post("http://localhost:5000", data={"text": "sample_text"}, timeout=2)
            if response.status_code == 200:
                print("Spam classifier is ready")
                return True
        except Exception as e:
            print(f"Error checking spam classifier status: {e}")

        print("Spam classifier is not ready yet, retrying...")
        time.sleep(retry_delay)

    print("Max retries exceeded, spam classifier is not ready")
    return False


def test_docker_spam_classifier():
    # Build the Docker image
    subprocess.run(["docker", "build", "-t", "spam-classifier", "Assignment 4"])

    # Run the Docker container
    subprocess.run(["docker", "run", "-d", "-p", "5000:5000", "--name", "spam-container", "spam-classifier"])

    # Wait for the container to be ready
    if wait_for_spam_classifier_ready():
        print("Test passed!")
        with open(os.path.join("Assignment 4", "test_results.txt"), "a") as f:
            f.write("Test passed!\n")
    else:
        print("Test failed!")
        with open(os.path.join("Assignment 4", "test_results.txt"), "a") as f:
            f.write("Test failed!\n")

    # Close the Docker container
    subprocess.run(["docker", "stop", "spam-container"])
    subprocess.run(["docker", "rm", "spam-container"])
    subprocess.run(["docker", "rmi", "spam-classifier"])


if __name__ == "__main__":
    test_docker_spam_classifier()
