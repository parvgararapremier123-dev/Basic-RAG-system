// --- ELEMENTS ---
const chatFeed = document.getElementById('chat-feed');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const uploadBtn = document.getElementById('upload-btn');
const toggleSidebar = document.getElementById('toggle-sidebar');
const sidebar = document.getElementById('sidebar');
const themeSwitch = document.getElementById('theme-switch');
const thinkingIndicator = document.getElementById('thinking-indicator');
const statusText = document.getElementById('status-text');
const statusDot = document.getElementById('status-dot');
const docList = document.getElementById('doc-list');

let currentAiBubble = null;

// --- EEL CALLBACKS (Python to JS) ---

eel.expose(updateStatus);
function updateStatus(status) {
    statusText.innerText = status;
    if (status === "Ready") {
        statusDot.className = "status-ready";
    } else {
        statusDot.className = "status-idle";
    }
}

eel.expose(addDocumentToList);
function addDocumentToList(filename) {
    const li = document.createElement('li');
    li.innerText = `• ${filename}`;
    docList.appendChild(li);
}

eel.expose(streamResponse);
function streamResponse(content) {
    // IMMEDIATELY hide indicator on first callback
    thinkingIndicator.classList.add('hidden');
    
    if (!currentAiBubble) {
        currentAiBubble = createBubble('ai', '');
    }
    
    if (content) {
        currentAiBubble.innerText += content;
        scrollToBottom();
    }
}

eel.expose(finishResponse);
function finishResponse() {
    currentAiBubble = null;
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
    thinkingIndicator.classList.add('hidden'); // Safety check
}

// --- UI LOGIC ---

function createBubble(sender, text) {
    // Remove welcome message on first interaction
    const welcome = document.querySelector('.welcome-msg');
    if (welcome) welcome.remove();

    const bubble = document.createElement('div');
    bubble.className = `bubble ${sender}-bubble`;
    bubble.innerText = text;
    chatFeed.appendChild(bubble);
    scrollToBottom();
    return bubble;
}

function scrollToBottom() {
    chatFeed.scrollTop = chatFeed.scrollHeight;
}

function handleSend() {
    const text = userInput.value.trim();
    if (!text || userInput.disabled) return;

    // UI Updates
    createBubble('user', text);
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;
    currentAiBubble = null;
    
    // Show thinking animation
    thinkingIndicator.classList.remove('hidden');
    
    // Call Python
    eel.ask_ai(text);
}

// --- EVENT LISTENERS ---

sendBtn.addEventListener('click', handleSend);

uploadBtn.addEventListener('click', () => {
    eel.upload_pdf();
});

userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
});

toggleSidebar.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

themeSwitch.addEventListener('change', (e) => {
    const theme = e.target.checked ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', theme);
});

document.getElementById('clear-chat').addEventListener('click', () => {
    chatFeed.innerHTML = `
        <div class="welcome-msg">
            <h2>Welcome to Hub</h2>
            <p>Upload a PDF to start analyzing document intelligence.</p>
        </div>
    `;
    currentAiBubble = null;
});

// Initialize
window.addEventListener('DOMContentLoaded', () => {
    userInput.focus();
});