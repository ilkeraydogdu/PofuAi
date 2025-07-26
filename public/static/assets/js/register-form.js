document.addEventListener('DOMContentLoaded', function() {
    // Form elementlerini seç
    const nameInput = document.getElementById('inputName');
    const emailInput = document.getElementById('inputEmailAddress');
    const phoneInput = document.getElementById('inputPhone');
    const termsCheckbox = document.getElementById('flexSwitchCheckChecked');
    const captchaInput = document.getElementById('captchaAnswer');
    const submitButton = document.getElementById('submitButton');
    const securityVerification = document.getElementById('securityVerification');
    
    // Doğrulama mesajı elementleri
    const nameValidation = document.getElementById('nameValidation');
    const emailValidation = document.getElementById('emailValidation');
    const phoneValidation = document.getElementById('phoneValidation');
    
    // Domain kontrolü için zamanlayıcı
    let domainCheckTimeout = null;
    
    // Captcha doğrulama durumu
    let isCaptchaVerified = false;
    
    // Captcha oluştur
    generateCaptcha();
    
    // Form alanlarını izle
    nameInput.addEventListener('input', checkFormProgress);
    nameInput.addEventListener('blur', validateName);
    emailInput.addEventListener('input', checkFormProgress);
    emailInput.addEventListener('blur', validateEmail);
    phoneInput.addEventListener('input', formatPhoneNumber);
    phoneInput.addEventListener('blur', validatePhone);
    termsCheckbox.addEventListener('change', validateForm);
    captchaInput.addEventListener('input', validateCaptcha);
    
    // Form gönderilmeden önce kontrol
    document.getElementById('registerForm').addEventListener('submit', function(event) {
        if (!isCaptchaVerified) {
            event.preventDefault();
            showToast('Lütfen güvenlik doğrulamasını tamamlayın.', 'error');
        }
    });
    
    // Captcha doğrulama
    function validateCaptcha() {
        const captchaAnswer = captchaInput.value.trim();
        const expectedAnswer = document.getElementById('captchaExpectedAnswer').value;
        
        if (captchaAnswer === expectedAnswer) {
            // Doğrulama başarılı
            isCaptchaVerified = true;
            securityVerification.style.display = 'none';
            captchaInput.classList.add('is-valid');
            captchaInput.classList.remove('is-invalid');
            showToast('Güvenlik doğrulaması başarılı!', 'info');
        } else if (captchaAnswer.length >= expectedAnswer.length) {
            // Yanlış cevap
            isCaptchaVerified = false;
            captchaInput.classList.add('is-invalid');
            captchaInput.classList.remove('is-valid');
        }
        
        validateForm();
    }
    
    // Form ilerleme kontrolü - güvenlik doğrulamasını göster/gizle
    function checkFormProgress() {
        const nameValid = isValidName(nameInput.value);
        const emailValid = isValidEmail(emailInput.value);
        const phoneValid = isValidPhone(phoneInput.value);
        
        // Tüm form alanları doğru doldurulduğunda güvenlik kodu alanını aç
        if (nameValid && emailValid && phoneValid) {
            securityVerification.style.display = 'block';
            showToast('Form doğrulandı! Güvenlik kodunu girin.', 'info');
        } else {
            securityVerification.style.display = 'none';
            isCaptchaVerified = false;
            captchaInput.classList.remove('is-valid');
        }
        
        validateForm();
    }
    
    // Form doğrulama
    function validateForm() {
        const nameValid = isValidName(nameInput.value);
        const emailValid = isValidEmail(emailInput.value);
        const phoneValid = isValidPhone(phoneInput.value);
        const termsAccepted = termsCheckbox.checked;
        
        // Gönder butonu durumunu güncelle
        submitButton.disabled = !(nameValid && emailValid && phoneValid && termsAccepted && isCaptchaVerified);
        
        if (submitButton.disabled) {
            submitButton.classList.add('opacity-50');
        } else {
            submitButton.classList.remove('opacity-50');
        }
    }
    
    // Ad soyad doğrulama
    function validateName() {
        const value = nameInput.value.trim();
        const valid = isValidName(value);
        
        if (!value) {
            nameValidation.textContent = '';
            nameInput.classList.remove('is-valid', 'is-invalid');
        } else if (valid) {
            nameValidation.textContent = '';
            nameValidation.style.color = '#198754';
            nameInput.classList.add('is-valid');
            nameInput.classList.remove('is-invalid');
        } else {
            nameValidation.textContent = 'Ad Soyad en az iki kelimeden oluşmalı ve her kelime en az 3 karakter olmalıdır.';
            nameValidation.style.color = '#dc3545';
            nameInput.classList.add('is-invalid');
            nameInput.classList.remove('is-valid');
        }
        
        checkFormProgress();
    }
    
    // E-posta doğrulama
    function validateEmail() {
        const value = emailInput.value.trim();
        const basicValid = isValidEmail(value);
        
        if (!value) {
            emailValidation.textContent = '';
            emailInput.classList.remove('is-valid', 'is-invalid');
            checkFormProgress();
            return;
        }
        
        if (!basicValid) {
            emailValidation.textContent = 'Geçerli bir e-posta adresi giriniz.';
            emailValidation.style.color = '#dc3545';
            emailInput.classList.add('is-invalid');
            emailInput.classList.remove('is-valid');
            checkFormProgress();
            return;
        }
        
        // Domain kontrolünü hızlandır - önceki zamanlayıcıyı iptal et
        if (domainCheckTimeout) {
            clearTimeout(domainCheckTimeout);
        }
        
        // Domain kontrolü yap
        const domain = value.split('@')[1];
        
        // DNS kontrolü için loading göster
        emailValidation.textContent = 'Domain kontrol ediliyor...';
        emailValidation.style.color = '#0d6efd';
        
        // 300ms gecikme ile domain kontrolü yap (hızlı yazarken sürekli istek göndermemek için)
        domainCheckTimeout = setTimeout(() => {
            checkDomainExists(domain)
                .then(exists => {
                    if (exists) {
                        emailValidation.textContent = '';
                        emailValidation.style.color = '#198754';
                        emailInput.classList.add('is-valid');
                        emailInput.classList.remove('is-invalid');
                    } else {
                        emailValidation.textContent = 'Bu e-posta domaininin MX kaydı bulunamadı.';
                        emailValidation.style.color = '#dc3545';
                        emailInput.classList.add('is-invalid');
                        emailInput.classList.remove('is-valid');
                    }
                    checkFormProgress();
                })
                .catch(error => {
                    // Hata durumunda sadece temel doğrulama yap
                    emailValidation.textContent = '';
                    emailValidation.style.color = '#198754';
                    emailInput.classList.add('is-valid');
                    emailInput.classList.remove('is-invalid');
                    checkFormProgress();
                });
        }, 300);
    }
    
    // Domain varlığını kontrol et
    async function checkDomainExists(domain) {
        try {
            // Cache kontrolü - localStorage'da domain sonucu var mı?
            const cachedResult = localStorage.getItem(`domain_${domain}`);
            if (cachedResult !== null) {
                return cachedResult === 'true';
            }
            
            const response = await fetch(`/auth/check-domain?domain=${encodeURIComponent(domain)}`);
            const data = await response.json();
            
            // Sonucu cache'le (1 saat geçerli)
            localStorage.setItem(`domain_${domain}`, data.exists);
            setTimeout(() => {
                localStorage.removeItem(`domain_${domain}`);
            }, 3600000); // 1 saat
            
            return data.exists;
        } catch (error) {
            console.error('Domain kontrolü sırasında hata oluştu:', error);
            return true; // Hata durumunda geçerli kabul et
        }
    }
    
    // Telefon doğrulama
    function validatePhone() {
        const value = phoneInput.value;
        const valid = isValidPhone(value);
        
        if (!value) {
            phoneValidation.textContent = '';
            phoneInput.classList.remove('is-valid', 'is-invalid');
        } else if (valid) {
            phoneValidation.textContent = '';
            phoneValidation.style.color = '#198754';
            phoneInput.classList.add('is-valid');
            phoneInput.classList.remove('is-invalid');
        } else {
            phoneValidation.textContent = 'Geçerli bir telefon numarası giriniz (05XX XXX XX XX formatında).';
            phoneValidation.style.color = '#dc3545';
            phoneInput.classList.add('is-invalid');
            phoneInput.classList.remove('is-valid');
        }
        
        checkFormProgress();
    }
    
    // Ad soyad geçerli mi
    function isValidName(value) {
        if (!value) return false;
        const words = value.split(/\s+/).filter(word => word.length > 0);
        if (words.length < 2) return false;
        return words.every(word => word.length >= 3);
    }
    
    // E-posta geçerli mi
    function isValidEmail(value) {
        if (!value) return false;
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    }
    
    // Telefon numarası geçerli mi
    function isValidPhone(value) {
        if (!value) return false;
        const digitsOnly = value.replace(/\D/g, '');
        if (digitsOnly.length !== 11) return false;
        if (digitsOnly.charAt(0) !== '0') return false;
        return /^0(5)[0-9]{9}$/.test(digitsOnly);
    }
    
    // Telefon numarası formatla
    function formatPhoneNumber() {
        let value = phoneInput.value.replace(/\D/g, '');
        
        if (value && value.charAt(0) !== '0') {
            value = '0' + value;
        }
        
        value = value.substring(0, 11);
        
        if (value.length > 1) {
            let formattedValue = value.substring(0, 1);
            
            if (value.length > 4) {
                formattedValue += value.substring(1, 4) + ' ';
                
                if (value.length > 7) {
                    formattedValue += value.substring(4, 7) + ' ';
                    
                    if (value.length > 9) {
                        formattedValue += value.substring(7, 9) + ' ';
                        formattedValue += value.substring(9, 11);
                    } else {
                        formattedValue += value.substring(7);
                    }
                } else {
                    formattedValue += value.substring(4);
                }
            } else {
                formattedValue += value.substring(1);
            }
            
            phoneInput.value = formattedValue;
        } else {
            phoneInput.value = value;
        }
        
        validatePhone();
    }
});

// Toast bildirim göster
function showToast(message, type = 'info') {
    let toastContainer = document.querySelector('.toast-container');
    
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center border-0 ${type === 'error' ? 'bg-danger' : 'bg-info'} text-white`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    
    const toast = new bootstrap.Toast(toastEl, {
        autohide: true,
        delay: 5000
    });
    
    toast.show();
}

// Orta zorlukta matematik captcha oluştur (sadece toplama ve çıkarma)
function generateCaptcha() {
    // Sadece toplama ve çıkarma işlemleri
    const operations = [
        { symbol: '+', func: (a, b) => a + b, text: 'topla' },
        { symbol: '-', func: (a, b) => a - b, text: 'çıkar' }
    ];
    
    // İki haneli bir sayı (10-99 arası)
    const num1 = Math.floor(Math.random() * 90) + 10;
    
    // Tek haneli bir sayı (1-9 arası)
    const num2 = Math.floor(Math.random() * 9) + 1;
    
    const operationIndex = Math.floor(Math.random() * operations.length);
    const operation = operations[operationIndex];
    
    // Çıkarma işlemi için her zaman büyük sayıdan küçük sayıyı çıkar
    const a = num1;
    const b = num2;
    
    const result = operation.func(a, b);
    
    const questionLabel = document.getElementById('captchaQuestionLabel');
    if (questionLabel) {
        questionLabel.textContent = `${a} ${operation.symbol} ${b} = ?`;
    }
    
    const expectedAnswerInput = document.getElementById('captchaExpectedAnswer');
    if (expectedAnswerInput) {
        expectedAnswerInput.value = result.toString();
    }
    
    const operationInput = document.getElementById('captchaOperation');
    if (operationInput) {
        operationInput.value = `${a}${operation.symbol}${b}`;
    }
} 