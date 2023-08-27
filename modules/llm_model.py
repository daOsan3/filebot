import os
import openai
import asyncio
import openai_async

# Call the OpenAI GPT-4 API
with open("openai_api_key", "r") as key_file:
    openai_api_key = key_file.read().strip()

os.environ["OPENAI_API_KEY"] = openai_api_key
openai.api_key = os.getenv("OPENAI_API_KEY")

async def generate_completion(prompt, model_name="gpt-4", max_tokens=8192, temperature=1.0):
    response = await openai_async.chat_complete(
        openai_api_key,
        timeout=60,
        payload={
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant and great at guessing what files may have info based on loose summaries of the files."},
                {"role": "user", "content": prompt},
            ]
        }
    )
    json_response = response.json()
    llm_content = json_response['choices'][0]['message']['content']

    return llm_content