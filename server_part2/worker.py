import socket
import json
import sys
import threading

# Configuration for this worker node
HOST = '127.0.0.1'
PORT = int(sys.argv[1])  # Change for each worker
DATA = []  # Local storage for the worker node
LOCKED_TWEETS = {}  # Keeps track of locked tweets
LOCK_TIMEOUT = 10  # Lock timeout in seconds

# Function to handle transactions
def handle_transaction(data):
    global DATA, LOCKED_TWEETS
    phase = data.get('phase')
    transaction = data.get('transaction')
    tweet_id = transaction.get('tweet', {}).get('id') if transaction else None
    
    if phase == 'prepare':
        # Check if the tweet is already locked
        if tweet_id in LOCKED_TWEETS:
            return {'vote': 'abort', 'reason': 'Tweet is locked'}
        # Lock the tweet
        LOCKED_TWEETS[tweet_id] = True
        # Start a timer to unlock the tweet after a timeout
        threading.Timer(LOCK_TIMEOUT, unlock_tweet, args=(tweet_id,)).start()
        return {'vote': 'commit'}

    elif phase == 'commit':
        # Check if the tweet is locked by this transaction
        if tweet_id not in LOCKED_TWEETS:
            return {'status': 'abort', 'reason': 'No lock on tweet'}
        # Apply the transaction
        if transaction['action'] == 'post':
            DATA.append(transaction['tweet'])
        elif transaction['action'] == 'update':
            for tweet in DATA:
                if tweet['id'] == tweet_id:
                    tweet['content'] = transaction['tweet']['content']
                    tweet['username'] = transaction['tweet']['username']
                    break
        elif transaction['action'] == 'delete':
            DATA = [tweet for tweet in DATA if tweet['id'] != tweet_id]
        # Unlock the tweet
        unlock_tweet(tweet_id)
        return {'status': 'committed'}

    elif phase == 'abort':
        # Unlock the tweet if it was locked
        unlock_tweet(tweet_id)
        return {'status': 'aborted'}
    
    elif phase == 'get_tweets':
        # Return the current state of DATA without changing any locks
        return {'status': 'OK', 'tweets': DATA}

def unlock_tweet(tweet_id):
    """Unlock a tweet."""
    LOCKED_TWEETS.pop(tweet_id, None)

# Start worker server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Worker listening on {HOST}:{PORT}")

while True:
    client_sock, addr = server_socket.accept()
    try:
        data = client_sock.recv(1024).decode('utf-8')
        transaction_data = json.loads(data)
        response = handle_transaction(transaction_data)
        print(f"Sending response to coordinator: {response}")
        client_sock.sendall(json.dumps(response).encode('utf-8'))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_sock.close()
