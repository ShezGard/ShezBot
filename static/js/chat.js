// ==================== Логика чата ====================

class Chat {
    constructor() {
        this.chatMessages = document.getElementById('chat-messages');
        this.userInput = document.getElementById('user-input');
        this.sendBtn = document.getElementById('send-btn');
        this.isProcessing = false;
    }
    
    /**
     * Инициализация чата
     */
    init() {
        if (!this.userInput || !this.sendBtn) return;
        
        // Авто-ресайз текстареи
        this.userInput.addEventListener('input', () => {
            utils.autoResizeTextarea(this.userInput);
        });
        
        // Отправка по Enter
        this.userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Отправка по кнопке
        this.sendBtn.addEventListener('click', () => this.sendMessage());
    }
    
    /**
     * Добавить сообщение в чат
     */
    addMessage(text, isUser = false) {
        if (!this.chatMessages) return;
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'message-user' : 'message-ai'}`;
        const timeStr = utils.formatTime(new Date());
        
        messageDiv.innerHTML = `
            <div class="message-content">${isUser ? utils.escapeHtml(text) : utils.escapeHtml(text).replace(/\n/g, '<br>')}</div>
            <div class="message-time">${timeStr}</div>
            ${!isUser ? `
                <button class="btn btn-sm copy-btn" onclick="chat.copyMessage(this)">
                    <i class="fas fa-copy me-1"></i>Копировать эпик
                </button>
            ` : ''}
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    /**
     * Добавить сообщение об ошибке
     */
    addErrorMessage(text) {
        if (!this.chatMessages) return;
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message message-ai';
        errorDiv.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle me-2"></i>${utils.escapeHtml(text)}
            </div>
            <div class="message-time">${utils.formatTime(new Date())}</div>
        `;
        
        this.chatMessages.appendChild(errorDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    /**
     * Установить состояние загрузки
     */
    setLoading(isLoading) {
        this.isProcessing = isLoading;
        
        if (this.sendBtn) {
            this.sendBtn.disabled = isLoading;
            this.sendBtn.innerHTML = isLoading 
                ? '<div class="loading"></div>' 
                : '<i class="fas fa-paper-plane"></i>';
        }
        
        if (this.userInput) {
            this.userInput.disabled = isLoading;
        }
    }
    
    /**
     * Отправить сообщение
     */
    async sendMessage() {
        const text = this.userInput.value.trim();
        
        if (!text || text.length < 10) {
            utils.showToast('Напиши подробнее (минимум 10 символов)');
            return;
        }
        
        if (text.length > 2000) {
            utils.showToast('Слишком длинно (максимум 2000 символов)');
            return;
        }
        
        if (this.isProcessing) return;
        
        this.addMessage(text, true);
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
        
        // Показываем индикатор загрузки
        const loadingDiv = this.showLoading();
        
        this.setLoading(true);
        
        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ description: text }),
            });
            
            // Убираем индикатор загрузки
            if (loadingDiv && loadingDiv.parentNode) {
                this.chatMessages.removeChild(loadingDiv);
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Ошибка сервера: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.epic) {
                this.addMessage(data.epic);
            } else {
                throw new Error('Сервер не вернул поле "epic"');
            }
        } catch (error) {
            console.error('Ошибка при генерации:', error);
            
            // Убираем индикатор загрузки если он ещё есть
            if (loadingDiv && loadingDiv.parentNode) {
                this.chatMessages.removeChild(loadingDiv);
            }
            
            this.addErrorMessage(`❌ ${error.message || 'Неизвестная ошибка'}`);
        } finally {
            this.setLoading(false);
        }
    }
    
    /**
     * Показать индикатор загрузки
     */
    showLoading() {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message message-ai';
        loadingDiv.innerHTML = `
            <div class="message-content text-center py-3">
                <div class="loading mb-3"></div>
                <div style="color: var(--text-secondary); font-size: 0.95rem; font-weight: 400;">
                    <i class="fas fa-robot me-2" style="color: var(--accent-color);"></i>
                    ShezGard Bot думает
                    <span class="typing-indicator"></span>
                    <span class="typing-indicator"></span>
                    <span class="typing-indicator"></span>
                </div>
            </div>
        `;
        
        this.chatMessages.appendChild(loadingDiv);
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        return loadingDiv;
    }
    
    /**
     * Скопировать сообщение
     */
    copyMessage(button) {
        const messageDiv = button.closest('.message');
        const textElement = messageDiv.querySelector('.message-content');
        const text = textElement.innerText || textElement.textContent;
        
        utils.copyToClipboard(text).then(success => {
            if (success) {
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="fas fa-check me-1"></i>Скопировано!';
                button.style.background = 'linear-gradient(135deg, var(--accent-color), #5a4ae9)';
                button.style.color = 'white';
                button.style.borderColor = 'transparent';
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.style.background = '';
                    button.style.color = '';
                    button.style.borderColor = '';
                }, 2000);
            } else {
                utils.showToast('Не удалось скопировать текст');
            }
        });
    }
}

// Создаём экземпляр чата и инициализируем при загрузке
const chat = new Chat();

document.addEventListener('DOMContentLoaded', () => {
    chat.init();
});

// Экспортируем для глобального доступа
window.chat = chat;