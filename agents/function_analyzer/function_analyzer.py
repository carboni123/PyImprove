# agents/function_analyzer/function_analyzer.py
import asyncio
import logging
from agents.base_agent import BaseAgent
from api.api import API


class FunctionAnalyzer(BaseAgent):
    """
    The Script Function Analyzer is responsible for examining each function
    in a Python script, identifying potential issues, and proposing targeted
    improvements.
    """

    def __init__(self, api: API):
        """
        Initialize the ScriptFunctionAnalyzer.
        """
        super().__init__(
            api,
            role_path="agents/function_analyzer/role.xml",
            structure_path="agents/function_analyzer/structure.xml",
        )

    def _load_instructions(self) -> str:
        return """
        Analyze the function in the original script to identify potential issues and propose targeted improvements.
        """

    def load_file(self, file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()
        
    def run_agent(
        self,
        original_script: str,
    ) -> str:
        """
        The main workflow:
          1) Parse the analysis report and locate the corresponding functions
             in the original Python script.
          2) Identify performance bottlenecks, logical errors, code smells, and
             areas where best practices are not followed.
          3) Provide specific and actionable improvements that enhance the script’s
             overall quality, maintainability, and efficiency.
        """
        if not original_script:
            raise ValueError(f"Could not find the script at '{original_script}'.")

        # Create the root element
        prompt = "<function_analyzer>"
        # Add subelements
        prompt += f"<instructions>{self._load_instructions()}</instructions>"
        prompt += f"<original_script path='{original_script}'>{self.load_file(original_script)}</original_script>"
        prompt += f"<role_description>{self.role_description}</role_description>"
        prompt += f"<structure>{self.structure}</structure>"
        prompt += "</function_analyzer>"
        # logging.info(f"Editing function with prompt: {prompt}")

        # Log the prompt to a file
        with open(
            "function_analyzer_sent_prompts.log", "a", encoding="utf-8"
        ) as log_file:
            log_file.write(f"Prompt Sent:\n{prompt}\n\n")

        response = asyncio.run(self.api.generate_text(prompt))
        return response


if __name__ == "__main__":
    from api.google_api import GoogleAPI

    api = GoogleAPI()
    agent = FunctionAnalyzer(api)
    with open("example/load_dic.py", "r", encoding="utf-8") as file:
        script = file.read()
    print(agent.run_agent(script))
