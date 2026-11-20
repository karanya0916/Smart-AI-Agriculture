// AgriPulse AI - Multilingual Voice Assistant Tool

document.addEventListener('DOMContentLoaded', function () {
  const micBtn = document.getElementById('micToggleBtn');
  const micStatus = document.getElementById('micStatusText');
  const voiceWave = document.getElementById('voiceWaveAnim');
  const langSelect = document.getElementById('voiceLangSelect');
  const transcriptBox = document.getElementById('voiceTranscript');
  const responseBox = document.getElementById('voiceResponseCard');
  const responseText = document.getElementById('voiceResponseText');
  const playAudioBtn = document.getElementById('playAudioBtn');
  const samplePromptsContainer = document.getElementById('voiceSamplePrompts');

  let recognition = null;
  let isListening = false;
  let currentLanguage = langSelect ? langSelect.value : 'hi';
  let lastSpokenText = '';

  // Language mapping to BCP-47 speech tags
  const speechLangCodes = {
    'en': 'en-IN',
    'hi': 'hi-IN',
    'mr': 'mr-IN',
    'te': 'te-IN',
    'ta': 'ta-IN',
    'bn': 'bn-IN',
    'gu': 'gu-IN',
    'kn': 'kn-IN',
    'pa': 'pa-IN'
  };

  // Sample prompt phrases per language for fast demo testing
  const samplePrompts = {
    'hi': [
      "नमस्ते, आप कैसे मदद कर सकते हैं?",
      "अर्ली ब्लाइट बीमारी का क्या इलाज है?",
      "यूरिया खाद कितनी मात्रा में डालें?",
      "फसल के लिए सिंचाई कब करनी चाहिए?",
      "पीएम किसान योजना के बारे में बताएं"
    ],
    'mr': [
      "नमस्कार, पिकांची माहिती सांगा",
      "पानांवरील करपा रोगाचे उपाय सांगा",
      "युरिया खताचे प्रमाण किती असावे?",
      "पाणी कधी द्यावे?"
    ],
    'te': [
      "నమస్కారం, సహాయం కావాలి",
      "ఆకు మచ్చ తెగులు నివారణ ఏమిటి?",
      "యూరియా ఎరువు ఎంత వేయాలి?",
      "నీరు ఎప్పుడు పెట్టాలి?"
    ],
    'ta': [
      "வணக்கம், எனக்கு உதவி தேவை",
      "இலைக்கருகல் நோய் கட்டுப்பாடு எப்படி?",
      "யூரியா உரம் எவ்வளவு இட வேண்டும்?"
    ],
    'en': [
      "How to treat Early Blight on leaves?",
      "What is the recommended dose of Urea?",
      "When is the best time for irrigation?",
      "Tell me about PM-KISAN scheme",
      "How to prepare organic Jeevamrutha?"
    ],
    'bn': [
      "নমস্কার, আমাকে ফসলের পরামর্শ দিন",
      "পাতায় ব্লাইট রোগের চিকিৎসা কী?"
    ],
    'gu': [
      "નમસ્તે, કયો પાક સારો રહેશે?",
      "યુરિયા ખાતર કેટલું આપવું?"
    ],
    'kn': [
      "ನಮಸ್ಕಾರ, ಬೆಳೆ ಶಿಫಾರಸು ತಿಳಿಸಿ"
    ],
    'pa': [
      "ਸਤਿ ਸ਼੍ਰੀ ਅਕਾਲ, ਖਾਦ ਦੀ ਮਾਤਰਾ ਦੱਸੋ",
      "ਬਿਮਾਰੀ ਦਾ ਇਲਾਜ ਕੀ ਹੈ?"
    ]
  };

  function updateSampleChips(lang) {
    if (!samplePromptsContainer) return;
    samplePromptsContainer.innerHTML = '';
    const prompts = samplePrompts[lang] || samplePrompts['en'];
    prompts.forEach(text => {
      const chip = document.createElement('span');
      chip.className = 'sample-chip';
      chip.innerHTML = `🎙️ "${text}"`;
      chip.addEventListener('click', () => {
        if (transcriptBox) transcriptBox.innerText = text;
        processVoiceQuery(text, lang);
      });
      samplePromptsContainer.appendChild(chip);
    });
  }

  if (langSelect) {
    updateSampleChips(currentLanguage);
    langSelect.addEventListener('change', function () {
      currentLanguage = this.value;
      updateSampleChips(currentLanguage);
      if (isListening && recognition) {
        recognition.stop();
        isListening = false;
        micBtn.classList.remove('listening');
        voiceWave.style.display = 'none';
        micStatus.innerText = 'Click microphone to speak';
      }
    });
  }

  // Initialize Speech Recognition
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;

    recognition.onstart = function () {
      isListening = true;
      if (micBtn) micBtn.classList.add('listening');
      if (voiceWave) voiceWave.style.display = 'flex';
      if (micStatus) micStatus.innerText = `Listening in ${speechLangCodes[currentLanguage]}... Speak now`;
    };

    recognition.onresult = function (event) {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      if (transcriptBox) {
        transcriptBox.innerText = finalTranscript || interimTranscript || 'Listening...';
      }

      if (finalTranscript) {
        processVoiceQuery(finalTranscript, currentLanguage);
      }
    };

    recognition.onerror = function (event) {
      console.warn("Speech recognition error:", event.error);
      isListening = false;
      if (micBtn) micBtn.classList.remove('listening');
      if (voiceWave) voiceWave.style.display = 'none';
      if (micStatus) {
        if (event.error === 'not-allowed') {
          micStatus.innerText = 'Microphone access denied. You can click any sample voice chip below to test!';
        } else {
          micStatus.innerText = `Voice error (${event.error}). Click mic to retry or use sample prompts.`;
        }
      }
    };

    recognition.onend = function () {
      isListening = false;
      if (micBtn) micBtn.classList.remove('listening');
      if (voiceWave) voiceWave.style.display = 'none';
      if (micStatus && !micStatus.innerText.includes('Microphone access denied')) {
        micStatus.innerText = 'Click microphone to speak again';
      }
    };
  } else {
    if (micStatus) {
      micStatus.innerText = 'Browser Speech Recognition API not detected. Use 1-Click voice sample buttons below!';
    }
  }

  if (micBtn) {
    micBtn.addEventListener('click', function () {
      if (!recognition) {
        alert("Speech Recognition is not supported by your browser engine. You can click any of the voice prompt chips below to test the multilingual assistant!");
        return;
      }
      if (isListening) {
        recognition.stop();
      } else {
        recognition.lang = speechLangCodes[currentLanguage] || 'hi-IN';
        if (transcriptBox) transcriptBox.innerText = 'Listening for speech...';
        try {
          recognition.start();
        } catch (e) {
          console.error(e);
        }
      }
    });
  }

  // Send Transcribed Speech to Backend Multilingual AI Engine
  function processVoiceQuery(queryText, lang) {
    if (micStatus) micStatus.innerText = 'AgriPulse is reasoning & synthesizing response...';

    fetch('/api/voice/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: queryText, language: lang })
    })
    .then(res => res.json())
    .then(data => {
      lastSpokenText = data.response;
      if (responseBox) responseBox.style.display = 'block';
      if (responseText) responseText.innerText = data.response;
      if (micStatus) micStatus.innerText = `Speaking response in ${speechLangCodes[lang]}...`;

      // Speak back using Web Speech Synthesis or Backend Audio
      speakResponse(data.response, lang);
    })
    .catch(err => {
      console.error(err);
      if (micStatus) micStatus.innerText = 'Error processing speech. Please try again.';
    });
  }

  // Multilingual Speech Synthesis (Text-to-Speech)
  function speakResponse(text, lang) {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel(); // Stop any previous speech
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = speechLangCodes[lang] || 'hi-IN';
      utterance.rate = 0.95; // Slightly slower for clarity
      utterance.pitch = 1.0;

      // Select regional voice if installed
      const voices = window.speechSynthesis.getVoices();
      const targetLang = speechLangCodes[lang];
      const matchedVoice = voices.find(v => v.lang.startsWith(targetLang.split('-')[0]));
      if (matchedVoice) {
        utterance.voice = matchedVoice;
      }

      utterance.onend = function () {
        if (micStatus) micStatus.innerText = 'Response finished. Click mic to speak again.';
      };

      window.speechSynthesis.speak(utterance);
    } else {
      // Fallback: Trigger Backend gTTS Audio Player
      playServerAudio(text, lang);
    }
  }

  function playServerAudio(text, lang) {
    const audioUrl = `/api/voice/tts?text=${encodeURIComponent(text)}&lang=${lang}`;
    const audio = new Audio(audioUrl);
    audio.play().catch(e => console.warn("Audio autoplay blocked:", e));
  }

  if (playAudioBtn) {
    playAudioBtn.addEventListener('click', function () {
      if (lastSpokenText) {
        speakResponse(lastSpokenText, currentLanguage);
      }
    });
  }
});
