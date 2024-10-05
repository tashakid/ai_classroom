import json
import logging
import re  # Regular expressions for robust text processing
from typing import Dict, Any, List, Optional
from pathlib import Path  # For handling file paths
from .agent_base import AgentBase, AgentMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain  # Import LLMChain
from mistralai import Mistral
import os  # Ensure os is imported for environment variables

class ForemanAgent(AgentBase):
    """
    ForemanAgent is responsible for translating a high-level video structure
    into detailed visual instructions that can be used by the CodeGeneratorAgent
    to produce the necessary code for animations.
    """

    def __init__(self, name: str, llm, message_bus, registry):
        """
        Initialize the ForemanAgent.

        Args:
            name (str): The name of the agent.
            llm: The language model instance (should be an instance of MistralLLM).
            message_bus: The communication system for inter-agent messaging.
            registry: The registry for storing agent capabilities.
        """
        super().__init__(name, llm, message_bus, registry)

        # Load the instruction_example.json as a reference for visual instructions
        instruction_example_path = Path("/home/tash/my_files/ai_classroom_assistant/ai_classroom_assistant/instruction_example.json")
        try:
            with open(instruction_example_path, "r") as f:
                self.instruction_example = json.load(f)
            logging.info(f"Loaded instruction example from {instruction_example_path}.")
        except FileNotFoundError:
            logging.error(f"Error: {instruction_example_path} not found. Ensure the file exists.")
            self.instruction_example = {}

        # Define the prompt template
        self.prompt = PromptTemplate(
            input_variables=["video_structure", "instruction_example"],
            template="""You are a Foreman Agent responsible for interpreting video structures and creating detailed visual instructions for Manim animations. 
You can communicate with other agents to accomplish tasks. Here is an example of detailed visual instructions:

{instruction_example}

Translate the following video structure into highly detailed visual instructions suitable for generating Manim animations in Python:

Video Structure:
{video_structure}

Ensure that each instruction includes the timeframe, specific visual elements with detailed properties, animations with precise parameters, and comprehensive configurations for Manim. 
**Respond only with valid JSON. Do not include any code fences, markdown, or additional text.**"""
        )

        # Initialize LLMChain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt
        )

        # Register the agent's capabilities in the registry
        self.registry.register_agent_capability(
            self.name,
            "interpret_video_structure",
            "Translate high-level video structure into specific visual instructions"
        )

    async def interpret_video_structure(self, video_structure: dict) -> dict:
        """
        Interpret the video structure and provide detailed visual instructions.

        Args:
            video_structure (dict): The high-level video structure to be interpreted.

        Returns:
            dict: A dictionary containing detailed visual instructions for Manim animations or clarification requests.
        """
        agent_capabilities = self.get_all_agents_description()
        # Use 'ainvoke' for asynchronous invocation with LLMChain
        response = await self.chain.ainvoke({
            "video_structure": json.dumps(video_structure),
            "instruction_example": json.dumps(self.instruction_example)
        })
        parsed_response = self.parse_response(response)

        if "needs_clarification" in parsed_response:
            clarification = await self.request_clarification("supervisor", parsed_response["needs_clarification"])
            updated_structure = await self.request_updated_structure(video_structure, clarification)
            return await self.interpret_video_structure(updated_structure)

        return parsed_response

    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Process incoming messages from other agents.

        This method handles clarification requests from other agents.

        Args:
            message (AgentMessage): The incoming message from another agent.

        Returns:
            Optional[AgentMessage]: A response message if applicable, or None.
        """
        if message.content.get("type") == "clarification_request":
            clarification = await self.provide_clarification(message.content["question"])
            return AgentMessage(
                content={"type": "clarification", "clarification": clarification},
                sender=self.name,
                recipient=message.sender
            )
        return None

    def parse_response(self, response: str) -> dict:
        """
        Parse the response from the language model.

        This method attempts to interpret the model's response as JSON and
        handles various cases such as clarification requests or invalid responses.

        Args:
            response (str): The raw response from the language model.

        Returns:
            dict: A structured dictionary of the parsed response.
        """
        # Remove code fences using regex for robustness
        response_content = re.sub(r'^```json\s*', '', response, flags=re.MULTILINE)
        response_content = re.sub(r'^```python\s*', '', response_content, flags=re.MULTILINE)
        response_content = re.sub(r'^```', '', response_content, flags=re.MULTILINE)
        response_content = re.sub(r'```$', '', response_content, flags=re.MULTILINE)

        try:
            parsed = json.loads(response_content)
            if "needs_clarification" in parsed:
                return parsed
            elif "visual_instructions" in parsed:
                return parsed
            else:
                # If the response is in JSON format but doesn't contain expected keys,
                # treat it as needing clarification
                return {"needs_clarification": ["Could you please provide more context or specify your request?"]}
        except json.JSONDecodeError:
            # If the response is not in JSON format, assume clarification is needed
            return {"needs_clarification": ["I couldn't understand the video structure. Could you please rephrase or provide more details?"]}

    async def request_clarification(self, recipient: str, questions: List[str]) -> str:
        """
        Request clarification from another agent.

        Args:
            recipient (str): The name of the agent to request clarification from.
            questions (List[str]): A list of specific questions for clarification.

        Returns:
            str: The clarification received from the other agent.
        """
        await self.send_message(recipient, {"type": "clarification_request", "question": questions})
        response = await self.receive_message()
        return response.content.get("clarification", "")

    async def request_updated_structure(self, original_structure: dict, clarification: str) -> dict:
        """
        Request an updated video structure based on clarification.

        Args:
            original_structure (dict): The original video structure.
            clarification (str): The clarification provided by the Supervisor agent.

        Returns:
            dict: The updated video structure.
        """
        message = {
            "type": "update_request",
            "original_structure": original_structure,
            "clarification": clarification
        }
        await self.send_message("supervisor", message)
        response = await self.receive_message()
        return response.content.get("updated_structure", original_structure)

    async def provide_clarification(self, question: str) -> str:
        """
        Provide clarification for a given question.

        Args:
            question (str): The question requiring clarification.

        Returns:
            str: The clarification text.
        """
        clarification_prompt = PromptTemplate(
            input_variables=["question"],
            template="Provide a detailed clarification for the following question about visual instructions: {question}"
        )
        # Initialize LLMChain for clarification
        clarification_chain = LLMChain(
            llm=self.llm,
            prompt=clarification_prompt
        )
        # Use 'ainvoke' instead of deprecated methods
        clarification = await clarification_chain.ainvoke({
            "question": question
        })
        return clarification

    async def save_visual_instructions(self, visuals_instructions: Dict[str, Any], file_path: str):
        """
        Saves the visual instructions to a specified JSON file.
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(visuals_instructions, f, indent=4)
            logging.info(f"Visual instructions saved to {file_path}.")
        except Exception as e:
            # Capture any exceptions that occur during file writing
            error_message = f"Failed to save visual instructions to {file_path}: {e}"
            logging.error(error_message)
            # Store the error message to pass to the refinement (if needed)
            self.last_error = error_message
            # Optionally, you might want to raise the exception or handle it differently based on your use case
            raise