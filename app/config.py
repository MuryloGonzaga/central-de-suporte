import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env (se existir localmente)
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

def get_env_flexible(*keys: str, default: str = "") -> str:
    """
    Busca variável de ambiente com máxima compatibilidade:
    - Múltiplos nomes e aliases (USER, USUARIO, LOGIN, SENHA, PASSWORD)
    - Case-insensitive (maiúsculas ou minúsculas no Vercel)
    - Remove aspas acidentais ("valor" ou 'valor') e espaços
    """
    val = None
    # 1. Busca direta nas chaves fornecidas
    for key in keys:
        v = os.getenv(key)
        if v:
            val = v
            break

    # 2. Se não achou, busca case-insensitive em todo o os.environ
    if not val:
        keys_upper = {k.upper() for k in keys}
        for env_k, env_v in os.environ.items():
            if env_k.upper() in keys_upper and env_v:
                val = env_v
                break

    if not val:
        return default

    val = str(val).strip()
    # Remove aspas se o usuário salvou com aspas no Vercel
    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
        val = val[1:-1].strip()
    return val

# Configurações do WebRota
WEBROTA_USER = get_env_flexible("WEBROTA_USER", "WEBROTA_USUARIO", "WEBROTA_LOGIN")
WEBROTA_PASS = get_env_flexible("WEBROTA_PASS", "WEBROTA_PASSWORD", "WEBROTA_SENHA")

# Credenciais exclusivas para Ranking de OS (compatível com .env e Vercel)
# Se não for informado um usuário específico para ranking, utiliza o WEBROTA_USER padrão
WEBROTA_RANKING_USER = get_env_flexible(
    "WEBROTA_RANKING_USER", "WEBROTA_RANKING_USUARIO",
    default=WEBROTA_USER
)
WEBROTA_RANKING_PASS = get_env_flexible(
    "WEBROTA_RANKING_PASS", "WEBROTA_RANKING_PASSWORD", "WEBROTA_RANKING_SENHA",
    default=WEBROTA_PASS
)

# Configurações do Servidor Web
APP_HOST = get_env_flexible("APP_HOST", default="0.0.0.0")
APP_PORT = int(get_env_flexible("APP_PORT", default="8000"))
SECRET_KEY = get_env_flexible("SECRET_KEY", default="chave-secreta-central-suporte-2026")
DEBUG_MODE = get_env_flexible("DEBUG", default="false").lower() in ("true", "1", "yes")

# Título e Informações da Aplicação
APP_NAME = get_env_flexible("APP_NAME", default="Central de Suporte - Rastreamento & WebRota")
