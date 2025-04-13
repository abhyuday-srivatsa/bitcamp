document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("avoid").addEventListener("change", function() {
      if (this.checked) {
        document.getElementById("include").checked = false;
      }
    });
  
    document.getElementById("include").addEventListener("change", function() {
      if (this.checked) {
        document.getElementById("avoid").checked = false;
      }
    });
  });

window.addEventListener('load', () => {
  logo = document.body.querySelector('#logo')
  container = document.body.querySelector('#chatContainer');
  userMsgs = document.body.querySelector('#user-messages');
  botMsgs = document.body.querySelector('#bot-messages');
  chatInput = document.body.querySelector('#chatInput');

  const filePassed = localStorage.getItem("filePassed") === "true";
  console.log(filePassed)
  if (filePassed){
    var text = "Thank you for uploading your degree audit. Please enter any time restrictions or any other information you would like me to know before I suggest courses."
  setTimeout(() => {
    addMessage(text, 'bot');
  }, 500);
  }

});

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
    chatInput.value = '';
    if (text == "final"){
      setTimeout(() => {
        addMessage("Preparing your Cinder experience", 'bot');
      }, 1000);
      fetch('/final_agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: text })
      })
      .then(response => response.json())
      .then(data => {
        const botResponse = data.response;
        const regex = /[\d]+\..+([A-Z]{4}[0-9]{3})/g;
        const matches = [];
        let match;

        while ((match = regex.exec(botResponse)) !== null) {
          matches.push(match[1]);
        }

        localStorage.setItem('matches', JSON.stringify(matches));
        window.location.href = '/tinder';
        
      }).catch(error => {
        console.error('Error calling Flask:', error);
        addMessage("Sorry, something went wrong.", 'bot');
      });

    } else{
      fetch('/ask_agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ input: text })
      }).catch(error => {
        console.error('Error calling Flask:', error);
        addMessage("Sorry, something went wrong.", 'bot');
      });
  
      setTimeout(() => {
        addMessage("Got it! Thanks for the update.", 'bot');
      }, 1000);
    }

    
}

let logo, container, userMsgs, botMsgs, chatInput;

window.addEventListener('keydown', (evt) => {
    const key = evt.which || evt.keyCode || 0;
    if (key == 13 && chatInput === document.activeElement) {
    setTimeout(sendMessage, 100)
    }
})

function addMessage(text, sender) {
    container = document.body.querySelector('#chatContainer');
    const messageClass = 'message ' + sender;
    const messageContent = sender === 'bot'
    ? b('div', { class: messageClass }, b('span', { text }))
    : b('div', { class: messageClass }, b('span', { text }));

    const row = b('div', { class: 'text_row ' + sender }, messageContent);
    container.appendChild(row);
    container.scrollTop = container.scrollHeight;
}

  function save_times(){
    // Get weekdays
    const weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
      .filter(id => document.getElementById(id).checked)
      .join(', ');
  
    // Get preferences
    const preferences = ['avoid', 'include']
      .filter(id => document.getElementById(id).checked)
      .join(', ');
  
    // Get time inputs
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;
  
    let summary = ""
    // Create summary string
    if (preferences == 'avoid'){
      summary = `DO NOT schedule classes on ${weekdays} from ${startTime} to ${endTime}`
    } else {
      summary = `You CAN schedule classes on ${weekdays} from ${startTime} to ${endTime}`
    }
  
    textbox = document.getElementById("chatInput")
    textbox.value = summary
  }