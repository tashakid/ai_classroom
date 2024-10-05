from typing import Dict, List, Any

class AgentRegistry:
    """
    A registry for managing agents and their capabilities.

    This class keeps track of all agents in the system and their respective capabilities.
    It provides methods for registering agents, adding capabilities, and querying
    agent information.

    Attributes:
        agents (Dict[str, Any]): A dictionary mapping agent names to agent instances.
        capabilities (Dict[str, Dict[str, str]]): A nested dictionary storing agent capabilities.

    Example:
        registry = AgentRegistry()
        registry.register_agent("supervisor", supervisor_agent)
        registry.register_agent_capability("supervisor", "design_video", "Create video structure")
    """

    def __init__(self):
        """
        Initialize the AgentRegistry with empty dictionaries for agents and capabilities.
        """
        self.agents = {}
        self.capabilities = {}

    def register_agent(self, name: str, agent: Any):
        """
        Register an agent in the registry.

        Args:
            name (str): The name of the agent.
            agent (Any): The agent instance.

        Example:
            registry.register_agent("foreman", foreman_agent)
        """
        self.agents[name] = agent

    def register_agent_capability(self, agent_name: str, capability: str, description: str):
        """
        Register a capability for a specific agent.

        Args:
            agent_name (str): The name of the agent.
            capability (str): The capability being registered.
            description (str): A description of the capability.

        Example:
            registry.register_agent_capability("code_generator", "generate_manim", "Generate Manim animation code")
        """
        if agent_name not in self.capabilities:
            self.capabilities[agent_name] = {}
        self.capabilities[agent_name][capability] = description

    def describe_all_capabilities(self) -> Dict[str, Dict[str, str]]:
        """
        Get a description of all registered agent capabilities.

        Returns:
            Dict[str, Dict[str, str]]: A nested dictionary of all agent capabilities.

        Example:
            all_capabilities = registry.describe_all_capabilities()
            print(all_capabilities)
        """
        return self.capabilities

    def describe_all_agents(self) -> Dict[str, str]:
        """
        Get a description of all registered agents.

        Returns:
            Dict[str, str]: A dictionary mapping agent names to their class names.

        Example:
            all_agents = registry.describe_all_agents()
            print(all_agents)
        """
        return {name: agent.__class__.__name__ for name, agent in self.agents.items()}

    def get_capabilities(self, agent_name: str) -> List[str]:
        """
        Get the capabilities of a specific agent.

        Args:
            agent_name (str): The name of the agent.

        Returns:
            List[str]: A list of capabilities for the specified agent.

        Example:
            supervisor_capabilities = registry.get_capabilities("supervisor")
        """
        return list(self.capabilities.get(agent_name, {}).keys())

    def get_agents_with_capability(self, capability: str) -> List[str]:
        """
        Get a list of agents that have a specific capability.

        Args:
            capability (str): The capability to search for.

        Returns:
            List[str]: A list of agent names that have the specified capability.

        Example:
            video_capable_agents = registry.get_agents_with_capability("generate_video")
        """
        return [agent for agent, caps in self.capabilities.items() if capability in caps]