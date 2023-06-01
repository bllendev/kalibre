# django
from django.http import JsonResponse
from django.utils import timezone

# tools
import os
import json
import openai

# local
from ai.models import TokenUsage
from ai.constants import TOKEN_USAGE_DAILY_LIMIT
import tiktoken


# update your `update_token_usage` function to use `tiktoken`
def update_token_usage(request, messages):
    date_today = timezone.now().date()
    token_usage, created = TokenUsage.objects.get_or_create(user=request.user, date=date_today)

    # use tiktoken to count the tokens in the new messages only
    tokenizer = tiktoken.get_encoding("cl100k_base")  # moved outside of the loop
    new_tokens = 0
    for message in messages:
        token_ids = list(tokenizer.encode(message["content"]))
        new_tokens += len(token_ids)

    # update the user's total tokens used
    token_usage.tokens_used += new_tokens
    token_usage.save()


def query_ai(request, messages, summary=False):
    """
    - sends a message to the AI Librarian (GPT-3.5 Turbo)
    - accounts for token usage (TokenUsage model)
    returns:
       the AI's response (str)
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=1000,
        temperature=0.7,
    )
    ai_response = response['choices'][0]['message']['content'].strip()

    # summarize if the user has exceeded their daily token limit
    if summary:
        ai_response = set_latest_messages(ai_response)

    # update the token usage after a successful request
    update_token_usage(request, messages)  # updating with the correct argument
    return ai_response


def set_latest_messages(messages):
    """
    - sets the latest messages to the last two messages in the conversation (to lower TokenUsage)
    - the last message is the system's role
    - the second to last message is the summary of the conversation
    """
    if len(messages) > 2:
        # Take only the last two messages
        messages = messages[-2:]
    return messages


def ai_librarian(request):
    """
    - ajax view that sends a message to the AI Librarian (GPT-3.5 Turbo)
    """
    if request.method == 'POST':
        # extract messages from request
        ai_response = None
        messages_json = None
        messages = None
        try:
            messages_json = request.POST.get('messages')
            messages = json.loads(messages_json)
        except Exception as e:
            print(f"ERROR: {e}")
            print(f"request.POST.items(): {request.POST.items()}")
            print(f"messages_json: {messages_json}")
            print(f"messages: {messages}")

        date_today = timezone.now().date()
        token_usage, created = TokenUsage.objects.get_or_create(user=request.user, date=date_today)

        try:

            # check if the user has exceeded their daily token limit
            if token_usage.tokens_used > TOKEN_USAGE_DAILY_LIMIT:
                print(f"DAILY LIMIT EXCEEDED: SUMMARIZING CONVERSATION...{messages}")
                messages.append({"role": "user", "content": "summarize the conversation succinctly thus far so that you as a generative AI model can continue the conversation meaningfully without other context."})
                # Truncate the messages to the last two
                messages = set_latest_messages(messages)
                ai_response = query_ai(request, messages, summary=True)
            else:
                ai_response = query_ai(request, messages)
        except Exception as e:
            return JsonResponse({'error': f'An error occurred while processing your request...{e}'}, status=500)  # 500 -> internal server error

        return JsonResponse({'message': ai_response})

    return JsonResponse({'error': 'Invalid request method'}, status=400)  # 400 -> bad request