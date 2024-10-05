from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class AgentMessage:
    """
    Represents a message exchanged between agents.

    Attributes:
        content (Dict[str, Any]): The content of the message.
        sender (str): The name of the agent sending the message.
        recipient (str): The name of the agent receiving the message.
    """
    def __init__(self, content: Dict[str, Any], sender: str, recipient: str):
        self.content = content
        self.sender = sender
        self.recipient = recipient

class AgentBase(ABC):
    """
    Abstract base class for all agents in the AI Classroom Assistant.

    This class defines the common interface and functionality for all agents.
    It includes methods for communication, capability management, and workflow control.

    Attributes:
        name (str): The name of the agent.
        llm: The language model used by the agent.
        message_bus: The communication system for inter-agent messaging.
        registry: The registry for storing agent capabilities.
        workflow (Dict[str, List[str]]): A dictionary defining the workflow steps for each agent.
    """

    def __init__(self, name: str, llm, message_bus, registry):
        self.name = name
        self.llm = llm
        self.message_bus = message_bus
        self.registry = registry
        self.workflow = {
            "supervisor": ["design_video_structure"],
            "foreman": ["interpret_video_structure"],
            "code_generator": ["generate_manim_code"],
            "video_watcher": ["evaluate_video"],
            "confirmer": ["consolidate_videos"]
        }

    @abstractmethod
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """
        Process an incoming message from another agent.

        This method should be implemented by each specific agent to handle
        incoming messages according to their role.

        Args:
            message (AgentMessage): The incoming message to process.

        Returns:
            Optional[AgentMessage]: A response message if applicable, or None.
        """
        pass

    async def send_message(self, recipient: str, content: Dict[str, Any]):
        """
        Send a message to another agent.

        Args:
            recipient (str): The name of the agent to receive the message.
            content (Dict[str, Any]): The content of the message.

        Example:
            await agent.send_message("foreman", {"type": "clarification_request", "question": "How to animate a sine wave?"})
        """
        message = AgentMessage(content=content, sender=self.name, recipient=recipient)
        await self.message_bus.send_message(message)

    async def receive_message(self) -> AgentMessage:
        """
        Receive a message from another agent.

        Returns:
            AgentMessage: The received message.

        Example:
            incoming_message = await agent.receive_message()
        """
        return await self.message_bus.receive_message(self.name)

    def get_agent_capabilities(self, agent_name: str) -> List[str]:
        """
        Get the capabilities of a specific agent.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            List[str]: A list of capabilities for the specified agent.
        """
        return self.registry.get_capabilities(agent_name)

    def get_agents_with_capability(self, capability: str) -> List[str]:
        """
        Get a list of agents that have a specific capability.

        Args:
            capability (str): The capability to search for.

        Returns:
            List[str]: A list of agent names that have the specified capability.
        """
        return self.registry.get_agents_with_capability(capability)

    def get_all_agents_description(self) -> str:
        """
        Get a description of all agents and their capabilities.

        Returns:
            str: A formatted string describing all agents and their capabilities.
        """
        agents_description = self.registry.describe_all_agents()
        capabilities = self.registry.describe_all_capabilities()
        
        description = ""
        for agent_name, agent_type in agents_description.items():
            description += f"{agent_name} ({agent_type}):\n"
            if agent_name in capabilities:
                for capability, desc in capabilities[agent_name].items():
                    description += f"  - {capability}: {desc}\n"
            description += "\n"
        
        return description.strip()

    async def request_clarification(self, recipient: str, question: str) -> str:
        """
        Request clarification from another agent.

        Args:
            recipient (str): The name of the agent to request clarification from.
            question (str): The question or topic requiring clarification.

        Returns:
            str: The clarification received from the other agent.
        """
        await self.send_message(recipient, {"type": "clarification_request", "question": question})
        response = await self.receive_message()
        return response.content.get("clarification", "")

    def next_agent_in_workflow(self) -> Optional[str]:
        """
        Determine the next agent in the workflow.

        Returns:
            Optional[str]: The name of the next agent in the workflow, or None if this is the last agent.
        """
        current_index = list(self.workflow.keys()).index(self.name)
        if current_index < len(self.workflow) - 1:
            return list(self.workflow.keys())[current_index + 1]
        return None

    def should_consult_agent(self, issue: str) -> Optional[str]:
        """
        Determine which agent should be consulted based on a given issue.

        Args:
            issue (str): The issue or topic requiring consultation.

        Returns:
            Optional[str]: The name of the agent to consult, or None if no suitable agent is found.
        """
        for agent, capabilities in self.workflow.items():
            if any(capability in issue.lower() for capability in capabilities):
                return agent
        return None