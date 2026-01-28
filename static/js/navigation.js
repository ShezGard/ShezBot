// ==================== Навигация по вкладкам ====================

/**
 * Инициализация навигации
 */
function initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link[data-tab]');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Убираем активный класс у всех ссылок
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Добавляем активный класс текущей ссылке
            this.classList.add('active');
            
            // Скрываем все вкладки
            tabContents.forEach(tab => tab.classList.remove('active'));
            
            // Показываем нужную вкладку
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            
            // Если переключились на чат, фокусируем поле ввода
            if (tabId === 'epic-generator') {
                setTimeout(() => {
                    const userInput = document.getElementById('user-input');
                    if (userInput) userInput.focus();
                }, 100);
            }
            
            // Скролл наверх при переключении вкладки
            window.scrollTo(0, 0);
        });
    });
}

// Инициализируем навигацию при загрузке страницы
document.addEventListener('DOMContentLoaded', initNavigation);

// Экспортируем для использования в других файлах
window.navigation = {
    init: initNavigation
};