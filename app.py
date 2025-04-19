from flask import Flask, redirect, request, render_template, session, url_for
import os
import uuid
from datetime import datetime, timedelta
from modules.assistant import create_assistant, deleteNotesFromDatabase, get_assistant_response, getAllNotes
from modules.thread import create_thread
from modules.fileManagement import load_thread_store, save_thread_store, returnVectorDatabase,saveVectorDatabase,createNewIndexDatabase
import logging

# Logging setup for systemd journal (stdout/stderr)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Use environment variable for better security

# Path to save and load thread_store data

INDEX_DATABASE_PATH='databases/indexDatabase.bin'
TEXT_DATABASE_PATH='databases/assistantDatabase.db'
# Initialize assistant globally
assistant = create_assistant()


# Load thread store at the start
thread_store = load_thread_store()
if os.path.exists(INDEX_DATABASE_PATH):
    index=returnVectorDatabase(INDEX_DATABASE_PATH)
else:
    index=createNewIndexDatabase()
    saveVectorDatabase(index,INDEX_DATABASE_PATH)

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/trident')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/ass', methods=['GET', 'POST'])
def chat():
    global thread_store

    logging.debug(f"Session data: {dict(session)}")
    session_id = session.get('session_id')

    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        logging.debug(f"New session created with session_id: {session_id}")
        thread = create_thread()
        thread_store[session_id] = {
            'thread': thread,
            'chat_history': [],
            'createdAt': datetime.now()
        }
    else:
        thread_data = thread_store.get(session_id)
        logging.debug(f"Retrieved thread_data for session_id {session_id}: {thread_data}")

        try:
            thread = thread_data['thread']
            created_at = thread_data.get('createdAt', datetime.now())
            current_time = datetime.now()

            if (current_time - created_at > timedelta(hours=1)):
                logging.debug("Thread expired. Creating new thread.")
                thread = create_thread()
                thread_store[session_id] = {
                    'thread': thread,
                    'chat_history': [],
                    'createdAt': current_time
                }

        except Exception as e:
            logging.error(f"Error retrieving thread: {e}")
            thread = create_thread()
            thread_store[session_id] = {
                'thread': thread,
                'chat_history': [],
                'createdAt': datetime.now()
            }

    thread_data = thread_store.get(session_id)
    logging.debug(f"Final thread_data for session_id {session_id}: {thread_data}")

    if request.method == 'POST':
        try:
            user_message = request.form.get('user_message', type=str)
            logging.debug(f"User message received: {user_message}")

            if not user_message:
                return render_template('chat.html', chat_history=thread_data['chat_history'])

            bot_response = get_assistant_response(thread_data['thread'], assistant, user_message, index, TEXT_DATABASE_PATH, INDEX_DATABASE_PATH)

            logging.debug(f"Bot response: {bot_response}")

            thread_data['chat_history'].append(f"You: {user_message}")
            thread_data['chat_history'].append(f"Bot: {bot_response}")

            save_thread_store(thread_store)
            return render_template('chat.html', chat_history=thread_data['chat_history'])
        except Exception as e:
            logging.exception("Exception in POST /ass")
            return render_template('chat.html', chat_history=[f"An error occurred: {str(e)}"])
    else:
        return render_template('chat.html', chat_history=thread_data['chat_history'])

@app.route('/deleteNotes', methods=['GET', 'POST'])
def deleteNotesPage():
    if request.method == 'POST':
        note_ids = request.form.getlist('note_ids')
        note_ids = [int(id) for id in note_ids]
        deleteNotesFromDatabase(note_ids,index,TEXT_DATABASE_PATH,INDEX_DATABASE_PATH)
        return redirect(url_for('deleteNotesPage'))
    
    notes = getAllNotes(TEXT_DATABASE_PATH)
    return render_template('deleteNotes.html', notes=notes)

@app.teardown_appcontext
def save_on_shutdown(exception=None):
    """Save the thread store when the application shuts down."""
    save_thread_store(thread_store)

if __name__ == '__main__':
    thread_store = load_thread_store()
    app.run(host='0.0.0.0', port=443, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem',
                                                   '/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))
