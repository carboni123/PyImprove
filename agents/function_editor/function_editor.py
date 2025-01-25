# agents/function_editor/function_editor.py
import asyncio
import logging
from agents.base_agent import BaseAgent
from api.api import API
import xml.etree.ElementTree as ET
from typing import Dict, List, Any


class FunctionEditorAgent(BaseAgent):
    """
    Editing functions in a Python script.
    """

    def __init__(self, api: API):
        """
        Initialize the FunctionEditorAgent.
        """
        super().__init__(
            api,
            role_path="agents/function_editor/role.xml",
            structure_path="agents/function_editor/structure.xml",
        )
        self.set_prefix(
            """Output Structure Instructions:
1. The LLM must adhere strictly to the schema provided.
2. The LLM must use the XML format provided.
3. The LLM must not use markdown or any other formatting. Use text only.
4. Replace '<' and '>' characters with '&lt;' and '&gt;' respectively.
        """
        )

    def _load_instructions(self) -> str:
        return """
        Edit the functions in the original script to fix the issues identified in the analysis report.
        """

    def load_file(self, file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()

    def run_agent(
        self,
        original_script: str,
        analysis_report: str,
    ) -> str:
        """
        The main workflow:
          1) Parse the analysis report and locate the corresponding functions
             in the original Python script.
          2) Apply the recommended refactors, bug fixes, and improvements, ensuring
             alignment with best practices and consistency in coding style.
          3) Produce a finalized version of the Python script that reflects all approved
             changes, preserving unchanged functionality in other areas of the script.
        """
        if not original_script:
            raise ValueError(f"Could not find the script at '{original_script}'.")
        if not analysis_report:
            raise ValueError(
                f"Could not find the analysis report at '{analysis_report}'."
            )
        # Create the root element
        prompt = "<function_editor>"
        # Add subelements
        prompt += f"<instructions>{self._load_instructions()}</instructions>"
        prompt += f"<original_script path='{original_script}'>{self.load_file(original_script)}</original_script>"
        prompt += f"<analysis_report>{analysis_report}</analysis_report>"
        prompt += f"<role_description>{self.role_description}</role_description>"
        prompt += f"<structure>{self.structure}</structure>"
        prompt += "</function_editor>"
        # logging.info(f"Editing function with prompt: {prompt}")

        # Log the prompt to a file
        with open(
            "function_editor_sent_prompts.log", "a", encoding="utf-8"
        ) as log_file:
            log_file.write(f"Prompt Sent:\n{prompt}\n\n")

        response = asyncio.run(self.api.generate_text(prompt))
        return self.parse_actions(response)

    def parse_actions(self, xml_string: str) -> List[Dict[str, Any]]:
        """
        Parses the XML response from the FunctionEditorAgent into a structured format.

        Args:
            xml_string: The XML string to parse.

        Returns:
            A list of dictionaries, where each dictionary represents an action
            and its associated data (type, file path, file contents, metadata).
            Returns an empty list if no actions are found or if the input is invalid.
        """
        print(xml_string)
        try:
            root = ET.fromstring(xml_string)
        except ET.ParseError:
            print("Error: Invalid XML format.")
            return []

        actions = []
        for action_element in root.findall("action"):
            action_type = action_element.find("type")
            file_path = action_element.find("file_path")
            file_contents = action_element.find("file_contents")

            if action_type is None:
                print("Warning: Missing action type.")
                continue

            action_data: Dict[str, Any] = {"type": action_type.text}

            if file_path is not None:
                action_data["file_path"] = file_path.text
            if file_contents is not None:
                action_data["file_contents"] = file_contents.text

            actions.append(action_data)

        return actions


if __name__ == "__main__":
    from api.google_api import GoogleAPI

    api = GoogleAPI()
    agent = FunctionEditorAgent(api)
    with open("example/load_dic.py", "r", encoding="utf-8") as file:
        script = file.read()
    print(agent.run_agent(script, "load dic uses eval and it's not safe"))
