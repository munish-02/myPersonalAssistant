import openai
from openai import OpenAI
import time
# Initialize the OpenAI client
#client = OpenAI()

# Create the Assistant
def create_assistant(client):
    
    return client.beta.assistants.retrieve("asst_kGLwlT0vAnEA3IhRHqn4huHO")

# Create a conversation thread
def create_thread(client):
    thread = client.beta.threads.create()
    return thread

# Add a message to the thread
def add_message(client,thread, user_input):
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )
    return message

# Create and poll the run to get the assistant's response
def create_run(client,thread, assistant):
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
 #       instructions="Please address the user as Jane Doe. The user has a premium account."
    )
    return run

# Main loop to interact with the assistant
def main():
    openai.api_key=''

    client=openai.OpenAI()
    assistant = create_assistant(client)
    thread = create_thread(client)

    print("Assistant is ready. Type 'exit' to stop the conversation.")

    while True:
        # Get user input
        user_input = input("You: ")

        # Exit condition
        if user_input.lower() == 'exit':
            print("Exiting the conversation.")
            break

        # Add user message to the thread
        add_message(client,thread, user_input)

        # Get the assistant's response
        run = create_run(client,thread, assistant)

        # Check the run status and print the response
        while run.status != 'completed':
            time.sleep(0.1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
                )
            
        if run.status == 'completed':
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            # Print the latest assistant message
            for msg in messages.data:
                if msg.role == 'assistant':
                    for block in msg.content:
                        print(f"Assistant: {block.text.value}")
        else:
            print("Waiting for the assistant's response...")

if __name__ == "__main__":
    main()
