// ==================== Генерация презентации ====================

class PresentationGenerator {
    constructor() {
        this.epicInput = document.getElementById('epic-input');
        this.generateBtn = document.getElementById('generate-presentation-btn');
        this.progress = document.getElementById('presentation-progress');
        this.result = document.getElementById('presentation-result');
    }
    
    /**
     * Инициализация
     */
    init() {
        if (!this.generateBtn) return;
        
        this.generateBtn.addEventListener('click', () => this.generatePresentation());
        
        // Авто-ресайз текстареи
        this.epicInput?.addEventListener('input', () => {
            this.autoResizeTextarea(this.epicInput);
        });
    }
    
    /**
     * Авто-ресайз текстареи
     */
    autoResizeTextarea(textarea) {
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = (textarea.scrollHeight) + 'px';
        }
    }
    
    /**
     * Генерация презентации
     */
    async generatePresentation() {
        const epicText = this.epicInput.value.trim();
        
        if (epicText.length < 50) {
            utils.showToast('Эпик слишком короткий (минимум 50 символов)');
            return;
        }
        
        // Показываем прогресс
        this.progress.style.display = 'block';
        this.result.style.display = 'none';
        
        // Имитация прогресса
        const progressInterval = this.startProgressSimulation();
        
        try {
            const response = await fetch('/api/presentation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ epic: epicText }),
            });
            
            // ОЧИЩАЕМ ИНТЕРВАЛ ПОСЛЕ ЗАПРОСА
            clearInterval(progressInterval);
            
            // Устанавливаем прогресс в 100%
            document.querySelector('#presentation-progress .progress-bar').style.width = '100%';
            document.getElementById('presentation-progress-percent').textContent = '100%';
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `Ошибка сервера: ${response.status}`);
            }
            
            const data = await response.json();
            
            setTimeout(() => {
                this.progress.style.display = 'none';
                
                if (data.error) {
                    utils.showError(this.result, data.error);
                } else {
                    this.showPresentationResult(data);
                }
            }, 300);
            
        } catch (error) {
            // ОЧИЩАЕМ ИНТЕРВАЛ ПРИ ОШИБКЕ
            clearInterval(progressInterval);
            
            // Устанавливаем прогресс в 100% даже при ошибке
            document.querySelector('#presentation-progress .progress-bar').style.width = '100%';
            document.getElementById('presentation-progress-percent').textContent = '100%';
            
            this.progress.style.display = 'none';
            utils.showError(this.result, 'Ошибка генерации: ' + error.message);
        }
    }
    
    /**
     * Запустить симуляцию прогресса
     */
    startProgressSimulation() {
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            if (progress >= 95) { // ← ОСТАНАВЛИВАЕМ НА 95%
                clearInterval(interval);
            }
            document.querySelector('#presentation-progress .progress-bar').style.width = `${progress}%`;
            document.getElementById('presentation-progress-percent').textContent = `${progress}%`;
        }, 200);
        
        return interval; // ← ВОЗВРАЩАЕМ ИНТЕРВАЛ ДЛЯ ОЧИСТКИ
    }
    
    /**
     * Показать результат презентации
     */
    showPresentationResult(data) {
        const slides = data.slides || [];
        const presentationText = data.presentation;
        
        let html = `
            <div class="alert alert-success bg-dark border-success text-white">
                <i class="fas fa-check-circle me-2"></i>
                <strong>✅ Презентация готова!</strong> Сгенерировано ${slides.length} слайдов.
            </div>
            
            <div class="d-flex gap-2 mb-4">
                <button class="btn btn-sm copy-btn" onclick="presentationGenerator.copyPresentation()">
                    <i class="fas fa-copy me-1"></i>Копировать всю презентацию
                </button>
                <button class="btn btn-sm btn-secondary" onclick="presentationGenerator.downloadPresentation()">
                    <i class="fas fa-download me-1"></i>Скачать .txt
                </button>
            </div>
            
            <div class="row">
        `;
        
        // Отображаем каждый слайд
        slides.forEach((slide, index) => {
            html += `
                <div class="col-md-6 mb-4">
                    <div class="card bg-secondary border-0 h-100">
                        <div class="card-body">
                            <div class="badge bg-primary mb-3">Слайд ${slide.number}</div>
                            <h5 class="card-title mb-3" style="color: var(--accent-color);">
                                ${utils.escapeHtml(slide.title)}
                            </h5>
                            <div class="card-text">
            `;
            
            slide.content.forEach(line => {
                if (line.startsWith('•')) {
                    html += `<p class="mb-2"><i class="fas fa-circle text-primary me-2" style="font-size: 0.5rem;"></i>${utils.escapeHtml(line)}</p>`;
                } else if (line.startsWith('-')) {
                    html += `<p class="mb-2 ms-3"><i class="fas fa-minus text-muted me-2" style="font-size: 0.5rem;"></i>${utils.escapeHtml(line)}</p>`;
                } else {
                    html += `<p class="mb-2">${utils.escapeHtml(line)}</p>`;
                }
            });
            
            html += `
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Перенос на новую строку каждые 2 слайда
            if ((index + 1) % 2 === 0 && index < slides.length - 1) {
                html += `</div><div class="row">`;
            }
        });
        
        html += `
            </div>
            
            <div class="mt-4">
                <h5 class="mb-3" style="color: var(--accent-color);">
                    <i class="fas fa-file-alt me-2"></i>Полный текст презентации
                </h5>
                <div class="card bg-card border-secondary">
                    <div class="card-body" style="white-space: pre-wrap; line-height: 1.6;">
                        ${utils.escapeHtml(presentationText).replace(/\n/g, '<br>')}
                    </div>
                </div>
            </div>
        `;
        
        this.result.innerHTML = html;
        this.result.style.display = 'block';
        
        // Скролл к результату
        this.result.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    /**
     * Скопировать всю презентацию
     */
    copyPresentation() {
        const presentationText = document.querySelector('#presentation-result .card.bg-card .card-body').innerText;
        utils.copyToClipboard(presentationText).then(success => {
            if (success) {
                utils.showToast('Презентация скопирована!');
            }
        });
    }
    
    /**
     * Скачать презентацию в файл
     */
    downloadPresentation() {
        const presentationText = document.querySelector('#presentation-result .card.bg-card .card-body').innerText;
        const blob = new Blob([presentationText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Презентация_${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        utils.showToast('Презентация скачана!');
    }
}

// Создаём экземпляр и инициализируем при загрузке
const presentationGenerator = new PresentationGenerator();

document.addEventListener('DOMContentLoaded', () => {
    presentationGenerator.init();
});

// Экспортируем для глобального доступа
window.presentationGenerator = presentationGenerator;