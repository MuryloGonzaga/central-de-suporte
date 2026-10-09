import sys
import uvicorn
from app.config import APP_HOST, APP_PORT, DEBUG_MODE

# Configura encoding UTF-8 no Windows para evitar erros de charset
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

if __name__ == "__main__":
    print("=" * 60)
    print(">> Iniciando Central de Suporte - Aplicacao Web")
    print(f">> Endereco Local: http://localhost:{APP_PORT}")
    print(f">> Documentacao Swagger API: http://localhost:{APP_PORT}/docs")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=DEBUG_MODE
    )

