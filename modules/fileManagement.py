import pickle
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