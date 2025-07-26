/**
 * PofuAi App JavaScript
 * Ana uygulama JavaScript dosyası
 */

(function() {
    'use strict';
    
    // DOM yüklendiğinde çalışacak fonksiyonlar
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });
    
    function initializeApp() {
        // Tema değiştirme
        initializeThemeSwitcher();
        
        // Sidebar toggle
        initializeSidebarToggle();
        
        // Form validasyonları
        initializeFormValidations();
        
        // Toast bildirimleri
        initializeToastNotifications();
        
        // Password show/hide
        initializePasswordToggles();
    }
    
    function initializeThemeSwitcher() {
        const themeSwitchers = document.querySelectorAll('[data-theme]');
        themeSwitchers.forEach(switcher => {
            switcher.addEventListener('click', function(e) {
                e.preventDefault();
                const theme = this.getAttribute('data-theme');
                setTheme(theme);
            });
        });
    }
    
    function setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Tema değişikliği eventi
        const event = new CustomEvent('themeChanged', { detail: { theme: theme } });
        document.dispatchEvent(event);
    }
    
    function initializeSidebarToggle() {
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        const sidebar = document.querySelector('.sidebar');
        
        if (sidebarToggle && sidebar) {
            sidebarToggle.addEventListener('click', function() {
                sidebar.classList.toggle('collapsed');
                localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
            });
        }
    }
    
    function initializeFormValidations() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!validateForm(this)) {
                    e.preventDefault();
                }
            });
        });
    }
    
    function validateForm(form) {
        let isValid = true;
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                showFieldError(input, 'Bu alan zorunludur');
                isValid = false;
            } else {
                clearFieldError(input);
            }
        });
        
        return isValid;
    }
    
    function showFieldError(field, message) {
        clearFieldError(field);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.classList.add('is-invalid');
        field.parentNode.appendChild(errorDiv);
    }
    
    function clearFieldError(field) {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    function initializeToastNotifications() {
        // Toast bildirimleri için global fonksiyon
        window.showToast = function(message, type = 'info', duration = 5000) {
            const toast = document.createElement('div');
            toast.className = `toast align-items-center text-white bg-${type} border-0`;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'assertive');
            toast.setAttribute('aria-atomic', 'true');
            
            toast.innerHTML = `
                <div class="d-flex">
                    <div class="toast-body">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            `;
            
            const toastContainer = document.querySelector('.toast-container') || createToastContainer();
            toastContainer.appendChild(toast);
            
            const bsToast = new bootstrap.Toast(toast, { delay: duration });
            bsToast.show();
            
            // Otomatik temizlik
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.remove();
                }
            }, duration + 1000);
        };
    }
    
    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
    
    function initializePasswordToggles() {
        const passwordToggles = document.querySelectorAll('[id^="show_hide_"]');
        passwordToggles.forEach(toggle => {
            const link = toggle.querySelector('a');
            const input = toggle.querySelector('input');
            const icon = link.querySelector('i');
            
            if (link && input && icon) {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    
                    if (input.type === 'password') {
                        input.type = 'text';
                        icon.classList.remove('bi-eye-slash-fill');
                        icon.classList.add('bi-eye-fill');
                    } else {
                        input.type = 'password';
                        icon.classList.remove('bi-eye-fill');
                        icon.classList.add('bi-eye-slash-fill');
                    }
                });
            }
        });
    }
    
    // Global utility fonksiyonları
    window.PofuAi = {
        showToast: window.showToast,
        setTheme: setTheme,
        validateForm: validateForm
    };
    
})(); 