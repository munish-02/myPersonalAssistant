from flask import Flask, request, render_template, session
import time
import os
import openai

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Initialize the OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI()

def create_assistant(client):
    return client.beta.assistants.retrieve("asst_fCJHgmM09VKGs9lRbxXdybes")

def create_thread(client):
    return client.beta.threads.create()

def add_message(client, thread, user_input):
    return client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )

def create_run(client, thread, assistant):
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

def get_assistant_response(client, thread, assistant, user_input):
    try:
        # Add user message to the thread
        add_message(client, thread, user_input)

        # Create a run to process the assistant's response
        run = create_run(client, thread, assistant)

        # Wait for the run to complete
        while run.status != 'completed':
            time.sleep(0.1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        # Retrieve the latest assistant message
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data[::-1]:  # Reverse iterate to find the latest assistant message
            if msg.role == 'assistant':
                return "\n".join([block.text.value for block in msg.content])
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize assistant and thread globally
assistant = create_assistant(client)
thread = create_thread(client)

@app.route('/', methods=['GET', 'POST'])
def chat():
    # Initialize chat history if not already in session
    if 'chat_history' not in session:
        session['chat_history'] = []

    if request.method == 'POST':
        try:
            # Get the user's message from the form
            user_message = request.form.get('user_message', type=str)
            if not user_message:
                return render_template('chat.html', chat_history=session['chat_history'])

            # Get assistant response
            bot_response = get_assistant_response(client, thread, assistant, user_message)

            # Append user and bot messages to chat history
            session['chat_history'].append(f"You: {user_message}")
            session['chat_history'].append(f"Bot: {bot_response}")

            return render_template('chat.html', chat_history=session['chat_history'])
        except Exception as e:
            return render_template('chat.html', chat_history=[f"An error occurred: {str(e)}"])
    else:
        return render_template('chat.html', chat_history=session['chat_history'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem',
                                                   '/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))
