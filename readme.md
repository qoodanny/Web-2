# 2PC Tweet Database

This project implements a simple tweet storage system using the Two-Phase Commit (2PC) protocol to ensure consistency across multiple worker nodes. It includes a coordinator node that manages the transaction processes and worker nodes that store the tweet data.

## Getting Started

These instructions will get your copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

You need Python 3.9 or higher installed on your machine to run this project.

### Installing

To get the project running, follow these steps:

1. There is no need to install dependencies as the project uses the Python standard library.

## Running the Code

### Frontend Server
To start the frondend web server (root directory):
```bash
python server_part2/server.py
```

### Coordinator Node
To start the coordinator node:
```bash
python server_part2/coordinator.py
```
### Worker Nodes
```bash
python server_part2/worker.py 10001
python server_part2/worker.py 10002
```

### Oddities and Notes
1. Ensure that you start the coordinator before the workers.
2. The system does not currently handle network partitions or worker crashes.

## Communicating with the Database
To test the database independently, you can interact with the coordinator using any TCP client (e.g., telnet, nc, or a custom Python script). The coordinator expects JSON-formatted messages. Here are some examples of how to interact with the database:

### Posting a Tweet
```json
{
  "action": "post",
  "tweet": {
    "id": "<unique_tweet_id>",
    "username": "<user>",
    "content": "<message content>"
  }
}
```

### Updating a Tweet
```json
{
  "action": "update",
  "tweet": {
    "id": "<unique_tweet_id>",
    "content": "<new message content>"
  }
}
```

### Deleting a Tweet
```json
{
  "action": "delete",
  "tweet": {
    "id": "<unique_tweet_id>"
  }
}
```

### Retrieving All Tweets
```json
{
  "action": "get_tweets"
}
```

## Data Locking and Concurrency Control

To maintain data consistency during concurrent transactions, the workers utilize a simple locking mechanism. Here's how it works:

### Lock Mechanism

- When a transaction begins, if it intends to modify data (via post, update, or delete actions), the worker places a lock on the specific data item.
- If another transaction tries to modify the same data item while it's locked, the action will fail with an appropriate error message indicating that the item is currently being modified.
- The lock is released when the transaction is either committed or aborted.

### Timeout and Deadlock Prevention

- Each lock has a timeout mechanism to prevent deadlocks. If a transaction does not complete (commit or abort) within a predetermined timeframe, the lock is automatically released to allow other transactions to proceed.
- In the current implementation, the timeout is set to `X` seconds (you should specify the exact timeout used in your implementation).

### Testing Locks

To test the lock mechanism, you can try to perform concurrent transactions on the same data item using separate TCP client sessions. Here's an example sequence to illustrate:

1. Start a `post` or `update` transaction on one client session.
2. Before completing the first transaction, attempt to start a new `post` or `update` transaction on the same data item in a different client session.
3. Observe that the second transaction fails with an error message about the data item being locked.

## Bonus Tasks Completion

### Implemented Bonus Features
- DELETE /api/tweet/[tweet-id] - Delete tweet tweet-id
- DELETE /api/login - Log out of the system (return the user to the login page)
