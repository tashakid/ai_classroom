import json
import logging
from pathlib import Path
import re  # Regular expressions for robust text processing
from typing import Dict, Any, Optional
from .agent_base import AgentBase, AgentMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain 


class CodeGeneratorAgent(AgentBase):
    """
    CodeGeneratorAgent is responsible for generating Manim code based on visual instructions.
    
    This agent uses a language model to interpret visual instructions and produce
    corresponding Python code that utilizes the Manim library for animations.
    """

    def __init__(self, name: str, llm, message_bus, registry):
        """
        Initialize the CodeGeneratorAgent.
        
        Args:
            name (str): The name of the agent.
            llm: The language model instance.
            message_bus: The communication system for inter-agent messaging.
            registry: The registry for storing agent capabilities.
        """
        super().__init__(name, llm, message_bus, registry)

        # Load the example_anim.py to use as a reference for the language model
        example_path = Path("/home/tash/my_files/ai_classroom_assistant/ai_classroom_assistant/example_anim.py")
        try:
            with open(example_path, "r") as f:
                self.example_of_code = f.read()
            logging.info(f"Loaded example code from {example_path}.")
        except FileNotFoundError:
            logging.error(f"Error: {example_path} not found. Ensure the file exists.")
            self.example_of_code = ""

        # Define the prompt template
        self.prompt = PromptTemplate(
            input_variables=["visuals_instructions", "example_of_code"],
            template="""You are a Code Generator Agent specialized in creating Manim animations for educational videos.
You are provided with detailed visual instructions. Based on these instructions and the example code provided, generate well-commented Python code using the Manim library to create the described animations.

Here is an example of Manim code that creates an animation:
{example_of_code}

Visual Instructions:
{visuals_instructions}

**Only provide the Python code with no additional explanations or instructions. Do not include code fences or markdown.**"""
        )

        # Initialize LLMChain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt
        )

        # Register the agent's capabilities in the registry
        self.registry.register_agent_capability(
            self.name,
            "generate_manim_code",
            "Generate Manim animation code based on visual instructions"
        )

    async def generate_code(self, visuals_instructions: Dict[str, Any]) -> Optional[str]:
        """
        Generates Manim code based on visual instructions.
        
        Args:
            visuals_instructions (Dict[str, Any]): Detailed instructions for visual elements.
        
        Returns:
            Optional[str]: Manim code as a string or None if generation fails.
        """
        try:
            prompt_input = {
                "visuals_instructions": json.dumps(visuals_instructions, indent=4),
                "example_of_code": self.example_of_code
            }

            logging.debug("Sending prompt to language model for code generation.")

            # Use 'ainvoke' for asynchronous invocation with LLMChain
            response = await self.chain.ainvoke(prompt_input)
            code_generated = response.strip()

            logging.debug(f"Raw Response Content:\n{code_generated}\n")

            # Remove code fences using regex for robustness
            code_generated = re.sub(r'^```python\s*', '', code_generated, flags=re.MULTILINE)
            code_generated = re.sub(r'^```', '', code_generated, flags=re.MULTILINE)
            code_generated = re.sub(r'```$', '', code_generated, flags=re.MULTILINE)
            code_generated = code_generated.strip()

            # Validate the code starts with the correct import statement
            if not code_generated.startswith("from manim import *"):
                logging.warning("Generated code does not start with 'from manim import *'")

            # Validate that the code compiles to catch incomplete code early
            try:
                compile(code_generated, '<string>', 'exec')
                logging.info("Generated code is syntactically correct.")
            except SyntaxError as se:
                logging.error(f"Generated code has syntax errors: {se}")
                return None

            return code_generated

        except Exception as e:
            logging.error(f"Failed to generate code: {e}")
            return None

    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Process incoming messages from other agents.
        
        This method handles code revision requests and can execute generated code if needed.
        
        Args:
            message (AgentMessage): The incoming message from another agent.
        
        Returns:
            Optional[AgentMessage]: A response message if applicable, or None.
        """
        message_type = message.content.get("type")
        
        if message_type == "code_revision":
            revision_request = message.content.get("revision")
            if not revision_request:
                logging.warning("No revision request found in the message.")
                return None
            
            # Generate revised code based on the revision request
            revised_code = await self.generate_revised_code(revision_request)
            if revised_code:
                return AgentMessage(
                    content={"revised_code": revised_code},
                    sender=self.name,
                    recipient="video_watcher"  # Assuming "video_watcher" is the recipient
                )
        
        elif message_type == "execute_code":
            code_str = message.content.get("code")
            if not code_str:
                logging.warning("No code found in the execute_code message.")
                return None
            
            execution_result = self.run_code(code_str)
            return AgentMessage(
                content={"execution_result": execution_result},
                sender=self.name,
                recipient=message.sender
            )
        
        return None

    async def generate_revised_code(self, revision_request: str) -> Optional[str]:
        """
        Generates revised Manim code based on a revision request.
        
        Args:
            revision_request (str): The revision details or specific changes needed.
        
        Returns:
            Optional[str]: Revised Manim code as a string or None if generation fails.
        """
        try:
            prompt = (
                "Revise the following Manim code based on the revision request provided. "
                "Ensure all changes adhere to best practices and maintain the functionality of the original animation.\n\n"
                "Revision Request:\n"
                f"{revision_request}\n\n"
                "Original Code:\n"
                "{original_code}\n\n"
                "Revised Code:\n"
                "**Only provide the revised Python code with no additional explanations or instructions. Do not include code fences or markdown.**"
            )
            
            prompt_template = PromptTemplate(
                input_variables=["revision_request", "original_code"],
                template=prompt
            )
            # Initialize LLMChain for revision
            revision_chain = LLMChain(
                llm=self.llm,
                prompt=prompt_template
            )
            
            prompt_input = {
                "original_code": self.example_of_code,
                "revision_request": revision_request
            }

            logging.debug("Sending prompt to language model for code revision.")

            # Use 'ainvoke' instead of deprecated methods
            response = await revision_chain.ainvoke(**prompt_input)
            revised_code = response.strip()

            logging.debug(f"Raw Revised Code:\n{revised_code}\n")

            # Remove code fences using regex for robustness
            revised_code = re.sub(r'^```python\s*', '', revised_code, flags=re.MULTILINE)
            revised_code = re.sub(r'^```', '', revised_code, flags=re.MULTILINE)
            revised_code = re.sub(r'```$', '', revised_code, flags=re.MULTILINE)
            revised_code = revised_code.strip()

            # Validate the revised code starts with the correct import statement
            if not revised_code.startswith("from manim import *"):
                logging.warning("Revised code does not start with 'from manim import *'")

            # Validate that the revised code compiles to catch incomplete code early
            try:
                compile(revised_code, '<string>', 'exec')
                logging.info("Revised code is syntactically correct.")
            except SyntaxError as se:
                logging.error(f"Revised code has syntax errors: {se}")
                return None

            return revised_code

        except Exception as e:
            logging.error(f"Failed to generate revised code: {e}")
            return None