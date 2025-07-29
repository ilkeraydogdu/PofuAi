#!/usr/bin/env python3
"""
Marketplace Integrations Installation Script
Bu script tüm marketplace entegrasyonları için gerekli kurulumu yapar.
"""

import os
import sys
import subprocess
import logging
import shutil
from pathlib import Path

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MarketplaceInstaller:
    """Marketplace entegrasyonları kurulum sınıfı"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def check_python_version(self):
        """Python versiyonunu kontrol et"""
        logger.info("Checking Python version...")
        
        if sys.version_info < (3, 8):
            error = "Python 3.8 or higher is required"
            self.errors.append(error)
            logger.error(error)
            return False
        
        logger.info(f"✅ Python {sys.version} detected")
        return True
    
    def install_dependencies(self):
        """Python dependencies'lerini kur"""
        logger.info("Installing Python dependencies...")
        
        try:
            # requirements.txt dosyasını kontrol et
            requirements_file = self.project_root / "requirements.txt"
            if not requirements_file.exists():
                error = "requirements.txt file not found"
                self.errors.append(error)
                logger.error(error)
                return False
            
            # Dependencies'leri kur
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                error = f"Failed to install dependencies: {result.stderr}"
                self.errors.append(error)
                logger.error(error)
                return False
            
            logger.info("✅ Dependencies installed successfully")
            return True
            
        except Exception as e:
            error = f"Error installing dependencies: {e}"
            self.errors.append(error)
            logger.error(error)
            return False
    
    def setup_environment(self):
        """Environment dosyasını ayarla"""
        logger.info("Setting up environment configuration...")
        
        try:
            env_example = self.project_root / ".env.example"
            env_file = self.project_root / ".env"
            
            # .env.example dosyasını kontrol et
            if not env_example.exists():
                warning = ".env.example file not found, creating basic .env"
                self.warnings.append(warning)
                logger.warning(warning)
                
                # Basic .env oluştur
                basic_env_content = """
# Basic Marketplace Integration Settings
DATABASE_URL=sqlite:///marketplace.db
REDIS_URL=redis://localhost:6379/0

# Marketplace Settings (fill in your credentials)
TRENDYOL_ENABLED=false
TRENDYOL_API_KEY=your_trendyol_api_key
TRENDYOL_API_SECRET=your_trendyol_api_secret
TRENDYOL_SUPPLIER_ID=your_supplier_id
TRENDYOL_SANDBOX=true

HEPSIBURADA_ENABLED=false
HEPSIBURADA_USERNAME=your_hepsiburada_username
HEPSIBURADA_PASSWORD=your_hepsiburada_password
HEPSIBURADA_MERCHANT_ID=your_merchant_id
HEPSIBURADA_SANDBOX=true

N11_ENABLED=false
N11_API_KEY=your_n11_api_key
N11_API_SECRET=your_n11_api_secret
N11_SANDBOX=true

IYZICO_ENABLED=false
IYZICO_API_KEY=your_iyzico_api_key
IYZICO_SECRET_KEY=your_iyzico_secret_key
IYZICO_SANDBOX=true

# Security
SECRET_KEY=your_secret_key_here
MARKETPLACE_ENCRYPTION_KEY=your_encryption_key_here

# Logging
LOG_LEVEL=INFO
MARKETPLACE_ENABLE_LOGGING=true
"""
                with open(env_file, 'w') as f:
                    f.write(basic_env_content)
            else:
                # .env.example'dan kopyala
                if not env_file.exists():
                    shutil.copy(env_example, env_file)
                    logger.info("✅ .env file created from .env.example")
                else:
                    logger.info("✅ .env file already exists")
            
            return True
            
        except Exception as e:
            error = f"Error setting up environment: {e}"
            self.errors.append(error)
            logger.error(error)
            return False
    
    def setup_directories(self):
        """Gerekli dizinleri oluştur"""
        logger.info("Creating necessary directories...")
        
        try:
            directories = [
                "logs",
                "storage",
                "storage/cache",
                "storage/sessions",
                "storage/uploads"
            ]
            
            for directory in directories:
                dir_path = self.project_root / directory
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Created directory: {directory}")
            
            return True
            
        except Exception as e:
            error = f"Error creating directories: {e}"
            self.errors.append(error)
            logger.error(error)
            return False
    
    def setup_database(self):
        """Database'i ayarla"""
        logger.info("Setting up database...")
        
        try:
            # Database setup script'ini çalıştır
            setup_script = self.project_root / "setup_database.py"
            if setup_script.exists():
                result = subprocess.run([
                    sys.executable, str(setup_script)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    error = f"Database setup failed: {result.stderr}"
                    self.errors.append(error)
                    logger.error(error)
                    return False
                
                logger.info("✅ Database setup completed")
            else:
                warning = "setup_database.py not found, skipping database setup"
                self.warnings.append(warning)
                logger.warning(warning)
            
            return True
            
        except Exception as e:
            error = f"Error setting up database: {e}"
            self.errors.append(error)
            logger.error(error)
            return False
    
    def test_imports(self):
        """Kritik modüllerin import edilebilirliğini test et"""
        logger.info("Testing critical imports...")
        
        critical_imports = [
            "flask",
            "sqlalchemy",
            "requests",
            "cryptography",
            "redis"
        ]
        
        optional_imports = [
            "iyzipay"
        ]
        
        success = True
        
        # Kritik imports
        for module in critical_imports:
            try:
                __import__(module)
                logger.info(f"✅ {module} import successful")
            except ImportError as e:
                error = f"Critical import failed: {module} - {e}"
                self.errors.append(error)
                logger.error(error)
                success = False
        
        # Optional imports
        for module in optional_imports:
            try:
                __import__(module)
                logger.info(f"✅ {module} import successful")
            except ImportError as e:
                warning = f"Optional import failed: {module} - {e}"
                self.warnings.append(warning)
                logger.warning(warning)
        
        return success
    
    def test_marketplace_apis(self):
        """Marketplace API modüllerini test et"""
        logger.info("Testing marketplace API modules...")
        
        try:
            # Test basic imports
            sys.path.append(str(self.project_root))
            
            from core.Services.trendyol_marketplace_api import TrendyolMarketplaceAPI
            from core.Services.n11_marketplace_api import N11MarketplaceAPI
            from core.Services.hepsiburada_marketplace_api import HepsiburadaMarketplaceAPI
            from core.Services.real_integration_manager import RealIntegrationManager
            
            logger.info("✅ All marketplace API modules imported successfully")
            
            # Test configuration system
            try:
                from config.marketplace_config import get_all_marketplace_status
                status = get_all_marketplace_status()
                logger.info("✅ Configuration system working")
                logger.info(f"Marketplace status: {len(status)} marketplaces configured")
            except Exception as e:
                warning = f"Configuration system test failed: {e}"
                self.warnings.append(warning)
                logger.warning(warning)
            
            return True
            
        except Exception as e:
            error = f"Marketplace API test failed: {e}"
            self.errors.append(error)
            logger.error(error)
            return False
    
    def generate_encryption_key(self):
        """Şifreleme anahtarı oluştur"""
        logger.info("Generating encryption key...")
        
        try:
            from cryptography.fernet import Fernet
            
            # Yeni key oluştur
            key = Fernet.generate_key()
            key_string = key.decode()
            
            # .env dosyasına ekle
            env_file = self.project_root / ".env"
            if env_file.exists():
                with open(env_file, 'r') as f:
                    content = f.read()
                
                # Eğer encryption key yoksa ekle
                if 'MARKETPLACE_ENCRYPTION_KEY=' in content and 'your_encryption_key_here' in content:
                    content = content.replace(
                        'MARKETPLACE_ENCRYPTION_KEY=your_encryption_key_here',
                        f'MARKETPLACE_ENCRYPTION_KEY={key_string}'
                    )
                    
                    with open(env_file, 'w') as f:
                        f.write(content)
                    
                    logger.info("✅ Encryption key generated and added to .env")
                else:
                    logger.info("✅ Encryption key already configured")
            
            return True
            
        except Exception as e:
            warning = f"Failed to generate encryption key: {e}"
            self.warnings.append(warning)
            logger.warning(warning)
            return False
    
    def create_startup_script(self):
        """Startup script oluştur"""
        logger.info("Creating startup script...")
        
        try:
            startup_content = """#!/usr/bin/env python3
\"\"\"
Marketplace Integration Startup Script
\"\"\"

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def main():
    print("🚀 Starting Marketplace Integration System...")
    
    # Import and run the main application
    try:
        from app import app
        
        # Development server
        if os.getenv('FLASK_ENV') == 'development':
            app.run(
                host='0.0.0.0',
                port=int(os.getenv('PORT', 5000)),
                debug=True
            )
        else:
            # Production server (use gunicorn)
            print("For production, use: gunicorn -w 4 -b 0.0.0.0:5000 app:app")
            
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        print("Make sure Flask is installed and app.py exists")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
            
            startup_file = self.project_root / "start_marketplace.py"
            with open(startup_file, 'w') as f:
                f.write(startup_content)
            
            # Make executable
            os.chmod(startup_file, 0o755)
            
            logger.info("✅ Startup script created: start_marketplace.py")
            return True
            
        except Exception as e:
            warning = f"Failed to create startup script: {e}"
            self.warnings.append(warning)
            logger.warning(warning)
            return False
    
    def run_installation(self):
        """Tam kurulum sürecini çalıştır"""
        logger.info("🚀 Starting Marketplace Integration Installation")
        logger.info("=" * 60)
        
        success = True
        
        # Adım adım kurulum
        steps = [
            ("Python Version Check", self.check_python_version),
            ("Install Dependencies", self.install_dependencies),
            ("Setup Environment", self.setup_environment),
            ("Create Directories", self.setup_directories),
            ("Generate Encryption Key", self.generate_encryption_key),
            ("Setup Database", self.setup_database),
            ("Test Imports", self.test_imports),
            ("Test Marketplace APIs", self.test_marketplace_apis),
            ("Create Startup Script", self.create_startup_script)
        ]
        
        completed_steps = []
        failed_steps = []
        
        for step_name, step_function in steps:
            logger.info(f"\n📋 {step_name}...")
            try:
                if step_function():
                    completed_steps.append(step_name)
                    logger.info(f"✅ {step_name} completed")
                else:
                    failed_steps.append(step_name)
                    logger.error(f"❌ {step_name} failed")
                    success = False
            except Exception as e:
                failed_steps.append(step_name)
                logger.error(f"❌ {step_name} failed with exception: {e}")
                success = False
        
        # Sonuçları göster
        logger.info("\n" + "=" * 60)
        logger.info("📊 INSTALLATION SUMMARY")
        logger.info("=" * 60)
        
        logger.info(f"✅ Completed steps: {len(completed_steps)}")
        for step in completed_steps:
            logger.info(f"   - {step}")
        
        if failed_steps:
            logger.info(f"\n❌ Failed steps: {len(failed_steps)}")
            for step in failed_steps:
                logger.info(f"   - {step}")
        
        if self.warnings:
            logger.info(f"\n⚠️  Warnings: {len(self.warnings)}")
            for warning in self.warnings:
                logger.info(f"   - {warning}")
        
        if self.errors:
            logger.info(f"\n🚨 Errors: {len(self.errors)}")
            for error in self.errors:
                logger.info(f"   - {error}")
        
        # Final status
        if success:
            logger.info("\n🎉 INSTALLATION COMPLETED SUCCESSFULLY!")
            logger.info("\n📝 Next Steps:")
            logger.info("1. Edit .env file with your API credentials")
            logger.info("2. Enable integrations (set TRENDYOL_ENABLED=true etc.)")
            logger.info("3. Run: python start_marketplace.py")
            logger.info("4. Test integrations: python test_real_integrations.py")
        else:
            logger.info("\n❌ INSTALLATION FAILED!")
            logger.info("Please fix the errors above and run the installation again.")
        
        return success

def main():
    """Ana fonksiyon"""
    installer = MarketplaceInstaller()
    success = installer.run_installation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()