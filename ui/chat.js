let socket = null;
const userAuthSection = document.getElementById('user-auth');
const chatInterface = document.getElementById('chat-interface');

document.getElementById('start-btn').addEventListener('click', function() {
    startSession();
});

function startSession() {
    const userId = document.getElementById('user-id').value.trim();

    if (!userId) {
        showNotification("Please enter a User ID.", "error");
        return;
    }

    // Show loading state
    const startBtn = document.getElementById('start-btn');
    const originalBtnText = startBtn.innerHTML;
    startBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Connecting...</span>';
    startBtn.disabled = true;

    fetch('/start_session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        // Reset button state
        startBtn.innerHTML = originalBtnText;
        startBtn.disabled = false;

        if (data.error) {
            showNotification(data.error, "error");
            return;
        }

        const threadId = data.thread_id;
        document.getElementById('thread-id-display').innerText = `Thread ID: ${threadId}`;

        // Switch from auth to chat interface
        userAuthSection.classList.add('hidden');
        chatInterface.classList.remove('hidden');

        startChatSession(threadId, userId);
    })
    .catch(error => {
        console.error("Error starting session:", error);
        startBtn.innerHTML = originalBtnText;
        startBtn.disabled = false;
        showNotification("Failed to connect to server. Please try again.", "error");
    });
}

function startChatSession(threadId, userId) {
    socket = io();

    socket.on('connect', function() {
        socket.emit('join', { thread_id: threadId });

        updateStatus("Connected", "success");
        document.getElementById('message-input').disabled = false;
        document.getElementById('send-btn').disabled = false;

        // Add welcome message
        addSystemMessage("Connected to Sakha. Start chatting!");
    });

    socket.on('disconnect', function() {
        updateStatus("Disconnected", "secondary");
        disableChat();
    });

    socket.on('connect_error', function() {
        updateStatus("Connection error", "danger");
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

    // Focus the input field
    document.getElementById('message-input').focus();
}

function sendMessage(threadId, userId) {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (message && socket) {
        addUserMessage(message);

        // Show typing indicator
        addTypingIndicator();

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
    scrollToBottom();
}

function addBotMessage(text) {
    // Remove typing indicator if exists
    removeTypingIndicator();

    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-bot';
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    scrollToBottom();
}

function addSystemMessage(text) {
    const chatBox = document.getElementById('chat-box');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message-system';
    messageDiv.innerText = text;
    chatBox.appendChild(messageDiv);
    scrollToBottom();
}

function addTypingIndicator() {
    removeTypingIndicator();

    const chatBox = document.getElementById('chat-box');
    const indicator = document.createElement('div');
    indicator.className = 'message-bot typing-indicator';
    indicator.innerHTML = '<span>.</span><span>.</span><span>.</span>';
    chatBox.appendChild(indicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    const typingIndicator = document.querySelector('.typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function updateStatus(message, statusClass) {
    const statusIndicator = document.getElementById('status-indicator');
    statusIndicator.className = `status-${statusClass}`;
    statusIndicator.querySelector('.status-text').innerText = message;
}

function disableChat() {
    const messageInput = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    messageInput.disabled = true;
    sendBtn.disabled = true;

    addSystemMessage("Connection lost. Please refresh the page to reconnect.");
}

function scrollToBottom() {
    const chatBox = document.getElementById('chat-box');
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showNotification(message, type) {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Add this to the end of your CSS file
document.head.insertAdjacentHTML('beforeend', `
<style>
.typing-indicator {
    display: flex;
    align-items: center;
    padding: 10px 16px;
    min-width: 60px;
}

.typing-indicator span {
    height: 8px;
    width: 8px;
    background-color: var(--text-secondary);
    border-radius: 50%;
    display: inline-block;
    margin: 0 3px;
    opacity: 0.4;
    animation: typing-dot 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
    animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing-dot {
    0%, 60%, 100% {
        transform: translateY(0);
        opacity: 0.4;
    }
    30% {
        transform: translateY(-5px);
        opacity: 1;
    }
}

.notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-20px);
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 1000;
}

.notification.show {
    transform: translateY(0);
    opacity: 1;
}

.notification.error {
    border-left: 4px solid #ef4444;
}

.notification.success {
    border-left: 4px solid #10b981;
}

.notification-content {
    display: flex;
    align-items: center;
    gap: 10px;
}

.notification-content i {
    font-size: 1.2rem;
}

.notification.error i {
    color: #ef4444;
}

.notification.success i {
    color: #10b981;
}
</style>
`);