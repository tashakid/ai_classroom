from asyncio import Queue
from typing import Dict
from agents.agent_base import AgentBase, AgentMessage

class MessageBus:
    """
    A message bus for asynchronous communication between agents.

    This class manages message queues for each agent, allowing them to send and receive
    messages asynchronously. It's a crucial component for inter-agent communication
    in the AI Classroom Assistant system.

    Attributes:
        queues (Dict[str, Queue]): A dictionary mapping agent names to their message queues.

    Example:
        message_bus = MessageBus()
        message_bus.register_agent(supervisor_agent)
        await message_bus.send_message(AgentMessage(content="Hello", sender="supervisor", recipient="foreman"))
    """

    def __init__(self):
        """
        Initialize the MessageBus with an empty dictionary of queues.
        """
        self.queues: Dict[str, Queue] = {}

    def register_agent(self, agent: AgentBase):
        """
        Register an agent with the message bus.

        This method creates a new message queue for the agent.

        Args:
            agent (AgentBase): The agent to be registered.

        Example:
            message_bus.register_agent(foreman_agent)
        """
        self.queues[agent.name] = Queue()

    async def send_message(self, message: AgentMessage):
        """
        Send a message to an agent.

        This method adds the message to the recipient agent's queue.

        Args:
            message (AgentMessage): The message to be sent.

        Example:
            await message_bus.send_message(AgentMessage(content="Task complete", sender="code_generator", recipient="supervisor"))
        """
        await self.queues[message.recipient].put(message)

    async def receive_message(self, agent_name: str) -> AgentMessage:
        """
        Receive a message for a specific agent.

        This method retrieves and returns the next message from the agent's queue.

        Args:
            agent_name (str): The name of the agent receiving the message.

        Returns:
            AgentMessage: The received message.

        Example:
            message = await message_bus.receive_message("foreman")
        """
        return await self.queues[agent_name].get()