from typing import Any, Dict, List, Optional
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from mistralai import Mistral
from pydantic import Field
import os
import logging
from dataclasses import dataclass
import re  # Added regex import for robustness

@dataclass
class UserMessage:
    content: str
    role: str = "user"

@dataclass
class SystemMessage:
    content: str
    role: str = "system"

class MistralLLM(LLM):
    """
    Wrapper class to integrate mistralai.Mistral with LangChain.
    
    This class allows the Mistral model to be used within the LangChain framework,
    providing a standardized interface for language model operations.

    Attributes:
        client (Mistral): The Mistral model instance.
        model_name (str): The name of the Mistral model being used.

    Example:
        mistral_llm = MistralLLM.from_env()
        response = await mistral_llm("What is the capital of France?")
    """

    # Define class fields using Pydantic for type checking and validation
    client: Mistral = Field(...)  # The Mistral model instance
    model_name: str = Field(...)  # The name of the Mistral model being used

    @property
    def _llm_type(self) -> str:
        """
        Returns the type of the LLM (Language Model).
        This is used by LangChain for identification purposes.

        Returns:
            str: The identifier string for this LLM type.
        """
        return "mistral"

    async def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generates a response for the given prompt using the Mistral model.

        This method is called by LangChain when using the LLM. It handles the actual
        interaction with the Mistral API.

        Args:
            prompt (str): The input string prompt.
            stop (Optional[List[str]]): Optional list of stop words to end the generation.
            run_manager (Optional[CallbackManagerForLLMRun]): Optional callback manager for the LLM run.
            **kwargs: Any additional arguments to be passed to the Mistral chat model.

        Returns:
            str: The generated response string.

        Example:
            response = await mistral_llm._call("Explain the theory of relativity")
        """
        try:
            # Ensure the client call is awaited
            response_content = await self.client(prompt)
        except Exception as e:
            logging.error(f"Error during model interaction: {e}")
            return ""

        # Remove code fences using regex for robustness
        response_content = re.sub(r'^```json\s*', '', response_content, flags=re.MULTILINE)
        response_content = re.sub(r'^```python\s*', '', response_content, flags=re.MULTILINE)
        response_content = re.sub(r'^```', '', response_content, flags=re.MULTILINE)
        response_content = re.sub(r'```$', '', response_content, flags=re.MULTILINE)

        return response_content

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name
        }

    @classmethod
    def from_env(cls):
        """
        Creates a MistralLLM instance using environment variables.
        
        This method sets up the Mistral model with the appropriate API key and endpoint.
        It uses environment variables to securely manage API credentials.

        Returns:
            MistralLLM: An instance of MistralLLM.

        Example:
            mistral_llm = MistralLLM.from_env()
        """
        token = os.getenv("GITHUB_TOKEN")
        endpoint = "https://models.inference.ai.azure.com"
        model_name = "Mistral-large-2407"
        if not token:
            raise ValueError("GITHUB_TOKEN environment variable not set")
        client = Mistral(api_key=token, server_url=endpoint)
        return cls(client=client, model_name=model_name)