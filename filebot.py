import sys
import os
import json
import asyncio
import re
import configparser
import argparse

# Ensure the project root directory is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.file_summary import create_file_summaries
from modules.find_info import find_relevant_info, answer_prompt
from modules.file_ranker import rank_files, get_file_answers
from modules.docubot.modules import generate_prompts

# Answer user prompt
async def answer_user_prompt(relevant_info):
    """Generate a response to the user's prompt based on the relevant info."""
    if not relevant_info:
        return "I'm sorry, I couldn't find any relevant files to answer your question. Please rephrase or try another search."
    else:
        response = "Answer: {}".format(relevant_info)
        return response

# Extract file paths from response
#def extract_file_paths(response, code_mode):
#    """Extract file paths from the response using regular expressions."""
#    pattern = r"(filebot-store-000\S*)`"
#    file_paths = re.findall(pattern, response)
#
#    # If in code-mode, strip `_docs.md` from the end of file paths
#    if code_mode:
#        file_paths = [fp.replace('_docs.md', '') for fp in file_paths]
#
#    return file_paths

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

async def main_async():
    parser = argparse.ArgumentParser(description='Run filebot with the specified model.')
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo", help='Which model to use: gpt-3.5-turbo or gpt-3.5-turbo (default is gpt-3.5-turbo)')
    parser.add_argument('--num-files', type=int, default=3, help='Number of top files to consider (default is 3)')
    parser.add_argument('--code-mode', action='store_true', help='Your code flag description')

    args = parser.parse_args()
    model_name = args.model
    code_mode = args.code_mode

    config = configparser.ConfigParser()
    config.read('filebot.config')
    file_summaries_path = config['OPTIONS'].get('RelativeFileSummariesPath', '')
    file_store_path = config['OPTIONS'].get('RelativeFileStorePath', '')

    print("code mode:", code_mode)

    # Pass the flag value to create_file_summaries
    await create_file_summaries(file_store_path, file_summaries_path, code_mode=code_mode)

    while True:
        user_prompt = input("\033[92mPrompt:\033[0m ")
        relevant_info = await find_relevant_info(user_prompt)

        response = await answer_user_prompt(relevant_info)

        # Extract file paths
        file_paths = extract_file_paths(response, code_mode)
        # In code-mode, strip '_doc.md' from file paths that have it
        if code_mode:
            file_paths = [path.replace('_docs.md', '') if path.endswith('_docs.md') else path for path in file_paths]

        if file_paths:
            # Rank and get top files as per user's choice
            top_files = await rank_files(file_paths, args.num_files)

            # In code_mode, only consider the first two items in the top_files list, if they exist
            if code_mode and len(top_files) > 1:
                top_files = top_files[:2]

            # Asynchronously get answers for the top 3 files, but one top two if in code mode.
            answers = await get_file_answers(top_files, user_prompt, answer_prompt)

            # Display the results
            print("\nTop answers from relevant files:")
            for index, (file, answer) in enumerate(answers, start=1):
                print(f"{index}. {answer}\nsource: {file}\n\n")
            print("")

            while True:
                # Ask the user to select a file
                file_choice = input("Please select a file by typing its number or press 'Enter' to skip or select another: ")

                # If the user presses 'Enter' without choosing a file, break to outer loop
                if file_choice.strip() == '':
                    break

                selected_index = int(file_choice) - 1

                # Ensure valid selection
                if selected_index < 0 or selected_index >= len(file_paths):
                    print("\033[38;5;208mInvalid selection\033[0m")
                    continue

                # Use the selected file
                selected_file = re.sub(r'\.\d+$', '', file_paths[selected_index])
                answer = await answer_prompt(selected_file, user_prompt, answer_type='final_answer')
                print(f"\n\n{answer}")
                print(f"\033[1;97m\nsource: {selected_file}\033[0m")
                print("\n\n")

        else:
            print(f"\033[38;5;208mNo files found\033[0m\n\n{response}")

if __name__ == '__main__':
    asyncio.run(main_async())