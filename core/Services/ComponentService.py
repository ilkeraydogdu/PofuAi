"""
Component Service
Component yönetim ve entegrasyon servisi
"""
from pathlib import Path
import os
from typing import Dict, Any, Optional, List
from flask import render_template_string

class ComponentService:
    """
    Component yönetim servisi.
    Bu servis, component'lerin merkezi yönetimini sağlar.
    """
    
    def __init__(self):
        """Component servisini başlat"""
        self.component_path = Path("public/Views/components")
        self.component_cache = {}
        self._init_component_cache()
        self._load_macros()
    
    def _init_component_cache(self):
        """Component dosyalarını cache'le"""
        if not os.path.exists(self.component_path):
            return
        
        # Tüm component dosyalarını listele
        for file_path in self.component_path.glob("*.html"):
            file_name = file_path.name
            # Parça componentler (_component.html)
            if file_name.startswith("_"):
                component_name = file_name[1:-5]  # _name.html -> name
                if component_name not in self.component_cache:
                    self.component_cache[component_name] = {}
                self.component_cache[component_name]['partial'] = file_name
            # Tam sayfa componentler (component.html)
            elif not file_name.startswith("_"):
                component_name = file_name[:-5]  # name.html -> name
                if component_name not in self.component_cache:
                    self.component_cache[component_name] = {}
                self.component_cache[component_name]['full'] = file_name
    
    def _load_macros(self):
        """Makro dosyasını yükle"""
        macro_path = self.component_path / "_macros.html"
        if os.path.exists(macro_path):
            with open(macro_path, 'r', encoding='utf-8') as f:
                self.macros = f.read()
        else:
            self.macros = ""
    
    def render_component(self, component_name: str, data: Dict[str, Any] = None) -> str:
        """
        Component'i render et
        
        Args:
            component_name (str): Component adı
            data (Dict[str, Any], optional): Component verisi
            
        Returns:
            str: Render edilmiş HTML içeriği
        """
        data = data or {}
        
        # Makroyu çağır
        template = f"{{% import 'components/_macros.html' as components %}}\n"
        template += f"{{ components.{component_name}("
        
        # Parametreleri ekle
        params = []
        for key, value in data.items():
            if isinstance(value, str):
                params.append(f"{key}='{value}'")
            elif isinstance(value, bool):
                params.append(f"{key}={str(value).lower()}")
            else:
                params.append(f"{key}={value}")
        
        template += ", ".join(params)
        template += ") }}"
        
        # Render et
        return render_template_string(template, **data)
    
    def get_component_list(self):
        """
        Mevcut componentlerin listesini al
        
        Returns:
            dict: Component adı -> {'full': 'file.html', 'partial': '_file.html'}
        """
        return self.component_cache
    
    def component_exists(self, component_name):
        """
        Component'in var olup olmadığını kontrol et
        
        Args:
            component_name (str): Component adı
            
        Returns:
            bool: Component varsa True, yoksa False
        """
        return component_name in self.component_cache
    
    def get_component_path(self, component_name, partial=True):
        """
        Component dosya yolunu al
        
        Args:
            component_name (str): Component adı
            partial (bool): Parça component mi
            
        Returns:
            str: Component dosya yolu
        """
        if not self.component_exists(component_name):
            return None
        
        key = 'partial' if partial else 'full'
        if key not in self.component_cache[component_name]:
            return None
            
        return str(self.component_path / self.component_cache[component_name][key])
    
    # Component oluşturma metotları
    def create_alert(self, message, type="info", title=None, dismissible=True, icon=None):
        """Alert component oluştur"""
        return self.render_component('alert', {
            'message': message,
            'type': type,
            'title': title,
            'dismissible': dismissible,
            'icon': icon
        })
    
    def create_button(self, text, style="basic", class_name="btn-primary", size=None, 
                     icon=None, icon_position="left", disabled=False, loading=False, 
                     full_width=False, rounded=False, href=None, target=None, id=None, 
                     custom_classes=None, attributes=None, type="button"):
        """Button component oluştur"""
        return self.render_component('button', {
            'text': text,
            'style': style,
            'class_name': class_name,
            'size': size,
            'icon': icon,
            'icon_position': icon_position,
            'disabled': disabled,
            'loading': loading,
            'full_width': full_width,
            'rounded': rounded,
            'href': href,
            'target': target,
            'id': id,
            'custom_classes': custom_classes,
            'attributes': attributes,
            'type': type
        })
    
    def create_card(self, title=None, subtitle=None, content=None, header=True, 
                  footer=None, class_name=None, header_class=None, body_class=None, 
                  footer_class=None):
        """Card component oluştur"""
        return self.render_component('card', {
            'title': title,
            'subtitle': subtitle,
            'content': content,
            'header': header,
            'footer': footer,
            'class_name': class_name,
            'header_class': header_class,
            'body_class': body_class,
            'footer_class': footer_class
        })
    
    def create_modal(self, id, title, content=None, size=None, centered=False, 
                    scrollable=False, static=False, footer=None, close_button=True, 
                    primary_button=None, secondary_button=None):
        """Modal component oluştur"""
        return self.render_component('modal', {
            'id': id,
            'title': title,
            'content': content,
            'size': size,
            'centered': centered,
            'scrollable': scrollable,
            'static': static,
            'footer': footer,
            'close_button': close_button,
            'primary_button': primary_button,
            'secondary_button': secondary_button
        })
    
    def create_pagination(self, current_page, total_pages, size=None, alignment="start", 
                         with_arrows=True, with_numbers=True, url_pattern=None):
        """Pagination component oluştur"""
        return self.render_component('pagination', {
            'current_page': current_page,
            'total_pages': total_pages,
            'size': size,
            'alignment': alignment,
            'with_arrows': with_arrows,
            'with_numbers': with_numbers,
            'url_pattern': url_pattern
        }) 