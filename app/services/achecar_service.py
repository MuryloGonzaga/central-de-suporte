import re
import asyncio
import random
import aiohttp
from typing import List, Dict, Any, Optional

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

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
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
                timeout=aiohttp.ClientTimeout(total=15)
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
                        "erro": "Acesso temporariamente bloqueado pela API Pública (Rate Limit / Bloqueio). Tente novamente em instantes ou utilize a consulta Webrota."
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
                "erro": "Tempo de espera esgotado (Timeout) ao consultar a API pública."
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
        placas: List[str],
        intervalo_seguro: bool = True
    ) -> Dict[str, Any]:
        """
        Consulta uma lista de placas com intervalo seguro para evitar bloqueio.
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

                # Intervalo seguro apenas se houver mais placas a consultar
                if idx < len(placas) - 1:
                    delay = random.uniform(2.5, 4.0) if intervalo_seguro else 0.8
                    await asyncio.sleep(delay)

        return {
            "total_consultadas": len(resultados),
            "total_solicitadas": len(placas),
            "bloqueio_detectado": bloqueado,
            "resultados": resultados
        }

