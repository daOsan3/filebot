import os
import json
import configparser
from .token_checker import check_token_length
from .llm_model import generate_completion

async def find_relevant_info(user_prompt, max_token_length=3900):
    # Read config file.
    config = configparser.ConfigParser()
    config.read('filebot.config')

    # Get path of file summaries path.
    file_summaries_path = config['OPTIONS'].get('RelativeFileSummariesPath', '')

    with open(file_summaries_path, 'r') as json_file:
        file_summaries = json.load(json_file)


    # Get prepend text
    prepend_prompt = config['DEFAULT'].get('PrependPrompt', '')


    user_prompt = f"{prepend_prompt}. Based on the following summaries```{file_summaries}``` which file or files based on the summaries should we open to see if it has any info regarding. List the most promising files first. Prepend and append a bracket to each filepath given like this `[filebot-store-00/file/path]`: ```{user_prompt}```"
    is_within_limit, user_prompt = check_token_length(user_prompt, max_token_length, 'gpt-3')

    if not is_within_limit:
        return "The content is too large to summarize."

    response = await generate_completion(user_prompt)

    return response

def get_file_content(file_path):
    """Fetch the content of a file at a given file path."""
    with open(file_path, 'r') as file:
        content = file.read()

    return content

async def answer_prompt(file_path, user_prompt, max_token_length=3900, answer_type="non_final_answer"):
    content = get_file_content(file_path)

    config = configparser.ConfigParser()
    config.read('filebot.config')

    # Get prepend text
    if answer_type == "final_answer":
        prepend_prompt = config['ANSWER'].get('PrependPrompt', '')
    else:
        prepend_prompt = config['DEFAULT'].get('PrependPrompt', '')

    is_within_limit, user_prompt = check_token_length(user_prompt, max_token_length, 'gpt-3')

    if not is_within_limit:
        return "The content is too large to summarize."

    final_prompt = f"{prepend_prompt}. {user_prompt}, based on the following: ```{content}```"

    #response = await generate_completion(final_prompt, max_tokens=8500, temperature=0.8)

    return final_prompt
