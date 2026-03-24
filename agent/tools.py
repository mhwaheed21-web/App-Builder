
import pathlib
import subprocess
from typing import Tuple

from langchain_core.tools import tool

PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"


def safe_path_for_project(path: str) -> pathlib.Path:
    p = (PROJECT_ROOT / path).resolve()
    if PROJECT_ROOT.resolve() not in p.parents and PROJECT_ROOT.resolve() != p.parent and PROJECT_ROOT.resolve() != p:
        raise ValueError("Attempt to write outside project root")
    return p


@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file at the specified path within the project root."""
    p = safe_path_for_project(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return f"WROTE:{p}"


@tool
def read_file(path: str) -> str:
    """Reads content from a file at the specified path within the project root."""
    p = safe_path_for_project(path)
    if not p.exists():
        return ""
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


@tool
def get_current_directory() -> str:
    """Returns the current working directory."""
    return str(PROJECT_ROOT)


@tool
def list_files(directory: str) -> str:
    """Lists all files in the specified directory within the project root."""
    p = safe_path_for_project(directory)
    if not p.is_dir():
        return f"ERROR: {p} is not a directory"
    files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
    return "\n".join(files) if files else "No files found."


@tool
def run_cmd(cmd: str, cwd: str, timeout: int) -> str:
    """Runs a shell command and returns exit code, stdout, stderr."""
    cwd_dir = safe_path_for_project(cwd)
    res = subprocess.run(
        cmd,
        shell=True,
        cwd=str(cwd_dir),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return (
        f"returncode={res.returncode}\n"
        f"stdout:\n{res.stdout}\n"
        f"stderr:\n{res.stderr}"
    )




def init_project_root():
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
    return str(PROJECT_ROOT)

# import pathlib
# import subprocess
# from typing import Dict, Optional

# from langchain_core.tools import tool

# # Project root directory for all file operations
# PROJECT_ROOT = pathlib.Path.cwd() / "generated_project"


# def safe_path_for_project(path: str) -> pathlib.Path:
#     """
#     Resolves a path inside the project root. Raises an error if the path is outside.
#     """
#     p = (PROJECT_ROOT / path).resolve()
#     root_resolved = PROJECT_ROOT.resolve()
#     if root_resolved not in p.parents and root_resolved != p.parent and root_resolved != p:
#         raise ValueError("Attempt to write outside project root")
#     return p


# @tool
# def write_file(path: str, content: str) -> str:
#     """
#     Writes content to a file at the specified path within the project root.

#     Args:
#         path (str): Path relative to the project root.
#         content (str): Content to write into the file.

#     Returns:
#         str: Confirmation message including the absolute file path.
#     """
#     p = safe_path_for_project(path)
#     p.parent.mkdir(parents=True, exist_ok=True)
#     with open(p, "w", encoding="utf-8") as f:
#         f.write(content)
#     return f"WROTE:{str(p)}"


# @tool
# def read_file(path: str) -> str:
#     """
#     Reads content from a file at the specified path within the project root.

#     Args:
#         path (str): Path relative to the project root.

#     Returns:
#         str: File content, or empty string if the file does not exist.
#     """
#     p = safe_path_for_project(path)
#     if not p.exists():
#         return ""
#     with open(p, "r", encoding="utf-8") as f:
#         return f.read()


# @tool
# def get_current_directory() -> str:
#     """
#     Returns the current project root directory.

#     Returns:
#         str: Absolute path of the project root.
#     """
#     return str(PROJECT_ROOT)


# @tool
# def list_files(directory: str = ".") -> str:
#     """
#     Lists all files in the specified directory within the project root.

#     Args:
#         directory (str, optional): Directory relative to the project root. Defaults to ".".

#     Returns:
#         str: Newline-separated list of file paths relative to project root.
#     """
#     p = safe_path_for_project(directory)
#     if not p.is_dir():
#         return f"ERROR: {str(p)} is not a directory"
#     files = [str(f.relative_to(PROJECT_ROOT)) for f in p.glob("**/*") if f.is_file()]
#     return "\n".join(files) if files else "No files found."


# @tool
# def run_cmd(cmd: str, cwd: Optional[str] = None, timeout: int = 30) -> Dict[str, str]:
#     """
#     Runs a shell command in the specified directory within the project root.

#     Args:
#         cmd (str): Command to execute.
#         cwd (str, optional): Directory relative to project root. Defaults to project root.
#         timeout (int): Maximum seconds to wait. Defaults to 30.

#     Returns:
#         dict: Dictionary with keys 'returncode', 'stdout', 'stderr'.
#     """
#     cwd_dir = safe_path_for_project(cwd) if cwd else PROJECT_ROOT
#     try:
#         res = subprocess.run(
#             cmd,
#             shell=True,
#             cwd=str(cwd_dir),
#             capture_output=True,
#             text=True,
#             timeout=timeout
#         )
#         return {
#             "returncode": res.returncode,
#             "stdout": res.stdout.strip(),
#             "stderr": res.stderr.strip(),
#         }
#     except subprocess.TimeoutExpired:
#         return {
#             "returncode": -1,
#             "stdout": "",
#             "stderr": "Command timed out"
#         }
#     except Exception as e:
#         return {
#             "returncode": -1,
#             "stdout": "",
#             "stderr": str(e)
#         }


# def init_project_root() -> str:
#     """
#     Initializes the project root directory if it doesn't exist.

#     Returns:
#         str: Absolute path of the project root.
#     """
#     PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
#     return str(PROJECT_ROOT)
