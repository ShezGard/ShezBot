// ==================== Точка входа приложения ====================
// Этот файл подключается ПОСЛЕДНИМ и инициализирует всё приложение

console.log('🚀 ShezGard Bot загружается...');

// Проверка загрузки всех модулей
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM загружен');
    
    // Проверяем наличие всех необходимых модулей
    const modules = {
        'utils': window.utils,
        'navigation': window.navigation,
        'chat': window.chat,
        'dataAnalysis': window.dataAnalysis,
        'periodComparison': window.periodComparison
    };
    
    Object.keys(modules).forEach(moduleName => {
        if (modules[moduleName]) {
            console.log(`✅ Модуль "${moduleName}" загружен`);
        } else {
            console.warn(`⚠️ Модуль "${moduleName}" не найден`);
        }
    });
    
    // Инициализация настроек (если есть)
    initSettings();
    
    console.log('🎉 ShezGard Bot готов к работе!');
});

/**
 * Инициализация настроек
 */
function initSettings() {
    const temperatureRange = document.getElementById('temperature-range');
    const temperatureValue = document.getElementById('temperature-value');
    
    if (temperatureRange && temperatureValue) {
        temperatureRange.addEventListener('input', function() {
            temperatureValue.textContent = this.value;
        });
    }
    
    // Кнопка сохранения настроек
    const saveSettingsBtn = document.querySelector('#settings .btn-success');
    if (saveSettingsBtn) {
        saveSettingsBtn.addEventListener('click', function() {
            const model = document.getElementById('model-select')?.value;
            const temperature = document.getElementById('temperature-range')?.value;
            
            // Здесь можно сохранить настройки в localStorage или отправить на сервер
            localStorage.setItem('shezgard_model', model);
            localStorage.setItem('shezgard_temperature', temperature);
            
            utils.showToast('Настройки сохранены!');
        });
    }
}

/**
 * Глобальные обработчики ошибок
 */
window.addEventListener('error', function(event) {
    console.error('❌ Глобальная ошибка:', event.error);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('❌ Необработанное промис-исключение:', event.reason);
});

// Экспортируем глобальные функции для удобства
window.app = {
    init: function() {
        console.log('🔄 Ручная инициализация приложения...');
        // Здесь можно добавить дополнительную логику инициализации
    },
    reload: function() {
        location.reload();
    }
};