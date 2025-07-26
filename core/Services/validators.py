"""
Validation Service
Gelişmiş veri doğrulama sistemi
"""
import re
import os
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime, date

class Validator:
    """Gelişmiş validation sistemi"""
    
    def __init__(self):
        self.errors = {}
        self.custom_rules = {}
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Varsayılan validation kurallarını ayarla"""
        # Email regex
        self.email_regex = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        
        # URL regex
        self.url_regex = re.compile(r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$')
        
        # Phone regex (Türkiye)
        self.phone_regex = re.compile(r'^(\+90|0)?[5][0-9]{9}$')
        
        # TC Kimlik No regex
        self.tc_regex = re.compile(r'^[1-9][0-9]{10}$')
        
        # Password regex
        self.password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    
    def validate(self, data: Dict[str, Any], rules: Dict[str, str]) -> bool:
        """Veriyi doğrula"""
        self.errors = {}
        
        for field, rule_string in rules.items():
            value = data.get(field)
            field_rules = self._parse_rules(rule_string)
            
            for rule, params in field_rules.items():
                if not self._apply_rule(field, value, rule, params):
                    break
        
        return len(self.errors) == 0
    
    def _parse_rules(self, rule_string: str) -> Dict[str, Any]:
        """Kural string'ini parse et"""
        rules = {}
        
        for rule_part in rule_string.split('|'):
            if ':' in rule_part:
                rule_name, params = rule_part.split(':', 1)
                rules[rule_name.strip()] = params.strip()
            else:
                rules[rule_part.strip()] = None
        
        return rules
    
    def _apply_rule(self, field: str, value: Any, rule: str, params: Any) -> bool:
        """Kuralı uygula"""
        rule_method = getattr(self, f'_rule_{rule}', None)
        
        if rule_method:
            return rule_method(field, value, params)
        
        # Custom rule kontrolü
        if rule in self.custom_rules:
            return self.custom_rules[rule](field, value, params)
        
        print(f"Unknown validation rule: {rule}")
        return True
    
    def get_errors(self) -> Dict[str, List[str]]:
        """Hataları döndür"""
        return self.errors
    
    def get_first_error(self) -> Optional[str]:
        """İlk hatayı döndür"""
        for field_errors in self.errors.values():
            if field_errors:
                return field_errors[0]
        return None
    
    def has_error(self, field: str) -> bool:
        """Belirli alan için hata var mı kontrol et"""
        return field in self.errors and len(self.errors[field]) > 0
    
    def add_error(self, field: str, message: str):
        """Hata ekle"""
        if field not in self.errors:
            self.errors[field] = []
        self.errors[field].append(message)
    
    def add_custom_rule(self, rule_name: str, rule_function: Callable):
        """Özel kural ekle"""
        self.custom_rules[rule_name] = rule_function
    
    # Temel Kurallar
    def _rule_required(self, field: str, value: Any, params: Any) -> bool:
        """Zorunlu alan kontrolü"""
        if value is None or (isinstance(value, str) and not value.strip()):
            self.add_error(field, f"{field} alanı zorunludur")
            return False
        return True
    
    def _rule_email(self, field: str, value: Any, params: Any) -> bool:
        """Email format kontrolü"""
        if value and not self.email_regex.match(str(value)):
            self.add_error(field, f"{field} geçerli bir email adresi olmalıdır")
            return False
        return True
    
    def _rule_url(self, field: str, value: Any, params: Any) -> bool:
        """URL format kontrolü"""
        if value and not self.url_regex.match(str(value)):
            self.add_error(field, f"{field} geçerli bir URL olmalıdır")
            return False
        return True
    
    def _rule_phone(self, field: str, value: Any, params: Any) -> bool:
        """Telefon format kontrolü"""
        if value and not self.phone_regex.match(str(value)):
            self.add_error(field, f"{field} geçerli bir telefon numarası olmalıdır")
            return False
        return True
    
    def _rule_tc(self, field: str, value: Any, params: Any) -> bool:
        """TC Kimlik No kontrolü"""
        if value and not self.tc_regex.match(str(value)):
            self.add_error(field, f"{field} geçerli bir TC Kimlik No olmalıdır")
            return False
        return True
    
    def _rule_password(self, field: str, value: Any, params: Any) -> bool:
        """Şifre güvenlik kontrolü"""
        if value and not self.password_regex.match(str(value)):
            self.add_error(field, f"{field} en az 8 karakter, büyük/küçük harf, rakam ve özel karakter içermelidir")
            return False
        return True
    
    def _rule_min(self, field: str, value: Any, params: Any) -> bool:
        """Minimum değer kontrolü"""
        try:
            min_value = int(params)
            if value is not None:
                if isinstance(value, str):
                    if len(value) < min_value:
                        self.add_error(field, f"{field} en az {min_value} karakter olmalıdır")
                        return False
                elif isinstance(value, (int, float)):
                    if value < min_value:
                        self.add_error(field, f"{field} en az {min_value} olmalıdır")
                        return False
        except (ValueError, TypeError):
            pass
        return True
    
    def _rule_max(self, field: str, value: Any, params: Any) -> bool:
        """Maksimum değer kontrolü"""
        try:
            max_value = int(params)
            if value is not None:
                if isinstance(value, str):
                    if len(value) > max_value:
                        self.add_error(field, f"{field} en fazla {max_value} karakter olmalıdır")
                        return False
                elif isinstance(value, (int, float)):
                    if value > max_value:
                        self.add_error(field, f"{field} en fazla {max_value} olmalıdır")
                        return False
        except (ValueError, TypeError):
            pass
        return True
    
    def _rule_between(self, field: str, value: Any, params: Any) -> bool:
        """Aralık kontrolü"""
        try:
            min_val, max_val = map(int, params.split(','))
            if value is not None:
                if isinstance(value, str):
                    if not (min_val <= len(value) <= max_val):
                        self.add_error(field, f"{field} {min_val} ile {max_val} karakter arasında olmalıdır")
                        return False
                elif isinstance(value, (int, float)):
                    if not (min_val <= value <= max_val):
                        self.add_error(field, f"{field} {min_val} ile {max_val} arasında olmalıdır")
                        return False
        except (ValueError, TypeError):
            pass
        return True
    
    def _rule_numeric(self, field: str, value: Any, params: Any) -> bool:
        """Sayısal değer kontrolü"""
        if value is not None:
            try:
                float(value)
            except (ValueError, TypeError):
                self.add_error(field, f"{field} sayısal bir değer olmalıdır")
                return False
        return True
    
    def _rule_integer(self, field: str, value: Any, params: Any) -> bool:
        """Tam sayı kontrolü"""
        if value is not None:
            try:
                int(value)
            except (ValueError, TypeError):
                self.add_error(field, f"{field} tam sayı olmalıdır")
                return False
        return True
    
    def _rule_alpha(self, field: str, value: Any, params: Any) -> bool:
        """Sadece harf kontrolü"""
        if value and not str(value).replace(' ', '').isalpha():
            self.add_error(field, f"{field} sadece harf içermelidir")
            return False
        return True
    
    def _rule_alphanumeric(self, field: str, value: Any, params: Any) -> bool:
        """Harf ve rakam kontrolü"""
        if value and not str(value).replace(' ', '').isalnum():
            self.add_error(field, f"{field} sadece harf ve rakam içermelidir")
            return False
        return True
    
    def _rule_date(self, field: str, value: Any, params: Any) -> bool:
        """Tarih format kontrolü"""
        if value:
            try:
                if isinstance(value, str):
                    datetime.strptime(value, params or '%Y-%m-%d')
                elif not isinstance(value, (datetime, date)):
                    self.add_error(field, f"{field} geçerli bir tarih olmalıdır")
                    return False
            except ValueError:
                self.add_error(field, f"{field} geçerli bir tarih formatında olmalıdır")
                return False
        return True
    
    def _rule_in(self, field: str, value: Any, params: Any) -> bool:
        """Değer listesi kontrolü"""
        if value is not None:
            allowed_values = params.split(',')
            if str(value) not in allowed_values:
                self.add_error(field, f"{field} şu değerlerden biri olmalıdır: {', '.join(allowed_values)}")
                return False
        return True
    
    def _rule_not_in(self, field: str, value: Any, params: Any) -> bool:
        """Yasaklı değer kontrolü"""
        if value is not None:
            forbidden_values = params.split(',')
            if str(value) in forbidden_values:
                self.add_error(field, f"{field} şu değerlerden biri olamaz: {', '.join(forbidden_values)}")
                return False
        return True
    
    def _rule_unique(self, field: str, value: Any, params: Any) -> bool:
        """Benzersiz değer kontrolü"""
        if value is not None:
            try:
                table, column = params.split(',')
                # Veritabanı kontrolü
                from core.Database.connection import get_connection
                db = get_connection()
                
                # SQLite için uygun sorgu
                query = f"SELECT COUNT(*) FROM {table} WHERE {column} = ?"
                result = db.execute_query(query, (value,))
                
                if result and result[0]['COUNT(*)'] > 0:
                    self.add_error(field, f"{field} zaten kullanılmaktadır")
                    return False
            except Exception as e:
                print(f"Unique validation error: {str(e)}")
                # Hata durumunda geçerli kabul et
                pass
        return True
    
    def _rule_exists(self, field: str, value: Any, params: Any) -> bool:
        """Var olan değer kontrolü"""
        if value is not None:
            try:
                table, column = params.split(',')
                from core.Database.connection import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = %s", (value,))
                count = cursor.fetchone()[0]
                cursor.close()
                
                if count == 0:
                    self.add_error(field, f"{field} bulunamadı")
                    return False
            except Exception as e:
                print(f"Exists validation error: {str(e)}")
        return True
    
    def _rule_file(self, field: str, value: Any, params: Any) -> bool:
        """Dosya kontrolü"""
        if value is not None:
            if not os.path.isfile(str(value)):
                self.add_error(field, f"{field} geçerli bir dosya olmalıdır")
                return False
        return True
    
    def _rule_image(self, field: str, value: Any, params: Any) -> bool:
        """Resim dosyası kontrolü"""
        if value is not None:
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            file_ext = os.path.splitext(str(value))[1].lower()
            if file_ext not in image_extensions:
                self.add_error(field, f"{field} geçerli bir resim dosyası olmalıdır")
                return False
        return True
    
    def _rule_confirmed(self, field: str, value: Any, params: Any) -> bool:
        """Onay alanı kontrolü"""
        if value is not None:
            confirmation_field = f"{field}_confirmation"
            confirmation_value = getattr(self, 'data', {}).get(confirmation_field)
            if value != confirmation_value:
                self.add_error(field, f"{field} onayı eşleşmiyor")
                return False
        return True
    
    def validate_password(self, password: str) -> bool:
        """Şifre güvenlik kontrolü"""
        if not password:
            return False
        
        # Minimum 8 karakter
        if len(password) < 8:
            return False
        
        # En az bir büyük harf
        if not re.search(r'[A-Z]', password):
            return False
        
        # En az bir küçük harf
        if not re.search(r'[a-z]', password):
            return False
        
        # En az bir rakam
        if not re.search(r'\d', password):
            return False
        
        # En az bir özel karakter
        if not re.search(r'[@$!%*?&]', password):
            return False
        
        return True
    
    def validate_tc_kimlik(self, tc_no: str) -> bool:
        """TC Kimlik No doğrulama"""
        if not tc_no or len(tc_no) != 11:
            return False
        
        # Sadece rakam kontrolü
        if not tc_no.isdigit():
            return False
        
        # İlk rakam 0 olamaz
        if tc_no[0] == '0':
            return False
        
        # İlk 10 rakamın toplamının birler basamağı 11. rakam olmalı
        digits = [int(d) for d in tc_no]
        
        # 1, 3, 5, 7, 9. rakamların toplamı
        odd_sum = sum(digits[i] for i in range(0, 9, 2))
        
        # 2, 4, 6, 8. rakamların toplamı
        even_sum = sum(digits[i] for i in range(1, 8, 2))
        
        # 10. rakam kontrolü
        digit_10 = (odd_sum * 7 - even_sum) % 10
        if digit_10 != digits[9]:
            return False
        
        # 11. rakam kontrolü
        first_10_sum = sum(digits[:10])
        digit_11 = first_10_sum % 10
        if digit_11 != digits[10]:
            return False
        
        return True 