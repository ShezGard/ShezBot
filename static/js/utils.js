// ==================== Вспомогательные функции ====================

/**
 * Экранирование HTML для предотвращения XSS
 */
function escapeHtml(unsafe) {
    if (!unsafe) return '';
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Показать уведомление (toast)
 */
function showToast(message) {
    const toastEl = document.getElementById('toast');
    const toastBody = document.getElementById('toast-body');
    
    if (toastBody && toastEl) {
        toastBody.textContent = message;
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
    }
}

/**
 * Копирование текста в буфер обмена
 */
function copyToClipboard(text) {
    return navigator.clipboard.writeText(text)
        .then(() => true)
        .catch(err => {
            console.error('Ошибка копирования:', err);
            return false;
        });
}

/**
 * Форматирование даты и времени
 */
function formatTime(date) {
    return `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
}

/**
 * Авто-ресайз текстареи
 */
function autoResizeTextarea(textarea) {
    if (textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = (textarea.scrollHeight) + 'px';
    }
}

/**
 * Проверка размера файла (возвращает ошибку или null)
 */
function validateFileSize(file, maxSizeMB = 100) {
    const maxSize = maxSizeMB * 1024 * 1024;
    if (file.size > maxSize) {
        return `Файл слишком большой! Максимальный размер: ${maxSizeMB} МБ. Текущий размер: ${(file.size / 1024 / 1024).toFixed(2)} МБ`;
    }
    return null;
}

/**
 * Показать ошибку в блоке
 */
function showError(container, message) {
    container.innerHTML = `
        <div class="alert alert-danger bg-dark border-danger text-white">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <strong>Ошибка:</strong> ${escapeHtml(message)}
        </div>
    `;
    container.style.display = 'block';
    container.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Показать успех в блоке
 */
function showSuccess(container, message) {
    container.innerHTML = `
        <div class="alert alert-success bg-dark border-success text-white">
            <i class="fas fa-check-circle me-2"></i>
            <strong>✅ ${escapeHtml(message)}</strong>
        </div>
    `;
    container.style.display = 'block';
}

// Экспортируем функции для использования в других файлах
window.utils = {
    escapeHtml,
    showToast,
    copyToClipboard,
    formatTime,
    autoResizeTextarea,
    validateFileSize,
    showError,
    showSuccess
};