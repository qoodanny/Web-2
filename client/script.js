function postTweet() {
    const username = document.getElementById('username').value;
    const content = document.getElementById('new-post').value;

    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/api/tweet", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
            // Success logic here
        }
    }
    xhr.send(JSON.stringify({ username, content }));
}
