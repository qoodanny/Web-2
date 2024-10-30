import socket
import threading
import json
import uuid
import http.cookies as Cookie

HOST = '127.0.0.1'
PORT = 8570
WEBROOT = "client"
# In-memory storage for tweets (using a list for simplicity)
tweets = []

# In-memory 'database' for storing usernames associated with session IDs
sessions = {}

def handle_client_connection(client_socket):
    try:
        request = client_socket.recv(1024).decode()
        headers, body = request.split('\r\n\r\n', 1)
        header_lines = headers.split('\r\n')
        method, path, _ = header_lines[0].split()

        # Determine the route
        if method == 'GET' and path == '/':
            # Serve the index.html file
            serve_file(client_socket, WEBROOT+'/index.html')
        elif path.startswith('/api/'):
            # Handle API requests
            if method == 'POST' and path == '/api/login':
                handle_login(client_socket, body)
            elif method == 'GET' and path == '/api/tweet':
                handle_get_tweets(client_socket)
            elif method == 'POST' and path == '/api/tweet':
                handle_post_tweet(client_socket, body)
            elif path.startswith('/api/tweet/') and method == 'PUT':
                tweet_id = path.split('/')[-1]
                handle_put_tweet(client_socket, tweet_id, body)
            elif method == 'DELETE' and path.startswith('/api/tweet/'):
                tweet_id = path.split('/')[-1]
                handle_delete_tweet(client_socket, tweet_id)
            elif method == 'DELETE' and path == '/api/login':
                handle_logout(client_socket)
            else:
                # Return 404 Not Found for unrecognized paths
                send_response(client_socket, '404 Not Found', 'Path not found.')
        else:
            # Return 404 Not Found for unrecognized paths
            send_response(client_socket, '404 Not Found', 'Path not found.')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        
def handle_logout(client_socket):
    # Here you would invalidate the session or cookie
    
    send_response(client_socket, '200 OK', 'Logged out successfully')
def serve_file(client_socket, file_name):
    try:
        with open(file_name, 'rb') as file:
            content = file.read()
        send_response(client_socket, '200 OK', content, content_type='text/html')
    except FileNotFoundError:
        send_response(client_socket, '404 Not Found', 'File not found.')
def handle_delete_tweet(client_socket, tweet_id):
    global tweets  # Reference the global tweets variable
    # Assuming tweets is a list of dictionaries with 'id' as one of the keys
    tweets = [tweet for tweet in tweets if tweet['id'] != tweet_id]
    send_response(client_socket, '200 OK', 'Tweet deleted successfully')

def handle_login(client_socket, body):
    # Create a new session ID
    #session_id = str(uuid.uuid4())
    # Parse the JSON body to get the username
    #data = json.loads(body)
    #username = data.get('username')
    send_response(client_socket, '200 OK', 'Logged in successfully.')

def handle_get_tweets(client_socket):
    # Convert the tweets to JSON
    tweets_json = json.dumps(tweets)
    send_response(client_socket, '200 OK', tweets_json, content_type='application/json')

def handle_post_tweet(client_socket, body):
    # Parse the JSON body to get the tweet content and username
    data = json.loads(body)
    username = data.get('username')
    content = data.get('content')
    # Create a new tweet with a unique ID
    tweet = {'id': str(uuid.uuid4()), 'username': username, 'content': content}
    # Add the new tweet to the list
    tweets.append(tweet)
    send_response(client_socket, '200 OK', 'Tweet posted successfully.')

def handle_put_tweet(client_socket, tweet_id, body):
    # Find the tweet by ID
    for tweet in tweets:
        if tweet['id'] == tweet_id:
            # Update the tweet's content
            data = json.loads(body)
            tweet['content'] = data['content']
            send_response(client_socket, '200 OK', 'Tweet updated successfully.')
            return
    # If not found, return 404
    send_response(client_socket, '404 Not Found', 'Tweet not found.')

def send_response(client_socket, status_code, body, headers=None, content_type='text/plain'):
    response = f'HTTP/1.1 {status_code}\r\n'
    if headers:
        for header, value in headers.items():
            response += f'{header}: {value}\r\n'
    response += f'Content-Type: {content_type}\r\n'
    response += f'Content-Length: {len(body)}\r\n'
    response += 'Connection: close\r\n\r\n'
    response += body if isinstance(body, str) else body.decode('utf-8')
    client_socket.sendall(response.encode())

# Start the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f'Server listening on {HOST}:{PORT}')

while True:
    client_sock, address = server_socket.accept()
    print(f'Accepted connection from {address[0]}:{address[1]}')
    client_handler = threading.Thread(
        target=handle_client_connection,
        args=(client_sock,)
    )
    client_handler.start()
