function b(
  type,
  attributes,
  ...children
) {
  let element = document.createElement(type);

  if (attributes && typeof attributes == "string") {
    element.textContent = attributes;
  } else if (attributes && typeof attributes == "object" && attributes.text) {
    element.textContent = attributes.text;
  }

  if (typeof attributes == "object" && attributes != null) {
    Object.keys(attributes).forEach(item => {
      if (item == "text") return;
      if (element.hasAttribute(item) || item in element) {
        element.setAttribute(item, attributes[item]);
      } else if (item == "class") {
        element.classList.add(...(attributes[item]).split(" "));
      } else if (item.startsWith("data") && attributes) {
        element.dataset[item.slice(5)] = attributes[item];
      }
    });
  }

  if (children.length >= 1) children.forEach((i) => element.appendChild(i))

  return element;
}

function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  addMessage(text, 'user');

  // Fake bot reply for demo
  setTimeout(() => {
    addMessage(text, 'bot');
  }, 1000);

  chatInput.value = '';
}

let logo, container, userMsgs, botMsgs, chatInput;

window.addEventListener('load', () => {
  logo = document.body.querySelector('#logo')
  container = document.body.querySelector('#chatContainer');
  userMsgs = document.body.querySelector('#user-messages');
  botMsgs = document.body.querySelector('#bot-messages');
  chatInput = document.body.querySelector('#chatInput');
})

window.addEventListener('keydown', (evt) => {
  const key = evt.which || evt.keyCode || 0;
  if (key == 13 && chatInput === document.activeElement) {
    setTimeout(sendMessage, 100)
  }
})

function addMessage(text, sender) {
  const messageClass = 'message ' + sender;
  const messageContent = sender === 'bot'
    ? b('div', { class: messageClass }, logo.cloneNode(true), b('span', { text }))
    : b('div', { class: messageClass }, b('span', { text }));

  const row = b('div', { class: 'text_row ' + sender }, messageContent);
  container.appendChild(row);
  container.scrollTop = container.scrollHeight;
}

