
import os
import json
import asyncio
import re
import configparser
import argparse
import functools
import logging
from aiohttp import web

response = """"
Based on your request, here are the most promising files:

1. `[/app/filebot-store-000/turbosrc-service/.docubot/server.js_doc.md]`
2. `[/app/filebot-store-000/turbosrc-service/README.md]`
3. `[/app/filebot-store-000/turbosrc-service/tsrc-dev]`
4. `[/app/filebot-store-000/turbosrc-service/tsrc-test]`

The `server.js_doc.md` file seems the most relevant as it outlines the functionality related to GraphQL schema and endpoint operations of `server.js`. The `README.md` may contain overall information about modifying the service, and the `tsrc-dev` and `tsrc-test` could be pertinent as they handle service operations and testing.Based on the provided files and summaries it seems like these are the most relevant files:

1. `[/app/filebot-store-000/turbosrc-service/.docubot/src/lib/state.js_doc.md]`
2. `[/app/filebot-store-000/turbosrc-service/.docubot/src/lib/actions.js_doc.md]`
3. `[/app/filebot-store-000/turbosrc-service/.docubot/src/utils/engineRequests.js_doc.md]`
4. `[/app/filebot-store-000/turbosrc-service/.docubot/src/utils/requests.js_doc.md]`
5. `[/app/filebot-store-000/turbosrc-service/.docubot/src/utils/ghServiceRequests.js_doc.md]`
"""

def elimination_round(response, code_mode=False):
    file_paths = extract_file_paths(response, code_mode)
    return file_paths

def file_summaries_abbreviated(user_store, file_paths):
    file_summaries_abbreviated = {}
    file_summaries = {}

    file_summaries_path = f"filebot-store-000/{user_store}/.docubot/file_summaries.json"
    with open(file_summaries_path, 'r') as json_file:
        file_summaries = json.load(json_file)

    for file_path in file_paths:
        file_summaries_abbreviated[file_path] = file_summaries[file_path]
    return file_summaries_abbreviated

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

if __name__ == '__main__':
    file_paths = elimination_round(response)
    file_summaries = file_summaries_abbreviated('turbosrc-service', file_paths)
    file_summaries = json.dumps(file_summaries, indent=4)
    print(file_summaries)