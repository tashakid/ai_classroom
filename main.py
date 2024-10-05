import os
import json
import logging
import asyncio

from agents.supervisor import SupervisorAgent
from agents.foreman import ForemanAgent
from agents.code_generator import CodeGeneratorAgent
from agent_registry import AgentRegistry
from message_bus import MessageBus
from utils.helpers import save_json, load_json
from dotenv import load_dotenv
import re  # Ensure this import is present

from agents.mistralllm import MistralLLM 

def correct_spelling(query: str) -> str:
    """
    Basic spell checker to correct common typos.
    This can be enhanced with more sophisticated libraries like TextBlob or autocorrect.
    
    :param query: The user's input query.
    :return: Corrected query string.
    """
    corrections = {
        "sinuisodal": "sinusoidal",
        # Add more common typos and their corrections here
    }
    words = query.split()
    corrected_words = [corrections.get(word.lower(), word) for word in words]
    return ' '.join(corrected_words)

async def main_async():
    """
    Main function orchestrating the AI-driven educational video generation workflow.
    It includes generating video structure, visual instructions, and generating code.
    """
    print("\n=== AI Classroom Assistant ===\n")

    # Load environment variables at the very start
    load_dotenv()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialize AgentRegistry and MessageBus
    agent_registry = AgentRegistry()
    message_bus = MessageBus()

    # Initialize MistralLLM model using the wrapper
    try:
        llm = MistralLLM.from_env()
        logging.info("MistralLLM initialized successfully.")
    except ValueError as ve:
        logging.error(f"Initialization Error: {ve}")
        return

    # Initialize agents with name, llm, message_bus, and registry
    supervisor = SupervisorAgent(name="supervisor", llm=llm, message_bus=message_bus, registry=agent_registry)
    foreman = ForemanAgent(name="foreman", llm=llm, message_bus=message_bus, registry=agent_registry)  # Pass llm here
    code_generator = CodeGeneratorAgent(name="code_generator", llm=llm, message_bus=message_bus, registry=agent_registry)

    # Register agents with the message bus
    message_bus.register_agent(supervisor)
    message_bus.register_agent(foreman)
    message_bus.register_agent(code_generator)

    logging.info("Agents initialized and registered with MessageBus.")

    while True:
        # Prompt the user for input
        teacher_query = input("Enter the concept to generate video structure (or 'exit' to quit): ").strip()

        if teacher_query.lower() == 'exit':
            logging.info("Exiting the program.")
            break

        if not teacher_query:
            logging.warning("Empty input received. Please enter a valid concept.")
            continue

        # Correcting common typos (basic example)
        corrected_query = correct_spelling(teacher_query)

        logging.info(f"Processing query: '{corrected_query}'")

        # Step 1: Supervisor designs the video structure
        logging.info("Supervisor Agent: Designing video structure.")
        video_structure = await supervisor.design_video_structure(corrected_query)
        save_json(video_structure, "video_structure.json")  # Save video structure to JSON

        # Log the video structure to verify SupervisorAgent's response
        logging.info("Supervisor Agent Response:")
        logging.info(json.dumps(video_structure, indent=4))
        logging.info("Video structure saved to 'video_structure.json'\n")

        # Step 2: Foreman translates video structure to visual instructions
        logging.info("Foreman Agent: Translating video structure to visual instructions.")
        visual_instructions = await foreman.interpret_video_structure(video_structure)
        save_json(visual_instructions, "video_instructions.json")  # Save visual instructions to JSON

        logging.info("Foreman Agent Response:")
        logging.info(json.dumps(visual_instructions, indent=4))
        logging.info("Visual instructions saved to 'video_instructions.json'\n")

        # Step 3: Code Generator generates code based on visual_instructions
        logging.info("Code Generator Agent: Generating Manim code.")
        code_generated = await code_generator.generate_code(visual_instructions)

        if code_generated:
            logging.info("Code Generator Agent: Code generated successfully.")
            # Save the code to a file
            try:
                with open("manim_code.py", "w") as file:
                    file.write(code_generated)
                logging.info(f"Generated code saved to 'manim_code.py'.")
            except Exception as e:
                logging.error(f"Failed to write code to file: {e}")
                continue  # Skip execution if saving failed

        else:
            logging.error("Code Generator Agent: Failed to generate code.")

async def run_main():
    await main_async()

if __name__ == "__main__":
    asyncio.run(run_main())