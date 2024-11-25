from flask import Flask, request, render_template, session
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

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
            
            # Process the user's message (you can replace this with AI or chatbot logic)
            bot_response = f"Echo: {user_message}"
            
            # Append user and bot messages to chat history
            session['chat_history'].append(f"You: {user_message}")
            session['chat_history'].append(f"Bot: {bot_response}")
            
            return render_template('chat.html', chat_history=session['chat_history'])
        except Exception as e:
            return render_template('chat.html', chat_history=[f"An error occurred: {str(e)}"])
    else:
        return render_template('chat.html', chat_history=session['chat_history'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem','/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))
