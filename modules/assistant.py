import openai
import time
from modules.config import OPENAI_API_KEY
from modules.run import create_run
from modules.fileManagement import save_thread_store, saveVectorDatabase
import faiss
import numpy as np
import sqlite3
import json



# Initialize OpenAI client
openai.api_key = OPENAI_API_KEY

def create_assistant():
    return openai.beta.assistants.retrieve("asst_fCJHgmM09VKGs9lRbxXdybes")

def get_assistant_response(thread, assistant, user_input,index,TEXT_DATABASE_PATH,INDEX_DATABASE_PATH):
    try:
        # Add user message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Create a run to process the assistant's response
        run = create_run(thread, assistant)

        # Wait for the run to complete
        while run.status != 'completed':
            time.sleep(0.1)
            if(run.status=='requires_action'):
                tool_outputs = []
                if(run.required_action.type=='submit_tool_outputs'):
                    for i in run.required_action.submit_tool_outputs.tool_calls:
                        if(i.function.name=="addNotesToDatabase"):
                            data = json.loads(i.function.arguments)
                            input_notes = data.get("inputNotes", "")
                            status=addNotesToDatabase(input_notes,index,TEXT_DATABASE_PATH,INDEX_DATABASE_PATH)
                            tool_outputs.append({"tool_call_id":i.id,"output":str(status)})
                        elif(i.function.name=="getRelaventInfoFromDatabase"):
                            data = json.loads(i.function.arguments)
                            input_notes = data.get("searchString", "")
                            relaventNotes=getRelaventInfoFromDatabase(input_notes,index,TEXT_DATABASE_PATH,10)
                            tool_outputs.append({"tool_call_id":i.id,"output":str(relaventNotes)})

                    openai.beta.threads.runs.submit_tool_outputs(run.id,thread_id=thread.id,tool_outputs=tool_outputs)

            run = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        # Retrieve the latest assistant message
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in messages.data:  # Reverse iterate to find the latest assistant message
            if msg.role == 'assistant':
                return "\n".join([block.text.value for block in msg.content])
    except Exception as e:
        return f"Error: {str(e)}"
    
def getEmbeddings(inputForEmbedding):
    response= openai.embeddings.create(
        input=inputForEmbedding,
        model="text-embedding-3-small"
    )
    return np.array(response.data[0].embedding)

def getRelaventInfoFromDatabase(query,index,TEXT_DATABASE_PATH,numberOfRelaventEntries=10):
    conn=sqlite3.connect(TEXT_DATABASE_PATH)
    relaventInfo=[]
    indices=findSimilarities(query,index,numberOfRelaventEntries)
    cursor=conn.cursor()
    for i in indices[0]:
        index_value = int(i)
        if(index_value>-1):
            cursor.execute("SELECT * FROM my_table LIMIT 1 OFFSET ?", (index_value,))
            row = cursor.fetchone()
            relaventInfo.append(row[1])

    conn.close()
    return " ".join(relaventInfo)




from datetime import datetime

def addNotesToDatabase(input, indexDb, TEXT_DATABASE_PATH, INDEX_DATABASE_PATH):
    try:
        # Get the current date and time
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append the date and time to the input string
        input_with_date = f"{input} Today's date: {current_datetime}"
        
        # Connect to the text database
        conn = sqlite3.connect(TEXT_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO my_table (string) VALUES (?)", (input_with_date,))
        conn.commit()
        
        # Get embeddings and add to the index database
        embedding = getEmbeddings(input_with_date)
        embedding = embedding.reshape(1, -1)
        indexDb.add(np.array(embedding))
        
        # Close the connection and save the vector database
        conn.close()
        saveVectorDatabase(indexDb, INDEX_DATABASE_PATH)
        
        return "success"
    except Exception as e:
        return {"status": "error", "message": str(e)}


    




def findSimilarities(query,index, nTopQueries):
    queryEmbedding=getEmbeddings(query)
    queryEmbedding = queryEmbedding.reshape(1, -1)
    distances,indices=index.search(queryEmbedding,nTopQueries)
    return indices

