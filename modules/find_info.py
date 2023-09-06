import os
import json
import configparser
import logging
from .token_checker import get_model_and_tokens
from .token_counter import num_tokens_from_string
from .llm_model import generate_completion

def break_dict_by_tokens(dict_obj, token_limit, model_name='gpt-3'):
    # Initialize variables
    part1 = {}
    part2 = {}
    current_token_count = 0

    # Iterate through the dictionary
    for key, value in dict_obj.items():
        token_count_key_value = num_tokens_from_string(f"{key}: {value}", model_name)

        if current_token_count + token_count_key_value <= token_limit:
            part1[key] = value
            current_token_count += token_count_key_value
        else:
            part2[key] = value

    return part1, part2

async def find_relevant_info(user_prompt, user_store, max_token_length=8192):
    # Read config file.
    config = configparser.ConfigParser()
    config.read('filebot.config')

    model_name = "gpt-4"
    max_tokens = 8192

    file_summaries_path = f"filebot-store-000/{user_store}/.docubot/file_summaries.json"
    with open(file_summaries_path, 'r') as json_file:
        file_summaries = json.load(json_file)

    prepend_prompt = config['DEFAULT'].get('PrependPrompt', '')

    total_tokens_file_summaries = num_tokens_from_string(json.dumps(file_summaries), 'gpt-3')

    # Break dictionary if it exceeds max_token_length
    if total_tokens_file_summaries > 7000:
        file_summaries1, file_summaries2 = break_dict_by_tokens(file_summaries, 3500, model_name='gpt-3')
        # Replace `file_summaries` with `file_summaries1` or `file_summaries2` depending on which you want to use
        file_summaries = file_summaries1  # or file_summaries2

    print(file_summaries)

    prompt = f"{prepend_prompt}. Based on the following summaries```{json.dumps(file_summaries)}``` which file or files based on the summaries should we open to see if it has any info regarding. List the most promising files first. Prepend and append a bracket to each filepath given like this `[/app/filebot-store-000/path/to/file]`: ```{user_prompt}```"

    total_tokens = num_tokens_from_string(prompt, 'gpt-3')
    model_name, max_tokens = get_model_and_tokens(prompt)

    if model_name is None or max_tokens is None:
        raise ValueError(f"No suitable model found for the given token length {total_tokens}.")

    logging.info(f"Sending request to OpenAI {model_name}")
    response = await generate_completion(prompt, model_name=model_name, max_tokens=max_tokens)
    logging.info(f"Completed request to OpenAI {model_name}")
    return response

def get_file_content(file_path):
    """Fetch the content of a file at a given file path."""
    with open(file_path, 'r') as file:
        content = file.read()

    return content

async def answer_prompt(file_path, user_prompt, max_token_length=8192, answer_type="non_final_answer"):
    content = get_file_content(file_path)

    config = configparser.ConfigParser()
    config.read('filebot.config')

    # Get prepend text
    if answer_type == "final_answer":
        prepend_prompt = config['ANSWER'].get('PrependPrompt', '')
    else:
        prepend_prompt = config['DEFAULT'].get('PrependPrompt', '')

    # Check if final_prompt (less user_prompt) exceeds token limit
    final_prompt_without_user_prompt = f"{prepend_prompt}. based on the following: ```{content}```"
    final_prompt_without_user_prompt_token_count = num_tokens_from_string(final_prompt_without_user_prompt, 'gpt-3')
    if final_prompt_without_user_prompt_token_count > max_token_length:
        excess_tokens = final_prompt_without_user_prompt_token_count - max_token_length
        return f"Content filebot needs to retrieve exceeds the token limit by {excess_tokens}."

    # Check if there are excess tokens available for user_prompt
    excess_tokens = max_token_length - final_prompt_without_user_prompt_token_count
    user_prompt_token_count = num_tokens_from_string(user_prompt, 'gpt-3')
    if user_prompt_token_count > excess_tokens:
        return f"Your query is consuming too many tokens ({user_prompt_token_count}). Reduce your prompt by {user_prompt_token_count - excess_tokens} tokens, please."

    final_prompt = f"{prepend_prompt}. {user_prompt}, based on the following: ```{content}```"

    #response = await generate_completion(final_prompt, max_tokens=8500, temperature=0.8)

    return final_prompt
