from fastapi import FastAPI, Request, Query, HTTPException, Cookie, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import re
import json

from app.config import APP_NAME, DEBUG_MODE
from app.services.achecar_service import AcheCarService, extrair_placas
from app.services.webrota_service import WebrotaService
from app.services.guias_service import GuiasService
from app.services.auth_service import AuthService
from app.ai.neural_model import neural_brain
from app.ai.knowledge_base import KNOWLEDGE_CHUNKS, INTENTS_LIST

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=APP_NAME,
    description="Central de Suporte Web: Consultas de Veículos, Placas, Ordens de Serviço, Rastreamento e Rankings WebRota.",
    version="1.0.0",
    docs_url=None,
    redoc_url=None
)

# Monta diretórios de arquivos estáticos e templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Modelos Pydantic para requisições da API
class PlacasRequest(BaseModel):
    placas: str = Field(..., description="Uma ou mais placas separadas por linha, espaço ou vírgula")

class IdentificadoresRequest(BaseModel):
    identificadores: str = Field(..., description="Uma ou mais placas ou identificadores de equipamentos/máquinas")

class ChatRequest(BaseModel):
    mensagem: str = Field(..., description="Dúvida ou pergunta em linguagem natural sobre o aparelho ou instalação")
    aparelho: Optional[str] = Field(None, description="Filtro opcional do modelo (ex: ST340UR, ST8300, ST310, ST8310UM)")
    historico: Optional[List[Dict[str, str]]] = Field(None, description="Histórico prévio da conversa")

# Helper: valida sessão e obtém token da WebRota
def obter_usuario_sessao(cs_session: Optional[str]) -> Optional[Dict[str, Any]]:
    return AuthService.validar_sessao(cs_session)

def obter_token_webrota(cs_session: Optional[str] = None) -> Optional[str]:
    usuario = obter_usuario_sessao(cs_session)
    if usuario and usuario.get("webrota_token"):
        return usuario["webrota_token"]
    return WebrotaService._token

# ==========================================
# ROTAS DE AUTENTICAÇÃO
# ==========================================

@app.get("/login", response_class=HTMLResponse)
async def pagina_login(request: Request, cs_session: Optional[str] = Cookie(default=None)):
    """Página de login. Redireciona para home se já autenticado."""
    if obter_usuario_sessao(cs_session):
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"erro": None}
    )

@app.post("/login", response_class=HTMLResponse)
async def processar_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Processa o formulário de login via API WebRota."""
    usuario = await AuthService.autenticar(username, password)
    if not usuario:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"erro": "Usuário ou senha inválidos no sistema WebRota. Verifique suas credenciais."}
        )
    token = AuthService.criar_sessao(usuario)
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="cs_session",
        value=token,
        max_age=43200,
        httponly=True,
        samesite="lax"
    )
    return response

@app.get("/logout")
async def logout(cs_session: Optional[str] = Cookie(default=None)):
    """Encerra a sessão do usuário."""
    AuthService.encerrar_sessao(cs_session)
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("cs_session")
    return response

# ==========================================
# ROTAS DE PÁGINAS (FRONTEND)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def pagina_inicial(request: Request, cs_session: Optional[str] = Cookie(default=None)):
    """Página principal da Central de Suporte — requer autenticação."""
    usuario = obter_usuario_sessao(cs_session)
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": APP_NAME,
            "cabos": GuiasService.get_cabos(),
            "leds": GuiasService.get_leds(),
            "aba_inicial": "tab-home",
            "usuario": usuario
        }
    )

@app.get("/chat", response_class=HTMLResponse)
async def pagina_chat(request: Request, cs_session: Optional[str] = Cookie(default=None)):
    """Página dedicada do Chat Inteligente com a Rede Neural dos Manuais — requer autenticação."""
    usuario = obter_usuario_sessao(cs_session)
    if not usuario:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": APP_NAME,
            "cabos": GuiasService.get_cabos(),
            "leds": GuiasService.get_leds(),
            "aba_inicial": "tab-chat",
            "usuario": usuario
        }
    )

# ==========================================
# ROTAS DE API (REST / JSON)
# ==========================================

@app.get("/api/status")
async def status_sistema(cs_session: Optional[str] = Cookie(default=None)):
    """Verifica a integridade do sistema e conexão com a API da WebRota"""
    token = obter_token_webrota(cs_session)
    status_webrota = {
        "conectado": bool(token),
        "mensagem": "Autenticado na API WebRota com credenciais ativas." if token else "Aguardando login de usuário."
    }
    return {
        "status": "online",
        "app_name": APP_NAME,
        "webrota": status_webrota
    }

# ------------------------------------------
# 1. Consulta AcheCar (Base Pública)
# ------------------------------------------

@app.get("/api/consulta/placa/stream")
async def consultar_placas_stream(placas: str = Query(..., description="Placas separadas por vírgula ou linha")):
    """Streaming SSE para consulta de placas AcheCar com barra de progresso em tempo real."""
    extracao = extrair_placas(placas)
    placas_validas = extracao["validas"]
    placas_invalidas = extracao["invalidas"]

    async def event_generator():
        if not placas_validas:
            payload = json.dumps({"tipo": "erro", "mensagem": "Nenhuma placa válida encontrada.", "invalidas": placas_invalidas}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
            return

        async for evento in AcheCarService.consultar_em_massa_stream(placas_validas):
            payload = json.dumps(evento, ensure_ascii=False)
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

@app.get("/api/consulta/placa/{placa}")
async def consultar_placa_unica(placa: str):
    """Consulta individual de placa na base pública AcheCar"""
    resultado = await AcheCarService.consultar_placa(placa)
    return resultado

@app.post("/api/consulta/placa")
async def consultar_placas_lote(req: PlacasRequest):
    """Consulta em lote de placas na base pública AcheCar"""
    extracao = extrair_placas(req.placas)
    placas_validas = extracao["validas"]
    placas_invalidas = extracao["invalidas"]

    if not placas_validas:
        return {
            "sucesso": False,
            "mensagem": "Nenhuma placa válida encontrada no texto informado.",
            "invalidas": placas_invalidas,
            "resultados": []
        }

    resultado_busca = await AcheCarService.consultar_em_massa(placas_validas)

    return {
        "sucesso": True,
        "total_validas": len(placas_validas),
        "invalidas": placas_invalidas,
        **resultado_busca
    }

# ------------------------------------------
# 2. Consulta Veículo (WebRota)
# ------------------------------------------

@app.get("/api/consulta/veiculo/{placa}")
async def consultar_veiculo_webrota_unico(placa: str, cs_session: Optional[str] = Cookie(default=None)):
    """Consulta individual de veículo na base cadastral da WebRota"""
    token = obter_token_webrota(cs_session)
    resultado = await WebrotaService.consultar_veiculo(placa, token=token)
    return resultado

@app.post("/api/consulta/veiculo")
async def consultar_veiculos_webrota_lote(req: PlacasRequest, cs_session: Optional[str] = Cookie(default=None)):
    """Consulta em lote de veículos na base cadastral da WebRota"""
    token = obter_token_webrota(cs_session)
    linhas = [linha.strip() for linha in req.placas.split('\n') if linha.strip()]
    placas_validas = []
    placas_invalidas = []

    for linha in linhas:
        placa_limpa = re.sub(r'[^a-zA-Z0-9]', '', linha).upper()
        if len(placa_limpa) == 7:
            if placa_limpa not in placas_validas:
                placas_validas.append(placa_limpa)
        else:
            placas_invalidas.append(linha)

    if not placas_validas:
        return {
            "sucesso": False,
            "mensagem": "Nenhuma placa de 7 caracteres válida informada.",
            "invalidas": placas_invalidas,
            "resultados": []
        }

    resultados = await WebrotaService.consultar_veiculos_em_massa(placas_validas, token=token)
    return {
        "sucesso": True,
        "total_consultadas": len(resultados),
        "invalidas": placas_invalidas,
        "resultados": resultados
    }

# ------------------------------------------
# 3. Consulta Local de Instalação (WebRota)
# ------------------------------------------

@app.get("/api/consulta/local/{identificador}")
async def consultar_local_unico(identificador: str, cs_session: Optional[str] = Cookie(default=None)):
    """Consulta local de instalação da última OS para uma placa ou máquina"""
    token = obter_token_webrota(cs_session)
    resultado = await WebrotaService.consultar_local_instalacao(identificador, token=token)
    return resultado

@app.post("/api/consulta/local")
async def consultar_locais_lote(req: IdentificadoresRequest, cs_session: Optional[str] = Cookie(default=None)):
    """Consulta locais de instalação para múltiplos identificadores/placas"""
    token = obter_token_webrota(cs_session)
    linhas = [linha.strip().upper() for linha in req.identificadores.split('\n') if linha.strip()]
    identificadores = list(dict.fromkeys(linhas))

    if not identificadores:
        return {
            "sucesso": False,
            "mensagem": "Nenhum identificador informado.",
            "resultados": []
        }

    resultados = await WebrotaService.consultar_locais_em_massa(identificadores, token=token)
    return {
        "sucesso": True,
        "total_consultadas": len(resultados),
        "resultados": resultados
    }

@app.post("/api/consulta/local/stream")
async def consultar_locais_stream(req: IdentificadoresRequest, cs_session: Optional[str] = Cookie(default=None)):
    """Streaming SSE para consulta de locais de instalação com barra de progresso."""
    token = obter_token_webrota(cs_session)
    linhas = [linha.strip().upper() for linha in req.identificadores.split('\n') if linha.strip()]
    identificadores = list(dict.fromkeys(linhas))

    async def event_generator():
        if not identificadores:
            payload = json.dumps({"tipo": "erro", "mensagem": "Nenhum identificador informado."}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
            return
        async for evento in WebrotaService.consultar_locais_em_massa_stream(identificadores, token=token):
            payload = json.dumps(evento, ensure_ascii=False)
            yield f"data: {payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )

# ------------------------------------------
# 4. Rankings de Execução de OS (WebRota)
# ------------------------------------------

@app.get("/api/ranking/diario")
async def ranking_diario(
    data: Optional[str] = Query(None, description="Data no formato AAAA-MM-DD (padrão: hoje)"),
    cs_session: Optional[str] = Cookie(default=None)
):
    """Ranking diário de ordens de serviço executadas na WebRota"""
    token = obter_token_webrota(cs_session)
    return await WebrotaService.ranking_diario(data_referencia=data, token=token)

@app.get("/api/ranking/mensal")
async def ranking_mensal(
    ano: Optional[int] = Query(None, description="Ano de referência"),
    mes: Optional[int] = Query(None, description="Mês de referência (1-12)"),
    cs_session: Optional[str] = Cookie(default=None)
):
    """Ranking mensal comparativo entre os técnicos (Túlio x Kaio)"""
    token = obter_token_webrota(cs_session)
    return await WebrotaService.ranking_mensal(ano=ano, mes=mes, token=token)

# ------------------------------------------
# 5. Guias Técnicos
# ------------------------------------------

@app.get("/api/guias/cabos")
async def obter_guia_cabos():
    """Retorna dados do padrão de cores de chicotes para instalação"""
    return {"cabos": GuiasService.get_cabos()}

@app.get("/api/guias/leds")
async def obter_guia_leds():
    """Retorna diagnóstico de piscadas de LEDs Suntech"""
    return GuiasService.get_leds()

# ------------------------------------------
# 6. Assistente de IA / Rede Neural dos Manuais
# ------------------------------------------

@app.post("/api/chat/perguntar")
async def chat_perguntar(req: ChatRequest):
    """
    Processa a dúvida do técnico/usuário através da Rede Neural dos Manuais.
    Entende o desejo do usuário em linguagem natural mesmo com digitação informal ou sem exatidão.
    """
    if not req.mensagem or not req.mensagem.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

    resultado = neural_brain.gerar_resposta(
        query=req.mensagem,
        filtro_aparelho=req.aparelho
    )
    return {
        "sucesso": True,
        **resultado
    }

@app.get("/api/chat/status")
async def chat_status_rede_neural():
    """Retorna o status e arquitetura da Rede Neural carregada"""
    return {
        "status": "online" if neural_brain.is_trained else "treinando",
        "arquitetura": "Rede Neural Multicamadas (MLPClassifier: 128 -> 64 nós, ReLU, Softmax)",
        "vetorizacao": "TF-IDF N-Grams (1 a 3) + Projeção Latente SVD Denso (LSA)",
        "total_intencoes": len(INTENTS_LIST),
        "intencoes": INTENTS_LIST,
        "total_chunks_conhecimento": len(KNOWLEDGE_CHUNKS),
        "aparelhos_cobertos": [
            "Queclink GV50CG",
            "ST4305", "ST8300", "ST8300R", "ST8300H",
            "ST340UR",
            "ST310U", "ST310UC", "ST310UC2", "ST310ULC",
            "ST8310UM", "ST8210"
        ]
    }

@app.post("/api/chat/retreinar")
async def chat_retreinar_rede_neural():
    """Força o retreinamento da Rede Neural a partir da base atualizada de manuais"""
    neural_brain.treinar()
    return {
        "sucesso": True,
        "mensagem": "Rede neural retreinada e salva com sucesso!"
    }
