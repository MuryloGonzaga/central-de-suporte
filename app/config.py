import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Configurações do WebRota
WEBROTA_USER = os.getenv("WEBROTA_USER", "").strip()
WEBROTA_PASS = os.getenv("WEBROTA_PASS", os.getenv("WEBROTA_PASSWORD", "")).strip()

# Credenciais exclusivas para Ranking de OS (compatível com .env e Vercel)
# Se não for informado um usuário específico para ranking, utiliza o WEBROTA_USER padrão
WEBROTA_RANKING_USER = (os.getenv("WEBROTA_RANKING_USER") or WEBROTA_USER).strip()
WEBROTA_RANKING_PASS = (os.getenv("WEBROTA_RANKING_PASS") or os.getenv("WEBROTA_RANKING_PASSWORD") or WEBROTA_PASS).strip()

# Configurações do Servidor Web
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
SECRET_KEY = os.getenv("SECRET_KEY", "chave-secreta-central-suporte-2026")
DEBUG_MODE = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

# Título e Informações da Aplicação
APP_NAME = os.getenv("APP_NAME", "Central de Suporte - Rastreamento & WebRota")

# Modo Manutenção — quando True, todas as rotas exibem a página de manutenção
# Para ativar:   MAINTENANCE_MODE=true  (ou 1 ou yes)
# Para desativar: MAINTENANCE_MODE=false (ou 0 ou no)
MAINTENANCE_MODE = os.getenv("MAINTENANCE_MODE", "false").lower() in ("true", "1", "yes")
