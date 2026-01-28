// ==================== Сравнение периодов ====================

class PeriodComparison {
    constructor() {
        this.uploadArea1 = document.getElementById('upload-area-1');
        this.fileInput1 = document.getElementById('file-input-1');
        this.fileName1 = document.getElementById('file-name-1');
        
        this.uploadArea2 = document.getElementById('upload-area-2');
        this.fileInput2 = document.getElementById('file-input-2');
        this.fileName2 = document.getElementById('file-name-2');
        
        this.compareBtn = document.getElementById('compare-btn');
        this.compareProgress = document.getElementById('compare-progress');
        this.comparisonResult = document.getElementById('comparison-result');
        
        this.file1 = null;
        this.file2 = null;
    }
    
    /**
     * Инициализация
     */
    init() {
        if (!this.uploadArea1 || !this.uploadArea2) return;
        
        // Обработчики для первого файла
        this.uploadArea1.addEventListener('click', () => this.fileInput1.click());
        this.fileInput1.addEventListener('change', () => this.handleFileSelect1());
        
        this.uploadArea1.addEventListener('dragover', (e) => this.handleDragOver(e, this.uploadArea1));
        this.uploadArea1.addEventListener('dragleave', () => this.handleDragLeave(this.uploadArea1));
        this.uploadArea1.addEventListener('drop', (e) => this.handleDrop(e, this.fileInput1, this.handleFileSelect1.bind(this)));
        
        // Обработчики для второго файла
        this.uploadArea2.addEventListener('click', () => this.fileInput2.click());
        this.fileInput2.addEventListener('change', () => this.handleFileSelect2());
        
        this.uploadArea2.addEventListener('dragover', (e) => this.handleDragOver(e, this.uploadArea2));
        this.uploadArea2.addEventListener('dragleave', () => this.handleDragLeave(this.uploadArea2));
        this.uploadArea2.addEventListener('drop', (e) => this.handleDrop(e, this.fileInput2, this.handleFileSelect2.bind(this)));
        
        // Кнопка сравнения
        this.compareBtn?.addEventListener('click', () => this.comparePeriods());
    }
    
    /**
     * Обработчик перетаскивания
     */
    handleDragOver(e, area) {
        e.preventDefault();
        area.style.borderColor = 'var(--accent-color)';
        area.style.backgroundColor = 'rgba(121, 184, 255, 0.1)';
    }
    
    /**
     * Обработчик выхода курсора
     */
    handleDragLeave(area) {
        area.style.borderColor = 'var(--border-color)';
        area.style.backgroundColor = '';
    }
    
    /**
     * Обработчик сброса файла
     */
    handleDrop(e, fileInput, callback) {
        e.preventDefault();
        e.target.closest('.upload-area').style.borderColor = 'var(--border-color)';
        e.target.closest('.upload-area').style.backgroundColor = '';
        
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            callback();
        }
    }
    
    /**
     * Выбор первого файла
     */
    handleFileSelect1() {
        this.file1 = this.fileInput1.files[0];
        if (this.file1) {
            this.fileName1.textContent = this.file1.name;
            this.fileName1.classList.add('has-file');
            this.checkFilesReady();
        }
    }
    
    /**
     * Выбор второго файла
     */
    handleFileSelect2() {
        this.file2 = this.fileInput2.files[0];
        if (this.file2) {
            this.fileName2.textContent = this.file2.name;
            this.fileName2.classList.add('has-file');
            this.checkFilesReady();
        }
    }
    
    /**
     * Проверка готовности файлов
     */
    checkFilesReady() {
        if (this.file1 && this.file2) {
            this.compareBtn.disabled = false;
        } else {
            this.compareBtn.disabled = true;
        }
    }
    
    /**
     * Сравнить периоды
     */
    comparePeriods() {
        if (!this.file1 || !this.file2) {
            utils.showToast('Загрузите оба файла для сравнения');
            return;
        }
        
        // Проверка размера файлов
        const maxSize = 100 * 1024 * 1024;
        if (this.file1.size > maxSize || this.file2.size > maxSize) {
            const largeFile = this.file1.size > maxSize ? this.file1.name : this.file2.name;
            const size = this.file1.size > maxSize ? (this.file1.size / 1024 / 1024).toFixed(2) : (this.file2.size / 1024 / 1024).toFixed(2);
            utils.showError(this.comparisonResult, `Файл "${largeFile}" слишком большой! Максимальный размер: 100 МБ. Текущий размер: ${size} МБ`);
            return;
        }
        
        const formData = new FormData();
        formData.append('file1', this.file1);
        formData.append('file2', this.file2);
        
        // Показываем прогресс
        this.compareProgress.style.display = 'block';
        this.comparisonResult.style.display = 'none';
        
        // Имитация прогресса
        const progressInterval = this.startProgressSimulation();
        
        fetch('/api/compare', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            clearInterval(progressInterval);
            document.querySelector('#compare-progress .progress-bar').style.width = '100%';
            document.getElementById('compare-progress-percent').textContent = '100%';
            return response.json();
        })
        .then(data => {
            setTimeout(() => {
                this.compareProgress.style.display = 'none';
                
                if (data.error) {
                    utils.showError(this.comparisonResult, data.error);
                } else {
                    this.showComparisonResult(data);
                }
            }, 300);
        })
        .catch(error => {
            clearInterval(progressInterval);
            this.compareProgress.style.display = 'none';
            utils.showError(this.comparisonResult, 'Ошибка сравнения: ' + error.message);
        });
    }
    
    /**
     * Запустить симуляцию прогресса
     */
    startProgressSimulation() {
        let progress = 0;
        return setInterval(() => {
            progress += 3;
            if (progress > 90) clearInterval(progress);
            document.querySelector('#compare-progress .progress-bar').style.width = `${progress}%`;
            document.getElementById('compare-progress-percent').textContent = `${progress}%`;
        }, 150);
    }
    
    /**
     * Показать результат сравнения
     */
    showComparisonResult(data) {
        const comparison = data.comparison;
        const aiComparison = data.ai_comparison;
        
        let html = `
            <div class="alert alert-success bg-dark border-success text-white">
                <i class="fas fa-check-circle me-2"></i>
                <strong>✅ Сравнение завершено!</strong> 
                ${data.filename1} vs ${data.filename2}
            </div>
        `;
        
        // Сводка по общим метрикам
        html += this.renderComparisonSummary(comparison);
        
        // ТОП-5 роста
        if (comparison.top_growers && comparison.top_growers.length > 0) {
            html += this.renderTrendTable(
                comparison.top_growers,
                'ТОП-5 категорий с наибольшим ростом',
                'fa-arrow-up',
                'var(--success)',
                'up'
            );
        }
        
        // ТОП-5 падения
        if (comparison.top_decliners && comparison.top_decliners.length > 0) {
            html += this.renderTrendTable(
                comparison.top_decliners,
                'ТОП-5 категорий с наибольшим падением',
                'fa-arrow-down',
                'var(--danger)',
                'down'
            );
        }
        
        // Новые категории
        if (comparison.new_categories && comparison.new_categories.length > 0) {
            html += this.renderCategoryBadges(
                comparison.new_categories,
                'Новые категории (появились во 2 периоде)',
                'fa-plus-circle',
                'var(--success)',
                'new'
            );
        }
        
        // Исчезнувшие категории
        if (comparison.disappeared_categories && comparison.disappeared_categories.length > 0) {
            html += this.renderCategoryBadges(
                comparison.disappeared_categories,
                'Исчезнувшие категории (были в 1 периоде)',
                'fa-minus-circle',
                'var(--danger)',
                'disappeared'
            );
        }
        
        // AI-анализ сравнения
        if (aiComparison) {
            html += `
                <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                    <i class="fas fa-robot me-2"></i>AI-анализ сравнения и рекомендации
                </h5>
                <div class="card bg-secondary border-secondary">
                    <div class="card-body">
                        ${utils.escapeHtml(aiComparison).replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}
                    </div>
                </div>
                
                <button class="btn btn-sm copy-btn mt-3" onclick="periodComparison.copyComparison()">
                    <i class="fas fa-copy me-1"></i>Копировать анализ сравнения
                </button>
            `;
        }
        
        this.comparisonResult.innerHTML = html;
        this.comparisonResult.style.display = 'block';
        
        // Скролл к результату
        this.comparisonResult.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    /**
     * Отобразить сводку сравнения
     */
    renderComparisonSummary(comparison) {
        const totalChange = comparison.summary.total_change;
        const totalChangePercent = comparison.summary.total_change_percent;
        const totalTrendClass = totalChange > 0 ? 'trend-up' : totalChange < 0 ? 'trend-down' : '';
        const totalTrendIcon = totalChange > 0 ? '↑' : totalChange < 0 ? '↓' : '→';
        
        const uniqueChange = comparison.summary.unique_change;
        const uniqueChangePercent = comparison.summary.unique_change_percent;
        const uniqueTrendClass = uniqueChange > 0 ? 'trend-up' : uniqueChange < 0 ? 'trend-down' : '';
        const uniqueTrendIcon = uniqueChange > 0 ? '↑' : uniqueChange < 0 ? '↓' : '→';
        
        return `
            <div class="comparison-header">
                <h4><i class="fas fa-chart-line me-2"></i>Общая динамика</h4>
                <p class="mb-0">Сравнение количества обращений и уникальных категорий между периодами</p>
            </div>
            
            <div class="comparison-summary">
                <div class="summary-card ${totalTrendClass}">
                    <span class="metric-label">Обращений</span>
                    <span class="metric-value">${comparison.summary.period1_total} → ${comparison.summary.period2_total}</span>
                    <span class="metric-label">${totalTrendIcon} ${Math.abs(totalChange)} (${totalChangePercent}%)</span>
                </div>
                
                <div class="summary-card ${uniqueTrendClass}">
                    <span class="metric-label">Уникальных категорий</span>
                    <span class="metric-value">${comparison.summary.period1_unique} → ${comparison.summary.period2_unique}</span>
                    <span class="metric-label">${uniqueTrendIcon} ${Math.abs(uniqueChange)} (${uniqueChangePercent}%)</span>
                </div>
            </div>
        `;
    }
    
    /**
     * Отобразить таблицу трендов
     */
    renderTrendTable(categories, title, icon, iconColor, trendType) {
        let html = `
            <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                <i class="fas ${icon} me-2" style="color: ${iconColor};"></i>${title}
            </h5>
            <div class="table-responsive">
                <table class="table table-dark table-striped comparison-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Категория</th>
                            <th>Период 1</th>
                            <th>Период 2</th>
                            <th>Изменение</th>
                            <th>% ${trendType === 'up' ? 'роста' : 'падения'}</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        categories.forEach((cat, i) => {
            const sign = trendType === 'up' ? '+' : '';
            const colorClass = trendType === 'up' ? 'text-success' : 'text-danger';
            const badgeClass = trendType === 'up' ? 'up' : 'down';
            const percentValue = trendType === 'up' ? cat.change_percent : Math.abs(cat.change_percent);
            
            html += `
                <tr>
                    <td><strong>${i + 1}</strong></td>
                    <td><i class="fas fa-folder me-2" style="color: ${iconColor};"></i>${utils.escapeHtml(cat.name)}</td>
                    <td>${cat.period1_count}</td>
                    <td>${cat.period2_count}</td>
                    <td><span class="${colorClass}">${sign}${cat.change}</span></td>
                    <td><span class="trend-badge ${badgeClass}">${trendType === 'up' ? '↗️' : '↘️'} ${percentValue}%</span></td>
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
     * Отобразить бейджи категорий
     */
    renderCategoryBadges(categories, title, icon, iconColor, type) {
        let html = `
            <h5 class="mt-4 mb-3" style="color: var(--accent-color);">
                <i class="fas ${icon} me-2" style="color: ${iconColor};"></i>${title}
            </h5>
            <div class="d-flex flex-wrap gap-2 mb-3">
        `;
        
        categories.forEach(cat => {
            const countField = type === 'new' ? 'period2_count' : 'period1_count';
            const countLabel = type === 'new' ? 'обращений' : 'было';
            
            html += `
                <span class="badge category-badge ${type} px-3 py-2">
                    <i class="fas ${type === 'new' ? 'fa-plus' : 'fa-minus'} me-1"></i>${utils.escapeHtml(cat.name)}
                    <span class="ms-2">(${countLabel} ${cat[countField]})</span>
                </span>
            `;
        });
        
        html += `</div>`;
        
        return html;
    }
    
    /**
     * Скопировать анализ сравнения
     */
    copyComparison() {
        const comparisonText = document.querySelector('#comparison-result .card.bg-secondary .card-body').innerText;
        utils.copyToClipboard(comparisonText).then(success => {
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
const periodComparison = new PeriodComparison();

document.addEventListener('DOMContentLoaded', () => {
    periodComparison.init();
});

// Экспортируем для глобального доступа
window.periodComparison = periodComparison;