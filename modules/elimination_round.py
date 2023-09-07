
import os
import json
import asyncio
import re
import configparser
import argparse
import functools
import logging
import unicodedata
from aiohttp import web

#response = """"
#Based on your request, here are the most promising files:
#
#1. `[/app/filebot-store-000/turbosrc-service/.docubot/server.js_doc.md]`
#2. `[/app/filebot-store-000/turbosrc-service/README.md]`
#3. `[/app/filebot-store-000/turbosrc-service/tsrc-dev]`
#4. `[/app/filebot-store-000/turbosrc-service/tsrc-test]`
#
#The `server.js_doc.md` file seems the most relevant as it outlines the functionality related to GraphQL schema and endpoint operations of `server.js`. The `README.md` may contain overall information about modifying the service, and the `tsrc-dev` and `tsrc-test` could be pertinent as they handle service operations and testing.Based on the provided files and summaries it seems like these are the most relevant files:
#
#1. `[/app/filebot-store-000/turbosrc-service/.docubot/src/lib/state.js_doc.md]`
#2. `[/app/filebot-store-000/turbosrc-service/.docubot/src/lib/actions.js_doc.md]`
#3. `[/app/filebot-store-000/turbosrc-service/.docubot/src/utils/engineRequests.js_doc.md]`
#4. `[/app/filebot-store-000/turbosrc-service/.docubot/src/utils/requests.js_doc.md]`
#5. `[/app/filebot-store-000/turbosrc-service/.docubot/src/utils/ghServiceRequests.js_doc.md]`
#"""

def elimination_round(response, code_mode=False):
    logging.info('start elimination')
    file_paths = extract_file_paths(response, code_mode)
    logging.info(file_paths)
    return file_paths

def normalize_key(key):
    key = key.strip()
    key = ' '.join(key.split())
    key = re.sub(r'[^\x20-\x7E]', '', key)
    key = unicodedata.normalize('NFKD', key).encode('ASCII', 'ignore').decode('ASCII')
    return key

def use_non_doc_file_path(path):
    cleaned_path = path.replace('_doc.md', '')
    cleaned_path = cleaned_path.replace('/.docubot', '')
    return cleaned_path

def normalize_file_summaries(file_summaries):
    # Normalize the keys in file_summaries
    normalized_file_summaries = {modify_path_if_docubot(k): v for k, v in file_summaries.items()}
    normalized_file_summaries = {normalize_key(k): v for k, v in normalized_file_summaries.items()}
    normalized_file_summaries = {use_non_doc_file_path(k): v for k, v in normalized_file_summaries.items()}

    return normalized_file_summaries

def file_summaries_abbreviated(user_store, file_paths):
    try:
        logging.info('start abbreviating file summaries')
        file_summaries_abbreviated = {}
        file_summaries = {}

        file_summaries_path = f"filebot-store-000/{user_store}/.docubot/file_summaries.json"

        # Try to open and read the JSON file
        try:
            with open(file_summaries_path, 'r') as json_file:
                file_summaries = json.load(json_file)
        except FileNotFoundError:
            logging.error(f"{file_summaries_path} not found.")
            return {}
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON in {file_summaries_path}")
            return {}

        # Debugging: Print the available keys in the file_summaries dictionary
        logging.debug(f"Available keys in file_summaries: {list(file_summaries.keys())}")

        # Normalize the keys in file_summaries
        normalized_file_summaries = normalize_file_summaries(file_summaries)

        # Try to extract data for each file_path
        for file_path in file_paths:
            file_path = modify_path_if_docubot(file_path)
            file_path = normalize_key(file_path)
            file_path = use_non_doc_file_path(file_path)
            summary = normalized_file_summaries.get(file_path)  # Use .get() to avoid KeyError

            if summary is not None:
                file_summaries_abbreviated[file_path] = summary
            else:
                logging.warning(f"{file_path} not found in file_summaries")

        logging.info('completed abbreviating file summaries')
        return file_summaries_abbreviated

    except Exception as e:
        logging.exception("An unexpected error occurred")
        return {}

# Assuming `modify_path_if_docubot` is defined elsewhere in your code

# Extract file paths from response
def extract_file_paths(response, code_mode=False):
    """Extract file paths from the response using regular expressions."""
    pattern = r"\[(.*?)\]"
    file_paths = re.findall(pattern, response)

    # In code-mode, strip '_doc.md' from file paths that have it and remove './docubot'
    if code_mode:
        file_paths = [
            path.replace('_doc.md', '').replace('./docubot', '') if path.endswith('_doc.md') and path.startswith('./docubot')
            else path
            for path in file_paths
        ]

    return file_paths

def modify_path_if_docubot(original_path):
    # Check if './docubot' is part of the original path
    if './docubot' in original_path:
        # Remove the './docubot' portion from the path
        modified_path = original_path.replace('./docubot', '')

        # Extract the directory and file name from the modified path
        directory, filename = os.path.split(modified_path)

        # Check if filename already ends with '_doc.md'
        if not filename.endswith('_doc.md'):
            # Append '_doc.md' to the file name
            filename = f"{filename}_doc.md"

        # Construct the new full path
        new_path = os.path.join(directory, filename)

        return new_path

    return original_path

if __name__ == '__main__':
    file_paths = elimination_round(response)
    file_summaries = file_summaries_abbreviated('turbosrc-service', file_paths)
    file_summaries = json.dumps(file_summaries, indent=4)
    print(file_summaries)