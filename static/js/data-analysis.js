// ==================== Анализ данных из CSV ====================

class DataAnalysis {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.uploadProgress = document.getElementById('upload-progress');
        this.analysisResult = document.getElementById('analysis-result');
    }
    
    /**
     * Инициализация
     */
    init() {
        if (!this.uploadArea || !this.fileInput) return;
        
        // Клик по области загрузки
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        
        // Перетаскивание файлов
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', () => this.handleDragLeave());
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Выбор файла через кнопку
        this.fileInput.addEventListener('change', () => this.handleFileUpload());
    }
    
    /**
     * Обработчик перетаскивания
     */
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.style.borderColor = 'var(--accent-color)';
        this.uploadArea.style.backgroundColor = 'rgba(121, 184, 255, 0.1)';
    }
    
    /**
     * Обработчик выхода курсора
     */
    handleDragLeave() {
        this.uploadArea.style.borderColor = 'var(--border-color)';
        this.uploadArea.style.backgroundColor = '';
    }
    
    /**
     * Обработчик сброса файла
     */
    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.style.borderColor = 'var(--border-color)';
        this.uploadArea.style.backgroundColor = '';
        if (e.dataTransfer.files.length) {
            this.fileInput.files = e.dataTransfer.files;
            this.handleFileUpload();
        }
    }
    
    /**
     * Обработка загрузки файла
     */
    handleFileUpload() {
        const file = this.fileInput.files[0];
        if (!file) return;
        
        // Проверка размера файла
        const error = utils.validateFileSize(file);
        if (error) {
            utils.showError(this.analysisResult, error);
            this.fileInput.value = '';
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        // Показываем прогресс
        this.uploadProgress.style.display = 'block';
        this.analysisResult.style.display = 'none';
        
        // Имитация прогресса
        const progressInterval = this.startProgressSimulation();
        
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            // ОЧИЩАЕМ ИНТЕРВАЛ ПОСЛЕ ЗАПРОСА
            clearInterval(progressInterval);
            
            // Устанавливаем прогресс в 100%
            document.querySelector('#upload-progress .progress-bar').style.width = '100%';
            document.getElementById('progress-percent').textContent = '100%';
            
            return response.json();
        })
        .then(data => {
            setTimeout(() => {
                this.uploadProgress.style.display = 'none';
                
                if (data.error) {
                    utils.showError(this.analysisResult, data.error);
                } else {
                    this.showAnalysisResult(data);
                }
            }, 300);
        })
        .catch(error => {
            // ОЧИЩАЕМ ИНТЕРВАЛ ПРИ ОШИБКЕ
            clearInterval(progressInterval);
            
            // Устанавливаем прогресс в 100% даже при ошибке
            document.querySelector('#upload-progress .progress-bar').style.width = '100%';
            document.getElementById('progress-percent').textContent = '100%';
            
            this.uploadProgress.style.display = 'none';
            utils.showError(this.analysisResult, 'Ошибка загрузки файла: ' + error.message);
        });
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
            // ИСПОЛЬЗУЕМ КОНКРЕТНЫЙ СЕЛЕКТОР
            document.querySelector('#upload-progress .progress-bar').style.width = `${progress}%`;
            document.getElementById('progress-percent').textContent = `${progress}%`;
        }, 200);
        
        return interval; // ← ВОЗВРАЩАЕМ ИНТЕРВАЛ ДЛЯ ОЧИСТКИ
    }
    
    /**
     * Показать результат анализа
     */
    showAnalysisResult(data) {
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
            html += this.renderCategoriesTable(
                analysis.top_categories_level_1,
                'ТОП-10 категорий (Уровень 1)',
                '(основные направления)',
                'fa-folder',
                'var(--accent-color)'
            );
        }
        
        // Уровень 2 (подкатегории)
        if (analysis.top_categories_level_2 && analysis.top_categories_level_2.length > 0) {
            html += this.renderCategoriesTable(
                analysis.top_categories_level_2,
                'ТОП-10 подкатегорий (Уровень 2)',
                '(детализация)',
                'fa-folder-open',
                '#5a4ae9'
            );
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
                        ${utils.escapeHtml(insight.message)}
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
                        ${utils.escapeHtml(aiAnalysis).replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
                    </div>
                </div>
                
                <button class="btn btn-sm copy-btn mt-3" onclick="dataAnalysis.copyAnalysis()">
                    <i class="fas fa-copy me-1"></i>Копировать анализ
                </button>
            `;
        }
        
        this.analysisResult.innerHTML = html;
        this.analysisResult.style.display = 'block';
        
        // Скролл к результату
        this.analysisResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    /**
     * Отобразить таблицу категорий
     */
    renderCategoriesTable(categories, title, subtitle, icon, iconColor) {
        let html = `
            <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                <i class="fas ${icon} me-2"></i>${title}
                <small class="text-muted ms-2" style="font-size: 0.8rem;">${subtitle}</small>
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
        
        categories.forEach((cat, i) => {
            const barWidth = Math.min(cat.percent, 100);
            html += `
                <tr>
                    <td><strong>${i + 1}</strong></td>
                    <td><i class="fas ${icon} me-2" style="color: ${iconColor};"></i>${utils.escapeHtml(cat.name)}</td>
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
        
        return html;
    }
    
    /**
     * Скопировать анализ
     */
    copyAnalysis() {
        const analysisText = document.querySelector('.card.bg-secondary .card-body').innerText;
        utils.copyToClipboard(analysisText).then(success => {
            if (success) {
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
            }
        });
    }
}

// Создаём экземпляр и инициализируем при загрузке
const dataAnalysis = new DataAnalysis();

document.addEventListener('DOMContentLoaded', () => {
    dataAnalysis.init();
});

// Экспортируем для глобального доступа
window.dataAnalysis = dataAnalysis;