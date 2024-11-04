from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Munish is the best!"

@app.errorhandler(400)
def bad_request(error):
    return "Bad request. Please check your request format.", 400

@app.errorhandler(Exception)
def handle_exception(e):
    # You can log the error here if needed
    return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
