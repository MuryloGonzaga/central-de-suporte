import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Configurações do WebRota
WEBROTA_USER = os.getenv("WEBROTA_USER", "")
WEBROTA_PASS = os.getenv("WEBROTA_PASS", "")

# Configurações do Servidor Web
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-central-suporte-2026")
DEBUG_MODE = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Título e Informações da Aplicação
APP_NAME = os.getenv("APP_NAME", "Central de Suporte - Rastreamento & WebRota")

