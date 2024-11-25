from flask import Flask, request, render_template
import time

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', result=None, text_output=None)

@app.route('/square', methods=['POST'])
def square():
    try:
        # Get the number from the form input
        number = request.form.get('number', type=float)
        if number is None:
            return "Please provide a number.", 400
        
        # Calculate the square of the number
        result = number ** 2
        return render_template('index.html', result=result, text_output=None)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.route('/submit_text', methods=['POST'])
def submit_text():
    try:
        # Get the text input from the form
        text_input = request.form.get('text_input', type=str)
        if text_input is None:
            return "Please provide some text.", 400

        # Print the text to the terminal
        print(text_input)

        return render_template('index.html', result=None, text_output=text_input)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

@app.errorhandler(400)
def bad_request(error):
    return "Bad request. Please check your request format.", 400

@app.errorhandler(Exception)
def handle_exception(e):
    return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, ssl_context=('/etc/letsencrypt/live/www.ainythink.com/fullchain.pem','/etc/letsencrypt/live/www.ainythink.com/privkey.pem'))
