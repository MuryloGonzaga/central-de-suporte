import re
import asyncio
import random
import aiohttp
from typing import List, Dict, Any, Optional, AsyncGenerator

PADRAO_PLACA = re.compile(r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$')

def extrair_placas(texto: str) -> Dict[str, List[str]]:
    """
    Extrai e valida placas a partir de texto (quebras de linha, espaços, vírgulas).
    Retorna {'validas': [...], 'invalidas': [...]}
    """
    if not texto:
        return {"validas": [], "invalidas": []}

    itens = []
    for linha in texto.split('\n'):
        linha = linha.strip()
        if not linha:
            continue
        alfa_linha = re.sub(r'[^a-zA-Z0-9]', '', linha)
        if len(alfa_linha) == 7:
            itens.append(linha)
        else:
            partes = [p.strip() for p in re.split(r'[,;\s]+', linha) if p.strip()]
            if partes:
                itens.extend(partes)
            else:
                itens.append(linha)

    validas = []
    invalidas = []

    for item in itens:
        placa_limpa = re.sub(r'[^a-zA-Z0-9]', '', item).upper()
        if PADRAO_PLACA.match(placa_limpa):
            if placa_limpa not in validas:
                validas.append(placa_limpa)
        else:
            if item not in invalidas:
                invalidas.append(item)

    return {"validas": validas, "invalidas": invalidas}


class AcheCarService:
    BASE_URL = "https://www.achecar.com.br/api/free-lookup"
    # User-Agents realistas para alternar em caso de consultas e retentativas
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ]

    @classmethod
    async def consultar_placa_stream(
        cls,
        placa: str,
        session: aiohttp.ClientSession,
        max_tentativas: int = 3
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Consulta os dados do veículo na base pública AcheCar para uma placa.
        Em caso de Timeout ou instabilidade de rede transitória, tenta novamente
        automaticamente (até max_tentativas) para nunca deixar a placa no limbo.
        """
        placa_limpa = re.sub(r'[^a-zA-Z0-9]', '', placa).upper()
        if not PADRAO_PLACA.match(placa_limpa):
            yield {
                "tipo": "resultado",
                "resultado": {
                    "placa": placa_limpa,
                    "sucesso": False,
                    "status_code": 400,
                    "tentativas": 1,
                    "erro": "Formato de placa inválido. Use ABC1D23 ou ABC1234."
                }
            }
            return

        tentativa = 0
        ultimo_resultado = None

        while tentativa < max_tentativas:
            tentativa += 1
            ua = random.choice(cls.USER_AGENTS)
            headers = {
                "Content-Type": "application/json",
                "User-Agent": ua,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": f"https://www.achecar.com.br/consulta-gratuita?plate={placa_limpa}"
            }
            params = {"plate": placa_limpa, "ck": "true"}

            precisa_retentar = False
            motivo_retentativa = ""

            try:
                # Timeout de 14s por tentativa (tempo suficiente para responder sem travar a fila)
                async with session.get(
                    cls.BASE_URL,
                    params=params,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=14, connect=5)
                ) as response:
                    status = response.status
                    if status == 200:
                        dados = await response.json()
                        ultimo_resultado = {
                            "placa": placa_limpa,
                            "sucesso": True,
                            "status_code": 200,
                            "tentativas": tentativa,
                            "marca": dados.get("brand", "Desconhecida"),
                            "modelo": dados.get("model", ""),
                            "ano_fabricacao": dados.get("year", "N/A"),
                            "ano_modelo": dados.get("yearModel", "N/A"),
                            "cor": dados.get("color", "N/A"),
                            "tipo_veiculo": dados.get("vehicleType", "N/A"),
                            "combustivel": dados.get("fuel", "N/A"),
                            "municipio": dados.get("city", "N/A"),
                            "uf": dados.get("state", "N/A"),
                            "dados_completos": dados
                        }
                        yield {"tipo": "resultado", "resultado": ultimo_resultado}
                        return
                    elif status in (403, 429):
                        # Rate limit: parar para proteção
                        ultimo_resultado = {
                            "placa": placa_limpa,
                            "sucesso": False,
                            "status_code": status,
                            "tentativas": tentativa,
                            "erro": "Acesso temporariamente bloqueado pela API Pública (Rate Limit). O sistema pausará para proteção."
                        }
                        yield {"tipo": "resultado", "resultado": ultimo_resultado}
                        return
                    elif status == 404:
                        # Placa realmente não encontrada
                        ultimo_resultado = {
                            "placa": placa_limpa,
                            "sucesso": False,
                            "status_code": 404,
                            "tentativas": tentativa,
                            "erro": "Placa não encontrada na base pública."
                        }
                        yield {"tipo": "resultado", "resultado": ultimo_resultado}
                        return
                    elif status in (500, 502, 503, 504):
                        # Erro temporário do servidor da base pública
                        precisa_retentar = True
                        motivo_retentativa = f"Servidor público instável (HTTP {status})"
                        ultimo_resultado = {
                            "placa": placa_limpa,
                            "sucesso": False,
                            "status_code": status,
                            "tentativas": tentativa,
                            "erro": f"Erro na API Pública (Código de resposta: {status})."
                        }
                    else:
                        ultimo_resultado = {
                            "placa": placa_limpa,
                            "sucesso": False,
                            "status_code": status,
                            "tentativas": tentativa,
                            "erro": f"Erro na API Pública (Código de resposta: {status})."
                        }
                        yield {"tipo": "resultado", "resultado": ultimo_resultado}
                        return

            except (asyncio.TimeoutError, aiohttp.ServerTimeoutError) as e:
                precisa_retentar = True
                motivo_retentativa = "Tempo de espera esgotado (Timeout)"
                ultimo_resultado = {
                    "placa": placa_limpa,
                    "sucesso": False,
                    "status_code": 408,
                    "tentativas": tentativa,
                    "erro": f"Tempo de espera esgotado (Timeout) após {tentativa} tentativa(s)."
                }
            except (aiohttp.ClientError, ConnectionError) as e:
                precisa_retentar = True
                motivo_retentativa = f"Falha de conexão ({str(e)})"
                ultimo_resultado = {
                    "placa": placa_limpa,
                    "sucesso": False,
                    "status_code": 500,
                    "tentativas": tentativa,
                    "erro": f"Falha de conexão: {str(e)}"
                }
            except Exception as e:
                precisa_retentar = True
                motivo_retentativa = f"Erro inesperado ({str(e)})"
                ultimo_resultado = {
                    "placa": placa_limpa,
                    "sucesso": False,
                    "status_code": 500,
                    "tentativas": tentativa,
                    "erro": f"Falha: {str(e)}"
                }

            if precisa_retentar:
                if tentativa < max_tentativas:
                    # Notifica evento de retry em tempo real
                    yield {
                        "tipo": "tentativa",
                        "placa": placa_limpa,
                        "tentativa": tentativa + 1,
                        "max_tentativas": max_tentativas,
                        "mensagem": f"{motivo_retentativa} na placa {placa_limpa}. Tentando novamente ({tentativa + 1} de {max_tentativas})..."
                    }
                    # Pausa curta antes de retentar com outro User-Agent
                    await asyncio.sleep(2.0)
                else:
                    # Esgotou todas as tentativas
                    yield {"tipo": "resultado", "resultado": ultimo_resultado}
                    return

    @classmethod
    async def consultar_placa(
        cls,
        placa: str,
        session: Optional[aiohttp.ClientSession] = None,
        max_tentativas: int = 3
    ) -> Dict[str, Any]:
        """
        Consulta os dados do veículo na base pública AcheCar para uma placa,
        com retentativa automática em caso de timeout.
        """
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            ultimo = None
            async for evt in cls.consultar_placa_stream(placa, session=session, max_tentativas=max_tentativas):
                if evt.get("tipo") == "resultado":
                    ultimo = evt.get("resultado")
            return ultimo or {
                "placa": placa,
                "sucesso": False,
                "status_code": 408,
                "erro": "Falha na consulta após tentativas."
            }
        finally:
            if close_session:
                await session.close()

    @classmethod
    async def consultar_em_massa(
        cls,
        placas: List[str],
        max_tentativas: int = 3
    ) -> Dict[str, Any]:
        """
        Consulta uma lista de placas com intervalo suave e retentativa automática em timeouts.
        """
        resultados = []
        bloqueado = False

        async with aiohttp.ClientSession() as session:
            for idx, placa in enumerate(placas):
                res = await cls.consultar_placa(placa, session=session, max_tentativas=max_tentativas)
                resultados.append(res)

                if res.get("status_code") in (403, 429):
                    bloqueado = True
                    break

                # Intervalo suave OBRIGATÓRIO entre cada consulta (3.0 a 4.5 segundos)
                if idx < len(placas) - 1:
                    delay = random.uniform(3.0, 4.5)
                    await asyncio.sleep(delay)

        return {
            "total_consultadas": len(resultados),
            "total_solicitadas": len(placas),
            "bloqueio_detectado": bloqueado,
            "intervalo_obrigatorio": True,
            "resultados": resultados
        }

    @classmethod
    async def consultar_em_massa_stream(
        cls,
        placas: List[str],
        max_tentativas: int = 3
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Gerador assíncrono para streaming de progresso em tempo real (Server-Sent Events).
        Garante intervalo suave obrigatório e informa percentual, status e retentativas placa a placa.
        """
        total = len(placas)
        yield {
            "tipo": "inicio",
            "total": total,
            "mensagem": f"Iniciando consulta suave e segura de {total} placa(s)..."
        }

        resultados = []
        bloqueado = False

        async with aiohttp.ClientSession() as session:
            for idx, placa in enumerate(placas):
                numero_atual = idx + 1
                percentual = round((numero_atual / total) * 100, 1)

                # Notifica que está consultando a placa atual
                yield {
                    "tipo": "consultando",
                    "atual": numero_atual,
                    "total": total,
                    "percentual": percentual,
                    "placa": placa,
                    "mensagem": f"Consultando placa {placa} ({numero_atual} de {total})..."
                }

                res = None
                async for evt in cls.consultar_placa_stream(placa, session=session, max_tentativas=max_tentativas):
                    if evt.get("tipo") == "tentativa":
                        # Notifica o usuário na tela que ocorreu timeout e que a placa está sendo retentada
                        yield {
                            "tipo": "tentativa",
                            "atual": numero_atual,
                            "total": total,
                            "percentual": percentual,
                            "placa": placa,
                            "tentativa": evt.get("tentativa"),
                            "max_tentativas": evt.get("max_tentativas"),
                            "mensagem": evt.get("mensagem")
                        }
                    elif evt.get("tipo") == "resultado":
                        res = evt.get("resultado")

                if not res:
                    res = {
                        "placa": placa,
                        "sucesso": False,
                        "status_code": 408,
                        "erro": "Tempo de espera esgotado ao consultar base pública."
                    }

                resultados.append(res)

                # Notifica o resultado final obtido desta placa específica
                yield {
                    "tipo": "progresso",
                    "atual": numero_atual,
                    "total": total,
                    "percentual": percentual,
                    "placa": placa,
                    "resultado": res
                }

                if res.get("status_code") in (403, 429):
                    bloqueado = True
                    yield {
                        "tipo": "alerta",
                        "mensagem": "Aviso: A API pública retornou restrição de acesso. Consulta interrompida para sua proteção."
                    }
                    break

                # Intervalo suave obrigatório com feedback visual
                if idx < len(placas) - 1:
                    delay = round(random.uniform(3.0, 4.5), 1)
                    yield {
                        "tipo": "pausa",
                        "segundos": delay,
                        "atual": numero_atual,
                        "total": total,
                        "percentual": percentual,
                        "mensagem": f"Aguardando intervalo seguro anti-bloqueio ({delay}s)..."
                    }
                    await asyncio.sleep(delay)

        yield {
            "tipo": "concluido",
            "total_consultadas": len(resultados),
            "total_solicitadas": total,
            "bloqueio_detectado": bloqueado,
            "mensagem": f"Consulta concluída! {len(resultados)} de {total} placa(s) processadas."
        }
