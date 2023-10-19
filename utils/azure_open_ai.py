import openai
from config import AZURE_OPENAI_KEY, AZURE_OPENAI_BASE_URL, OPEN_AI_KEY, DEFAULT_SUMMARISATION_MODEL, EMBED_MODEL
from .open_ai_fallback import get_open_ai_chat_completion, get_vector_openai


async def get_vector(text):

    if AZURE_OPENAI_KEY:

        response = openai.Embedding.create(
            api_type="azure",
            api_key=AZURE_OPENAI_KEY,
            api_base=AZURE_OPENAI_BASE_URL,
            api_version="2023-07-01-preview",
            input=text,
            engine=EMBED_MODEL
        )
        embeddings = response['data'][0]['embedding']
        return embeddings
    else:
        embeddings_openai = await get_vector_openai(text)
        return embeddings_openai


async def get_chat_completion(messages, model=DEFAULT_SUMMARISATION_MODEL, max_res_tokens=200, temp=0.2, functions=None, function_to_call="auto"):

    # Initialize the arguments dictionary
    call_args = {
        "api_type": "azure",
        "api_key": AZURE_OPENAI_KEY,
        "api_base": AZURE_OPENAI_BASE_URL,
        "api_version": "2023-07-01-preview",
        "engine": model,
        "messages": messages,
        "max_tokens": max_res_tokens,
        "temperature": temp,
    }

    # If functions parameter is passed, include "functions" and "function_call" in the arguments dictionary
    if functions is not None:
        call_args["functions"] = functions
        call_args["function_call"] = function_to_call
    try:
        # Test if azure key is set and if not use openAI
        if not AZURE_OPENAI_KEY:
            raise Exception("AZURE_OPENAI_KEY is not set.")
        else:
            response = openai.ChatCompletion.create(**call_args)

            return response['choices'][0]

    except Exception as e:
        print(e)
        print(messages)
        if OPEN_AI_KEY:
            try:
                open_res = await get_open_ai_chat_completion(messages, model, max_res_tokens, temp, functions, function_to_call)
                return open_res
            except Exception as e:
                print('fError in openai fallback: {e}')
        else:
            raise Exception('fError in azure openai: {e}')
