"""
İyzico Payment API - Gerçek Implementasyon
Bu modül İyzico'nun resmi Python SDK'sını kullanır.
API Dokümantasyonu: https://dev.iyzipay.com/
"""

try:
    import iyzipay
    from iyzipay import Payment, CheckoutFormInitialize, Refund, Cancel
    IYZIPAY_AVAILABLE = True
except ImportError:
    IYZIPAY_AVAILABLE = False
    # Mock classes for when iyzipay is not available
    class Payment:
        @staticmethod
        def create(request, options):
            return {"status": "failure", "errorMessage": "iyzipay SDK not installed"}
    
    class CheckoutFormInitialize:
        @staticmethod
        def create(request, options):
            return {"status": "failure", "errorMessage": "iyzipay SDK not installed"}
    
    class Refund:
        @staticmethod
        def create(request, options):
            return {"status": "failure", "errorMessage": "iyzipay SDK not installed"}
    
    class Cancel:
        @staticmethod
        def create(request, options):
            return {"status": "failure", "errorMessage": "iyzipay SDK not installed"}

from typing import Dict, List, Optional, Any
import logging
import json

class IyzicoPaymentAPI:
    """İyzico Payment API Client"""
    
    def __init__(self, api_key: str, secret_key: str, sandbox: bool = True):
        self.api_key = api_key
        self.secret_key = secret_key
        self.sandbox = sandbox
        
        # API Options
        self.options = {
            'api_key': self.api_key,
            'secret_key': self.secret_key,
            'base_url': 'sandbox-api.iyzipay.com' if sandbox else 'api.iyzipay.com'
        }
        
        self.logger = logging.getLogger(__name__)
        
        # SDK availability kontrolü
        if not IYZIPAY_AVAILABLE:
            self.logger.warning("İyzico SDK is not available. Install with: pip install iyzipay")
        
        # Test credentials kontrolü
        if api_key in ['YOUR_API_KEY', 'YOUR_IYZICO_API_KEY', '']:
            self.logger.warning("Test or empty API key detected for İyzico")

    def _create_buyer(self, buyer_data: Dict) -> Dict:
        """Alıcı bilgilerini oluşturur"""
        return {
            'id': buyer_data.get('id', 'BY789'),
            'name': buyer_data.get('name', 'John'),
            'surname': buyer_data.get('surname', 'Doe'),
            'gsmNumber': buyer_data.get('gsm_number', '+905350000000'),
            'email': buyer_data.get('email', 'email@email.com'),
            'identityNumber': buyer_data.get('identity_number', '74300864791'),
            'lastLoginDate': buyer_data.get('last_login_date', '2015-10-05 12:43:35'),
            'registrationDate': buyer_data.get('registration_date', '2013-04-21 15:12:09'),
            'registrationAddress': buyer_data.get('registration_address', 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1'),
            'ip': buyer_data.get('ip', '85.34.78.112'),
            'city': buyer_data.get('city', 'Istanbul'),
            'country': buyer_data.get('country', 'Turkey'),
            'zipCode': buyer_data.get('zip_code', '34732')
        }

    def _create_address(self, address_data: Dict) -> Dict:
        """Adres bilgilerini oluşturur"""
        return {
            'contactName': address_data.get('contact_name', 'Jane Doe'),
            'city': address_data.get('city', 'Istanbul'),
            'country': address_data.get('country', 'Turkey'),
            'address': address_data.get('address', 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1'),
            'zipCode': address_data.get('zip_code', '34732')
        }

    def _create_basket_items(self, items: List[Dict]) -> List[Dict]:
        """Sepet öğelerini oluşturur"""
        basket_items = []
        for item in items:
            basket_items.append({
                'id': item.get('id', 'BI101'),
                'name': item.get('name', 'Product'),
                'category1': item.get('category1', 'Electronics'),
                'category2': item.get('category2', 'Accessories'),
                'itemType': item.get('item_type', 'PHYSICAL'),
                'price': str(item.get('price', '0.1'))
            })
        return basket_items

    # ÖDEME İŞLEMLERİ
    def _check_sdk_availability(self) -> Dict:
        """SDK availability kontrolü"""
        if not IYZIPAY_AVAILABLE:
            return {
                "success": False,
                "error": "İyzico SDK not installed. Run: pip install iyzipay"
            }
        return {"success": True}

    def create_payment(self, payment_data: Dict) -> Dict:
        """Ödeme oluşturur (Non-3DS)"""
        # SDK kontrolü
        sdk_check = self._check_sdk_availability()
        if not sdk_check["success"]:
            return sdk_check
            
        try:
            request = {
                'locale': payment_data.get('locale', 'tr'),
                'conversationId': payment_data.get('conversation_id', '123456789'),
                'price': str(payment_data.get('price', '1')),
                'paidPrice': str(payment_data.get('paid_price', '1.2')),
                'currency': payment_data.get('currency', 'TRY'),
                'installment': payment_data.get('installment', '1'),
                'basketId': payment_data.get('basket_id', 'B67832'),
                'paymentChannel': payment_data.get('payment_channel', 'WEB'),
                'paymentGroup': payment_data.get('payment_group', 'PRODUCT'),
                'paymentCard': payment_data.get('payment_card', {}),
                'buyer': self._create_buyer(payment_data.get('buyer', {})),
                'shippingAddress': self._create_address(payment_data.get('shipping_address', {})),
                'billingAddress': self._create_address(payment_data.get('billing_address', {})),
                'basketItems': self._create_basket_items(payment_data.get('basket_items', []))
            }

            payment = Payment().create(request, self.options)
            return self._parse_response(payment)

        except Exception as e:
            self.logger.error(f"İyzico payment creation failed: {e}")
            return {"success": False, "error": str(e)}

    def create_3ds_payment(self, payment_data: Dict) -> Dict:
        """3DS ödeme başlatır"""
        try:
            request = {
                'locale': payment_data.get('locale', 'tr'),
                'conversationId': payment_data.get('conversation_id', '123456789'),
                'price': str(payment_data.get('price', '1')),
                'paidPrice': str(payment_data.get('paid_price', '1.2')),
                'currency': payment_data.get('currency', 'TRY'),
                'installment': payment_data.get('installment', '1'),
                'basketId': payment_data.get('basket_id', 'B67832'),
                'paymentChannel': payment_data.get('payment_channel', 'WEB'),
                'paymentGroup': payment_data.get('payment_group', 'PRODUCT'),
                'callbackUrl': payment_data.get('callback_url', 'https://www.merchant.com/callback'),
                'paymentCard': payment_data.get('payment_card', {}),
                'buyer': self._create_buyer(payment_data.get('buyer', {})),
                'shippingAddress': self._create_address(payment_data.get('shipping_address', {})),
                'billingAddress': self._create_address(payment_data.get('billing_address', {})),
                'basketItems': self._create_basket_items(payment_data.get('basket_items', []))
            }

            three_ds_initialize = ThreedsInitialize().create(request, self.options)
            return self._parse_response(three_ds_initialize)

        except Exception as e:
            self.logger.error(f"İyzico 3DS payment initialization failed: {e}")
            return {"success": False, "error": str(e)}

    def complete_3ds_payment(self, payment_id: str, conversation_data: str) -> Dict:
        """3DS ödemeyi tamamlar"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'paymentId': payment_id,
                'conversationData': conversation_data
            }

            three_ds_payment = ThreedsPayment().create(request, self.options)
            return self._parse_response(three_ds_payment)

        except Exception as e:
            self.logger.error(f"İyzico 3DS payment completion failed: {e}")
            return {"success": False, "error": str(e)}

    # CHECKOUT FORM
    def initialize_checkout_form(self, payment_data: Dict) -> Dict:
        """Checkout form başlatır"""
        try:
            request = {
                'locale': payment_data.get('locale', 'tr'),
                'conversationId': payment_data.get('conversation_id', '123456789'),
                'price': str(payment_data.get('price', '1')),
                'paidPrice': str(payment_data.get('paid_price', '1.2')),
                'currency': payment_data.get('currency', 'TRY'),
                'basketId': payment_data.get('basket_id', 'B67832'),
                'paymentGroup': payment_data.get('payment_group', 'PRODUCT'),
                'callbackUrl': payment_data.get('callback_url', 'https://www.merchant.com/callback'),
                'enabledInstallments': payment_data.get('enabled_installments', ['2', '3', '6', '9']),
                'buyer': self._create_buyer(payment_data.get('buyer', {})),
                'shippingAddress': self._create_address(payment_data.get('shipping_address', {})),
                'billingAddress': self._create_address(payment_data.get('billing_address', {})),
                'basketItems': self._create_basket_items(payment_data.get('basket_items', []))
            }

            checkout_form_initialize = CheckoutFormInitialize().create(request, self.options)
            return self._parse_response(checkout_form_initialize)

        except Exception as e:
            self.logger.error(f"İyzico checkout form initialization failed: {e}")
            return {"success": False, "error": str(e)}

    def retrieve_checkout_form_result(self, token: str) -> Dict:
        """Checkout form sonucunu alır"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'token': token
            }

            checkout_form_result = CheckoutForm().retrieve(request, self.options)
            return self._parse_response(checkout_form_result)

        except Exception as e:
            self.logger.error(f"İyzico checkout form result retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    # ÖDEME SORGULAMA
    def retrieve_payment(self, payment_id: str, conversation_id: str = None) -> Dict:
        """Ödeme bilgisini sorgular"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': conversation_id or '123456789',
                'paymentId': payment_id
            }

            payment = Payment().retrieve(request, self.options)
            return self._parse_response(payment)

        except Exception as e:
            self.logger.error(f"İyzico payment retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    # İPTAL VE İADE
    def cancel_payment(self, payment_id: str, ip: str, reason: str = None) -> Dict:
        """Ödemeyi iptal eder"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'paymentId': payment_id,
                'ip': ip,
                'reason': reason or 'other'
            }

            cancel = Cancel().create(request, self.options)
            return self._parse_response(cancel)

        except Exception as e:
            self.logger.error(f"İyzico payment cancellation failed: {e}")
            return {"success": False, "error": str(e)}

    def refund_payment(self, payment_transaction_id: str, price: str, ip: str, 
                       currency: str = 'TRY', reason: str = None) -> Dict:
        """Ödeme iadesi yapar"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'paymentTransactionId': payment_transaction_id,
                'price': price,
                'ip': ip,
                'currency': currency,
                'reason': reason or 'other'
            }

            refund = Refund().create(request, self.options)
            return self._parse_response(refund)

        except Exception as e:
            self.logger.error(f"İyzico payment refund failed: {e}")
            return {"success": False, "error": str(e)}

    # KART SAKLAMA
    def create_card(self, card_data: Dict) -> Dict:
        """Kart bilgilerini saklar"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'email': card_data.get('email', 'email@email.com'),
                'externalId': card_data.get('external_id', 'external_id'),
                'card': {
                    'cardAlias': card_data.get('card_alias', 'card alias'),
                    'cardHolderName': card_data.get('card_holder_name', 'John Doe'),
                    'cardNumber': card_data.get('card_number', '5528790000000008'),
                    'expireMonth': card_data.get('expire_month', '12'),
                    'expireYear': card_data.get('expire_year', '2030')
                }
            }

            card = Card().create(request, self.options)
            return self._parse_response(card)

        except Exception as e:
            self.logger.error(f"İyzico card creation failed: {e}")
            return {"success": False, "error": str(e)}

    def delete_card(self, card_user_key: str, card_token: str) -> Dict:
        """Saklı kartı siler"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'cardUserKey': card_user_key,
                'cardToken': card_token
            }

            card = Card().delete(request, self.options)
            return self._parse_response(card)

        except Exception as e:
            self.logger.error(f"İyzico card deletion failed: {e}")
            return {"success": False, "error": str(e)}

    def list_cards(self, card_user_key: str) -> Dict:
        """Saklı kartları listeler"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'cardUserKey': card_user_key
            }

            card_list = CardList().retrieve(request, self.options)
            return self._parse_response(card_list)

        except Exception as e:
            self.logger.error(f"İyzico card listing failed: {e}")
            return {"success": False, "error": str(e)}

    # BIN SORGULAMA
    def retrieve_bin(self, bin_number: str) -> Dict:
        """BIN bilgisini sorgular"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'binNumber': bin_number
            }

            bin_number_result = BinNumber().retrieve(request, self.options)
            return self._parse_response(bin_number_result)

        except Exception as e:
            self.logger.error(f"İyzico BIN retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    # TAKSİT SORGULAMA
    def retrieve_installment_info(self, bin_number: str, price: str) -> Dict:
        """Taksit bilgilerini sorgular"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'binNumber': bin_number,
                'price': price
            }

            installment_info = InstallmentInfo().retrieve(request, self.options)
            return self._parse_response(installment_info)

        except Exception as e:
            self.logger.error(f"İyzico installment info retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    # ALT ÖDEME (MARKETPLACE)
    def create_sub_merchant(self, sub_merchant_data: Dict) -> Dict:
        """Alt üye oluşturur"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'subMerchantExternalId': sub_merchant_data.get('external_id', 'B49224'),
                'subMerchantType': sub_merchant_data.get('type', 'PERSONAL'),
                'address': sub_merchant_data.get('address', 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1'),
                'contactName': sub_merchant_data.get('contact_name', 'Jane Doe'),
                'email': sub_merchant_data.get('email', 'email@submerchantemail.com'),
                'gsmNumber': sub_merchant_data.get('gsm_number', '+905350000000'),
                'name': sub_merchant_data.get('name', 'John\'s market'),
                'iban': sub_merchant_data.get('iban', 'TR180006200119000006672315'),
                'identityNumber': sub_merchant_data.get('identity_number', '31300864726'),
                'currency': sub_merchant_data.get('currency', 'TRY')
            }

            sub_merchant = SubMerchant().create(request, self.options)
            return self._parse_response(sub_merchant)

        except Exception as e:
            self.logger.error(f"İyzico sub merchant creation failed: {e}")
            return {"success": False, "error": str(e)}

    def update_sub_merchant(self, sub_merchant_key: str, sub_merchant_data: Dict) -> Dict:
        """Alt üye günceller"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'subMerchantKey': sub_merchant_key,
                'iban': sub_merchant_data.get('iban', 'TR180006200119000006672315'),
                'address': sub_merchant_data.get('address', 'Nidakule Göztepe, Merdivenköy Mah. Bora Sok. No:1'),
                'contactName': sub_merchant_data.get('contact_name', 'Jane Doe'),
                'email': sub_merchant_data.get('email', 'email@submerchantemail.com'),
                'gsmNumber': sub_merchant_data.get('gsm_number', '+905350000000'),
                'name': sub_merchant_data.get('name', 'John\'s market'),
                'identityNumber': sub_merchant_data.get('identity_number', '31300864726'),
                'currency': sub_merchant_data.get('currency', 'TRY')
            }

            sub_merchant = SubMerchant().update(request, self.options)
            return self._parse_response(sub_merchant)

        except Exception as e:
            self.logger.error(f"İyzico sub merchant update failed: {e}")
            return {"success": False, "error": str(e)}

    def retrieve_sub_merchant(self, sub_merchant_external_id: str) -> Dict:
        """Alt üye bilgisini sorgular"""
        try:
            request = {
                'locale': 'tr',
                'conversationId': '123456789',
                'subMerchantExternalId': sub_merchant_external_id
            }

            sub_merchant = SubMerchant().retrieve(request, self.options)
            return self._parse_response(sub_merchant)

        except Exception as e:
            self.logger.error(f"İyzico sub merchant retrieval failed: {e}")
            return {"success": False, "error": str(e)}

    # YARDIMCI FONKSİYONLAR
    def _parse_response(self, response) -> Dict:
        """İyzico yanıtını parse eder"""
        try:
            if hasattr(response, 'read'):
                response_dict = json.loads(response.read().decode('utf-8'))
            else:
                response_dict = response.__dict__
            
            return {
                "success": response_dict.get('status') == 'success',
                "status": response_dict.get('status'),
                "error_code": response_dict.get('errorCode'),
                "error_message": response_dict.get('errorMessage'),
                "error_group": response_dict.get('errorGroup'),
                "conversation_id": response_dict.get('conversationId'),
                "system_time": response_dict.get('systemTime'),
                "data": response_dict
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Response parse error: {str(e)}",
                "raw_response": str(response)
            }

    def test_connection(self) -> Dict:
        """API bağlantısını test eder"""
        try:
            # BIN sorgulama ile test
            test_bin = "552879"
            result = self.retrieve_bin(test_bin)
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": "İyzico API bağlantısı başarılı",
                    "api_key": self.api_key[:8] + "...",
                    "sandbox": self.sandbox,
                    "test_result": result
                }
            else:
                return {
                    "success": False,
                    "message": f"İyzico API test başarısız: {result.get('error_message', 'Unknown error')}",
                    "error_code": result.get('error_code'),
                    "response": result
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"İyzico API bağlantı hatası: {str(e)}"
            }

    # TEST KARTLARI
    def get_test_cards(self) -> Dict:
        """Test kartlarını döndürür"""
        return {
            "success_cards": [
                {
                    "card_number": "5528790000000008",
                    "expire_month": "12",
                    "expire_year": "2030",
                    "cvc": "123",
                    "card_holder_name": "John Doe",
                    "bank": "Halkbank",
                    "card_type": "Master Card (Credit)"
                },
                {
                    "card_number": "4766620000000001",
                    "expire_month": "12",
                    "expire_year": "2030",
                    "cvc": "123",
                    "card_holder_name": "John Doe",
                    "bank": "Denizbank",
                    "card_type": "Visa (Debit)"
                },
                {
                    "card_number": "4603450000000000",
                    "expire_month": "12",
                    "expire_year": "2030",
                    "cvc": "123",
                    "card_holder_name": "John Doe",
                    "bank": "Denizbank",
                    "card_type": "Visa (Credit)"
                }
            ],
            "error_cards": [
                {
                    "card_number": "4111111111111129",
                    "error": "Not sufficient funds"
                },
                {
                    "card_number": "4129111111111111",
                    "error": "Do not honour"
                },
                {
                    "card_number": "4128111111111112",
                    "error": "Invalid transaction"
                }
            ]
        }


# Örnek kullanım ve test fonksiyonları
def test_iyzico_api():
    """İyzico API'sini test eder"""
    
    # Test credentials (gerçek projede environment variable'lardan alınmalı)
    api_key = "YOUR_API_KEY"
    secret_key = "YOUR_SECRET_KEY"
    
    # API client oluştur
    iyzico_api = IyzicoPaymentAPI(
        api_key=api_key,
        secret_key=secret_key,
        sandbox=True
    )
    
    print("🔄 İyzico API Bağlantı Testi...")
    connection_test = iyzico_api.test_connection()
    print(f"Bağlantı: {'✅ Başarılı' if connection_test['success'] else '❌ Başarısız'}")
    
    if connection_test['success']:
        print("\n💳 BIN Sorgulama Testi...")
        bin_result = iyzico_api.retrieve_bin("552879")
        print(f"BIN Sonucu: {'✅ Başarılı' if bin_result['success'] else '❌ Başarısız'}")
        
        print("\n📊 Taksit Bilgisi Testi...")
        installment_result = iyzico_api.retrieve_installment_info("552879", "100")
        print(f"Taksit Bilgisi: {'✅ Başarılı' if installment_result['success'] else '❌ Başarısız'}")
        
        print("\n💳 Test Kartları...")
        test_cards = iyzico_api.get_test_cards()
        print(f"Başarılı test kartı sayısı: {len(test_cards['success_cards'])}")
        print(f"Hata test kartı sayısı: {len(test_cards['error_cards'])}")


if __name__ == "__main__":
    test_iyzico_api()