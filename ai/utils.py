import os
import openai
from django.conf import settings
from ai.models import Message
import tiktoken
import numpy as np

import logging

logger = logging.getLogger(__name__)


def fx_query_openai(**kwargs):
    """
    - queries openai with the given query and messages
    - returns the response from openai
    """
    # get the kwargs or set defaults
    query = kwargs.get("query")
    user_messages = kwargs.get("user_messages", list())
    ai_messages = kwargs.get("ai_messages", list())
    system_prompt = kwargs.get("system_prompt", "")
    temperature = kwargs.get("temperature", 0.7)

    # add system prompt to the beginning of the conversation
    conversation_list = [Message.get_message(system_prompt, role="system")]

    # add existing (if available) user and ai messages to the conversation
    for idx, user_msg in enumerate(user_messages):
        user_msg = Message.get_message(user_msg, role="user")
        if user_msg:
            conversation_list.append(user_msg)

        ai_msg = Message.get_message(ai_messages[idx], role="ai")
        if ai_msg:
            conversation_list.append(ai_msg)

    # add final query to the conversation
    conversation_list.append(Message.get_message(query, role="user"))

    # query openai with the conversation
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation_list,
        max_tokens=2000,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)  # Explicit client instantiation


if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError("no api key set!")


def get_openai_embeddings(
    texts, embedding_model="text-embedding-3-small", max_tokens=8000
):
    """
    Generate embeddings for a list of texts using OpenAI's API.

    Args:
        texts (list of str): Texts to compute embeddings for.
        embedding_model (str, optional): OpenAI model to use.
        max_tokens (int, optional): Max token limit per input text.

    Returns:
        list: A single embedding (flattened list) if successful.
    """
    if settings.TESTING:
        from ai.models import VectorSearch

        logger.info(
            "testing get_openai_embeddings...using fake embeddings skip api")
        return [1.0] * VectorSearch.DIMENSION

    # count projected tokens
    tokenizer = tiktoken.get_encoding("cl100k_base")
    valid_texts = [text for text in texts if len(
        tokenizer.encode(text)) <= max_tokens]

    if not valid_texts:
        logger.error("No valid texts found for embedding generation.")
        return []

    try:
        response = client.embeddings.create(input=texts, model=embedding_model)
        embeddings = [
            np.array(embedding.embedding, dtype=np.float32)
            for embedding in response.data
        ]
        logger.info(f"Generated embeddings: {embeddings}")
        return embeddings[0].flatten().tolist()  # Ensure a 1D list
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise e
