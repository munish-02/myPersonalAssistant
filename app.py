from flask import Flask, request, render_template, session
import os
import uuid
import pickle

# Replace these with your actual assistant and thread modules
from modules.assistant import create_assistant, get_assistant_response
from modules.thread import create_thread

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Use environment variable for better security

# Path to save and load thread_store data
THREAD_STORE_FILE = 'thread_store.pkl'

# Initialize assistant globally
assistant = create_assistant()

def load_thread_store():
    """Load thread_store from the pickle file if it exists."""
    if os.path.exists(THREAD_STORE_FILE):
        with open(THREAD_STORE_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_thread_store(thread_store):
    """Save thread_store to a pickle file."""
    with open(THREAD_STORE_FILE, 'wb') as f:
        pickle.dump(thread_store, f)

# Load thread store at the start
thread_store = load_thread_store()

@app.route('/', methods=['GET', 'POST'])
def chat():
    global thread_store  # Ensure we're working with the global thread_store

    # Check if the session has a session_id; if not, create one
    if 'session_id' not in session:

        session_id = str(uuid.uuid4())  # Generate a unique session ID
        session['session_id'] = session_id
        thread = create_thread()  # Create a new thread object
        thread_store[session_id] = {'thread': thread, 'chat_history': []}  # Store thread and chat_history in memory
        thread_data = thread_store.get(session_id)
        
    else:
        session_id = session['session_id']
        thread_data = thread_store.get(session_id)  # Retrieve thread and chat history from the store
        thread = thread_data['thread']

    # Handle POST requests
    if request.method == 'POST':
        try:
            # Get the user's message from the form
            user_message = request.form.get('user_message', type=str)
            if not user_message:
                return render_template('chat.html', chat_history=thread_data['chat_history'])

            # Get assistant response
            bot_response = get_assistant_response(thread, assistant, user_message)

            # Append user and bot messages to chat history
            thread_data['chat_history'].append(f"You: {user_message}")
            thread_data['chat_history'].append(f"Bot: {bot_response}")

            # Save thread store after each interaction
            save_thread_store(thread_store)

            return render_template('chat.html', chat_history=thread_data['chat_history'])
        except Exception as e:
            return render_template('chat.html', chat_history=[f"An error occurred: {str(e)}"])
    else:
        # Handle GET requests
        return render_template('chat.html', chat_history=thread_data['chat_history'])

@app.teardown_appcontext
def save_on_shutdown(exception=None):
    """Save the thread store when the application shuts down."""
    save_thread_store(thread_store)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem',
                                                   '/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))
