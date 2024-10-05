from typing import List, Optional
from .agent_base import AgentBase, AgentMessage
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain  # Import LLMChain
from pathlib import Path
import json
import logging

class SupervisorAgent(AgentBase):
    """
    SupervisorAgent is responsible for designing educational video structures.
    
    This agent uses a language model to interpret user queries and create detailed
    video structures. It can request clarifications when needed and processes
    messages from other agents.
    """

    def __init__(self, name: str, llm, message_bus, registry):
        """
        Initialize the SupervisorAgent.
        
        Args:
            name (str): The name of the agent.
            llm: The language model instance (should be an instance of MistralLLM).
            message_bus: The communication system for inter-agent messaging.
            registry: The registry for storing agent capabilities.
        """
        super().__init__(name, llm, message_bus, registry)
        
        # Load the structure_example.json to use as a reference template
        example_path = Path("/home/tash/my_files/ai_classroom_assistant/ai_classroom_assistant/structure_example.json")
        try:
            with open(example_path, "r") as f:
                self.structure_example = json.load(f)
            logging.info(f"Loaded structure example from {example_path}.")
        except FileNotFoundError:
            logging.error(f"Error: {example_path} not found. Ensure the file exists.")
            self.structure_example = {}

        # Define the prompt template
        prompt = PromptTemplate(
            input_variables=["query", "agent_capabilities", "structure_example"],
            template="""You are a Supervisor Agent responsible for designing educational video structures. 
You can communicate with other agents to accomplish tasks. Here are the capabilities of all agents:

{agent_capabilities}

Here is an example of the expected video structure:
{structure_example}

Design a detailed video structure for the following query: {query}

If the query is unclear, unfamiliar, or nonsensical, or if you need any clarification to create a meaningful video structure, respond with a JSON object containing a 'needs_clarification' key with a list of specific questions as its value.
Only provide a video structure if you have enough clear information to create a meaningful educational video.
If you have enough information, provide a detailed video structure in JSON format with 'video_segments' as the main key."""
        )
        
        # Initialize LLMChain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=prompt
        )

        # Register the agent's capabilities in the registry
        self.registry.register_agent_capability(
            self.name, 
            "design_video_structure", 
            "Create a detailed plan for educational video content"
        )

    async def design_video_structure(self, query: str) -> dict:
        """
        Design a video structure based on the given query.
        
        This method uses the language model chain to generate a video structure
        or request clarifications if needed.
        
        Args:
            query (str): The user's query or topic for the educational video.
        
        Returns:
            dict: A dictionary containing either the video structure or clarification requests.
        """
        agent_capabilities = self.get_all_agents_description()
        
        # Use 'ainvoke' for asynchronous invocation with LLMChain
        response = await self.chain.ainvoke({
            "query": query, 
            "agent_capabilities": agent_capabilities, 
            "structure_example": json.dumps(self.structure_example)
        })
        parsed_response = await self.parse_response(response)
        return parsed_response

    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Process incoming messages from other agents.
        
        This method handles clarification requests from other agents and update requests from the Foreman.
        
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
        elif message.content.get("type") == "update_request":
            updated_structure = await self.update_video_structure(
                message.content["original_structure"], 
                message.content["clarification"]
            )
            return AgentMessage(
                content={"type": "updated_structure", "updated_structure": updated_structure},
                sender=self.name,
                recipient=message.sender
            )
        return None

    async def provide_clarification(self, question: str) -> str:
        """
        Provide clarification for a given question.
        
        This method uses a separate language model chain to generate clarifications.
        
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
        # Use 'ainvoke' instead of 'arun'
        clarification = await clarification_chain.ainvoke({
            "question": question
        })
        return clarification

    async def parse_response(self, response: str) -> dict:
        """
        Parse the response from the language model.
        
        This method attempts to interpret the model's response as JSON and
        handles various cases such as clarification requests or invalid responses.
        
        Args:
            response (str): The raw response from the language model.
        
        Returns:
            dict: A structured dictionary of the parsed response.
        """
        try:
            parsed = await json.loads(response)
            if "needs_clarification" in parsed:
                return parsed
            elif "video_segments" in parsed:
                return parsed
            else:
                # If the response is in JSON format but doesn't contain expected keys,
                # treat it as needing clarification
                return {"needs_clarification": ["Could you please provide more context or specify your request?"]}
        except json.JSONDecodeError:
            # If the response is not in JSON format, assume clarification is needed
            return {"needs_clarification": ["I couldn't understand the query. Could you please rephrase or provide more details?"]}

    async def update_video_structure(self, original_structure: dict, clarification: str) -> dict:
        """
        Update the video structure based on the clarification from the Foreman.
        
        This method interacts with the user if further clarification is needed.
        
        Args:
            original_structure (dict): The original video structure.
            clarification (str): The clarification provided by the Foreman agent.
        
        Returns:
            dict: The updated video structure.
        """
        update_prompt = PromptTemplate(
            input_variables=["original_structure", "clarification"],
            template="""Update the following video structure based on this clarification: {clarification}

Original structure:
{original_structure}

If you need more information to update the structure, respond with a JSON object containing a 'needs_user_clarification' key with a list of specific questions as its value. Otherwise, provide the updated structure in the same JSON format."""
        )
        # Initialize LLMChain for updating structure
        update_chain = LLMChain(
            llm=self.llm,
            prompt=update_prompt
        )
        # Use 'ainvoke' instead of 'arun'
        updated_structure_str = await update_chain.ainvoke({
            "original_structure": json.dumps(original_structure),
            "clarification": clarification
        })
        
        try:
            updated_structure = json.loads(updated_structure_str)
            if "needs_user_clarification" in updated_structure:
                user_clarification = await self.get_user_clarification(updated_structure["needs_user_clarification"])
                return await self.update_video_structure(original_structure, f"{clarification}\n\nAdditional clarification: {user_clarification}")
            
            # Save the updated structure to the JSON file
            with open("video_structure.json", "w") as f:
                json.dump(updated_structure, f, indent=2)
            
            return updated_structure
        except json.JSONDecodeError:
            print("Error: Invalid JSON response from the language model.")
            return original_structure

    async def get_user_clarification(self, questions: List[str]) -> str:
        """
        Get clarification from the user via the terminal.
        
        Args:
            questions (List[str]): List of questions to ask the user.
        
        Returns:
            str: The user's clarification.
        """
        print("\nSupervisor needs further clarification:")
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
        
        clarifications = []
        for i, question in enumerate(questions, 1):
            clarification = input(f"\nPlease provide clarification for question {i}: ")
            clarifications.append(clarification)
        
        return "\n".join(f"Q{i}: {q}\nA{i}: {a}" for i, (q, a) in enumerate(zip(questions, clarifications)))