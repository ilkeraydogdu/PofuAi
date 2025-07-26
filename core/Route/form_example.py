"""
Form Example
Form işleme ve doğrulama örnekleri
"""
from flask import Blueprint, jsonify, request

def create_form_example_blueprint():
    """Form örnekleri için blueprint"""
    bp = Blueprint('form_example', __name__, url_prefix='/examples/forms')
    
    @bp.route('/')
    def index():
        """Form örnekleri ana sayfası"""
        form_examples = [
            {'name': 'Basit Form', 'url': '/examples/forms/basic'},
            {'name': 'Doğrulama', 'url': '/examples/forms/validation'},
            {'name': 'Dosya Yükleme', 'url': '/examples/forms/file-upload'},
            {'name': 'AJAX Form', 'url': '/examples/forms/ajax'},
            {'name': 'Multi-step Form', 'url': '/examples/forms/multi-step'},
            {'name': 'Dynamic Form', 'url': '/examples/forms/dynamic'},
        ]
        
        return jsonify({
            'title': 'Form Örnekleri',
            'description': 'Form işleme ve doğrulama örnekleri',
            'examples': form_examples
        })
    
    @bp.route('/basic', methods=['GET', 'POST'])
    def basic_form():
        """Basit form örneği"""
        if request.method == 'GET':
            # Form şablonu
            form_fields = [
                {'name': 'name', 'label': 'İsim', 'type': 'text', 'required': True},
                {'name': 'email', 'label': 'E-posta', 'type': 'email', 'required': True},
                {'name': 'message', 'label': 'Mesaj', 'type': 'textarea', 'required': True},
            ]
            
            return jsonify({
                'title': 'Basit Form',
                'form_fields': form_fields,
                'submit_url': '/examples/forms/basic',
                'method': 'POST'
            })
        
        elif request.method == 'POST':
            # Form verilerini al
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            # Form verilerini işle
            return jsonify({
                'status': 'success',
                'message': 'Form başarıyla gönderildi',
                'data': {
                    'name': name,
                    'email': email,
                    'message': message
                }
            })
    
    @bp.route('/validation', methods=['GET', 'POST'])
    def validation_form():
        """Doğrulama örneği"""
        if request.method == 'GET':
            # Form şablonu
            form_fields = [
                {'name': 'username', 'label': 'Kullanıcı Adı', 'type': 'text', 'required': True, 'min_length': 3},
                {'name': 'email', 'label': 'E-posta', 'type': 'email', 'required': True},
                {'name': 'password', 'label': 'Şifre', 'type': 'password', 'required': True, 'min_length': 6},
                {'name': 'password_confirm', 'label': 'Şifre (Tekrar)', 'type': 'password', 'required': True},
                {'name': 'age', 'label': 'Yaş', 'type': 'number', 'required': True, 'min': 18},
                {'name': 'terms', 'label': 'Kullanım şartlarını kabul ediyorum', 'type': 'checkbox', 'required': True},
            ]
            
            return jsonify({
                'title': 'Doğrulama Örneği',
                'form_fields': form_fields,
                'submit_url': '/examples/forms/validation',
                'method': 'POST'
            })
        
        elif request.method == 'POST':
            # Form verilerini al
            username = request.form.get('username', '')
            email = request.form.get('email', '')
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')
            age = request.form.get('age', '')
            terms = request.form.get('terms', '')
            
            # Doğrulama hataları
            errors = {}
            
            # Kullanıcı adı doğrulama
            if not username:
                errors['username'] = ['Kullanıcı adı gerekli']
            elif len(username) < 3:
                errors['username'] = ['Kullanıcı adı en az 3 karakter olmalı']
            
            # E-posta doğrulama
            if not email:
                errors['email'] = ['E-posta adresi gerekli']
            elif '@' not in email or '.' not in email:
                errors['email'] = ['Geçerli bir e-posta adresi girin']
            
            # Şifre doğrulama
            if not password:
                errors['password'] = ['Şifre gerekli']
            elif len(password) < 6:
                errors['password'] = ['Şifre en az 6 karakter olmalı']
            
            # Şifre onay doğrulama
            if password != password_confirm:
                errors['password_confirm'] = ['Şifreler eşleşmiyor']
            
            # Yaş doğrulama
            try:
                if not age:
                    errors['age'] = ['Yaş gerekli']
                elif int(age) < 18:
                    errors['age'] = ['18 yaşından büyük olmalısınız']
            except ValueError:
                errors['age'] = ['Geçerli bir yaş girin']
            
            # Şartlar doğrulama
            if terms != 'on':
                errors['terms'] = ['Kullanım şartlarını kabul etmelisiniz']
            
            # Hata varsa geri döndür
            if errors:
                return jsonify({
                    'status': 'error',
                    'message': 'Form doğrulama hataları',
                    'errors': errors
                }), 422
            
            # Başarılı ise
            return jsonify({
                'status': 'success',
                'message': 'Form başarıyla doğrulandı ve gönderildi',
                'data': {
                    'username': username,
                    'email': email,
                    'password': '********',
                    'age': age,
                    'terms': True
                }
            })
    
    @bp.route('/file-upload', methods=['GET', 'POST'])
    def file_upload():
        """Dosya yükleme örneği"""
        if request.method == 'GET':
            # Form şablonu
            form_fields = [
                {'name': 'title', 'label': 'Başlık', 'type': 'text', 'required': True},
                {'name': 'description', 'label': 'Açıklama', 'type': 'textarea'},
                {'name': 'file', 'label': 'Dosya', 'type': 'file', 'required': True, 'accept': 'image/*'}
            ]
            
            return jsonify({
                'title': 'Dosya Yükleme Örneği',
                'form_fields': form_fields,
                'submit_url': '/examples/forms/file-upload',
                'method': 'POST',
                'enctype': 'multipart/form-data'
            })
        
        elif request.method == 'POST':
            # Form verilerini al
            title = request.form.get('title')
            description = request.form.get('description')
            
            # Dosya kontrolü
            if 'file' not in request.files:
                return jsonify({
                    'status': 'error',
                    'message': 'Dosya bulunamadı'
                }), 400
                
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({
                    'status': 'error',
                    'message': 'Dosya seçilmedi'
                }), 400
            
            # Gerçek uygulamada dosya kaydedilir
            # file.save('/path/to/upload/directory/' + file.filename)
            
            return jsonify({
                'status': 'success',
                'message': 'Dosya başarıyla yüklendi',
                'data': {
                    'title': title,
                    'description': description,
                    'filename': file.filename,
                    'mime_type': file.content_type,
                    'size': f"{len(file.read())} bytes"
                }
            })
    
    @bp.route('/ajax', methods=['GET', 'POST'])
    def ajax_form():
        """AJAX form örneği"""
        if request.method == 'GET':
            # Form şablonu
            form_fields = [
                {'name': 'search', 'label': 'Arama', 'type': 'text', 'required': True},
                {'name': 'category', 'label': 'Kategori', 'type': 'select', 'options': [
                    {'value': '', 'label': 'Seçiniz'},
                    {'value': 'blog', 'label': 'Blog'},
                    {'value': 'product', 'label': 'Ürün'},
                    {'value': 'user', 'label': 'Kullanıcı'}
                ]}
            ]
            
            return jsonify({
                'title': 'AJAX Form Örneği',
                'form_fields': form_fields,
                'submit_url': '/examples/forms/ajax',
                'method': 'POST',
                'is_ajax': True
            })
        
        elif request.method == 'POST':
            # JSON verilerini al
            data = request.json
            search = data.get('search', '')
            category = data.get('category', '')
            
            # Arama sonuçları oluştur (örnek)
            results = []
            if search:
                if category == 'blog':
                    results = [
                        {'id': 1, 'title': 'Blog Yazısı 1', 'url': '/blog/1'},
                        {'id': 2, 'title': 'Blog Yazısı 2', 'url': '/blog/2'}
                    ]
                elif category == 'product':
                    results = [
                        {'id': 1, 'title': 'Ürün 1', 'price': 100, 'url': '/product/1'},
                        {'id': 2, 'title': 'Ürün 2', 'price': 200, 'url': '/product/2'}
                    ]
                elif category == 'user':
                    results = [
                        {'id': 1, 'username': 'user1', 'url': '/user/1'},
                        {'id': 2, 'username': 'user2', 'url': '/user/2'}
                    ]
                else:
                    results = [
                        {'id': 1, 'title': 'Sonuç 1', 'url': '/result/1'},
                        {'id': 2, 'title': 'Sonuç 2', 'url': '/result/2'}
                    ]
            
            return jsonify({
                'status': 'success',
                'query': search,
                'category': category,
                'results': results
            })
    
    @bp.route('/multi-step', methods=['GET', 'POST'])
    def multi_step_form():
        """Çok adımlı form örneği"""
        if request.method == 'GET':
            # Form şablonu
            steps = [
                {
                    'title': 'Kişisel Bilgiler',
                    'fields': [
                        {'name': 'name', 'label': 'Ad', 'type': 'text', 'required': True},
                        {'name': 'surname', 'label': 'Soyad', 'type': 'text', 'required': True},
                        {'name': 'email', 'label': 'E-posta', 'type': 'email', 'required': True}
                    ]
                },
                {
                    'title': 'Adres Bilgileri',
                    'fields': [
                        {'name': 'address', 'label': 'Adres', 'type': 'textarea', 'required': True},
                        {'name': 'city', 'label': 'Şehir', 'type': 'text', 'required': True},
                        {'name': 'postal_code', 'label': 'Posta Kodu', 'type': 'text', 'required': True}
                    ]
                },
                {
                    'title': 'Ödeme Bilgileri',
                    'fields': [
                        {'name': 'card_number', 'label': 'Kart Numarası', 'type': 'text', 'required': True},
                        {'name': 'card_name', 'label': 'Kart Üzerindeki İsim', 'type': 'text', 'required': True},
                        {'name': 'expiry', 'label': 'Son Kullanma Tarihi', 'type': 'text', 'required': True},
                        {'name': 'cvv', 'label': 'CVV', 'type': 'text', 'required': True}
                    ]
                }
            ]
            
            return jsonify({
                'title': 'Çok Adımlı Form Örneği',
                'steps': steps,
                'submit_url': '/examples/forms/multi-step',
                'method': 'POST'
            })
        
        elif request.method == 'POST':
            # Form verilerini al
            data = request.json
            
            # Başarılı işlem
            return jsonify({
                'status': 'success',
                'message': 'Çok adımlı form başarıyla tamamlandı',
                'data': data
            })
    
    @bp.route('/dynamic', methods=['GET', 'POST'])
    def dynamic_form():
        """Dinamik form örneği"""
        if request.method == 'GET':
            # Form şablonu
            form_fields = [
                {'name': 'title', 'label': 'Başlık', 'type': 'text', 'required': True},
                {'name': 'type', 'label': 'Türü', 'type': 'select', 'options': [
                    {'value': 'article', 'label': 'Makale'},
                    {'value': 'news', 'label': 'Haber'},
                    {'value': 'review', 'label': 'İnceleme'}
                ], 'required': True}
            ]
            
            # Dinamik alanlar
            dynamic_fields = {
                'article': [
                    {'name': 'content', 'label': 'İçerik', 'type': 'textarea', 'required': True},
                    {'name': 'category', 'label': 'Kategori', 'type': 'select', 'options': [
                        {'value': 'tech', 'label': 'Teknoloji'},
                        {'value': 'science', 'label': 'Bilim'},
                        {'value': 'health', 'label': 'Sağlık'}
                    ], 'required': True},
                    {'name': 'tags', 'label': 'Etiketler (virgülle ayırın)', 'type': 'text'}
                ],
                'news': [
                    {'name': 'content', 'label': 'İçerik', 'type': 'textarea', 'required': True},
                    {'name': 'source', 'label': 'Kaynak', 'type': 'text', 'required': True},
                    {'name': 'publish_date', 'label': 'Yayın Tarihi', 'type': 'date', 'required': True}
                ],
                'review': [
                    {'name': 'content', 'label': 'İçerik', 'type': 'textarea', 'required': True},
                    {'name': 'product', 'label': 'Ürün', 'type': 'text', 'required': True},
                    {'name': 'rating', 'label': 'Puan', 'type': 'number', 'min': 1, 'max': 5, 'required': True},
                    {'name': 'pros', 'label': 'Artılar', 'type': 'textarea'},
                    {'name': 'cons', 'label': 'Eksiler', 'type': 'textarea'}
                ]
            }
            
            return jsonify({
                'title': 'Dinamik Form Örneği',
                'form_fields': form_fields,
                'dynamic_fields': dynamic_fields,
                'submit_url': '/examples/forms/dynamic',
                'method': 'POST'
            })
        
        elif request.method == 'POST':
            # Form verilerini al
            data = request.json
            
            # Başarılı işlem
            return jsonify({
                'status': 'success',
                'message': 'Dinamik form başarıyla gönderildi',
                'data': data
            })
    
    return bp

def get_form_example_bp():
    """Form example blueprint'ini döndür"""
    return create_form_example_blueprint() 