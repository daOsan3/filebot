from typing import Tuple
from .token_counter import num_tokens_from_string

def check_token_length(content: str, max_length: int, model: str) -> Tuple[bool, str]:
    """
    Check if the token length of the content is within the specified maximum length.
    Returns a tuple (is_within_limit, content), where is_within_limit is a boolean indicating if the content is within the limit,
    and content is the original content or truncated content if it exceeds the limit.
    """
    token_length = num_tokens_from_string(content, model)

    if token_length > max_length:
        return False, content

    return True, content

def get_model_and_tokens(prompt):
    is_within_limit_gpt3, prompt = check_token_length(prompt, 4192, 'gpt-3')
    is_within_limit_gpt4, prompt = check_token_length(prompt, 8000, 'gpt-3')
    is_within_limit_gpt3_big, prompt = check_token_length(prompt, 160000, 'gpt-3')

    model_name = None
    max_tokens = None

    if is_within_limit_gpt4:
        model_name = "gpt-4"
        max_tokens = 8000
    elif is_within_limit_gpt3:
        model_name = "gpt-3.5-turbo"
        max_tokens = 4192
    elif is_within_limit_gpt3_big:
        model_name = "gpt-3.5-turbo-16k-0613"
        max_tokens = 16000

    return model_name, max_tokens
