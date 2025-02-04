# main.py
import argparse
import os
import logging
from agents.function_analyzer.function_analyzer import FunctionAnalyzer
from agents.function_editor.function_editor import FunctionEditorAgent
from gitpython import GitRepo
from api import create_api_instance


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def parse_actions(actions, repo):
    for action in actions:
        if action["type"] == "create_file" or action["type"] == "edit_file":
            with open(action["file_path"], "w", encoding="utf-8") as f:
                f.write(action["file_contents"])
            repo.git_add_all()
            repo.git_commit()
            logging.info(f"Created or edited file {action['file_path']}.")

        elif action["type"] == "delete_file":
            if os.path.exists(action["file_path"]):
                os.remove(action["file_path"])
                logging.info(f"Deleted file {action['file_path']}.")
                repo.git_add_all()
                repo.git_commit()
            else:
                logging.warning(f"File {action['file_path']} not found for deletion.")


def main():
    """
    Main function to run the AI book generator.
    """
    parser = argparse.ArgumentParser(description="AI Book Generator")
    parser.add_argument(
        "input_script",
        type=str,
        help="Path to the input script",
    )
    parser.add_argument(
        "--api",
        type=str,
        default="google",
        choices=["deepseek", "openai", "google", "alibaba-qwen", "mock"],
        help="API to use (openai, google)",
    )
    parser.add_argument("--api_key", type=str, help="API key for the selected API")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Function Analyzer...")

    script_path = args.input_script
    directory = os.path.dirname(script_path)
    directory = os.path.abspath(os.path.dirname(script_path))
    if not os.path.exists(script_path):
        raise ValueError

    try:
        api = create_api_instance(args.api, args.api_key)
    except ValueError as e:
        logging.error(f"Failed to create API instance: {e}")
        return

    # Initialize agents and tools
    analyzer = FunctionAnalyzer(api)
    editor = FunctionEditorAgent(api)
    repo = GitRepo(directory, commit=True)

    # Generate the function analysis
    analysis = analyzer.run_agent(script_path)
    # Edit the function
    actions = editor.run_agent(script_path, analysis)
    # Parse actions and apply them to the script
    if actions:
        parse_actions(actions, repo)

    logging.info("\nFunction analysis process finished.")


if __name__ == "__main__":
    main()
