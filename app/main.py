from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import re

from app.config import APP_NAME, DEBUG_MODE
from app.services.achecar_service import AcheCarService, extrair_placas
from app.services.webrota_service import WebrotaService
from app.services.guias_service import GuiasService

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title=APP_NAME,
    description="Central de Suporte Web: Consultas de Veículos, Placas, Ordens de Serviço, Rastreamento e Rankings WebRota.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Monta diretórios de arquivos estáticos e templates
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Modelos Pydantic para requisições da API
class PlacasRequest(BaseModel):
    placas: str = Field(..., description="Uma ou mais placas separadas por linha, espaço ou vírgula")
    intervalo_seguro: Optional[bool] = Field(True, description="Se verdadeiro, aplica pausa suave contra bloqueios da API pública")

class IdentificadoresRequest(BaseModel):
    identificadores: str = Field(..., description="Uma ou mais placas ou identificadores de equipamentos/máquinas")

# ==========================================
# ROTAS DE PÁGINAS (FRONTEND)
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def pagina_inicial(request: Request):
    """Página principal da Central de Suporte"""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": APP_NAME,
            "cabos": GuiasService.get_cabos(),
            "leds": GuiasService.get_leds()
        }
    )

# ==========================================
# ROTAS DE API (REST / JSON)
# ==========================================

@app.get("/api/status")
async def status_sistema():
    """Verifica a integridade do sistema e conexão com a API da WebRota"""
    status_webrota = await WebrotaService.verificar_credenciais()
    return {
        "status": "online",
        "app_name": APP_NAME,
        "webrota": status_webrota
    }

# ------------------------------------------
# 1. Consulta AcheCar (Base Pública)
# ------------------------------------------

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

    resultado_busca = await AcheCarService.consultar_em_massa(
        placas_validas,
        intervalo_seguro=req.intervalo_seguro
    )

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
async def consultar_veiculo_webrota_unico(placa: str):
    """Consulta individual de veículo na base cadastral da WebRota"""
    resultado = await WebrotaService.consultar_veiculo(placa)
    return resultado

@app.post("/api/consulta/veiculo")
async def consultar_veiculos_webrota_lote(req: PlacasRequest):
    """Consulta em lote de veículos na base cadastral da WebRota"""
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

    resultados = await WebrotaService.consultar_veiculos_em_massa(placas_validas)
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
async def consultar_local_unico(identificador: str):
    """Consulta local de instalação da última OS para uma placa ou máquina"""
    resultado = await WebrotaService.consultar_local_instalacao(identificador)
    return resultado

@app.post("/api/consulta/local")
async def consultar_locais_lote(req: IdentificadoresRequest):
    """Consulta locais de instalação para múltiplos identificadores/placas"""
    linhas = [linha.strip().upper() for linha in req.identificadores.split('\n') if linha.strip()]
    # Remove duplicados mantendo a ordem
    identificadores = list(dict.fromkeys(linhas))

    if not identificadores:
        return {
            "sucesso": False,
            "mensagem": "Nenhum identificador informado.",
            "resultados": []
        }

    resultados = await WebrotaService.consultar_locais_em_massa(identificadores)
    return {
        "sucesso": True,
        "total_consultadas": len(resultados),
        "resultados": resultados
    }

# ------------------------------------------
# 4. Rankings de Execução de OS (WebRota)
# ------------------------------------------

@app.get("/api/ranking/diario")
async def ranking_diario(data: Optional[str] = Query(None, description="Data no formato AAAA-MM-DD (padrão: hoje)")):
    """Ranking diário de ordens de serviço executadas na WebRota"""
    return await WebrotaService.ranking_diario(data_referencia=data)

@app.get("/api/ranking/mensal")
async def ranking_mensal(
    ano: Optional[int] = Query(None, description="Ano de referência"),
    mes: Optional[int] = Query(None, description="Mês de referência (1-12)")
):
    """Ranking mensal comparativo entre os técnicos (Túlio x Kaio)"""
    return await WebrotaService.ranking_mensal(ano=ano, mes=mes)

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
