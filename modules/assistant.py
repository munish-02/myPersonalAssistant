import openai
import time
from modules.config import OPENAI_API_KEY
from modules.run import create_run

# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

def create_assistant():
    return openai.beta.assistants.retrieve("asst_fCJHgmM09VKGs9lRbxXdybes")

def get_assistant_response(thread, assistant, user_input):
    try:
        # Add user message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Create a run to process the assistant's response
        run = create_run(thread, assistant)

        # Wait for the run to complete
        while run.status != 'completed':
            time.sleep(0.1)
            run = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        # Retrieve the latest assistant message
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data:  # Reverse iterate to find the latest assistant message
            if msg.role == 'assistant':
                return "\n".join([block.text.value for block in msg.content])
    except Exception as e:
        return f"Error: {str(e)}"
