import openai

def create_thread():
    return openai.beta.threads.create()
