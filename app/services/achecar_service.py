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
    # User-Agents realistas para alternar em caso de consultas em lote
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0"
    ]

    @classmethod
    async def consultar_placa(cls, placa: str, session: Optional[aiohttp.ClientSession] = None) -> Dict[str, Any]:
        """
        Consulta os dados do veículo na base pública AcheCar para uma placa.
        """
        placa_limpa = re.sub(r'[^a-zA-Z0-9]', '', placa).upper()
        if not PADRAO_PLACA.match(placa_limpa):
            return {
                "placa": placa_limpa,
                "sucesso": False,
                "status_code": 400,
                "erro": "Formato de placa inválido. Use ABC1D23 ou ABC1234."
            }

        ua = random.choice(cls.USER_AGENTS)
        headers = {
            "Content-Type": "application/json",
            "User-Agent": ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": f"https://www.achecar.com.br/consulta-gratuita?plate={placa_limpa}"
        }
        params = {"plate": placa_limpa, "ck": "true"}

        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            async with session.get(
                cls.BASE_URL,
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=18)
            ) as response:
                status = response.status
                if status == 200:
                    dados = await response.json()
                    return {
                        "placa": placa_limpa,
                        "sucesso": True,
                        "status_code": 200,
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
                elif status in (403, 429):
                    return {
                        "placa": placa_limpa,
                        "sucesso": False,
                        "status_code": status,
                        "erro": "Acesso temporariamente bloqueado pela API Pública (Rate Limit). O sistema pausará para proteção."
                    }
                elif status == 404:
                    return {
                        "placa": placa_limpa,
                        "sucesso": False,
                        "status_code": 404,
                        "erro": "Placa não encontrada na base pública."
                    }
                else:
                    return {
                        "placa": placa_limpa,
                        "sucesso": False,
                        "status_code": status,
                        "erro": f"Erro na API Pública (Código de resposta: {status})."
                    }
        except asyncio.TimeoutError:
            return {
                "placa": placa_limpa,
                "sucesso": False,
                "status_code": 408,
                "erro": "Tempo de espera esgotado (Timeout) ao consultar a base pública."
            }
        except Exception as e:
            return {
                "placa": placa_limpa,
                "sucesso": False,
                "status_code": 500,
                "erro": f"Falha de conexão: {str(e)}"
            }
        finally:
            if close_session:
                await session.close()

    @classmethod
    async def consultar_em_massa(
        cls,
        placas: List[str]
    ) -> Dict[str, Any]:
        """
        Consulta uma lista de placas com intervalo OBRIGATORIAMENTE suave e seguro
        para blindar contra bloqueios e rate limit da API pública AcheCar.
        """
        resultados = []
        bloqueado = False

        async with aiohttp.ClientSession() as session:
            for idx, placa in enumerate(placas):
                res = await cls.consultar_placa(placa, session=session)
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
        placas: List[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Gerador assíncrono para streaming de progresso em tempo real (Server-Sent Events).
        Garante intervalo suave obrigatório e informa percentual e status placa a placa.
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

                res = await cls.consultar_placa(placa, session=session)
                resultados.append(res)

                # Notifica o resultado obtido desta placa específica
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
            "mensagem": f"Consulta concluída! {len(resultados)} de {total} placa(s) processadas com sucesso."
        }
