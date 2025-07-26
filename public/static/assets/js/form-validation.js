/**
 * Form Validation
 * Kayıt ve giriş formları için doğrulama işlemleri
 */

document.addEventListener('DOMContentLoaded', function() {
    // Form elementlerini seç
    const registerForm = document.querySelector('form[action="/auth/register"]');
    
    if (registerForm) {
        initRegisterFormValidation(registerForm);
    }
});

/**
 * Kayıt formu doğrulama işlemlerini başlat
 * @param {HTMLFormElement} form - Kayıt formu elementi
 */
function initRegisterFormValidation(form) {
    const nameInput = form.querySelector('#inputName');
    const emailInput = form.querySelector('#inputEmailAddress');
    const phoneInput = form.querySelector('#inputPhone');
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Form elementlerine doğrulama işlevlerini ekle
    if (nameInput) {
        nameInput.addEventListener('input', validateName);
        nameInput.addEventListener('blur', validateName);
    }
    
    if (emailInput) {
        emailInput.addEventListener('input', validateEmail);
        emailInput.addEventListener('blur', validateEmail);
    }
    
    if (phoneInput) {
        phoneInput.addEventListener('input', formatPhoneNumber);
        phoneInput.addEventListener('blur', validatePhoneNumber);
    }
    
    // Form gönderilmeden önce tüm doğrulamaları yap
    form.addEventListener('submit', function(event) {
        const nameValid = nameInput ? validateName({ target: nameInput }) : true;
        const emailValid = emailInput ? validateEmail({ target: emailInput }) : true;
        const phoneValid = phoneInput ? validatePhoneNumber({ target: phoneInput }) : true;
        
        // Herhangi bir doğrulama başarısız olursa formu gönderme
        if (!nameValid || !emailValid || !phoneValid) {
            event.preventDefault();
        }
    });
    
    // Doğrulama durumuna göre buton durumunu güncelle
    function updateSubmitButton() {
        const nameValid = nameInput ? isValidName(nameInput.value) : true;
        const emailValid = emailInput ? isValidEmail(emailInput.value) : true;
        const phoneValid = phoneInput ? isValidPhoneNumber(phoneInput.value) : true;
        
        if (submitButton) {
            submitButton.disabled = !(nameValid && emailValid && phoneValid);
        }
    }
    
    // İlk yükleme için buton durumunu ayarla
    updateSubmitButton();
}

/**
 * Ad soyad doğrulama
 * - En az iki kelime olmalı
 * - Her kelime en az 3 karakter olmalı
 * @param {Event} event - Input event
 * @returns {boolean} - Doğrulama sonucu
 */
function validateName(event) {
    const input = event.target;
    const value = input.value.trim();
    const isValid = isValidName(value);
    
    // Doğrulama mesajını göster/gizle
    showValidationMessage(input, isValid, 'Ad Soyad en az iki kelimeden oluşmalı ve her kelime en az 3 karakter olmalıdır.');
    
    return isValid;
}

/**
 * Ad soyad değerinin geçerli olup olmadığını kontrol et
 * @param {string} value - Ad soyad değeri
 * @returns {boolean} - Doğrulama sonucu
 */
function isValidName(value) {
    if (!value) return false;
    
    // Boşluklara göre kelimelere ayır
    const words = value.split(/\s+/).filter(word => word.length > 0);
    
    // En az iki kelime olmalı
    if (words.length < 2) return false;
    
    // Her kelime en az 3 karakter olmalı
    return words.every(word => word.length >= 3);
}

/**
 * E-posta doğrulama
 * - Geçerli e-posta formatı
 * - Alan adı kontrolü (MX kaydı)
 * @param {Event} event - Input event
 * @returns {boolean} - Doğrulama sonucu
 */
function validateEmail(event) {
    const input = event.target;
    const value = input.value.trim();
    
    // Basit format kontrolü
    const formatValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    
    if (!formatValid) {
        showValidationMessage(input, false, 'Geçerli bir e-posta adresi giriniz.');
        return false;
    }
    
    // Alan adı kontrolü
    if (value && formatValid) {
        const domain = value.split('@')[1];
        
        // Alan adı kontrolü için loading göster
        showValidationMessage(input, null, 'E-posta adresi kontrol ediliyor...');
        
        // Alan adı kontrolü (gerçek uygulamada API çağrısı yapılır)
        checkEmailDomain(domain).then(isValid => {
            showValidationMessage(input, isValid, isValid ? '' : 'Bu e-posta alan adı geçerli değil.');
        });
    }
    
    return formatValid;
}

/**
 * E-posta değerinin geçerli olup olmadığını kontrol et
 * @param {string} value - E-posta değeri
 * @returns {boolean} - Doğrulama sonucu
 */
function isValidEmail(value) {
    if (!value) return false;
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
}

/**
 * E-posta alan adı kontrolü
 * @param {string} domain - Alan adı
 * @returns {Promise<boolean>} - Alan adı geçerli mi
 */
async function checkEmailDomain(domain) {
    // Gerçek uygulamada bir API'ye istek yapılır
    // Burada simüle ediyoruz
    return new Promise(resolve => {
        setTimeout(() => {
            // Geçersiz kabul edilecek örnek alan adları
            const invalidDomains = [
                'example.com', 'test.com', 'invalid.com', 'fake.com'
            ];
            
            resolve(!invalidDomains.includes(domain));
        }, 500); // 500ms gecikme ile simüle et
    });
}

/**
 * Telefon numarası formatla
 * @param {Event} event - Input event
 */
function formatPhoneNumber(event) {
    const input = event.target;
    let value = input.value.replace(/\D/g, ''); // Sadece rakamları al
    
    // Başında 0 yoksa ekle
    if (value && value.charAt(0) !== '0') {
        value = '0' + value;
    }
    
    // Maksimum 11 karakter (0 dahil)
    value = value.substring(0, 11);
    
    // Formatlama: 0XXX XXX XX XX
    if (value.length > 1) {
        let formattedValue = value.substring(0, 1); // İlk rakam (0)
        
        if (value.length > 4) {
            formattedValue += value.substring(1, 4) + ' '; // Alan kodu (XXX)
            
            if (value.length > 7) {
                formattedValue += value.substring(4, 7) + ' '; // Orta grup (XXX)
                
                if (value.length > 9) {
                    formattedValue += value.substring(7, 9) + ' '; // Son gruplar (XX XX)
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
        
        input.value = formattedValue;
    } else {
        input.value = value;
    }
    
    // Doğrulama yap
    validatePhoneNumber({ target: input });
}

/**
 * Telefon numarası doğrulama
 * @param {Event} event - Input event
 * @returns {boolean} - Doğrulama sonucu
 */
function validatePhoneNumber(event) {
    const input = event.target;
    const value = input.value;
    const isValid = isValidPhoneNumber(value);
    
    // Doğrulama mesajını göster/gizle
    showValidationMessage(input, isValid, 'Geçerli bir telefon numarası giriniz (05XX XXX XX XX formatında).');
    
    return isValid;
}

/**
 * Telefon numarası değerinin geçerli olup olmadığını kontrol et
 * @param {string} value - Telefon numarası değeri
 * @returns {boolean} - Doğrulama sonucu
 */
function isValidPhoneNumber(value) {
    if (!value) return false;
    
    // Boşlukları kaldır ve sadece rakamları al
    const digitsOnly = value.replace(/\D/g, '');
    
    // 11 rakam olmalı ve 0 ile başlamalı
    if (digitsOnly.length !== 11) return false;
    if (digitsOnly.charAt(0) !== '0') return false;
    
    // Türkiye telefon numarası formatı: 05XX ile başlamalı
    return /^0(5)[0-9]{9}$/.test(digitsOnly);
}

/**
 * Doğrulama mesajını göster/gizle
 * @param {HTMLElement} input - Input elementi
 * @param {boolean|null} isValid - Doğrulama sonucu (null: loading)
 * @param {string} message - Hata mesajı
 */
function showValidationMessage(input, isValid, message) {
    // Mevcut mesaj elementini bul veya oluştur
    let messageElement = input.parentNode.querySelector('.validation-message');
    
    if (!messageElement) {
        messageElement = document.createElement('div');
        messageElement.className = 'validation-message';
        messageElement.style.fontSize = '12px';
        messageElement.style.marginTop = '5px';
        input.parentNode.appendChild(messageElement);
    }
    
    // CSS sınıflarını ayarla
    input.classList.remove('is-valid', 'is-invalid');
    
    if (isValid === null) {
        // Loading durumu
        messageElement.textContent = message;
        messageElement.style.color = '#6c757d';
    } else if (isValid) {
        // Geçerli
        messageElement.textContent = '';
        input.classList.add('is-valid');
    } else {
        // Geçersiz
        messageElement.textContent = message;
        messageElement.style.color = '#dc3545';
        input.classList.add('is-invalid');
    }
} 