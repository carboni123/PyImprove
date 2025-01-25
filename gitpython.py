# gitpython.py

import subprocess
import sys
import os

class GitRepo:
    """Class with system commands for git"""

    def __init__(self, repo_path: str, commit=False):
        self.repo_path = repo_path
        self.git_init(commit=commit)

    def git_init(self, commit=False):
        """Initialize a new Git repository or check if one already exists."""
        if self.is_git_repo():
            print(f"Git repository '{self.repo_path}' already initialized.")
            return
        try:
            subprocess.run(["git", "init"], cwd=self.repo_path, check=True)
            print("Git repository initialized.")
            if commit:
                self.git_add_all()
                self.git_commit("Initial commit")
        except subprocess.CalledProcessError as e:
            print(f"Git init failed: {e}")

    def git_add_all(self):
        """Stage all changes in the repository."""
        try:
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
            print("All files staged.")
        except subprocess.CalledProcessError as e:
            print(f"Git add failed: {e}")

    def git_add(self, files: list):
        """Stage all changes in the repository."""
        try:
            subprocess.run(["git", "add"] + files, cwd=self.repo_path, check=True)
            print("All files staged.")
        except subprocess.CalledProcessError as e:
            print(f"Git add failed: {e}")

    def git_commit(self, message="Update"):
        """Commit changes with a message."""
        try:
            subprocess.run(
                ["git", "commit", "-m", message], cwd=self.repo_path, check=True
            )
            print(f"Committed with message: '{message}'")
        except subprocess.CalledProcessError as e:
            print(f"Git commit failed: {e}")

    def git_status(self):
        """Check status of the repository."""
        try:
            result = subprocess.run(
                ["git", "status"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True,
            )
            print("Repository status:")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Git status failed: {e}")

    def git_log(self):
        """Show the commit logs."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True,
            )
            print("Commit log (one line per commit):")
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Git log failed: {e}")

    def git_diff(self):
        """Show differences between the working directory and the index."""
        try:
            result = subprocess.run(
                ["git", "diff"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
                text=True,
            )
            if result.stdout:
                print("Changes not staged for commit:")
                print(result.stdout)
            else:
                print("No changes detected in working directory.")
        except subprocess.CalledProcessError as e:
            print(f"Git diff failed: {e}")

    def git_reset(self):
        """
        Reset the current HEAD to the last commit, discarding all changes in the working directory and staging area.
        """
        try:
            subprocess.run(["git", "reset", "--hard"], cwd=self.repo_path, check=True)
            print("Reset to last commit. All changes discarded.")
        except subprocess.CalledProcessError as e:
            print(f"Git reset failed: {e.stderr if e.stderr else e}")

    def is_git_repo(self) -> bool:
        """Checks if the given directory is a git repository."""
        try:
            # Check if .git directory exists
            git_dir = os.path.join(self.repo_path, ".git")
            if os.path.isdir(git_dir):
                return True
            # Check if git command can successfully execute in the directory
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_path,
                check=True,
                capture_output=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False
        except FileNotFoundError:
            return False


if __name__ == "__main__":
    import os

    if len(sys.argv) < 2:
        print("Usage: python create_example_repo.py <folder_name>")
        sys.exit(1)
    folder_name = sys.argv[1]
    """
    Creates a folder (if it doesn't exist), initializes a Git repo inside it,
    writes a README.md file, stages and commits that file.
    """
    # 1) Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder '{folder_name}'.")
    else:
        print(f"Folder '{folder_name}' already exists; proceeding...")

    # 2) Initialize a Git repository in that folder
    repo = GitRepo(folder_name)
    repo.git_init()
    # 3) Create a README.md file with example text
    readme_path = os.path.join(folder_name, "README.md")
    with open(readme_path, "w") as f:
        f.write("this is an example repository\n")
    print(f"Created README.md in '{folder_name}'.")
    # 4) Add files
    repo.git_add_all()
    # 5) Commit
    repo.git_commit("Initial commit")
    print("Successfully created an example repository with an initial commit!")
