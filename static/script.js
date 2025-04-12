function sendMessage() {
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;

    addMessage(text, 'user');

    // Fake bot reply for demo
    setTimeout(() => {
      addMessage("You said: " + text, 'bot');
    }, 500);

    input.value = '';
  }

  function addMessage(text, sender) {
    const container = document.getElementById('chatContainer');
    const msg = document.createElement('div');
    msg.className = 'message ' + sender;
    msg.textContent = text;
    container.appendChild(msg);
    container.scrollTop = container.scrollHeight;
  }