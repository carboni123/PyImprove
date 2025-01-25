# agents/base_agent.py
from api.api import API
from abc import ABC, abstractmethod
from xml.etree import ElementTree


class BaseAgent(ABC):
    """
    An abstract base class for agents in the system.
    """

    def __init__(self, api: API, role_path: str, structure_path: str):
        self.api = api
        self.structure_prefix = """Output Structure Instructions:
1. The LLM must adhere strictly to the schema provided.
2. The LLM must use the XML format provided.
        """
        self.role_description = self._load_role_description(role_path)
        self.structure = self._load_output_structure(self.structure_prefix, structure_path)

    def _load_role_description(self, role_path: str) -> str:
        """
        Loads the role description for this agent from role.xml
        """
        tree = ElementTree.parse(role_path)
        root = tree.getroot()
        description = root.find("description").text
        return description

    def _load_output_structure(self, prefix: str, structure_path: str) -> str:
        """
        Loads the output structure for this agent from structure.xml
        """
        with open(structure_path, "r", encoding="utf-8") as xml:
            content = xml.read()  # Read the entire file content
        return prefix + content

    def set_prefix(self, prefix: str):
        self.structure_prefix = prefix

    @abstractmethod
    def _load_instructions(self) -> str:
        """
        Loads any additional instructions or context needed for this agent's operation.
        By default, returns a simple placeholder or reads from a dedicated section in the role.xml.
        """
        pass

    @abstractmethod
    def run_agent(self, *args, **kwargs):
        """
        An abstract method that concrete agents must implement.
        This method represents the main task or workflow the agent will perform.
        """
        pass
