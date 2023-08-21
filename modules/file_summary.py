import os
import json
import time
import math
from .token_counter import num_tokens_from_string
from .llm_model import generate_completion

def get_summary_instruction(config_path):
    """Parse the config file and get SUMMARY instruction."""
    with open(config_path, 'r') as file:
        lines = file.readlines()

    # Find the SUMMARY section
    try:
        start_index = lines.index("[SUMMARY]\n")
    except ValueError:
        return ""

    for line in lines[start_index:]:
        if line.startswith("PrependPrompt = "):
            # Return the instruction after removing the 'PrependPrompt = ' and trimming the quotes
            return line.replace("PrependPrompt = ", "").strip().strip('"')

    return ""

# Modify the summarize_file function
async def summarize_file(file_path, model_name="gpt-3.5-turbo", max_token_length=9000):
    """Read a file and return a summary."""
    with open(file_path, 'r') as file:
        content = file.read()

    total_tokens = num_tokens_from_string(content, 'gpt-3')
    summary_instruction = get_summary_instruction("./filebot.config")

    if total_tokens <= max_token_length:
        prompt = f"{summary_instruction} Here is the document:\n\n{content}"

        summary = await generate_completion(prompt, model_name=model_name)
        return [(file_path, summary)]

    # content exceeds max_token_length
    summaries = []
    for i in range(0, total_tokens, max_token_length):
        print(f"llm summary request {i}")
        chunk = content[i: i + max_token_length]
        prompt = f"{summary_instruction} Here is the document:\n\n{chunk}"

        summary = await generate_completion(prompt, model_name=model_name)
        summaries.append((f"{file_path}.{i//max_token_length}", summary))

    return summaries

# Modify the create_file_summaries function
# Define a list of source code extensions
SOURCE_CODE_EXTENSIONS = [
    # Common Languages
    '.py', '.java', '.c', '.cpp', '.h', '.hpp', '.js', '.ts', '.go', '.cs',
    '.php', '.rb', '.swift', '.html', '.css', '.scss', '.sass',

    # Web
    '.jsx', '.tsx', '.vue',

    # SQL and Databases
    '.sql', '.db', '.mdf', '.sdf',

    # Shell scripts
    '.sh', '.bash', '.zsh', '.fish',

    # Config
    '.yml', '.yaml', '.toml', '.xml', '.json', '.ini',

    # Mobile
    '.kt', '.dart',

    # Dotnet
    '.vb',

    # Functional
    '.ml', '.f#', '.f', '.fs', '.clj', '.cljs', '.cljc', '.hs', '.erl', '.scala',

    # Systems
    '.rs', '.lua',

    # Low Level
    '.asm', '.s',

    # Others
    '.perl', '.pl', '.tcl', '.r', '.pas', '.p', '.d',

    # Markup
    '.rst', '.tex', '.bib',

    # Web Assembly
    '.wasm',

    # Version Control
    '.gitignore'
]

async def create_file_summaries(directory, file_summaries_path, model_name="gpt-3.5-turbo", code_mode=False):
    ...
    ...

    """Walk through a directory and generate a summary for each file."""
    # Load existing summaries
    try:
        with open(file_summaries_path, 'r') as json_file:
            file_summaries = json.load(json_file)
    except FileNotFoundError:
        file_summaries = {}

    # Set a flag to check if file_summaries.json is updated
    is_updated = False

    for root, dirs, files in os.walk(directory):
        # Skip directories named .gitignore
        if ".git" in dirs:
            dirs.remove(".git")

        for file in files:
            # Skip files named .gitignore
            if file == ".gitignore":
                continue

            # Skip source code files if code_mode is True
            if code_mode and file.endswith(tuple(SOURCE_CODE_EXTENSIONS)):
                continue

            file_path = os.path.join(root, file)
            base_file_path, _ = os.path.splitext(file_path)

            # Check if the file is new or updated
            if all(not key.startswith(base_file_path) for key in file_summaries.keys()) or \
            any(file_summaries[key]['mtime'] < os.path.getmtime(file_path) for key in file_summaries.keys() if key.startswith(base_file_path)):
                print(f"New or updated file detected: '{file_path}'")
                summaries = await summarize_file(file_path, model_name=model_name)
                if summaries:
                    for path, summary in summaries:
                        file_summaries[path] = {
                            'summary': summary,
                            'mtime': os.path.getmtime(file_path)
                        }
                    # Set the flag to True when file_summaries.json is updated
                    is_updated = True

    with open(file_summaries_path, 'w') as json_file:
        json.dump(file_summaries, json_file, indent=4)

    # Notify the user if file_summaries.json is updated
    if is_updated:
        print(f"{file_summaries_path} has been updated.")