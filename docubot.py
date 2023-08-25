import os
import asyncio
import sys

from modules.docubot.modules.llm_model import generate_completion
from modules.docubot.modules.source_code_finder import document_source_files
from modules.docubot.modules.generate_prompts import generate_prompts

def read_api_key(file_path="openai_api_key"):
    """
    Read the OpenAI API key from a file.

    :param file_path: The path to the file containing the OpenAI API key.
    :type file_path: str
    :return: The OpenAI API key as a string.
    """
    with open(file_path, "r") as key_file:
        return key_file.read().strip()

# Set the OpenAI API key
openai_api_key = read_api_key()
os.environ["OPENAI_API_KEY"] = openai_api_key
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

async def process_files(input_dir, output_dir):
    """
    Asynchronously process files from the input directory
    and save the generated completions to the output directory.

    :param input_dir: The path to the directory with prompt files.
    :type input_dir: str
    :param output_dir: The path to the directory where output will be saved.
    :type output_dir: str
    """
    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Loop through all the files listed in files.txt
    with open("files.txt", 'r') as file:
        files = file.read().splitlines()

    for file_path in files:
        relative_path = os.path.relpath(file_path, input_dir)
        output_path = os.path.join(output_dir, os.path.dirname(relative_path))
        os.makedirs(output_path, exist_ok=True)

        with open(file_path, 'r') as source_file:
            prompt = source_file.read()

        # Generate completion using the OpenAI API
        completion = await generate_completion(prompt)

        # Write the completion to a new file in the output directory
        output_file_name = os.path.basename(file_path) + '_doc.md'
        output_file_path = os.path.join(output_path, output_file_name)

        with open(output_file_path, 'w') as output_file:
            output_file.write(completion)

def main(input_dir, output_dir):
    """
    Main function that gets invoked when the script is run directly.
    """
    print("input_dir arg:", input_dir)
    print("output_dir arg:", output_dir)

    # Run the document_source_files function from the source_code_finder module to generate mirrored directories
    document_source_files(input_dir, output_dir)

    # Run the generate_prompts function from the generate_prompts module
    generate_prompts()

    # Process all prompts
    asyncio.run(process_files(input_dir, output_dir))

# This is the standard boilerplate that calls the 'main' function
# when the script is run directly
if __name__ == "__main__":
    # Check if the command line arguments are provided
    if len(sys.argv) < 3:
        print("Usage: python docubot.py <input_dir_path> <output_dir_path>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
