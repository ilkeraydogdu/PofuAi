"""
Validator Helper
Form doğrulama işlemleri için yardımcı fonksiyonlar
"""
import re
from typing import Dict, Any, List, Union, Optional
from datetime import datetime

def validate(data: Dict[str, Any], rules: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Veriyi belirtilen kurallara göre doğrula
    
    Args:
        data (Dict[str, Any]): Doğrulanacak veriler
        rules (Dict[str, str]): Doğrulama kuralları
        
    Returns:
        Dict[str, List[str]]: Hata mesajları
    """
    errors = {}
    
    for field, rule_string in rules.items():
        # Kuralları parse et
        field_rules = [r.strip() for r in rule_string.split('|')]
        field_errors = []
        
        # Değeri al
        value = data.get(field)
        
        # Kuralları uygula
        for rule in field_rules:
            rule_parts = rule.split(':')
            rule_name = rule_parts[0]
            rule_params = rule_parts[1] if len(rule_parts) > 1 else None
            
            # Kural fonksiyonunu çağır
            error = _apply_rule(rule_name, field, value, rule_params)
            if error:
                field_errors.append(error)
        
        # Alanla ilgili hatalar varsa ekle
        if field_errors:
            errors[field] = field_errors
    
    return errors

def _apply_rule(rule_name: str, field: str, value: Any, params: Optional[str] = None) -> Optional[str]:
    """
    Tek bir kural uygular
    
    Args:
        rule_name (str): Kural adı
        field (str): Alan adı
        value (Any): Alan değeri
        params (str, optional): Kural parametreleri
        
    Returns:
        Optional[str]: Hata mesajı veya None (hata yoksa)
    """
    # Kuralları uygula
    if rule_name == 'required':
        if value is None or (isinstance(value, str) and not value.strip()):
            return f"{field.capitalize()} alanı gereklidir."
    
    elif rule_name == 'email':
        if value and not is_valid_email(value):
            return f"{field.capitalize()} geçerli bir e-posta adresi olmalıdır."
    
    elif rule_name == 'min':
        min_val = int(params) if params else 0
        if value is not None:
            if isinstance(value, str):
                if len(value) < min_val:
                    return f"{field.capitalize()} en az {min_val} karakter olmalıdır."
            elif isinstance(value, (int, float)):
                if value < min_val:
                    return f"{field.capitalize()} en az {min_val} olmalıdır."
            elif isinstance(value, list):
                if len(value) < min_val:
                    return f"{field.capitalize()} en az {min_val} öğe içermelidir."
    
    elif rule_name == 'max':
        max_val = int(params) if params else 0
        if value is not None:
            if isinstance(value, str):
                if len(value) > max_val:
                    return f"{field.capitalize()} en fazla {max_val} karakter olmalıdır."
            elif isinstance(value, (int, float)):
                if value > max_val:
                    return f"{field.capitalize()} en fazla {max_val} olmalıdır."
            elif isinstance(value, list):
                if len(value) > max_val:
                    return f"{field.capitalize()} en fazla {max_val} öğe içermelidir."
    
    elif rule_name == 'size':
        size_val = int(params) if params else 0
        if value is not None:
            if isinstance(value, str):
                if len(value) != size_val:
                    return f"{field.capitalize()} {size_val} karakter uzunluğunda olmalıdır."
            elif isinstance(value, list):
                if len(value) != size_val:
                    return f"{field.capitalize()} {size_val} öğe içermelidir."
    
    elif rule_name == 'numeric':
        if value and not is_numeric(value):
            return f"{field.capitalize()} sayısal bir değer olmalıdır."
    
    elif rule_name == 'integer':
        if value and not is_integer(value):
            return f"{field.capitalize()} tam sayı olmalıdır."
    
    elif rule_name == 'float':
        if value and not is_float(value):
            return f"{field.capitalize()} ondalıklı sayı olmalıdır."
    
    elif rule_name == 'bool' or rule_name == 'boolean':
        if value is not None and not isinstance(value, bool):
            return f"{field.capitalize()} boolean değer olmalıdır."
    
    elif rule_name == 'in':
        if not params:
            return None
        allowed_values = params.split(',')
        if value and str(value) not in allowed_values:
            return f"{field.capitalize()} şunlardan biri olmalıdır: {', '.join(allowed_values)}."
    
    elif rule_name == 'not_in':
        if not params:
            return None
        forbidden_values = params.split(',')
        if value and str(value) in forbidden_values:
            return f"{field.capitalize()} şunlardan biri olmamalıdır: {', '.join(forbidden_values)}."
    
    elif rule_name == 'alpha':
        if value and not value.isalpha():
            return f"{field.capitalize()} sadece alfabetik karakterler içermelidir."
    
    elif rule_name == 'alpha_num':
        if value and not value.isalnum():
            return f"{field.capitalize()} sadece alfabetik karakterler ve rakamlar içermelidir."
    
    elif rule_name == 'date':
        if value and not is_valid_date(value):
            return f"{field.capitalize()} geçerli bir tarih olmalıdır."
    
    elif rule_name == 'url':
        if value and not is_valid_url(value):
            return f"{field.capitalize()} geçerli bir URL olmalıdır."
    
    elif rule_name == 'regex':
        if not params:
            return None
        if value and not re.match(params, value):
            return f"{field.capitalize()} belirtilen formata uygun olmalıdır."
    
    elif rule_name == 'confirmed':
        confirmation_field = f"{field}_confirmation"
        confirmation_value = data.get(confirmation_field)
        if value != confirmation_value:
            return f"{field.capitalize()} onayı eşleşmiyor."
    
    return None

def is_valid_email(value: str) -> bool:
    """
    E-posta adresi geçerli mi kontrol et
    
    Args:
        value (str): Kontrol edilecek değer
        
    Returns:
        bool: Geçerli e-posta adresi ise True
    """
    if not isinstance(value, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, value))

def is_numeric(value: Any) -> bool:
    """
    Değer sayısal mı kontrol et
    
    Args:
        value (Any): Kontrol edilecek değer
        
    Returns:
        bool: Sayısal değer ise True
    """
    if isinstance(value, (int, float)):
        return True
    
    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    return False

def is_integer(value: Any) -> bool:
    """
    Değer tam sayı mı kontrol et
    
    Args:
        value (Any): Kontrol edilecek değer
        
    Returns:
        bool: Tam sayı ise True
    """
    if isinstance(value, int):
        return True
    
    if isinstance(value, str):
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    return False

def is_float(value: Any) -> bool:
    """
    Değer ondalıklı sayı mı kontrol et
    
    Args:
        value (Any): Kontrol edilecek değer
        
    Returns:
        bool: Ondalıklı sayı ise True
    """
    if isinstance(value, float):
        return True
    
    if isinstance(value, str):
        try:
            float(value)
            return '.' in value
        except ValueError:
            return False
    
    return False

def is_valid_date(value: str, formats: List[str] = None) -> bool:
    """
    Geçerli bir tarih mi kontrol et
    
    Args:
        value (str): Kontrol edilecek değer
        formats (List[str], optional): Tarih formatları
        
    Returns:
        bool: Geçerli tarih ise True
    """
    if not formats:
        formats = ['%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']
    
    for date_format in formats:
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            continue
    
    return False

def is_valid_url(value: str) -> bool:
    """
    Geçerli bir URL mi kontrol et
    
    Args:
        value (str): Kontrol edilecek değer
        
    Returns:
        bool: Geçerli URL ise True
    """
    pattern = r'^(https?|ftp)://[^\s/$.?#].[^\s]*$'
    return bool(re.match(pattern, value))

def validate_object(data: Dict[str, Any], schema: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Veriyi şemaya göre doğrula
    
    Args:
        data (Dict[str, Any]): Doğrulanacak veriler
        schema (Dict[str, Dict[str, Any]]): Doğrulama şeması
        
    Returns:
        Dict[str, List[str]]: Hata mesajları
    """
    errors = {}
    
    for field, field_schema in schema.items():
        field_errors = []
        value = data.get(field)
        
        # Zorunlu alan kontrolü
        if field_schema.get('required', False) and not value:
            field_errors.append(f"{field.capitalize()} alanı gereklidir.")
            errors[field] = field_errors
            continue
        
        # Değer yoksa ve zorunlu değilse devam et
        if value is None:
            continue
        
        # Tip kontrolü
        expected_type = field_schema.get('type')
        if expected_type:
            # Tip kontrolü
            if expected_type == 'string' and not isinstance(value, str):
                field_errors.append(f"{field.capitalize()} bir string olmalıdır.")
            elif expected_type == 'number' and not isinstance(value, (int, float)):
                field_errors.append(f"{field.capitalize()} bir sayı olmalıdır.")
            elif expected_type == 'integer' and not isinstance(value, int):
                field_errors.append(f"{field.capitalize()} bir tam sayı olmalıdır.")
            elif expected_type == 'boolean' and not isinstance(value, bool):
                field_errors.append(f"{field.capitalize()} bir boolean olmalıdır.")
            elif expected_type == 'array' and not isinstance(value, list):
                field_errors.append(f"{field.capitalize()} bir dizi olmalıdır.")
            elif expected_type == 'object' and not isinstance(value, dict):
                field_errors.append(f"{field.capitalize()} bir nesne olmalıdır.")
        
        # Min değer kontrolü
        min_value = field_schema.get('min')
        if min_value is not None:
            if isinstance(value, (int, float)) and value < min_value:
                field_errors.append(f"{field.capitalize()} en az {min_value} olmalıdır.")
        
        # Max değer kontrolü
        max_value = field_schema.get('max')
        if max_value is not None:
            if isinstance(value, (int, float)) and value > max_value:
                field_errors.append(f"{field.capitalize()} en fazla {max_value} olmalıdır.")
        
        # Min uzunluk kontrolü
        min_length = field_schema.get('minLength')
        if min_length is not None:
            if hasattr(value, '__len__') and len(value) < min_length:
                field_errors.append(f"{field.capitalize()} en az {min_length} karakter olmalıdır.")
        
        # Max uzunluk kontrolü
        max_length = field_schema.get('maxLength')
        if max_length is not None:
            if hasattr(value, '__len__') and len(value) > max_length:
                field_errors.append(f"{field.capitalize()} en fazla {max_length} karakter olmalıdır.")
        
        # Enum değer kontrolü
        enum_values = field_schema.get('enum')
        if enum_values is not None:
            if value not in enum_values:
                field_errors.append(f"{field.capitalize()} şunlardan biri olmalıdır: {', '.join(map(str, enum_values))}.")
        
        # Pattern kontrolü
        pattern = field_schema.get('pattern')
        if pattern is not None:
            if isinstance(value, str) and not re.match(pattern, value):
                field_errors.append(f"{field.capitalize()} belirtilen formata uygun olmalıdır.")
        
        # Format kontrolü
        format_type = field_schema.get('format')
        if format_type is not None:
            if format_type == 'email' and not is_valid_email(value):
                field_errors.append(f"{field.capitalize()} geçerli bir e-posta adresi olmalıdır.")
            elif format_type == 'date' and not is_valid_date(value):
                field_errors.append(f"{field.capitalize()} geçerli bir tarih olmalıdır.")
            elif format_type == 'url' and not is_valid_url(value):
                field_errors.append(f"{field.capitalize()} geçerli bir URL olmalıdır.")
        
        # Özel doğrulama fonksiyonu
        validator_func = field_schema.get('validator')
        if validator_func is not None:
            if callable(validator_func):
                result = validator_func(value)
                if result is not True:
                    field_errors.append(result if isinstance(result, str) else f"{field.capitalize()} geçerli değil.")
        
        # Nesne doğrulama
        properties = field_schema.get('properties')
        if properties is not None and isinstance(value, dict):
            nested_errors = validate_object(value, properties)
            for nested_field, nested_field_errors in nested_errors.items():
                errors[f"{field}.{nested_field}"] = nested_field_errors
        
        # Dizi doğrulama
        items = field_schema.get('items')
        if items is not None and isinstance(value, list):
            for idx, item in enumerate(value):
                if isinstance(items, dict):
                    nested_errors = validate_object({f"{field}[{idx}]": item}, {f"{field}[{idx}]": items})
                    errors.update(nested_errors)
        
        # Alan hataları varsa ekle
        if field_errors:
            errors[field] = field_errors
    
    return errors

# Dışa aktarılan fonksiyonlar
__all__ = [
    'validate',
    'validate_object',
    'is_valid_email',
    'is_numeric',
    'is_integer',
    'is_float',
    'is_valid_date',
    'is_valid_url'
]

# Global data değişkeni
# Bu değişken, doğrulama işlemleri arasında veri paylaşımı için kullanılabilir
data = {} 