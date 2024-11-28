from flask import Flask, request, render_template, session
from modules.assistant import create_assistant, get_assistant_response
from modules.thread import create_thread
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')  # Use environment variable for better security

# Initialize assistant and thread globally
assistant = create_assistant()
thread = create_thread()

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
            bot_response = get_assistant_response(thread, assistant, user_message)

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
