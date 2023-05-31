# django
from django.http import JsonResponse

# tools
import os
import json
import openai


def ai_librarian(request):
    """
    - ajax view that sends a message to the AI Librarian (GPT-3.5 Turbo)
    """
    if request.method == 'POST':
        messages_json = request.POST.get('messages')
        messages = json.loads(messages_json)
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
            temperature=0.4,
        )
        try:
            ai_response = response['choices'][0]['message']['content'].strip()
            print(f"response: {response}")
            print(f"ai_response: {ai_response}")
        except Exception as e:
            print(f"response: {response}")
            print(f"ERROR: {e}")
            print(f"response: {response}")
            print(f"response.json(): {response.json()}")
        return JsonResponse({'message': ai_response})
    return JsonResponse({'error': 'Invalid request method'}, status=400)
