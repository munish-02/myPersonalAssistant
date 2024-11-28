import openai

def create_run(thread, assistant):
    return openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
