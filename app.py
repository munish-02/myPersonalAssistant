from flask import Flask, request, render_template, session, redirect, url_for, flash
import os
import uuid
from datetime import datetime, timedelta
from modules.assistant import create_assistant, get_assistant_response,getAllNotes,deleteNotesFromDatabase
from modules.thread import create_thread
from modules.fileManagement import load_thread_store, save_thread_store, returnVectorDatabase,saveVectorDatabase,createNewIndexDatabase

# Flask app setup
app = Flask(__name__)

# Simplified session configuration - remove SECURE for testing
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-very-secure-secret-key-here')
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
    # Temporarily remove SECURE for debugging
    # SESSION_COOKIE_SECURE=True,
)

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

def get_or_create_session():
    """Simplified session management"""
    global thread_store
    
    session.permanent = True
    
    # Always check for existing session_id first
    session_id = session.get('session_id')
    
    # Debug: Print what we're working with
    print(f"DEBUG: Current session_id from session: {session_id}")
    print(f"DEBUG: Available thread_store keys: {list(thread_store.keys())}")
    
    # If no session_id or it doesn't exist in thread_store, create new one
    if not session_id or session_id not in thread_store:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        thread = create_thread()
        thread_store[session_id] = {
            'thread': thread, 
            'chat_history': [], 
            'createdAt': datetime.now(),
            'lastActivity': datetime.now()
        }
        save_thread_store(thread_store)
        print(f"DEBUG: Created NEW session: {session_id}")
    else:
        # Update existing session
        thread_store[session_id]['lastActivity'] = datetime.now()
        print(f"DEBUG: Using EXISTING session: {session_id}")
    
    return session_id

def cleanup_old_sessions():
    """Remove sessions older than 24 hours"""
    global thread_store
    current_time = datetime.now()
    sessions_to_remove = []
    
    for session_id, data in thread_store.items():
        last_activity = data.get('lastActivity', data.get('createdAt', datetime.now()))
        if current_time - last_activity > timedelta(hours=24):
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        del thread_store[session_id]
    
    if sessions_to_remove:
        save_thread_store(thread_store)
        print(f"DEBUG: Cleaned up {len(sessions_to_remove)} old sessions")

@app.before_request
def before_request():
    """Run before each request to clean up old sessions"""
    cleanup_old_sessions()

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

@app.route('/products/<category>')
def products(category):
    category_names = {
        'ceilings': 'Ceilings',
        'partitions': 'Partitions',
        'flooring': 'Flooring',
        'exterior-wall-cladding': 'Exterior Wall Cladding',
        'interior-wall-cladding': 'Interior Wall Cladding'
    }
    
    display_name = category_names.get(category, category.replace('-', ' ').title())
    
    return render_template('products.html', 
                          category=category,
                          display_name=display_name,
                          title=f"{display_name} | Products")

@app.route('/services')
def services():
    return render_template('services.html', title="Services & Projects")

@app.route('/quote', methods=['GET', 'POST'])
def quote():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        service = request.form.get('service')
        project_details = request.form.get('project_details')
        budget = request.form.get('budget')
        timeline = request.form.get('timeline')
        return redirect(url_for('quote'))
    
    return render_template('quote.html', title="Get a Quote")

@app.route('/trident-holdings')
def tridentHoldings():
    return render_template('trident_holdings.html')

@app.route('/trident-creations')
def tridentCreations():
    return render_template('trident_creations.html')

@app.route('/trident-creations-chennai')
def tridentCreationsChennai():
    return render_template('trident_creations_chennai.html')

@app.route('/trident-interiors')
def tridentInteriors():
    return render_template('trident_interiors.html')

@app.route('/our-people')
def people():
    return render_template('people.html')

@app.route('/our-quality')
def quality():
    return render_template('quality.html')

@app.route('/ass', methods=['GET', 'POST'])
def chat():
    global thread_store
    
    session_id = get_or_create_session()
    thread_data = thread_store[session_id]
    
    print(f"\n=== CHAT REQUEST DEBUG ===")
    print(f"Method: {request.method}")
    print(f"Final Session ID: {session_id}")
    print(f"Chat history length: {len(thread_data['chat_history'])}")
    print(f"Chat history: {thread_data['chat_history']}")
    
    # Check if thread needs to be recreated (older than 1 hour)
    current_time = datetime.now()
    thread_created_at = thread_data['createdAt']
    
    if current_time - thread_created_at > timedelta(hours=1):
        print(f"DEBUG: Recreating thread (age: {current_time - thread_created_at})")
        thread = create_thread()
        thread_data['thread'] = thread
        thread_data['createdAt'] = current_time
        save_thread_store(thread_store)

    if request.method == 'POST':
        try:
            user_message = request.form.get('user_message', '').strip()
            if not user_message:
                print("DEBUG: No user message received")
                return render_template('chat.html', 
                                     chat_history=thread_data['chat_history'],
                                     debug_info=f"Session: {session_id}, History: {len(thread_data['chat_history'])}")

            print(f"DEBUG: Processing message: '{user_message}'")

            # Get assistant response
            bot_response = get_assistant_response(
                thread_data['thread'], 
                assistant, 
                user_message,
                index,
                TEXT_DATABASE_PATH,
                INDEX_DATABASE_PATH
            )

            print(f"DEBUG: Bot response length: {len(bot_response)}")

            # Add messages to history
            thread_data['chat_history'].append(f"You: {user_message}")
            thread_data['chat_history'].append(f"Bot: {bot_response}")
            thread_data['lastActivity'] = current_time

            # Save immediately
            save_thread_store(thread_store)
            
            print(f"DEBUG: Updated chat history length: {len(thread_data['chat_history'])}")
            print(f"=== END CHAT DEBUG ===\n")

            # Return directly instead of redirect to test
            return render_template('chat.html', 
                                 chat_history=thread_data['chat_history'],
                                 debug_info=f"Session: {session_id}, History: {len(thread_data['chat_history'])}")
            
        except Exception as e:
            print(f"DEBUG: Error: {str(e)}")
            return render_template('chat.html', 
                                 chat_history=[f"Error: {str(e)}"],
                                 debug_info=f"Session: {session_id}, Error")
    else:
        # GET request
        print(f"DEBUG: GET request - showing {len(thread_data['chat_history'])} messages")
        print(f"=== END CHAT DEBUG ===\n")
        return render_template('chat.html', 
                             chat_history=thread_data['chat_history'],
                             debug_info=f"Session: {session_id}, History: {len(thread_data['chat_history'])}")

@app.route('/deleteNotes', methods=['GET', 'POST'])
def deleteNotesPage():
    if request.method == 'POST':
        note_ids = request.form.getlist('note_ids')
        note_ids = [int(id) for id in note_ids]
        deleteNotesFromDatabase(note_ids,index,TEXT_DATABASE_PATH,INDEX_DATABASE_PATH)
        return redirect(url_for('deleteNotesPage'))
    
    notes = getAllNotes(TEXT_DATABASE_PATH)
    return render_template('deleteNotes.html', notes=notes)

# Utility routes
@app.route('/force-clear-all-sessions')
def force_clear_all():
    """Clear ALL sessions - use with caution"""
    global thread_store
    thread_store.clear()
    session.clear()
    save_thread_store(thread_store)
    return "Cleared ALL sessions and thread store"

@app.route('/clear-chat-history')
def clear_chat_history():
    """Clear current session's chat history"""
    session_id = get_or_create_session()
    if session_id in thread_store:
        thread_store[session_id]['chat_history'] = []
        save_thread_store(thread_store)
        return f"Cleared chat history for session {session_id}. <a href='/ass'>Go to chat</a>"
    return "No active session found"

@app.route('/debug-session')
def debug_session():
    """Debug route to check session information"""
    session_id = get_or_create_session()
    return {
        'session_id': session_id,
        'session_data': dict(session),
        'thread_store_keys': list(thread_store.keys()) if thread_store else [],
        'cookies': dict(request.cookies),
        'thread_store_count': len(thread_store) if thread_store else 0,
        'current_session_history': thread_store[session_id]['chat_history'] if session_id in thread_store else 'Not found'
    }

@app.teardown_appcontext
def save_on_shutdown(exception=None):
    """Save the thread store when the application shuts down."""
    save_thread_store(thread_store)

if __name__ == '__main__':
    thread_store = load_thread_store()
    app.run(host='0.0.0.0', port=443, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem',
                                                   '/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))