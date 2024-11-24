from flask import Flask, request, render_template
import time

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        try:
            # Get the user's message from the form
            user_message = request.form.get('user_message', type=str)
            if not user_message:
                return render_template('chat.html', chat_history=["Please enter a message."])
            
            # Process the user's message (you can replace this logic with any AI or chatbot logic)
            bot_response = f"Echo: {user_message}"
            
            # Load chat history from the form data (for multi-turn chat)
            chat_history = request.form.getlist('chat_history')
            chat_history.append(f"You: {user_message}")
            chat_history.append(f"Bot: {bot_response}")
            
            return render_template('chat.html', chat_history=chat_history)
        except Exception as e:
            return render_template('chat.html', chat_history=[f"An error occurred: {str(e)}"])
    else:
        # Render the initial empty chat interface
        return render_template('chat.html', chat_history=[])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem','/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))
