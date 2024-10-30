import socket
import json
import threading

# Configuration
HOST = '127.0.0.1'
PORT = 8571
WORKER_NODES = [('127.0.0.1', 10002), ('127.0.0.1', 10001)]


# def gather_tweets_from_workers():
#     responses = broadcast_to_workers({'phase': 'get_tweets','transaction':{'action': 'get_tweets'}}, 'get_tweets')
#     tweets = [tweet for worker_response in responses for tweet in worker_response.get('tweets', [])]
#     return tweets
# Helper function to send transaction to all worker nodes and collect votes or statuses
def broadcast_to_workers(transaction, phase):
    global WORKER_NODES
    responses = []

    # For read-only operations like 'get_tweets', we can just query one worker
    if phase == 'get_tweets':
        # Pick the first worker for simplicity; you might use a load-balancing strategy here
        node = WORKER_NODES[0]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(node)
            sock.sendall(json.dumps(transaction).encode('utf-8'))
            response_data = sock.recv(1024).decode('utf-8')
            response = json.loads(response_data)
            print(f"Received response from worker: {response}")  # For debugging
            if response.get('status') == 'OK':
                # Directly return the tweets from the first worker
                return response.get('tweets', [])
            else:
                print(f"Error getting tweets from worker: {node}")
                return []
    else:
        # For all other operations, broadcast to all workers
        for node in WORKER_NODES:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(node)
                sock.sendall(json.dumps(transaction).encode('utf-8'))
                response_data = sock.recv(1024).decode('utf-8')
                response = json.loads(response_data)
                print(f"Received response from worker: {response}")  # For debugging
                if phase == 'prepare':
                    responses.append(response.get('vote'))
                else:  # commit or abort
                    responses.append(response.get('status'))
    
    return responses



# Function to handle client connections
def handle_client_connection(client_socket):
    try:
        data = client_socket.recv(1024).decode('utf-8')
        transaction = json.loads(data)
        print(transaction)

        if transaction.get('action') == 'get_tweets':
            # Handle 'get_tweets' action differently than other transactions
            #tweets = gather_tweets_from_workers()
            tweets = broadcast_to_workers({'phase': 'get_tweets', 'transaction': transaction}, 'get_tweets')
            client_socket.sendall(json.dumps({'status': 'OK', 'tweets': tweets}).encode('utf-8'))
        else:
            # Existing logic for other transaction types
            # Phase 1: Voting
            votes = broadcast_to_workers({'phase': 'prepare', 'transaction': transaction}, 'prepare')
            print(f"Received votes: {votes}")

            # Check votes from workers
            if all(vote == 'commit' for vote in votes):
                # Phase 2: Commit
                statuses = broadcast_to_workers({'phase': 'commit', 'transaction': transaction}, 'commit')
                print(f"Received commit statuses: {statuses}")
                if all(status == 'committed' for status in statuses):
                    client_socket.sendall(json.dumps({'status': 'OK'}).encode('utf-8'))
                else:
                    client_socket.sendall(json.dumps({'status': 'ERROR'}).encode('utf-8'))
            else:
                # Phase 2: Abort
                broadcast_to_workers({'phase': 'abort', 'transaction': transaction}, 'abort')
                client_socket.sendall(json.dumps({'status': 'ABORT'}).encode('utf-8'))

    except Exception as e:
        print(f"Error: {e}")
        client_socket.sendall(json.dumps({'status': 'ERROR'}).encode('utf-8'))
    finally:
        client_socket.close()



# Start coordinator server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Coordinator listening on {HOST}:{PORT}")

while True:
    client_sock, addr = server_socket.accept()
    thread = threading.Thread(target=handle_client_connection, args=(client_sock,))
    thread.start()
