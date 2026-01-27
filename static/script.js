const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const toastEl = document.getElementById('toast');
const toast = new bootstrap.Toast(toastEl);

// Авто-ресайз текстареи
userInput.addEventListener('input', function() {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';
});

// Отправка по Enter
userInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Отправка по кнопке
sendBtn.addEventListener('click', sendMessage);

function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'message-user' : 'message-ai'}`;
    
    const now = new Date();
    const timeStr = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
    
    messageDiv.innerHTML = `
        <div class="message-content">${isUser ? escapeHtml(text) : escapeHtml(text).replace(/\n/g, '<br>')}</div>
        <div class="message-time">${timeStr}</div>
        ${!isUser ? `
            <button class="btn btn-sm copy-btn" onclick="copyText(this)">
                <i class="fas fa-copy me-1"></i>Копировать эпик
            </button>
        ` : ''}
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addErrorMessage(text) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'message message-ai';
    errorDiv.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-triangle me-2"></i>${escapeHtml(text)}
        </div>
        <div class="message-time">${new Date().getHours()}:${new Date().getMinutes().toString().padStart(2, '0')}</div>
    `;
    chatMessages.appendChild(errorDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function setLoading(isLoading) {
    if (isLoading) {
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="loading"></div>';
        userInput.disabled = true;
    } else {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
        userInput.disabled = false;
    }
}

async function sendMessage() {
    const text = userInput.value.trim();
    
    if (!text || text.length < 10) {
        alert('Напиши подробнее (минимум 10 символов)');
        return;
    }
    
    if (text.length > 2000) {
        alert('Слишком длинно (максимум 2000 символов)');
        return;
    }
    
    addMessage(text, true);
    userInput.value = '';
    userInput.style.height = 'auto';
    
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
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    setLoading(true);
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ description: text }),
        });
        
        if (loadingDiv.parentNode) {
            chatMessages.removeChild(loadingDiv);
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Ошибка сервера: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.epic) {
            addMessage(data.epic);
        } else {
            throw new Error('Сервер не вернул поле "epic"');
        }
    } catch (error) {
        console.error('Ошибка при генерации:', error);
        
        if (loadingDiv.parentNode) {
            chatMessages.removeChild(loadingDiv);
        }
        
        addErrorMessage(`❌ ${error.message || 'Неизвестная ошибка'}`);
    } finally {
        setLoading(false);
    }
}

function copyText(button) {
    const messageDiv = button.closest('.message');
    const textElement = messageDiv.querySelector('.message-content');
    const text = textElement.innerText || textElement.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
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
    }).catch(err => {
        console.error('Ошибка копирования:', err);
        alert('Не удалось скопировать текст');
    });
}

// ==================== Анализ данных из CSV ====================

const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const uploadProgress = document.getElementById('upload-progress');
const analysisResult = document.getElementById('analysis-result');

// Клик по области загрузки
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Перетаскивание файлов
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--accent-color)';
    uploadArea.style.backgroundColor = 'rgba(106, 90, 249, 0.1)';
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.style.borderColor = 'var(--border-color)';
    uploadArea.style.backgroundColor = '';
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = 'var(--border-color)';
    uploadArea.style.backgroundColor = '';
    
    if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileUpload();
    }
});

// Выбор файла через кнопку
fileInput.addEventListener('change', handleFileUpload);

function handleFileUpload() {
    const file = fileInput.files[0];
    if (!file) return;
    
    // Проверка размера файла (100 МБ)
    const maxSize = 100 * 1024 * 1024; // 100 МБ
    if (file.size > maxSize) {
        showAnalysisError(`Файл слишком большой! Максимальный размер: 100 МБ. Текущий размер: ${(file.size / 1024 / 1024).toFixed(2)} МБ`);
        fileInput.value = ''; // Очищаем выбор файла
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Показываем прогресс
    uploadProgress.style.display = 'block';
    analysisResult.style.display = 'none';
    
    // Имитация прогресса (для красоты)
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 5;
        if (progress > 90) clearInterval(progressInterval);
        document.querySelector('.progress-bar').style.width = `${progress}%`;
    }, 200);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        clearInterval(progressInterval);
        document.querySelector('.progress-bar').style.width = '100%';
        return response.json();
    })
    .then(data => {
        setTimeout(() => {
            uploadProgress.style.display = 'none';
            
            if (data.error) {
                showAnalysisError(data.error);
            } else {
                showAnalysisResult(data);
            }
        }, 300);
    })
    .catch(error => {
        clearInterval(progressInterval);
        uploadProgress.style.display = 'none';
        showAnalysisError('Ошибка загрузки файла: ' + error.message);
    });
}

function showAnalysisError(message) {
    analysisResult.innerHTML = `
        <div class="alert alert-danger bg-dark border-danger text-white">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Ошибка:</strong> ${escapeHtml(message)}
        </div>
    `;
    analysisResult.style.display = 'block';
}

function showAnalysisResult(data) {
    const analysis = data.analysis;
    const aiAnalysis = data.ai_analysis;
    
    let html = `
        <div class="alert alert-success bg-dark border-success text-white">
            <i class="fas fa-check-circle me-2"></i>
            <strong>✅ Анализ завершён!</strong> Обработано ${analysis.total_rows} записей.
        </div>
    `;
    
    // Уровень 1 (основные категории)
    if (analysis.top_categories_level_1 && analysis.top_categories_level_1.length > 0) {
        html += `
            <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                <i class="fas fa-layer-group me-2"></i>ТОП-10 категорий (Уровень 1)
                <small class="text-muted ms-2" style="font-size: 0.8rem;">(основные направления)</small>
            </h5>
            <div class="table-responsive">
                <table class="table table-dark table-striped">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Категория</th>
                            <th>Количество</th>
                            <th>%</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        analysis.top_categories_level_1.forEach((cat, i) => {
            const barWidth = Math.min(cat.percent, 100);
            html += `
                <tr>
                    <td><strong>${i + 1}</strong></td>
                    <td><i class="fas fa-folder me-2" style="color: var(--accent-color);"></i>${escapeHtml(cat.name)}</td>
                    <td>${cat.count}</td>
                    <td>
                        <div class="progress" style="height: 6px; width: 80px; display: inline-block; margin-right: 8px; background-color: var(--bg-secondary);">
                            <div class="progress-bar" role="progressbar" style="width: ${barWidth}%; background: linear-gradient(90deg, var(--accent-color), #5a4ae9);"></div>
                        </div>
                        ${cat.percent}%
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
    }
    
    // Уровень 2 (подкатегории)
    if (analysis.top_categories_level_2 && analysis.top_categories_level_2.length > 0) {
        html += `
            <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                <i class="fas fa-layer-group me-2"></i>ТОП-10 подкатегорий (Уровень 2)
                <small class="text-muted ms-2" style="font-size: 0.8rem;">(детализация)</small>
            </h5>
            <div class="table-responsive">
                <table class="table table-dark table-striped">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Подкатегория</th>
                            <th>Количество</th>
                            <th>%</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        analysis.top_categories_level_2.forEach((cat, i) => {
            const barWidth = Math.min(cat.percent, 100);
            html += `
                <tr>
                    <td><strong>${i + 1}</strong></td>
                    <td><i class="fas fa-folder-open me-2" style="color: #5a4ae9;"></i>${escapeHtml(cat.name)}</td>
                    <td>${cat.count}</td>
                    <td>
                        <div class="progress" style="height: 6px; width: 80px; display: inline-block; margin-right: 8px; background-color: var(--bg-secondary);">
                            <div class="progress-bar" role="progressbar" style="width: ${barWidth}%; background: linear-gradient(90deg, #5a4ae9, var(--accent-color));"></div>
                        </div>
                        ${cat.percent}%
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
    }
    
    // Инсайты
    if (analysis.insights && analysis.insights.length > 0) {
        html += `
            <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                <i class="fas fa-lightbulb me-2"></i>Инсайты
            </h5>
        `;
        
        analysis.insights.forEach(insight => {
            const icon = insight.type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
            const color = insight.type === 'warning' ? 'text-warning' : 'text-info';
            const borderColor = insight.type === 'warning' ? 'border-warning' : 'border-info';
            html += `
                <div class="alert ${color} bg-dark ${borderColor}">
                    <i class="fas ${icon} me-2"></i>
                    ${escapeHtml(insight.message)}
                </div>
            `;
        });
    }
    
    // AI-анализ
    if (aiAnalysis) {
        html += `
            <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                <i class="fas fa-robot me-2"></i>AI-анализ и рекомендации
            </h5>
            <div class="card bg-secondary border-secondary">
                <div class="card-body">
                    ${escapeHtml(aiAnalysis).replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
                </div>
            </div>
            
            <button class="btn btn-sm copy-btn mt-3" onclick="copyAnalysis()">
                <i class="fas fa-copy me-1"></i>Копировать анализ
            </button>
        `;
    }
    
    analysisResult.innerHTML = html;
    analysisResult.style.display = 'block';
    
    // Скролл к результату
    analysisResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function copyAnalysis() {
    const analysisText = document.querySelector('.card.bg-secondary .card-body').innerText;
    navigator.clipboard.writeText(analysisText).then(() => {
        const btn = event.target;
        const originalText = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check me-1"></i>Скопировано!';
        btn.classList.remove('copy-btn');
        btn.classList.add('btn-success');
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.classList.remove('btn-success');
            btn.classList.add('copy-btn');
        }, 2000);
    });
}

// Фокус на поле ввода при загрузке
window.addEventListener('load', () => {
    userInput.focus();
});