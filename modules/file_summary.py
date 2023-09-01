import os
import json
import asyncio
import time
import math
import logging
import hashlib
from .token_counter import num_tokens_from_string
from .llm_model import generate_completion
from .is_binary_file import is_binary_file
from .token_checker import get_model_and_tokens
from .ignore import filter_ignored_files

def compute_file_sha256(file_path):
    """Compute the SHA256 hash of the file content."""
    sha256_hash = hashlib.sha256()

    with open(file_path, 'rb') as file:
        while chunk := file.read(4096):
            sha256_hash.update(chunk)

    return sha256_hash.hexdigest()

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

    prompt = f"{summary_instruction} Here is the document:\n\n{content}"

    model_name, max_tokens = get_model_and_tokens(prompt)

    if model_name is None or max_tokens is None:
        raise ValueError(f"No suitable model found for the given token length {total_tokens}.")

    logging.info(f"Sending request to OpenAI {model_name}")
    summary = await generate_completion(prompt, model_name=model_name, max_tokens=max_tokens)
    logging.info(f"Completed request to OpenAI {model_name}")
    return [(file_path, summary)]


    ## content exceeds max_token_length
    #summaries = []
    #for i in range(0, total_tokens, max_token_length):
    #    print(f"llm summary request {i}")
    #    chunk = content[i: i + max_token_length]
    #    prompt = f"{summary_instruction} Here is the document:\n\n{chunk}"

    #    summary = await generate_completion(prompt, model_name=model_name)
    #    summaries.append((f"{file_path}.{i//max_token_length}", summary))

    #return summaries

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
import os
import json

async def create_file_summaries(directory, file_summaries_path, model_name="gpt-3.5-turbo", code_mode=False):
    """Walk through a directory and generate a summary for each file."""

    try:
        with open(file_summaries_path, 'r') as json_file:
            file_summaries = json.load(json_file)
    except FileNotFoundError:
        file_summaries = {}
    except json.JSONDecodeError:
        logging.error("Error decoding JSON, initializing new summaries.")
        file_summaries = {}

    is_updated = False

    # Determine the path to the ignore file in the directory.
    ignore_file_path = os.path.join(directory, '.filebotignore')

    for root, dirs, files in os.walk(directory):
        if ".git" in dirs:
            dirs.remove(".git")

        # Filter out ignored files if ignore file exists
        filtered_files = filter_ignored_files(files, ignore_file_path) if os.path.exists(ignore_file_path) else files

        print(f"Files before filtering: {files}")
        for file in filtered_files:
            print(f"Files after filtering: {filtered_files}")

            if file == '.filebotignore':
                logging.info("Skipping .filebotignore as it should not be processed.")
                continue

            if code_mode and file.endswith(tuple(SOURCE_CODE_EXTENSIONS)):
                continue

            file_path = os.path.join(root, file)
            base_file_path, _ = os.path.splitext(file_path)
            file_sha256 = compute_file_sha256(file_path)  # Compute SHA256 hash of the file

            if all(not key.startswith(base_file_path) for key in file_summaries.keys()) or \
               any(file_summaries[key]['sha256'] != file_sha256 for key in file_summaries.keys() if key.startswith(base_file_path)):

                if is_binary_file(file_path):
                   logging.info(f"Binary file detected, skipping: '{file_path}'")
                else:
                    print(f"New or updated file detected: '{file_path}'")
                    summaries = await summarize_file(file_path, model_name=model_name)

                if summaries:
                    for path, summary in summaries:
                        file_summaries[path] = {
                            'summary': summary,
                            'sha256': compute_file_sha256(file_path)  # Store SHA256 hash instead of mtime
                        }
                    try:
                        with open(file_summaries_path, 'w') as json_file:
                            json.dump(file_summaries, json_file, indent=4)
                    except Exception as e:
                        logging.exception(f"An error occurred while writing to file: {e}")