# -*- coding: utf-8 -*-
"""
Serviço de Consulta e Decodificação de Chassi (VIN)
Utiliza a base do DecoderX (BlueFIX) e decodificador nativo ISO 3779 / NBR 6066
para identificar Marca, Modelo, Ano Modelo, Motorização, Combustível, País e Planta.
"""

import re
import asyncio
import random
import aiohttp
import html as html_lib
from typing import List, Dict, Any, Optional, AsyncGenerator

# Padrão internacional de chassi (17 caracteres alfanuméricos, sem as letras I, O e Q)
PADRAO_CHASSI = re.compile(r'^[A-HJ-NPR-Z0-9]{17}$')

# Tabela oficial de Ano Modelo (10ª posição do chassi)
TABELA_ANO_MODELO = {
    'A': '2010', 'B': '2011', 'C': '2012', 'D': '2013', 'E': '2014',
    'F': '2015', 'G': '2016', 'H': '2017', 'J': '2018', 'K': '2019',
    'L': '2020', 'M': '2021', 'N': '2022', 'P': '2023', 'R': '2024',
    'S': '2025', 'T': '2026', 'V': '2027', 'W': '2028', 'X': '2029',
    'Y': '2030', '1': '2001', '2': '2002', '3': '2003', '4': '2004',
    '5': '2005', '6': '2006', '7': '2007', '8': '2008', '9': '2009'
}

# Tabela WMI (World Manufacturer Identifier - 3 primeiros caracteres)
TABELA_WMI = {
    '9BW': {'marca': 'Volkswagen do Brasil', 'pais': 'Brasil'},
    '9BD': {'marca': 'Fiat Chrysler Automóveis Brasil', 'pais': 'Brasil'},
    '9BG': {'marca': 'General Motors do Brasil (Chevrolet)', 'pais': 'Brasil'},
    '93H': {'marca': 'Honda Automóveis do Brasil', 'pais': 'Brasil'},
    '9BR': {'marca': 'Toyota do Brasil', 'pais': 'Brasil'},
    '9BF': {'marca': 'Ford Brasil', 'pais': 'Brasil'},
    '93Y': {'marca': 'Renault do Brasil', 'pais': 'Brasil'},
    '935': {'marca': 'Citroën do Brasil', 'pais': 'Brasil'},
    '936': {'marca': 'Peugeot do Brasil', 'pais': 'Brasil'},
    '94D': {'marca': 'Nissan do Brasil', 'pais': 'Brasil'},
    '9BH': {'marca': 'Hyundai Motor Brasil', 'pais': 'Brasil'},
    '95P': {'marca': 'CAOA Chery Brasil', 'pais': 'Brasil'},
    '9BM': {'marca': 'Mercedes-Benz do Brasil', 'pais': 'Brasil'},
    '95V': {'marca': 'Scania Brasil', 'pais': 'Brasil'},
    '95Z': {'marca': 'Volvo do Brasil', 'pais': 'Brasil'},
    '9CD': {'marca': 'Yamaha Motor do Brasil', 'pais': 'Brasil'},
    '9C2': {'marca': 'Moto Honda da Amazônia', 'pais': 'Brasil'},
    '8AF': {'marca': 'Ford Argentina', 'pais': 'Argentina'},
    '8AG': {'marca': 'Chevrolet Argentina', 'pais': 'Argentina'},
    '8AD': {'marca': 'Peugeot Argentina', 'pais': 'Argentina'},
    '8AW': {'marca': 'Volkswagen Argentina', 'pais': 'Argentina'},
    '8AJ': {'marca': 'Toyota Argentina', 'pais': 'Argentina'},
    '1FA': {'marca': 'Ford Motor Company', 'pais': 'Estados Unidos'},
    '1FM': {'marca': 'Ford Motor Company', 'pais': 'Estados Unidos'},
    '1FT': {'marca': 'Ford Truck', 'pais': 'Estados Unidos'},
    '1GC': {'marca': 'Chevrolet Truck', 'pais': 'Estados Unidos'},
    '1GN': {'marca': 'Chevrolet SUV/Van', 'pais': 'Estados Unidos'},
    '2G1': {'marca': 'Chevrolet Canada', 'pais': 'Canadá'},
    '3VW': {'marca': 'Volkswagen de México', 'pais': 'México'},
    '3FA': {'marca': 'Ford Motor Company Mexico', 'pais': 'México'},
    'WAU': {'marca': 'Audi AG', 'pais': 'Alemanha'},
    'WBA': {'marca': 'BMW AG', 'pais': 'Alemanha'},
    'WDB': {'marca': 'Mercedes-Benz AG', 'pais': 'Alemanha'},
    'WDC': {'marca': 'DaimlerChrysler / Mercedes-Benz', 'pais': 'Alemanha'},
    'WP0': {'marca': 'Porsche AG', 'pais': 'Alemanha'},
    'WVW': {'marca': 'Volkswagen AG', 'pais': 'Alemanha'},
    'ZFA': {'marca': 'Fiat Auto S.p.A.', 'pais': 'Itália'},
    'ZAR': {'marca': 'Alfa Romeo', 'pais': 'Itália'},
    'VF1': {'marca': 'Renault', 'pais': 'França'},
    'VF3': {'marca': 'Peugeot', 'pais': 'França'},
    'VF7': {'marca': 'Citroën', 'pais': 'França'},
    'JHM': {'marca': 'Honda Motor Co.', 'pais': 'Japão'},
    'JT1': {'marca': 'Toyota Motor Corp.', 'pais': 'Japão'},
    'JTE': {'marca': 'Toyota Motor Corp.', 'pais': 'Japão'},
    'JN1': {'marca': 'Nissan Motor Co.', 'pais': 'Japão'},
    'KMH': {'marca': 'Hyundai Motor Company', 'pais': 'Coreia do Sul'},
    'KNA': {'marca': 'Kia Motors Corporation', 'pais': 'Coreia do Sul'},
}

def extrair_chassis(texto: str) -> Dict[str, List[str]]:
    """
    Extrai e valida números de chassi (VIN) a partir de texto
    (quebras de linha, espaços, vírgulas, pontos e traços).
    Retorna {'validas': [...], 'invalidas': [...]}
    """
    if not texto:
        return {"validas": [], "invalidas": []}

    validas = []
    invalidas = []

    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        # 1. Se a linha inteira sem caracteres especiais e espaços forma 17 caracteres
        alfa_linha = re.sub(r'[^a-zA-Z0-9]', '', linha).upper()
        if len(alfa_linha) == 17:
            if PADRAO_CHASSI.match(alfa_linha):
                if alfa_linha not in validas:
                    validas.append(alfa_linha)
            else:
                if linha not in invalidas:
                    invalidas.append(linha)
            continue

        # 2. Busca sequências contínuas de 17 caracteres válidos (sem I, O, Q)
        candidatos_diretos = re.findall(r'\b[A-HJ-NPR-Z0-9]{17}\b', linha, re.IGNORECASE)
        achou_na_linha = False
        if candidatos_diretos:
            for cand in candidatos_diretos:
                cand_u = cand.upper()
                if cand_u not in validas:
                    validas.append(cand_u)
            achou_na_linha = True

        # 3. Busca sequências de 17 caracteres separadas por espaços ou hífens internos
        # Ex: "chassi com espaco: 9BD 17822 68012 3456"
        candidatos_espacados = re.findall(r'(?:[A-HJ-NPR-Z0-9][\s\-]?){16}[A-HJ-NPR-Z0-9]', linha, re.IGNORECASE)
        for ce in candidatos_espacados:
            ce_limpo = re.sub(r'[^a-zA-Z0-9]', '', ce).upper()
            if len(ce_limpo) == 17 and PADRAO_CHASSI.match(ce_limpo):
                if ce_limpo not in validas:
                    validas.append(ce_limpo)
                achou_na_linha = True

        # 4. Se não achou nenhum chassi válido na linha, tenta tokens por delimitadores usuais
        if not achou_na_linha:
            partes = [p.strip() for p in re.split(r'[,;\t]+', linha) if p.strip()]
            for p in partes:
                p_limpo = re.sub(r'[^a-zA-Z0-9]', '', p).upper()
                if len(p_limpo) == 17 and PADRAO_CHASSI.match(p_limpo):
                    if p_limpo not in validas:
                        validas.append(p_limpo)
                elif len(p_limpo) >= 4:
                    if p not in invalidas:
                        invalidas.append(p)

    return {"validas": validas, "invalidas": invalidas}


class ChassiService:
    BASE_URL = "https://www.bluefix.com.br/decoderx/decoder.php"
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ]

    @classmethod
    def decodificar_offline(cls, chassi: str) -> Dict[str, Any]:
        """
        Decodificação estrutural offline baseada no padrão ISO 3779 / NBR 6066.
        Garante retorno imediato mesmo se o serviço externo estiver indisponível.
        """
        chassi_limpo = re.sub(r'[^a-zA-Z0-9]', '', chassi).upper()
        wmi = chassi_limpo[:3]
        info_wmi = TABELA_WMI.get(wmi, {})
        marca = info_wmi.get('marca', 'Fabricante não tabelado')
        pais = info_wmi.get('pais', 'Brasil' if wmi.startswith(('9A', '9B', '9C', '9D', '9E')) else 'Internacional')

        digito_ano = chassi_limpo[9] if len(chassi_limpo) >= 10 else ''
        ano_modelo = TABELA_ANO_MODELO.get(digito_ano, '-')

        return {
            "chassi": chassi_limpo,
            "sucesso": True,
            "status_code": 200,
            "marca": marca,
            "modelo": "Consultar modelo",
            "versao": "-",
            "ano_modelo": ano_modelo,
            "combustivel": "-",
            "motorizacao": "-",
            "cambio": "-",
            "carroceria": "-",
            "pais": pais,
            "planta": "-",
            "codigo_fipe": "-",
            "resumo": f"{marca} (Ano Mod: {ano_modelo})"
        }

    @classmethod
    def extrair_dados_html(cls, raw_html: str, chassi: str) -> Dict[str, Any]:
        """Extrai todos os cartões de informação decodificados da página BlueFIX DecoderX."""
        # Alerta de erro explícito
        if '<div class="alert' in raw_html:
            m_alert = re.search(r'<div[^>]*class=[\'"][^\'"]*alert[^\'"]*[\'"][^>]*>(.*?)</div>', raw_html, re.DOTALL)
            if m_alert:
                msg_clean = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m_alert.group(1))).strip()
                msg_clean = html_lib.unescape(msg_clean).strip()
                # Se ainda assim puder decodificar offline, retorna offline com aviso
                off = cls.decodificar_offline(chassi)
                off["erro"] = msg_clean
                off["origem"] = "offline"
                return off

        # Se não há resultado do DecoderX
        if 'card-result' not in raw_html and 'result-header' not in raw_html:
            off = cls.decodificar_offline(chassi)
            off["origem"] = "offline"
            return off

        info_map = {}
        pattern = r'<h6>(.*?)</h6>\s*<div class="info-value">(.*?)(?:</div>|$)'
        for m in re.finditer(pattern, raw_html, re.DOTALL):
            lbl = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            lbl = html_lib.unescape(lbl).lower()
            val = re.sub(r'<[^>]+>', '', m.group(2)).strip()
            val = html_lib.unescape(val).strip()
            lbl_clean = re.sub(r'[^a-z0-9]', '_', lbl)
            if lbl_clean not in info_map:
                info_map[lbl_clean] = val
            else:
                info_map[f"{lbl_clean}_2"] = val

        m_sub = re.search(r'<small class="text-secondary">\s*(.*?)\s*</small>', raw_html, re.DOTALL)
        header_sub = ""
        if m_sub:
            header_sub = re.sub(r'<[^>]+>', '', m_sub.group(1)).strip()
            header_sub = html_lib.unescape(header_sub).replace('&bull;', '•').strip()

        def get_field(*keywords, default=""):
            for k, v in info_map.items():
                if any(kw in k for kw in keywords):
                    if v and v != "consultando…" and v != "-" and v != "—":
                        return v
            return default

        pais = get_field('pa_s', 'area', default='Brasil')
        fabricante = get_field('fabricante', default='')
        modelo_vds = get_field('modelo', default='')
        versao = get_field('vers_o', default='')
        ano_modelo = get_field('ano', default='')
        motorizacao = get_field('motoriza', default='')
        combustivel = get_field('combust_vel', default='')
        cambio = get_field('c_mbio', default='')
        carroceria = get_field('carroceria', default='')
        planta = get_field('planta', default='')
        codigo_fipe = get_field('c_digo_fipe', default='')
        marca_fipe = get_field('marca', default='')
        modelo_fipe = info_map.get('modelo_2', '')

        # Se ano não veio do HTML, pega da tabela oficial pelo 10º dígito
        if not ano_modelo or ano_modelo in ('-', '—'):
            digito_ano = chassi[9] if len(chassi) >= 10 else ''
            ano_modelo = TABELA_ANO_MODELO.get(digito_ano, '-')

        marca_final = fabricante or marca_fipe
        if not marca_final or marca_final in ('-', '—'):
            off = cls.decodificar_offline(chassi)
            marca_final = off.get('marca', 'Desconhecida')

        modelo_final = modelo_vds
        if (not modelo_final or modelo_final in ('-', '—')) and modelo_fipe:
            modelo_final = modelo_fipe

        if (not modelo_final or modelo_final in ('-', '—')) and header_sub and '•' in header_sub:
            parts = [p.strip() for p in header_sub.split('•')]
            if len(parts) >= 2 and parts[0]:
                modelo_final = parts[0]

        if not modelo_final or modelo_final in ('-', '—'):
            modelo_final = "Modelo não especificado"

        return {
            "chassi": chassi,
            "sucesso": True,
            "status_code": 200,
            "origem": "bluefix",
            "marca": marca_final,
            "modelo": modelo_final,
            "versao": versao if versao not in ('-', '—') else "-",
            "ano_modelo": ano_modelo,
            "combustivel": combustivel if combustivel not in ('-', '—') else "-",
            "motorizacao": motorizacao if motorizacao not in ('-', '—') else "-",
            "cambio": cambio if cambio not in ('-', '—') else "-",
            "carroceria": carroceria if carroceria not in ('-', '—') else "-",
            "pais": pais,
            "planta": planta if planta not in ('-', '—') else "-",
            "codigo_fipe": codigo_fipe if codigo_fipe not in ('-', '—') else "-",
            "resumo": f"{marca_final} {modelo_final}".strip()
        }

    @classmethod
    async def consultar_chassi_stream(
        cls,
        chassi: str,
        session: aiohttp.ClientSession,
        max_tentativas: int = 3
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Consulta os dados do veículo pelo chassi na base pública DecoderX (BlueFIX).
        Em caso de timeout ou instabilidade de rede, tenta novamente automaticamente.
        """
        chassi_limpo = re.sub(r'[^a-zA-Z0-9]', '', chassi).upper()
        if not PADRAO_CHASSI.match(chassi_limpo):
            tem_proibidas = any(c in chassi_limpo for c in ('I', 'O', 'Q'))
            msg_erro = "O chassi deve ter exatamente 17 caracteres."
            if len(chassi_limpo) != 17:
                msg_erro = f"O chassi possui {len(chassi_limpo)} caracteres (deve ter exatamente 17)."
            elif tem_proibidas:
                msg_erro = "O chassi contém caracteres inválidos (I, O e Q não existem no padrão VIN)."

            yield {
                "tipo": "resultado",
                "resultado": {
                    "chassi": chassi_limpo,
                    "sucesso": False,
                    "status_code": 400,
                    "tentativas": 1,
                    "erro": msg_erro
                }
            }
            return

        tentativa = 0
        ultimo_resultado = None

        while tentativa < max_tentativas:
            tentativa += 1
            ua = random.choice(cls.USER_AGENTS)
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": cls.BASE_URL
            }
            payload = {"vin": chassi_limpo, "modelo_informado": "-"}

            precisa_retentar = False
            motivo_retentativa = ""

            try:
                async with session.post(
                    cls.BASE_URL,
                    data=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15, connect=6)
                ) as response:
                    status = response.status
                    if status == 200:
                        html = await response.text()
                        dados = cls.extrair_dados_html(html, chassi_limpo)
                        dados["tentativas"] = tentativa
                        ultimo_resultado = dados
                        yield {"tipo": "resultado", "resultado": dados}
                        return
                    elif status in (500, 502, 503, 504):
                        precisa_retentar = True
                        motivo_retentativa = f"Servidor temporariamente indisponível (HTTP {status})."
                    else:
                        off = cls.decodificar_offline(chassi_limpo)
                        off["tentativas"] = tentativa
                        off["erro"] = f"Resposta do serviço externo (Código {status}), dados obtidos offline."
                        yield {"tipo": "resultado", "resultado": off}
                        return

            except (asyncio.TimeoutError, aiohttp.ServerTimeoutError):
                precisa_retentar = True
                motivo_retentativa = "Tempo de espera esgotado (Timeout)."
            except Exception as e:
                if tentativa < max_tentativas and "timeout" in str(e).lower():
                    precisa_retentar = True
                    motivo_retentativa = f"Falha de conexão ({str(e)})."
                else:
                    off = cls.decodificar_offline(chassi_limpo)
                    off["tentativas"] = tentativa
                    off["erro"] = f"Erro de conexão com o DecoderX, dados obtidos offline."
                    yield {"tipo": "resultado", "resultado": off}
                    return

            if precisa_retentar:
                if tentativa < max_tentativas:
                    yield {
                        "tipo": "tentativa",
                        "chassi": chassi_limpo,
                        "tentativa": tentativa + 1,
                        "max_tentativas": max_tentativas,
                        "mensagem": f"Chassi {chassi_limpo}: {motivo_retentativa} Tentando novamente ({tentativa + 1} de {max_tentativas})..."
                    }
                    await asyncio.sleep(1.8)
                else:
                    off = cls.decodificar_offline(chassi_limpo)
                    off["tentativas"] = tentativa
                    off["erro"] = f"Timeout após {max_tentativas} tentativas. Dados obtidos via decodificador nativo."
                    yield {"tipo": "resultado", "resultado": off}
                    return

    @classmethod
    async def consultar_chassi(
        cls,
        chassi: str,
        session: Optional[aiohttp.ClientSession] = None,
        max_tentativas: int = 3
    ) -> Dict[str, Any]:
        """Consulta um único chassi."""
        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            ultimo = None
            async for evt in cls.consultar_chassi_stream(chassi, session=session, max_tentativas=max_tentativas):
                if evt.get("tipo") == "resultado":
                    ultimo = evt.get("resultado")
            return ultimo or cls.decodificar_offline(chassi)
        finally:
            if close_session:
                await session.close()

    @classmethod
    async def consultar_em_massa(
        cls,
        chassis: List[str],
        max_tentativas: int = 3
    ) -> Dict[str, Any]:
        """Consulta uma lista de chassis com intervalo suave e retentativa automática."""
        resultados = []
        async with aiohttp.ClientSession() as session:
            for idx, chassi in enumerate(chassis):
                res = await cls.consultar_chassi(chassi, session=session, max_tentativas=max_tentativas)
                resultados.append(res)
                if idx < len(chassis) - 1:
                    await asyncio.sleep(random.uniform(1.2, 2.0))

        return {
            "sucesso": True,
            "total_consultadas": len(resultados),
            "resultados": resultados
        }

    @classmethod
    async def consultar_em_massa_stream(
        cls,
        chassis: List[str],
        max_tentativas: int = 3
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Gerador assíncrono para streaming de progresso em tempo real (SSE)."""
        total = len(chassis)
        yield {
            "tipo": "iniciando",
            "total": total,
            "atual": 0,
            "percentual": 0,
            "mensagem": f"Iniciando decodificação de {total} chassi(s)..."
        }

        resultados = []
        async with aiohttp.ClientSession() as session:
            for idx, chassi in enumerate(chassis):
                numero_atual = idx + 1
                percentual = round((idx / total) * 100)

                yield {
                    "tipo": "consultando",
                    "atual": numero_atual,
                    "total": total,
                    "percentual": percentual,
                    "chassi": chassi,
                    "mensagem": f"Decodificando chassi {chassi} ({numero_atual} de {total})..."
                }

                res = None
                async for evt in cls.consultar_chassi_stream(chassi, session=session, max_tentativas=max_tentativas):
                    if evt.get("tipo") == "tentativa":
                        yield {
                            "tipo": "tentativa",
                            "atual": numero_atual,
                            "total": total,
                            "percentual": percentual,
                            "chassi": chassi,
                            "tentativa": evt.get("tentativa"),
                            "max_tentativas": evt.get("max_tentativas"),
                            "mensagem": evt.get("mensagem")
                        }
                    elif evt.get("tipo") == "resultado":
                        res = evt.get("resultado")

                if not res:
                    res = cls.decodificar_offline(chassi)

                resultados.append(res)

                yield {
                    "tipo": "progresso",
                    "atual": numero_atual,
                    "total": total,
                    "percentual": round((numero_atual / total) * 100),
                    "chassi": chassi,
                    "resultado": res,
                    "mensagem": f"Chassi {chassi} processado com sucesso."
                }

                if idx < total - 1:
                    intervalo = random.uniform(1.2, 1.8)
                    yield {
                        "tipo": "pausa",
                        "atual": numero_atual,
                        "total": total,
                        "percentual": round((numero_atual / total) * 100),
                        "mensagem": f"Aguardando {intervalo:.1f}s para próxima consulta segura..."
                    }
                    await asyncio.sleep(intervalo)

        yield {
            "tipo": "concluido",
            "atual": total,
            "total": total,
            "percentual": 100,
            "total_consultadas": len(resultados),
            "total_solicitadas": total,
            "mensagem": f"Decodificação concluída! {len(resultados)} de {total} chassi(s) processados."
        }
