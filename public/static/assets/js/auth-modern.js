// Modern Authentication JavaScript
(function() {
    'use strict';

    // Configuration
    const config = {
        passwordStrengthRegex: {
            weak: /^.{6,}$/,
            medium: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
            strong: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{10,}$/
        },
        emailRegex: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        phoneRegex: /^0(5)[0-9]{9}$/,
        animationDuration: 300
    };

    // DOM Elements Cache
    let elements = {};

    // Initialize on DOM Ready
    document.addEventListener('DOMContentLoaded', init);

    function init() {
        cacheElements();
        setupEventListeners();
        initializeAnimations();
        initializePasswordToggle();
        initializeFormValidation();
        initializeSocialLogin();
        initializeProgressSteps();
    }

    // Cache DOM Elements
    function cacheElements() {
        elements = {
            forms: document.querySelectorAll('form.auth-form'),
            passwordToggles: document.querySelectorAll('.password-toggle'),
            inputs: document.querySelectorAll('.form-control'),
            socialButtons: document.querySelectorAll('.btn-social'),
            progressSteps: document.querySelectorAll('.progress-steps'),
            submitButtons: document.querySelectorAll('button[type="submit"]')
        };
    }

    // Setup Event Listeners
    function setupEventListeners() {
        // Form submissions
        elements.forms.forEach(form => {
            form.addEventListener('submit', handleFormSubmit);
        });

        // Input focus effects
        elements.inputs.forEach(input => {
            input.addEventListener('focus', handleInputFocus);
            input.addEventListener('blur', handleInputBlur);
            input.addEventListener('input', handleInputChange);
        });

        // Social login buttons
        elements.socialButtons.forEach(button => {
            button.addEventListener('click', handleSocialLogin);
        });
    }

    // Initialize Animations
    function initializeAnimations() {
        // Add staggered animation to form elements
        const formElements = document.querySelectorAll('.form-group, .social-login, .auth-footer');
        formElements.forEach((element, index) => {
            element.style.animationDelay = `${index * 0.1}s`;
            element.classList.add('fade-in');
        });

        // Animate background shapes
        animateBackgroundShapes();
    }

    // Animate Background Shapes
    function animateBackgroundShapes() {
        const shapes = document.querySelectorAll('.shape');
        shapes.forEach(shape => {
            // Random initial position
            const randomX = Math.random() * window.innerWidth;
            const randomY = Math.random() * window.innerHeight;
            shape.style.transform = `translate(${randomX}px, ${randomY}px)`;
        });
    }

    // Password Toggle Functionality
    function initializePasswordToggle() {
        document.querySelectorAll('.input-group').forEach(group => {
            const toggle = group.querySelector('.input-group-text');
            const input = group.querySelector('input[type="password"], input[type="text"]');
            
            if (toggle && input && input.type === 'password' || (input && input.dataset.type === 'password')) {
                toggle.addEventListener('click', function() {
                    const icon = this.querySelector('i');
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

    // Form Validation
    function initializeFormValidation() {
        // Real-time validation for specific fields
        const emailInputs = document.querySelectorAll('input[type="email"]');
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        const phoneInputs = document.querySelectorAll('input[type="tel"]');

        emailInputs.forEach(input => {
            input.addEventListener('blur', validateEmail);
        });

        passwordInputs.forEach(input => {
            input.addEventListener('input', validatePassword);
        });

        phoneInputs.forEach(input => {
            input.addEventListener('input', formatPhoneNumber);
            input.addEventListener('blur', validatePhone);
        });
    }

    // Email Validation
    function validateEmail(e) {
        const input = e.target;
        const value = input.value.trim();
        const parent = input.closest('.form-group');
        let feedback = parent.querySelector('.validation-message');

        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'validation-message';
            parent.appendChild(feedback);
        }

        if (!value) {
            input.classList.remove('is-valid', 'is-invalid');
            feedback.textContent = '';
            return;
        }

        if (config.emailRegex.test(value)) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
            feedback.className = 'validation-message success';
            feedback.innerHTML = '<i class="bi bi-check-circle"></i> Geçerli e-posta adresi';
            
            // Check if email exists (simulated)
            checkEmailAvailability(value, input, feedback);
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            feedback.className = 'validation-message error';
            feedback.innerHTML = '<i class="bi bi-x-circle"></i> Geçerli bir e-posta adresi giriniz';
        }
    }

    // Check Email Availability (Simulated)
    async function checkEmailAvailability(email, input, feedback) {
        feedback.innerHTML = '<span class="spinner"></span> Kontrol ediliyor...';
        
        // Simulate API call
        setTimeout(() => {
            const exists = Math.random() > 0.7; // 30% chance email exists
            if (exists) {
                input.classList.add('is-invalid');
                input.classList.remove('is-valid');
                feedback.className = 'validation-message error';
                feedback.innerHTML = '<i class="bi bi-x-circle"></i> Bu e-posta adresi zaten kullanımda';
            } else {
                input.classList.add('is-valid');
                input.classList.remove('is-invalid');
                feedback.className = 'validation-message success';
                feedback.innerHTML = '<i class="bi bi-check-circle"></i> E-posta adresi kullanılabilir';
            }
        }, 1000);
    }

    // Password Validation with Strength Meter
    function validatePassword(e) {
        const input = e.target;
        const value = input.value;
        const parent = input.closest('.form-group');
        let strengthMeter = parent.querySelector('.password-strength');

        if (!strengthMeter) {
            strengthMeter = createPasswordStrengthMeter(parent);
        }

        const strength = calculatePasswordStrength(value);
        updatePasswordStrengthMeter(strengthMeter, strength);

        // Update input validation state
        if (strength.score >= 2) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
        } else if (value.length > 0) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
        } else {
            input.classList.remove('is-valid', 'is-invalid');
        }
    }

    // Create Password Strength Meter
    function createPasswordStrengthMeter(parent) {
        const meter = document.createElement('div');
        meter.className = 'password-strength';
        meter.innerHTML = `
            <div class="strength-meter">
                <div class="strength-meter-fill"></div>
            </div>
            <div class="strength-text"></div>
        `;
        parent.appendChild(meter);
        return meter;
    }

    // Calculate Password Strength
    function calculatePasswordStrength(password) {
        let score = 0;
        let feedback = [];

        if (!password) {
            return { score: 0, feedback: ['Şifre giriniz'], text: '' };
        }

        // Length check
        if (password.length >= 6) score++;
        if (password.length >= 10) score++;
        if (password.length >= 14) score++;

        // Complexity checks
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/\d/.test(password)) score++;
        if (/[@$!%*?&]/.test(password)) score++;

        // Determine strength level
        let strengthText = '';
        let strengthClass = '';
        
        if (score <= 2) {
            strengthText = 'Zayıf';
            strengthClass = 'weak';
        } else if (score <= 4) {
            strengthText = 'Orta';
            strengthClass = 'medium';
        } else if (score <= 6) {
            strengthText = 'Güçlü';
            strengthClass = 'strong';
        } else {
            strengthText = 'Çok Güçlü';
            strengthClass = 'very-strong';
        }

        return {
            score: Math.min(score, 7),
            text: strengthText,
            class: strengthClass
        };
    }

    // Update Password Strength Meter
    function updatePasswordStrengthMeter(meter, strength) {
        const fill = meter.querySelector('.strength-meter-fill');
        const text = meter.querySelector('.strength-text');
        
        // Update fill width and color
        const percentage = (strength.score / 7) * 100;
        fill.style.width = `${percentage}%`;
        
        // Remove all classes and add new one
        fill.className = 'strength-meter-fill';
        fill.classList.add(strength.class);
        
        // Update text
        text.textContent = strength.text;
        text.className = 'strength-text';
        text.classList.add(strength.class);
    }

    // Phone Number Formatting
    function formatPhoneNumber(e) {
        const input = e.target;
        let value = input.value.replace(/\D/g, '');
        
        if (value && value.charAt(0) !== '0') {
            value = '0' + value;
        }
        
        value = value.substring(0, 11);
        
        if (value.length > 0) {
            let formatted = value.substring(0, 4);
            if (value.length > 4) {
                formatted += ' ' + value.substring(4, 7);
            }
            if (value.length > 7) {
                formatted += ' ' + value.substring(7, 9);
            }
            if (value.length > 9) {
                formatted += ' ' + value.substring(9, 11);
            }
            input.value = formatted;
        }
    }

    // Phone Validation
    function validatePhone(e) {
        const input = e.target;
        const value = input.value.replace(/\D/g, '');
        const parent = input.closest('.form-group');
        let feedback = parent.querySelector('.validation-message');

        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'validation-message';
            parent.appendChild(feedback);
        }

        if (!value) {
            input.classList.remove('is-valid', 'is-invalid');
            feedback.textContent = '';
            return;
        }

        if (config.phoneRegex.test(value)) {
            input.classList.add('is-valid');
            input.classList.remove('is-invalid');
            feedback.className = 'validation-message success';
            feedback.innerHTML = '<i class="bi bi-check-circle"></i> Geçerli telefon numarası';
        } else {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            feedback.className = 'validation-message error';
            feedback.innerHTML = '<i class="bi bi-x-circle"></i> Geçerli bir telefon numarası giriniz';
        }
    }

    // Handle Input Focus
    function handleInputFocus(e) {
        const parent = e.target.closest('.form-group');
        if (parent) {
            parent.classList.add('focused');
        }
    }

    // Handle Input Blur
    function handleInputBlur(e) {
        const parent = e.target.closest('.form-group');
        if (parent) {
            parent.classList.remove('focused');
        }
    }

    // Handle Input Change
    function handleInputChange(e) {
        const input = e.target;
        const parent = input.closest('.form-group');
        
        if (input.value) {
            parent.classList.add('has-value');
        } else {
            parent.classList.remove('has-value');
        }
    }

    // Handle Form Submit
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        
        // Validate all inputs
        const inputs = form.querySelectorAll('.form-control[required]');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!input.value.trim()) {
                input.classList.add('is-invalid');
                isValid = false;
            }
        });
        
        if (!isValid) {
            showToast('Lütfen tüm zorunlu alanları doldurun', 'error');
            return;
        }
        
        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner"></span> İşleniyor...';
        
        // Simulate form submission
        setTimeout(() => {
            // Reset button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
            
            // Show success message
            showToast('İşlem başarıyla tamamlandı!', 'success');
            
            // Actually submit the form
            form.submit();
        }, 2000);
    }

    // Social Login Handler
    function handleSocialLogin(e) {
        e.preventDefault();
        const button = e.currentTarget;
        const provider = button.dataset.provider;
        
        // Add loading state
        button.classList.add('loading');
        button.disabled = true;
        
        // Show toast
        showToast(`${provider} ile giriş yapılıyor...`, 'info');
        
        // Simulate OAuth redirect
        setTimeout(() => {
            window.location.href = `/auth/oauth/${provider}`;
        }, 1000);
    }

    // Progress Steps
    function initializeProgressSteps() {
        const stepsContainer = document.querySelector('.progress-steps');
        if (!stepsContainer) return;
        
        const steps = stepsContainer.querySelectorAll('.step');
        let currentStep = 0;
        
        // Find current active step
        steps.forEach((step, index) => {
            if (step.classList.contains('active')) {
                currentStep = index;
            }
        });
        
        // Update progress line
        updateProgressLine(stepsContainer, currentStep, steps.length);
    }

    // Update Progress Line
    function updateProgressLine(container, currentStep, totalSteps) {
        let progressLine = container.querySelector('.progress-line');
        if (!progressLine) {
            progressLine = document.createElement('div');
            progressLine.className = 'progress-line';
            container.appendChild(progressLine);
        }
        
        const percentage = (currentStep / (totalSteps - 1)) * 100;
        progressLine.style.width = `${percentage}%`;
    }

    // Toast Notification
    function showToast(message, type = 'info') {
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast ${type} show`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="bi bi-${getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }

    // Create Toast Container
    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    // Get Toast Icon
    function getToastIcon(type) {
        const icons = {
            success: 'check-circle-fill',
            error: 'x-circle-fill',
            warning: 'exclamation-triangle-fill',
            info: 'info-circle-fill'
        };
        return icons[type] || icons.info;
    }

    // Add CSS for password strength meter
    const style = document.createElement('style');
    style.textContent = `
        .password-strength {
            margin-top: 10px;
        }
        
        .strength-meter {
            height: 4px;
            background: var(--gray-200);
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 5px;
        }
        
        .strength-meter-fill {
            height: 100%;
            transition: all 0.3s ease;
            border-radius: 2px;
        }
        
        .strength-meter-fill.weak {
            width: 25%;
            background: var(--danger-color);
        }
        
        .strength-meter-fill.medium {
            width: 50%;
            background: var(--warning-color);
        }
        
        .strength-meter-fill.strong {
            width: 75%;
            background: var(--info-color);
        }
        
        .strength-meter-fill.very-strong {
            width: 100%;
            background: var(--success-color);
        }
        
        .strength-text {
            font-size: 12px;
            font-weight: 600;
        }
        
        .strength-text.weak {
            color: var(--danger-color);
        }
        
        .strength-text.medium {
            color: var(--warning-color);
        }
        
        .strength-text.strong {
            color: var(--info-color);
        }
        
        .strength-text.very-strong {
            color: var(--success-color);
        }
        
        .form-group.focused .form-label {
            color: var(--primary-color);
        }
        
        .toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        }
        
        .toast {
            min-width: 300px;
            margin-bottom: 10px;
            padding: 16px;
            border-radius: 8px;
            color: white;
            display: flex;
            align-items: center;
            justify-content: space-between;
            animation: slideInRight 0.3s ease;
        }
        
        .toast.hide {
            animation: slideOutRight 0.3s ease;
        }
        
        .toast-content {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .toast-close {
            background: none;
            border: none;
            color: white;
            cursor: pointer;
            padding: 0;
            font-size: 20px;
        }
        
        .toast.success {
            background: var(--success-color);
        }
        
        .toast.error {
            background: var(--danger-color);
        }
        
        .toast.warning {
            background: var(--warning-color);
        }
        
        .toast.info {
            background: var(--info-color);
        }
        
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
        
        .btn.loading {
            position: relative;
            color: transparent;
        }
        
        .btn.loading::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            top: 50%;
            left: 50%;
            margin-left: -10px;
            margin-top: -10px;
            border: 2px solid var(--gray-300);
            border-radius: 50%;
            border-top-color: var(--primary-color);
            animation: spin 1s linear infinite;
        }
        
        .progress-line {
            position: absolute;
            top: 20px;
            left: 0;
            height: 2px;
            background: var(--primary-color);
            transition: width 0.3s ease;
            z-index: 0;
        }
    `;
    document.head.appendChild(style);

    // Export functions for external use
    window.AuthModern = {
        showToast,
        validateEmail,
        validatePassword,
        validatePhone,
        formatPhoneNumber
    };

})();