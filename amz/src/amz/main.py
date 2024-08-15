#!/usr/bin/env python
import os
import sys
from amz.crew import create_crew
import asyncio

# Set the OpenAI API key directly in the environment
os.environ["OPENAI_API_KEY"] = sys.argv[2] 

def save_results_to_file(result, filename):
    """
    Save the crew's output to a text file.
    """
    try:
        # Convert the CrewOutput to a string before writing
        with open(filename, 'w') as file:
            file.write(str(result))
        print(f"Results have been saved to {filename}")
    except Exception as e:
        raise Exception(f"An error occurred while saving results to file: {e}")

def run():
    """
    Run the crew.
    """
    crew = create_crew()
    inputs = {
        'topic': 'Python Coding'
    }
    result = crew.kickoff(inputs=inputs)  # No need to await, as kickoff is synchronous
    save_results_to_file(result, 'crew_output.txt')

def train():
    """
    Train the crew for a given number of iterations.
    """
    crew = create_crew()
    inputs = {
        "topic": "Python Coding"
    }
    try:
        crew.train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    crew = create_crew()
    try:
        crew.replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    crew = create_crew()
    inputs = {
        "topic": "Python Coding"
    }
    try:
        result = crew.test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
        save_results_to_file(result, 'crew_test_output.txt')
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'run':
            run()
        elif sys.argv[1] == 'train':
            train()
        elif sys.argv[1] == 'replay':
            replay()
        elif sys.argv[1] == 'test':
            test()
        else:
            print("Invalid command. Use 'run', 'train', 'replay', or 'test'.")
    else:
        print("No command provided. Use 'run', 'train', 'replay', or 'test'.")
