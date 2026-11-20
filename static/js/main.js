// AgriPulse AI - Client Application Logic

document.addEventListener('DOMContentLoaded', function () {
  // 1. Sync Range Sliders and Number Inputs
  const sliders = document.querySelectorAll('.range-slider');
  sliders.forEach(slider => {
    const targetId = slider.getAttribute('data-target');
    const numberInput = document.getElementById(targetId);
    if (numberInput) {
      slider.addEventListener('input', (e) => {
        numberInput.value = e.target.value;
      });
      numberInput.addEventListener('input', (e) => {
        slider.value = e.target.value;
      });
    }
  });

  // 2. Drag & Drop File Upload with Preview
  const dropzone = document.getElementById('uploadDropzone');
  const fileInput = document.getElementById('leafImageInput');
  const previewImg = document.getElementById('imagePreview');
  const previewText = document.getElementById('previewFilename');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelect(fileInput.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
      }
    });
  }

  function handleFileSelect(file) {
    if (!file) return;
    if (previewText) previewText.innerText = file.name;
    const reader = new FileReader();
    reader.onload = function (e) {
      if (previewImg) {
        previewImg.src = e.target.result;
        previewImg.style.display = 'block';
      }
    };
    reader.readAsDataURL(file);
  }

  // 3. Sample Leaf Selectors for 1-Click Instant Demo Testing
  const sampleChips = document.querySelectorAll('.sample-chip');
  sampleChips.forEach(chip => {
    chip.addEventListener('click', function () {
      const samplePath = this.getAttribute('data-img');
      const sampleName = this.getAttribute('data-name');
      if (previewImg && previewText) {
        previewImg.src = samplePath;
        previewImg.style.display = 'block';
        previewText.innerText = sampleName + " (Sample Loaded)";
        // Set hidden input value for sample test submission
        const sampleInput = document.getElementById('samplePathInput');
        if (sampleInput) {
          sampleInput.value = samplePath;
        }
      }
    });
  });

  // 4. Chatbot Interactive Communication
  const chatForm = document.getElementById('chatForm');
  const chatInput = document.getElementById('chatInput');
  const chatMessages = document.getElementById('chatMessages');

  if (chatForm && chatInput && chatMessages) {
    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const message = chatInput.value.trim();
      if (!message) return;

      appendChatMessage(message, 'user');
      chatInput.value = '';

      // Typing Indicator
      const typingDiv = document.createElement('div');
      typingDiv.className = 'chat-bubble bubble-bot';
      typingDiv.innerText = 'AgriPulse is thinking...';
      typingDiv.id = 'botTyping';
      chatMessages.appendChild(typingDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      // API Call
      fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
      })
      .then(res => res.json())
      .then(data => {
        const typing = document.getElementById('botTyping');
        if (typing) typing.remove();
        appendChatMessage(data.response, 'bot');
      })
      .catch(err => {
        const typing = document.getElementById('botTyping');
        if (typing) typing.remove();
        appendChatMessage("Sorry, I could not connect to the AgriPulse advisory service. Please try again.", 'bot');
      });
    });

    // Quick prompt pills
    const promptPills = document.querySelectorAll('.prompt-pill');
    promptPills.forEach(pill => {
      pill.addEventListener('click', function () {
        chatInput.value = this.innerText;
        chatForm.dispatchEvent(new Event('submit'));
      });
    });
  }

  function appendChatMessage(text, sender) {
    if (!chatMessages) return;
    const bubble = document.createElement('div');
    bubble.className = `chat-bubble bubble-${sender}`;
    bubble.innerText = text;
    chatMessages.appendChild(bubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});
