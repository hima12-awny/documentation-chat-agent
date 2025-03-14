import git
import os
import json
import datetime
import os
from pathlib import Path
import streamlit as st


class RepoCloner:
    repo_infos_path: str = "settings/repo_infos.json"

    def __init__(
        self,
        repo_url: str,
        repos_dir_path: str = "repos",
    ) -> None:

        self.repos_dir_path = repos_dir_path
        self.repo_url = repo_url

        self.repo_name = RepoCloner.extract_repo_name(
            repo_url=repo_url
        )

        # Create repos directory if it doesn't exist
        os.makedirs(self.repos_dir_path, exist_ok=True)

        self.target_dir = os.path.join(self.repos_dir_path, self.repo_name)

        if os.path.exists(self.target_dir):
            self.commit_hash = self.pull()
        else:
            self.commit_hash = self.clone()

        # Update hash records
        self.update_hash_record()

    @staticmethod
    def extract_repo_name(repo_url: str) -> str:
        # Remove trailing .git if present
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]

        # Get the path part of the URL (remove the domain)
        path = repo_url.split('github.com/')[-1]

        return path

    def clone(self) -> str:
        print(f"Cloning {self.repo_name} into {self.target_dir}...")

        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(self.target_dir), exist_ok=True)

        repo = git.Repo.clone_from(self.repo_url, self.target_dir)
        commit_hash = repo.head.commit.hexsha
        print(f"Current commit hash: {commit_hash}")
        print(f"Repository cloned successfully to {self.target_dir}")

        return commit_hash

    def pull(self) -> str:
        print(f"Repository already exists at {self.target_dir}")

        try:
            repo = git.Repo(self.target_dir)
            print(f"Pulling latest changes...")
            repo.remotes.origin.pull()
            commit_hash = repo.head.commit.hexsha
            print(f"Current commit hash: {commit_hash}")
            print(f"Repository updated successfully")
            return commit_hash

        except git.InvalidGitRepositoryError:
            print(f"The directory exists but is not a valid git repository")
            return None  # type: ignore

    def generate_repo_structure(
            self,
            exclude_dirs=None,
            exclude_files=None
    ):
        """
        Generate a text representation of a repository folder structure.

        Args:
            repo_path (str): Path to the repository root folder
            output_file (str, optional): Path to save the output. If None, prints to console.
            exclude_dirs (list, optional): List of directory names to exclude
            exclude_files (list, optional): List of file names to exclude

        Returns:
            str: Text representation of the folder structure
        """
        if exclude_dirs is None:
            exclude_dirs = [
                # Version control
                '.git', '.svn', '.hg', '.bzr',

                # Python
                '__pycache__', 'venv', 'env', '.env', '.venv', 'virtualenv',
                '.pytest_cache', '.coverage', 'htmlcov', '.tox', 'dist', 'build', 'eggs',

                # IDE and editors
                '.idea', '.vscode', '.vs', '.eclipse', '.settings', '.project',
                '.classpath', '.factorypath', '.nbproject', '.metadata',

                # JavaScript/Node.js
                'node_modules', 'bower_components', 'jspm_packages', '.npm', '.yarn',

                # Java/Gradle/Maven
                'target', 'bin', 'out', 'build', '.gradle', '.m2',

                # C/C++
                'cmake-build-debug', 'cmake-build-release', 'Debug', 'Release', 'x64',
                'Win32', 'obj', 'libs', 'lib', 'CMakeFiles'
            ]

        if exclude_files is None:
            exclude_files = [

                '.gitattributes'
                '.gitignore',

                # OS files
                '.DS_Store', 'Thumbs.db',

                # Python
                '*.pyc', '*.pyo', '*.pyd', '__pycache__', '*.so', '*.egg', '*.egg-info',
                '.pytest_cache', '.coverage', 'htmlcov', '.tox',

                # C/C++
                '*.o', '*.obj', '*.exe', '*.out', '*.app', '*.dll', '*.so', '*.dylib',
                '*.a', '*.lib', '*.la', '*.lo', '*.d', '*.gcda', '*.gcno', '*.dSYM',
                '*.sln'

                # JavaScript/TypeScript
                'node_modules', 'npm-debug.log', 'yarn-debug.log', 'yarn-error.log',
                '.npm', '.yarn', '*.min.js', '*.bundle.js', '*.map', '.eslintcache',
                'package-lock.json', 'yarn.lock',

                # Java
                '*.class', '*.jar', '*.war', '*.ear', '*.nar', 'hs_err_pid*',
                'target/', 'build/', '.gradle/', 'out/', '.mvn/'
            ]

        # Convert repo_path to a Path object
        repo_path = Path(self.target_dir)

        # Get the repo name for the top level
        repo_name = repo_path.name

        # Start building the structure with the repo name
        structure = [f"├── {repo_name}"]

        def should_exclude(path):
            # Check if path should be excluded
            name = path.name
            # Check directories
            if path.is_dir() and (name in exclude_dirs or any(name.startswith(d) for d in exclude_dirs)):
                return True
            # Check files
            if path.is_file():
                for pattern in exclude_files:
                    if pattern.startswith('*'):
                        if name.endswith(pattern[1:]):
                            return True
                    elif name == pattern:
                        return True
            return False

        def build_structure(directory, prefix=""):
            paths = sorted(directory.iterdir(),
                           key=lambda p: (p.is_file(), p.name))
            items = []

            # Filter out excluded paths
            paths = [p for p in paths if not should_exclude(p)]

            for i, path in enumerate(paths):
                is_last = i == len(paths) - 1

                # Determine the connector symbol
                connector = "└──" if is_last else "├──"

                # Add current item to the result
                if path.is_file():
                    items.append(f"{prefix}{connector} {path.name}")
                else:
                    items.append(f"{prefix}{connector} {path.name}")

                    # Prepare the prefix for the next level
                    next_prefix = f"{prefix}{'    ' if is_last else '│   '}"

                    # Process the subdirectory
                    items.extend(build_structure(path, next_prefix))

            return items

        # Build the structure starting from the repo root
        structure.extend(build_structure(repo_path))

        # Join all lines
        result = "\n".join(structure)

        print(result)

        return result

    def update_hash_record(self) -> None:
        """Update or add the repository hash in the hash record file"""
        if self.commit_hash is None:
            return

        # Load existing records or create new
        if os.path.exists(RepoCloner.repo_infos_path):
            try:
                with open(RepoCloner.repo_infos_path, 'r') as f:
                    records = json.load(f)
            except json.JSONDecodeError:
                records = {}
        else:
            records = {}

        if self.repo_url.endswith('.git'):
            self.repo_url = self.repo_url[:-4]
        # Update the record for this repository
        if self.repo_name not in records:
            records[self.repo_name] = {
                'repo_url': self.repo_url,
                'repo_path': self.target_dir,
                'commit_hash': self.commit_hash,
                'last_updated': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'repo_structure': self.generate_repo_structure()
            }
        else:
            records[self.repo_name]['commit_hash'] = self.commit_hash
            records[self.repo_name]['last_updated'] = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")
            records[self.repo_name]['repo_structure'] = self.generate_repo_structure()

        # Save the updated records
        with open(RepoCloner.repo_infos_path, 'w') as f:
            json.dump(records, f, indent=2)

        print(f"Updated hash record for {self.repo_name}")

    @staticmethod
    def get_repo_info(
        repo_name
    ) -> dict:

        with open(RepoCloner.repo_infos_path, 'r') as f:
            records = json.loads(f.read())

        return records[repo_name]

    @staticmethod
    def get_all_repos_info():
        with open(RepoCloner.repo_infos_path, 'r') as f:
            repos_infos = json.loads(f.read())
        return repos_infos

    @staticmethod
    def remove_repo(del_repo_name: str):
        import shutil
        import stat
        import subprocess

        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)

        repos_infos = RepoCloner.get_all_repos_info()

        repo_info = repos_infos[del_repo_name]

        try:
            shutil.rmtree(repo_info['repo_path'], onerror=remove_readonly)
            shutil.rmtree(f'vec_db/{del_repo_name}', onerror=remove_readonly)

            st.success("Repo Removed Successfully.")

            print(
                f"Directory '{repo_info['repo_path']}' and all its contents have been removed successfully.")

        except OSError as e:
            st.error(f"Error: {e.strerror}")

        del repos_infos[del_repo_name]

        with open(RepoCloner.repo_infos_path, 'w') as f:
            json.dump(repos_infos, f, indent=2)


# # Example usage
# if __name__ == "__main__":
#     import datetime

#     repo_url = "https://github.com/hima12-awny/read-csv-dataframe-cpp.git"
#     cloner = RepoCloner(repo_url)

#     print(f"Repository: {cloner.repo_name}")
