/* Campus AI Client Side Interactivity - Phase 8 Voice Agent + Real-Time Chat */

document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const typingIndicator = document.getElementById('typing-indicator');
    const sendBtn = document.getElementById('send-btn');
    const voiceBtn = document.getElementById('voice-btn');
    const voiceIcon = document.getElementById('voice-icon');
    const voiceLangSelect = document.getElementById('voice-lang-select');
    const voiceStatusBanner = document.getElementById('voice-status-banner');
    const voiceStatusText = document.getElementById('voice-status-text');
    const clearChatBtn = document.getElementById('clear-chat-btn');
    const activeContextBadge = document.getElementById('active-context-badge');
    const ttsToggleBtn = document.getElementById('tts-toggle-btn');
    const ttsToggleIcon = document.getElementById('tts-toggle-icon');
    const ttsToggleText = document.getElementById('tts-toggle-text');
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    let isProcessing = false;
    let isRecording = false;
    let isTtsEnabled = false;
    let recognition = null;
    let conversationHistory = [];
    let capturedTranscript = '';
    let hasSentCurrentVoice = false;

    // TTS Toggle Switch
    if (ttsToggleBtn) {
        ttsToggleBtn.addEventListener('click', function () {
            isTtsEnabled = !isTtsEnabled;
            if (isTtsEnabled) {
                ttsToggleBtn.classList.replace('btn-outline-light', 'btn-light');
                ttsToggleBtn.classList.add('text-primary');
                if (ttsToggleText) ttsToggleText.textContent = 'TTS: On';
            } else {
                ttsToggleBtn.classList.replace('btn-light', 'btn-outline-light');
                ttsToggleBtn.classList.remove('text-primary');
                if (ttsToggleText) ttsToggleText.textContent = 'TTS: Off';
                if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            }
        });
    }

    // Clear Chat / New Chat Action
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', async function () {
            if (confirm('Start a new chat session and clear conversation context?')) {
                try {
                    await fetch('/ai/chat/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        },
                        body: JSON.stringify({ clear_context: true })
                    });

                    conversationHistory = [];
                    const rows = chatMessages.querySelectorAll('.message-row:not(#typing-indicator)');
                    rows.forEach((r, idx) => { if (idx > 0) r.remove(); });
                    
                    if (activeContextBadge) activeContextBadge.classList.add('d-none');
                    appendMessage('ai', 'Conversation context cleared. Hello, I am Aisha! How can I assist you today?');
                } catch (e) {
                    console.error('Clear Chat Error:', e);
                }
            }
        });
    }

    // Web Speech API Initialization
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = voiceLangSelect ? voiceLangSelect.value : 'en-IN';

        recognition.onstart = function () {
            isRecording = true;
            hasSentCurrentVoice = false;
            capturedTranscript = '';
            voiceBtn.classList.add('btn-danger', 'pulse-recording');
            voiceBtn.classList.remove('btn-outline-primary');
            voiceBtn.setAttribute('aria-label', 'Stop voice input');
            if (voiceIcon) voiceIcon.className = 'bi bi-stop-circle-fill fs-5 text-white';
            
            const langLabel = (voiceLangSelect && voiceLangSelect.value === 'hi-IN') ? 'Hindi/Hinglish' : 'English';
            if (voiceStatusText) voiceStatusText.textContent = `🔴 Listening (${langLabel})... Speak into your microphone`;
            if (voiceStatusBanner) voiceStatusBanner.classList.remove('d-none');
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
            if (finalTranscript) {
                capturedTranscript = finalTranscript.trim();
                chatInput.value = capturedTranscript;
            } else if (interimTranscript) {
                chatInput.value = interimTranscript;
            }
            chatInput.style.height = 'auto';
            chatInput.style.height = (chatInput.scrollHeight) + 'px';
        };

        recognition.onerror = function (event) {
            stopRecording();
            let errMessage = 'Voice recognition error.';
            if (event.error === 'not-allowed') {
                errMessage = '🎙️ Microphone permission was denied. Please grant microphone access in browser settings.';
            } else if (event.error === 'no-speech') {
                errMessage = '🎙️ I didn't catch that. Please speak clearly into your microphone.';
            } else if (event.error === 'audio-capture') {
                errMessage = '🎙️ No microphone was detected on your device.';
            } else if (event.error === 'network') {
                errMessage = '🎙️ Network connection error during speech recognition.';
            }
            appendMessage('ai', errMessage);
        };

        recognition.onend = function () {
            stopRecording();
            if (capturedTranscript && !hasSentCurrentVoice && !isProcessing) {
                hasSentCurrentVoice = true;
                chatForm.dispatchEvent(new Event('submit'));
            }
        };

        if (voiceLangSelect) {
            voiceLangSelect.addEventListener('change', function () {
                if (recognition) recognition.lang = this.value;
            });
        }
    } else {
        if (voiceBtn) {
            voiceBtn.title = "Voice input is not supported in this browser.";
            voiceBtn.addEventListener('click', function () {
                appendMessage('ai', '🎙️ Voice input is not supported in this browser. Please type your message instead.');
            });
        }
    }

    function stopRecording() {
        isRecording = false;
        if (voiceBtn) {
            voiceBtn.classList.remove('btn-danger', 'pulse-recording');
            voiceBtn.classList.add('btn-outline-primary');
            voiceBtn.setAttribute('aria-label', 'Voice input');
            if (voiceIcon) voiceIcon.className = 'bi bi-mic-fill fs-5';
        }
        if (voiceStatusBanner) voiceStatusBanner.classList.add('d-none');
        if (recognition) { try { recognition.stop(); } catch (e) {} }
    }

    if (voiceBtn && SpeechRecognition) {
        voiceBtn.addEventListener('click', function () {
            if (isRecording) {
                stopRecording();
            } else {
                try {
                    if (voiceLangSelect) recognition.lang = voiceLangSelect.value;
                    recognition.start();
                } catch (err) {}
            }
        });
    }

    function scrollToBottom() { chatMessages.scrollTop = chatMessages.scrollHeight; }
    function getFormattedTime() { return (new Date()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }

    function speakText(text) {
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        
        const cleanText = text.replace(/<[^>]*>?/gm, '').replace(/[*#`|]/g, ' ');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = (voiceLangSelect && voiceLangSelect.value) ? voiceLangSelect.value : 'en-IN';
        
        // Find best matching voice
        const voices = window.speechSynthesis.getVoices();
        if (voices.length > 0) {
            const matchedVoice = voices.find(v => v.lang.startsWith(utterance.lang.substring(0, 2)));
            if (matchedVoice) utterance.voice = matchedVoice;
        }
        
        window.speechSynthesis.speak(utterance);
    }

    function appendMessage(sender, text, confirmationPreview = null, actionId = null) {
        const row = document.createElement('div');
        row.className = `message-row ${sender === 'user' ? 'user-message' : 'ai-message'}`;

        const avatar = document.createElement('div');
        avatar.className = 'msg-avatar';
        avatar.innerHTML = sender === 'user' ? '<i class="bi bi-person-fill"></i>' : '<i class="bi bi-robot"></i>';

        const bubble = document.createElement('div');
        bubble.className = 'msg-bubble';

        const header = document.createElement('div');
        header.className = 'msg-header d-flex justify-content-between align-items-center';
        header.innerHTML = `<span>${sender === 'user' ? 'You' : 'Aisha (Campus AI)'}</span>`;

        if (sender === 'ai' && 'speechSynthesis' in window) {
            const ttsContainer = document.createElement('div');
            ttsContainer.className = 'd-flex align-items-center gap-1';

            const ttsBtn = document.createElement('button');
            ttsBtn.type = 'button';
            ttsBtn.className = 'btn btn-sm btn-link p-0 text-secondary ms-2';
            ttsBtn.title = 'Listen to response';
            ttsBtn.innerHTML = '<i class="bi bi-volume-up-fill fs-6"></i>';
            ttsBtn.addEventListener('click', function () { speakText(text); });

            const stopTtsBtn = document.createElement('button');
            stopTtsBtn.type = 'button';
            stopTtsBtn.className = 'btn btn-sm btn-link p-0 text-danger ms-1';
            stopTtsBtn.title = 'Stop speaking';
            stopTtsBtn.innerHTML = '<i class="bi bi-stop-circle-fill fs-6"></i>';
            stopTtsBtn.addEventListener('click', function () { window.speechSynthesis.cancel(); });

            ttsContainer.appendChild(ttsBtn);
            ttsContainer.appendChild(stopTtsBtn);
            header.appendChild(ttsContainer);
        }

        const textDiv = document.createElement('div');
        textDiv.className = 'msg-text';
        textDiv.innerHTML = text.replace(/\n/g, '<br>');

        bubble.appendChild(header);
        bubble.appendChild(textDiv);

        if (confirmationPreview && actionId) {
            const card = document.createElement('div');
            card.className = 'card border-primary mt-3 shadow-sm';
            
            let detailsHtml = '';
            for (const [key, val] of Object.entries(confirmationPreview.details || {})) {
                detailsHtml += `<div><strong>${key}:</strong> ${val}</div>`;
            }

            card.innerHTML = `
                <div class="card-header bg-primary text-white fw-bold py-2">
                    <i class="bi bi-shield-lock-fill me-1"></i> ${confirmationPreview.title}
                </div>
                <div class="card-body py-2 px-3 bg-light text-dark font-monospace small">
                    ${detailsHtml}
                </div>
                <div class="card-footer bg-white d-flex justify-content-end gap-2 py-2">
                    <button type="button" class="btn btn-sm btn-outline-secondary cancel-act-btn">Cancel</button>
                    <button type="button" class="btn btn-sm btn-success confirm-act-btn" data-act-id="${actionId}">Confirm Action</button>
                </div>
            `;

            const cancelBtn = card.querySelector('.cancel-act-btn');
            const confirmBtn = card.querySelector('.confirm-act-btn');

            cancelBtn.addEventListener('click', function () {
                card.remove();
                appendMessage('ai', 'Action cancelled.');
            });

            confirmBtn.addEventListener('click', function () {
                card.remove();
                executeConfirmedAction(actionId);
            });

            bubble.appendChild(card);
        }

        const timeDiv = document.createElement('div');
        timeDiv.className = 'msg-time';
        timeDiv.textContent = getFormattedTime();
        bubble.appendChild(timeDiv);

        row.appendChild(avatar);
        row.appendChild(bubble);

        chatMessages.insertBefore(row, typingIndicator);
        scrollToBottom();

        // Auto read response if TTS is enabled
        if (sender === 'ai' && isTtsEnabled) {
            speakText(text);
        }
    }

    async function executeConfirmedAction(actionId) {
        if (isProcessing) return;
        isProcessing = true;
        sendBtn.disabled = true;
        chatInput.disabled = true;

        typingIndicator.classList.remove('d-none');
        scrollToBottom();

        try {
            const response = await fetch('/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ confirm_action_id: actionId })
            });

            const data = await response.json();
            typingIndicator.classList.add('d-none');

            appendMessage('ai', data.message || 'Action execution processed.');
        } catch (err) {
            typingIndicator.classList.add('d-none');
            appendMessage('ai', 'Network connection error during action confirmation.');
        } finally {
            isProcessing = false;
            sendBtn.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
            scrollToBottom();
        }
    }

    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    chatForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const messageText = chatInput.value.trim();

        if (!messageText || isProcessing) return;

        if (isRecording) stopRecording();

        isProcessing = true;
        sendBtn.disabled = true;
        chatInput.disabled = true;

        appendMessage('user', messageText);

        chatInput.value = '';
        chatInput.style.height = 'auto';

        typingIndicator.classList.remove('d-none');
        scrollToBottom();

        try {
            const response = await fetch('/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ 
                    message: messageText,
                    history: conversationHistory
                })
            });

            const data = await response.json();
            typingIndicator.classList.add('d-none');

            if (data.success) {
                appendMessage(
                    'ai', 
                    data.message, 
                    data.confirmation_preview, 
                    data.pending_action_id
                );

                if (data.active_context && activeContextBadge) {
                    activeContextBadge.textContent = data.active_context;
                    activeContextBadge.classList.remove('d-none');
                }

                conversationHistory.push({ role: 'user', content: messageText });
                conversationHistory.push({ role: 'model', content: data.message });
                if (conversationHistory.length > 10) {
                    conversationHistory.splice(0, conversationHistory.length - 10);
                }

                if (data.ui_action && data.ui_action.type === 'OPEN_URL' && data.ui_action.url) {
                    const targetUrl = data.ui_action.url;
                    if (targetUrl.startsWith('/') && !targetUrl.startsWith('//') && !targetUrl.includes(':')) {
                        setTimeout(function () {
                            window.location.href = targetUrl;
                        }, 1200);
                    }
                }
            } else {
                appendMessage('ai', data.message || 'Sorry, an error occurred. Please try again.');
            }
        } catch (error) {
            typingIndicator.classList.add('d-none');
            appendMessage('ai', 'Network connection error. Please check your internet connection.');
        } finally {
            isProcessing = false;
            sendBtn.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
            scrollToBottom();
        }
    });

    scrollToBottom();
});
