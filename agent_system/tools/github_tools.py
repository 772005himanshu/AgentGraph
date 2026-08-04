import os
from github import Github
from langchain_core.tools import tool

@tool
def search_codebase(repo_name: str, query: str) -> str:
    """
    Search a GitHub repository for a specific keyword or query.
    Args:
        repo_name: The full name of the repository (e.g., 'facebook/react')
        query: The search query (e.g., 'function process_data')
    Returns:
        A list of file paths and snippets matching the query.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        # Mock behavior for testing if no token is available
        return f"Mock search result: Found query '{query}' in file 'src/patched_code.py'."
        
    g = Github(github_token)
    try:
        results = g.search_code(f"{query} repo:{repo_name}")
        output = []
        for item in results[:5]: # limit to top 5
            output.append(f"File: {item.path}\nSnippet: {item.text_matches}")
        return "\n\n".join(output) if output else "No results found."
    except Exception as e:
        return f"Error searching codebase: {str(e)}"

@tool
def read_file(repo_name: str, file_path: str) -> str:
    """
    Read the contents of a specific file from a GitHub repository.
    Args:
        repo_name: The full name of the repository
        file_path: The path to the file in the repository (e.g., 'src/main.py')
    Returns:
        The text content of the file.
    """
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        # Mock behavior
        if "patch" in file_path or "process_data" in file_path:
            return "def process_data(arr):\n    for i in range(len(arr) - 1):\n        print(arr[i])\n"
        return f"Mock file content for {file_path}"
        
    g = Github(github_token)
    try:
        repo = g.get_repo(repo_name)
        contents = repo.get_contents(file_path)
        return contents.decoded_content.decode("utf-8")
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"
