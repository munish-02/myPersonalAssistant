import pickle
import os
import faiss
THREAD_STORE_FILE = 'thread_store.pkl'
def load_thread_store():
    """Load thread_store from the pickle file if it exists."""
    if os.path.exists(THREAD_STORE_FILE):
        with open(THREAD_STORE_FILE, 'rb') as f:
            return pickle.load(f)
    return {}

def save_thread_store(thread_store):
    """Save thread_store to a pickle file."""
    with open(THREAD_STORE_FILE, 'wb') as f:
        pickle.dump(thread_store, f)

def returnVectorDatabase(databaseName):
    return faiss.read_index(databaseName)

def saveVectorDatabase(index,databaseName):
    faiss.write_index(index,databaseName)

def createNewIndexDatabase():
    return faiss.IndexFlatL2(1536)