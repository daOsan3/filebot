import json
import asyncio
import re
import configparser
import argparse
import functools
from aiohttp import web
from modules.file_summary import create_file_summaries
from modules.find_info import find_relevant_info
from modules.find_info import answer_prompt
from modules.file_ranker import rank_files, get_file_answers

# Answer user prompt
async def answer_user_prompt(relevant_info):
    """Generate a response to the user's prompt based on the relevant info."""
    if not relevant_info:
        return "I'm sorry, I couldn't find any relevant files to answer your question. Please rephrase or try another search."
    else:
        response = "Answer: {}".format(relevant_info)
        return response

# Extract file paths from response
def extract_file_paths(response, code_mode=False):
    """Extract file paths from the response using regular expressions."""
    pattern = r"\[(.*?)\]"
    file_paths = re.findall(pattern, response)

    # In code-mode, strip '_doc.md' from file paths that have it
    if code_mode:
        file_paths = [path.replace('_doc.md', '') if path.endswith('_doc.md') else path for path in file_paths]

    return file_paths

def get_source_code_path(file_path, code_mode=False):
    # In code-mode, strip '_doc.md' from the file path if it has it
    if code_mode and file_path.endswith('_doc.md'):
        file_path = file_path.replace('_doc.md', '')

    return file_path

async def get_filebot_response(request, code_mode, num_files):
    try:
        data = await request.json()
        user_prompt = data.get('user_prompt')
        relevant_info = await find_relevant_info(user_prompt)
        print('relevant info', relevant_info)
        response = await answer_user_prompt(relevant_info)
        file_paths = extract_file_paths(response, code_mode)

        if code_mode:
            file_paths = [path.replace('_docs.md', '') if path.endswith('_docs.md') else path for path in file_paths]

        if file_paths:
            top_files = await rank_files(file_paths, num_files)
            if code_mode and len(top_files) > 1:
                top_files = top_files[:2]
            answers = await get_file_answers(top_files, user_prompt, answer_prompt)
            return web.Response(text=json.dumps(answers))
        else:
            return web.Response(text=json.dumps({"error": "No files found"}))
    except Exception as e:
        print(f"Error in get_filebot_response: {e}")
        return web.Response(status=500, text=f"Internal Server Error: {e}")

async def main_async():
    parser = argparse.ArgumentParser(description='Run filebot with the specified model.')
    parser.add_argument('--model', type=str, default="gpt-4", help='Which model to use: gpt-4 or gpt-4 (default is gpt-4)')
    parser.add_argument('--num-files', type=int, default=3, help='Number of top files to consider (default is 3)')
    parser.add_argument('--code-mode', action='store_true', help='Your code flag description')

    args = parser.parse_args()
    model_name = args.model
    code_mode = args.code_mode
    num_files = args.num_files

    config = configparser.ConfigParser()
    config.read('filebot.config')
    file_summaries_path = config['OPTIONS'].get('RelativeFileSummariesPath', '')
    file_store_path = config['OPTIONS'].get('RelativeFileStorePath', '')

    print("code mode:", code_mode)

    await create_file_summaries(file_store_path, file_summaries_path, code_mode=code_mode)

    app = web.Application()
    app.router.add_post('/get-filebot-response', functools.partial(get_filebot_response, code_mode=code_mode, num_files=num_files))

    return app

if __name__ == '__main__':
    app = asyncio.run(main_async())
    web.run_app(app) # Run the app here
