"""
Component Controller
Tüm componentlerin merkezi olarak yönetildiği controller
"""
from flask import render_template, abort, request
from core.Services.UIService import UIService
from core.Services.ComponentService import ComponentService

class ComponentController:
    """
    Component Controller sınıfı
    """
    
    def __init__(self):
        """Controller'ı başlat"""
        self.ui_service = UIService()
        self.component_service = ComponentService()
        self.component_list = self.component_service.get_component_list()
    
    def index(self):
        """
        Component ana sayfasını göster
        
        Returns:
            str: Render edilmiş HTML
        """
        components = self.component_list
        return render_template('components/index.html', components=components)
    
    def show_component(self, component_name):
        """
        Component sayfasını göster
        
        Args:
            component_name (str): Component adı
            
        Returns:
            str: Render edilmiş HTML
        """
        # Component var mı kontrol et
        if not self.component_service.component_exists(component_name):
            abort(404)
        
        # Tam sayfa componentler için örnek veri hazırla
        component_data = self._prepare_component_data(component_name)
        
        # Component'i render et
        return render_template(f'components/{component_name}.html', **component_data)
    
    def _prepare_component_data(self, component_name):
        """
        Component için örnek veri hazırla
        
        Args:
            component_name (str): Component adı
            
        Returns:
            dict: Component verisi
        """
        data = {}
        
        # Her component için uygun örnek veri hazırla
        if component_name == 'alert':
            data['alert'] = self.ui_service.create_alert(
                message="Bu bir örnek alert mesajıdır.",
                type="success",
                title="Başarılı!",
                dismissible=True
            )
            data['alert_examples'] = [
                self.ui_service.create_alert("Bu bir primary alert", "primary"),
                self.ui_service.create_alert("Bu bir success alert", "success"),
                self.ui_service.create_alert("Bu bir danger alert", "danger"),
                self.ui_service.create_alert("Bu bir warning alert", "warning"),
                self.ui_service.create_alert("Bu bir info alert", "info")
            ]
            
        elif component_name == 'badge':
            data['badge'] = self.ui_service.create_badge(
                text="New",
                style="basic",
                class_name="bg-primary"
            )
            data['badge_examples'] = [
                self.ui_service.create_badge("Primary", "basic", "bg-primary"),
                self.ui_service.create_badge("Success", "basic", "bg-success"),
                self.ui_service.create_badge("Danger", "pill", "bg-danger"),
                self.ui_service.create_badge("Warning", "pill", "bg-warning"),
                self.ui_service.create_badge("8", "icon", "bg-grd-primary", icon="notifications"),
                self.ui_service.create_badge("5", "positioned", "bg-danger", button_text="Messages")
            ]
            
        elif component_name == 'button':
            data['button'] = self.ui_service.create_button(
                text="Button",
                style="basic",
                class_name="btn-primary"
            )
            data['button_examples'] = [
                self.ui_service.create_button("Primary", "basic", "btn-primary"),
                self.ui_service.create_button("Success", "basic", "btn-success"),
                self.ui_service.create_button("Danger", "basic", "btn-danger"),
                self.ui_service.create_button("Outline", "outline", "btn-outline-primary"),
                self.ui_service.create_button("Gradient", "gradient", "btn-grd-primary"),
                self.ui_service.create_button("Icon", "basic", "btn-primary", icon="home")
            ]
            
        elif component_name == 'card':
            data['card'] = self.ui_service.create_card(
                title="Card Title",
                subtitle="Card Subtitle",
                content="Bu bir örnek kart içeriğidir."
            )
            data['card_examples'] = [
                self.ui_service.create_card("Başlıklı Kart", "Alt başlık", "İçerik metni"),
                self.ui_service.create_card(content="Sadece içerik", header=False),
                self.ui_service.create_card("Footer'lı Kart", "Alt başlık", "İçerik", footer="Footer içeriği"),
                self.ui_service.create_card("Özel Sınıflı", "Alt başlık", "İçerik", class_name="border-primary")
            ]
            
        elif component_name == 'chips':
            data['chip'] = self.ui_service.create_chip(
                text="Example Chip",
                style="bg-primary text-white"
            )
            data['chip_examples'] = [
                self.ui_service.create_chip("Primary", "bg-primary text-white"),
                self.ui_service.create_chip("Success", "bg-success text-white"),
                self.ui_service.create_chip("Small", "bg-primary text-white", size="sm"),
                self.ui_service.create_chip("Closable", "bg-danger text-white", closable=True),
                self.ui_service.create_chip("John Doe", "bg-primary text-white", image_src="/public/static/assets/images/avatars/01.png")
            ]
            
        elif component_name == 'modal':
            data['modal'] = self.ui_service.create_modal(
                id="exampleModal",
                title="Modal Title",
                content="Bu bir örnek modal içeriğidir."
            )
            data['modal_examples'] = [
                self.ui_service.create_modal("smallModal", "Small Modal", "Küçük modal içeriği", size="sm"),
                self.ui_service.create_modal("largeModal", "Large Modal", "Büyük modal içeriği", size="lg"),
                self.ui_service.create_modal("centeredModal", "Centered Modal", "Merkezlenmiş modal", centered=True),
                self.ui_service.create_modal("buttonModal", "Button Modal", "Butonlu modal", 
                                          primary_button={"text": "Save", "class": "btn-primary"},
                                          secondary_button={"text": "Close", "class": "btn-secondary"})
            ]
            data['button'] = self.ui_service.create_button(
                text="Open Modal",
                style="basic",
                class_name="btn-primary",
                attributes={"data-bs-toggle": "modal", "data-bs-target": "#exampleModal"}
            )
            
        elif component_name == 'pagination':
            data['pagination'] = self.ui_service.create_pagination(
                current_page=1,
                total_pages=5
            )
            data['pagination_examples'] = [
                self.ui_service.create_pagination(2, 10, alignment="start"),
                self.ui_service.create_pagination(3, 10, alignment="center"),
                self.ui_service.create_pagination(4, 10, alignment="end"),
                self.ui_service.create_pagination(5, 10, size="sm"),
                self.ui_service.create_pagination(6, 10, size="lg")
            ]
            
        elif component_name == 'progress_bars':
            data['progress_bar'] = self.ui_service.create_progress_bar([
                {"value": 25, "style": "bg-primary", "width": 25}
            ])
            data['progress_bar_examples'] = [
                self.ui_service.create_progress_bar([{"value": 25, "style": "bg-primary", "width": 25}]),
                self.ui_service.create_progress_bar([{"value": 50, "style": "bg-success", "width": 50}]),
                self.ui_service.create_progress_bar([{"value": 75, "style": "bg-danger", "width": 75}]),
                self.ui_service.create_progress_bar([{"value": 100, "style": "bg-info", "width": 100}]),
                self.ui_service.create_progress_bar([
                    {"value": 15, "style": "bg-success", "width": 15, "label": "15%"},
                    {"value": 30, "style": "bg-info", "width": 30, "label": "30%"},
                    {"value": 20, "style": "bg-warning", "width": 20, "label": "20%"}
                ])
            ]
            
        elif component_name == 'spinner':
            data['spinner'] = self.ui_service.create_spinner(
                type="border",
                color="primary"
            )
            data['spinner_examples'] = [
                self.ui_service.create_spinner("border", color="primary"),
                self.ui_service.create_spinner("grow", color="success"),
                self.ui_service.create_spinner("border", "sm", "danger"),
                self.ui_service.create_spinner("grow", "lg", "warning"),
                self.ui_service.create_spinner("border", color="info", custom_style="width: 3rem; height: 3rem;")
            ]
            
        elif component_name == 'tabs':
            data['tabs'] = self.ui_service.create_tabs(
                id="exampleTabs",
                tabs=[
                    {"id": "home", "title": "Home", "content": "Home content"},
                    {"id": "profile", "title": "Profile", "content": "Profile content"},
                    {"id": "contact", "title": "Contact", "content": "Contact content"}
                ]
            )
            data['tabs_examples'] = [
                self.ui_service.create_tabs("pills", [
                    {"id": "home", "title": "Home", "content": "Home content"},
                    {"id": "profile", "title": "Profile", "content": "Profile content"}
                ], style="pills"),
                self.ui_service.create_tabs("vertical", [
                    {"id": "home", "title": "Home", "content": "Home content"},
                    {"id": "profile", "title": "Profile", "content": "Profile content"}
                ], vertical=True),
                self.ui_service.create_tabs("fill", [
                    {"id": "home", "title": "Home", "content": "Home content"},
                    {"id": "profile", "title": "Profile", "content": "Profile content"}
                ], fill=True)
            ]
            
        return data 