let socket = null;

document.getElementById('start-btn').addEventListener('click', function() {
    startSession();
});


function startSession() {
    const userId = document.getElementById('user-id').value.trim();

    if (!userId) {
        alert("Please enter a User ID.");
        return;
    }

    fetch('/start_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }

        const threadId = data.thread_id;
        document.getElementById('thread-id-display').innerText = `Thread ID: ${threadId}`;
        startChatSession(threadId, userId);
    })
    .catch(error => console.error("Error starting session:", error));
}

function startChatSession(threadId, userId) {
    socket = io();

    socket.on('connect', function() {
        socket.emit('join', { thread_id: threadId });

        updateStatus("Connected to chat server", "success");
        document.getElementById('message-input').disabled = false;
        document.getElementById('send-btn').disabled = false;
    });

    socket.on('disconnect', function() {
        updateStatus("Disconnected from server", "secondary");
        disableChat();
    });

    socket.on('connect_error', function() {
        updateStatus("Failed to connect to server", "danger");
        disableChat();
    });

    socket.on('bot_message', function(data) {
        addBotMessage(data.text);
    });

    socket.on('system_message', function(data) {
        addSystemMessage(data.text);
    });

    document.getElementById('send-btn').addEventListener('click', function() {
        sendMessage(threadId, userId);
    });

    document.getElementById('message-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage(threadId, userId);
        }
    });
}

function sendMessage(threadId, userId) {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (message && socket) {
        addUserMessage(message);
        socket.emit('user_message', { thread_id: threadId, user_id: userId, text: message });
        input.value = '';
    }
}

function addUserMessage(text) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-user';
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addBotMessage(text) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-bot';
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function addSystemMessage(text) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-system';
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function updateStatus(message, statusClass) {
    const statusIndicator = document.getElementById('status-indicator');
    statusIndicator.className = `alert alert-${statusClass}`;
    statusIndicator.innerText = message;
}

function disableChat() {
    document.getElementById('message-input').disabled = true;
    document.getElementById('send-btn').disabled = true;
}
