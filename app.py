from flask import Flask, request, render_template, session, redirect, url_for, flash
import os
import uuid
from datetime import datetime, timedelta
from modules.assistant import create_assistant, get_assistant_response,getAllNotes,deleteNotesFromDatabase
from modules.thread import create_thread
from modules.fileManagement import load_thread_store, save_thread_store, returnVectorDatabase,saveVectorDatabase,createNewIndexDatabase

# Flask app setup
app = Flask(__name__)

# Improved session configuration
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-very-secure-secret-key-here')  # Use a strong secret key
app.config.update(
    SESSION_COOKIE_SECURE=True,  # Only send cookies over HTTPS
    SESSION_COOKIE_HTTPONLY=True,  # Prevent JavaScript access to session cookies
    SESSION_COOKIE_SAMESITE='Lax',  # CSRF protection
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),  # Session expires after 24 hours
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
    """Helper function to manage session creation and retrieval"""
    global thread_store
    
    # Make session permanent to use PERMANENT_SESSION_LIFETIME
    session.permanent = True
    
    # Check if session_id exists and is valid
    session_id = session.get('session_id')
    
    if not session_id or session_id not in thread_store:
        # Create new session
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        thread = create_thread()
        thread_store[session_id] = {
            'thread': thread, 
            'chat_history': [], 
            'createdAt': datetime.now(),
            'lastActivity': datetime.now()
        }
        # Save immediately after creating new session
        save_thread_store(thread_store)
    else:
        # Update last activity time
        thread_store[session_id]['lastActivity'] = datetime.now()
    
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
    # Map URL slugs to display names
    category_names = {
        'ceilings': 'Ceilings',
        'partitions': 'Partitions',
        'flooring': 'Flooring',
        'exterior-wall-cladding': 'Exterior Wall Cladding',
        'interior-wall-cladding': 'Interior Wall Cladding'
    }
    
    # Get the display name or use the slug if not found
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
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        service = request.form.get('service')
        project_details = request.form.get('project_details')
        budget = request.form.get('budget')
        timeline = request.form.get('timeline')
        
        # Here you would typically:
        # 1. Save the quote request to a database
        # 2. Send an email notification to your team
        # 3. Send a confirmation email to the customer
        
        # For now, we'll just show a success message
        #flash('Your quote request has been submitted successfully! Our team will contact you shortly.', 'success')
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
    
    # Get or create session using helper function
    session_id = get_or_create_session()
    thread_data = thread_store[session_id]
    
    # Check if thread needs to be recreated (older than 1 hour)
    current_time = datetime.now()
    thread_created_at = thread_data['createdAt']
    
    if current_time - thread_created_at > timedelta(hours=1):
        # Create new thread but keep chat history
        thread = create_thread()
        thread_data['thread'] = thread
        thread_data['createdAt'] = current_time
        save_thread_store(thread_store)

    # Handle POST requests
    if request.method == 'POST':
        try:
            # Get the user's message from the form
            user_message = request.form.get('user_message', type=str)
            if not user_message:
                return render_template('chat.html', 
                                     chat_history=thread_data['chat_history'])

            # Get assistant response
            bot_response = get_assistant_response(
                thread_data['thread'], 
                assistant, 
                user_message,
                index,
                TEXT_DATABASE_PATH,
                INDEX_DATABASE_PATH
            )

            # Append user and bot messages to chat history
            thread_data['chat_history'].append(f"You: {user_message}")
            thread_data['chat_history'].append(f"Bot: {bot_response}")
            thread_data['lastActivity'] = current_time

            # Save thread store after each interaction
            save_thread_store(thread_store)

            return render_template('chat.html', 
                                 chat_history=thread_data['chat_history'])
        except Exception as e:
            return render_template('chat.html', 
                                 chat_history=[f"An error occurred: {str(e)}"])
    else:
        # Handle GET requests
        return render_template('chat.html', 
                             chat_history=thread_data['chat_history'])

@app.route('/deleteNotes', methods=['GET', 'POST'])
def deleteNotesPage():
    if request.method == 'POST':
        note_ids = request.form.getlist('note_ids')
        note_ids = [int(id) for id in note_ids]
        deleteNotesFromDatabase(note_ids,index,TEXT_DATABASE_PATH,INDEX_DATABASE_PATH)
        return redirect(url_for('deleteNotesPage'))
    
    notes = getAllNotes(TEXT_DATABASE_PATH)
    return render_template('deleteNotes.html', notes=notes)

# Utility routes for debugging and maintenance
@app.route('/debug-session')
def debug_session():
    """Debug route to check session information"""
    return {
        'session_id': session.get('session_id'),
        'session_data': dict(session),
        'thread_store_keys': list(thread_store.keys()) if thread_store else [],
        'cookies': dict(request.cookies),
        'thread_store_count': len(thread_store) if thread_store else 0
    }

@app.route('/clear-session')
def clear_session():
    """Utility route to clear session cookies - remove in production"""
    session.clear()
    response = redirect(url_for('chat'))
    # Clear any old cookies that might be causing conflicts
    response.set_cookie('session', '', expires=0)
    response.set_cookie('trident_session', '', expires=0)
    return response

@app.teardown_appcontext
def save_on_shutdown(exception=None):
    """Save the thread store when the application shuts down."""
    save_thread_store(thread_store)

if __name__ == '__main__':
    # Ensure the thread store is loaded when the app starts
    thread_store = load_thread_store()
    app.run(host='0.0.0.0', port=443, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem',
                                                   '/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))