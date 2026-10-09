import asyncio
import re
import datetime
from typing import List, Dict, Any, Optional
import aiohttp
from app.config import WEBROTA_USER, WEBROTA_PASS

class WebrotaService:
    BASE_URL = "https://api.webrota.com.br"
    _token: Optional[str] = None
    _token_time: Optional[datetime.datetime] = None
    _lock = asyncio.Lock()

    @classmethod
    async def obter_token(cls, forcar_renovacao: bool = False) -> Optional[str]:
        """
        Obtém ou renova o token JWT de autenticação da WebRota com cache em memória.
        """
        async with cls._lock:
            agora = datetime.datetime.now(datetime.timezone.utc)
            # Reaproveita token se tiver menos de 4 horas
            if (
                not forcar_renovacao
                and cls._token
                and cls._token_time
                and (agora - cls._token_time).total_seconds() < 14400
            ):
                return cls._token

            if not WEBROTA_USER or not WEBROTA_PASS:
                return None

            url_login = f"{cls.BASE_URL}/auth/login/"
            payload = {"username": WEBROTA_USER, "password": WEBROTA_PASS}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url_login, json=payload, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        if resp.status in (200, 201):
                            dados = await resp.json()
                            token = dados.get('token') or dados.get('access_token') or dados.get('data', {}).get('token')
                            if token:
                                cls._token = token
                                cls._token_time = agora
                                return cls._token
            except Exception as e:
                print(f"[ERRO - WebRota Login] Falha ao autenticar: {e}")
                return None

            return None

    @classmethod
    async def verificar_credenciais(cls) -> Dict[str, Any]:
        """
        Verifica se as credenciais configuradas no .env estão válidas e ativas.
        """
        if not WEBROTA_USER or not WEBROTA_PASS:
            return {
                "configurado": False,
                "conectado": False,
                "mensagem": "Credenciais WEBROTA_USER e WEBROTA_PASS não configuradas no arquivo .env."
            }

        token = await cls.obter_token(forcar_renovacao=True)
        if token:
            return {
                "configurado": True,
                "conectado": True,
                "usuario": WEBROTA_USER,
                "mensagem": "Conexão com a WebRota estabelecida com sucesso."
            }
        else:
            return {
                "configurado": True,
                "conectado": False,
                "usuario": WEBROTA_USER,
                "mensagem": "Falha de autenticação na WebRota. Verifique usuário e senha no .env."
            }

    @classmethod
    async def consultar_veiculo(cls, placa: str, session: Optional[aiohttp.ClientSession] = None) -> Dict[str, Any]:
        """
        Consulta veículo cadastrado na WebRota pela placa.
        """
        token = await cls.obter_token()
        if not token:
            return {
                "placa": placa,
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota. Verifique credenciais no .env."
            }

        placa_limpa = re.sub(r'[^a-zA-Z0-9]', '', placa).upper()
        if len(placa_limpa) == 7:
            placa_formatada = f"{placa_limpa[:3]}-{placa_limpa[3:]}"
            placas_para_testar = [placa_formatada, placa_limpa]
        else:
            placas_para_testar = [placa]

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        veiculo_encontrado = None

        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            for formato in placas_para_testar:
                url_vehicle = f"{cls.BASE_URL}/vehicle/"
                params = {
                    "visible": "2",
                    "plate": formato,
                    "includes": "customer,device,vehicle_model,vehicle_model.vehicle_model_manufacturer,fuel_category,fleet,vehicle_color,vehicle_category,licenses,driver,work_shift,state,accessories_vehicle,cost_center,point_of_interest_base,customer.afiliate,vehicle_cost_centers,vehicle_cost_centers.cost_center"
                }

                async with session.get(url_vehicle, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        dados = await resp.json()
                        lista = dados if isinstance(dados, list) else dados.get('data', [])
                        if lista:
                            veiculo_encontrado = lista[0]
                            break
                    elif resp.status in (401, 403):
                        # Token expirado, tenta renovar
                        await cls.obter_token(forcar_renovacao=True)

            if veiculo_encontrado:
                modelo_data = veiculo_encontrado.get('vehicle_model') or {}
                marca_data = modelo_data.get('vehicle_model_manufacturer') or {}

                return {
                    "placa": placa_limpa if len(placa_limpa) == 7 else placa,
                    "sucesso": True,
                    "marca": marca_data.get('name', 'Desconhecida'),
                    "modelo": modelo_data.get('name', 'Desconhecido'),
                    "dados_completos": veiculo_encontrado
                }
            else:
                return {
                    "placa": placa,
                    "sucesso": False,
                    "erro": "Veículo não encontrado no cadastro da WebRota."
                }
        except Exception as e:
            return {
                "placa": placa,
                "sucesso": False,
                "erro": f"Erro de comunicação com a WebRota: {str(e)}"
            }
        finally:
            if close_session:
                await session.close()

    @classmethod
    async def consultar_veiculos_em_massa(cls, placas: List[str]) -> List[Dict[str, Any]]:
        """
        Consulta múltiplos veículos no cadastro da WebRota.
        """
        token = await cls.obter_token()
        if not token:
            return [{"placa": p, "sucesso": False, "erro": "Falha na autenticação da WebRota."} for p in placas]

        resultados = []
        async with aiohttp.ClientSession() as session:
            for placa in placas:
                res = await cls.consultar_veiculo(placa, session=session)
                resultados.append(res)
                await asyncio.sleep(0.15)  # Pequeno intervalo para respeitar a API

        return resultados

    @classmethod
    async def consultar_local_instalacao(cls, identificador: str, session: Optional[aiohttp.ClientSession] = None) -> Dict[str, Any]:
        """
        Rastreia seriais e busca o local de instalação na última OS finalizada (Status E ou F).
        """
        token = await cls.obter_token()
        if not token:
            return {
                "identificador": identificador,
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota."
            }

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        identificador_alfa = re.sub(r'[^A-Z0-9]', '', identificador.upper())

        formatos_para_testar = []
        if len(identificador_alfa) == 7:
            formatos_para_testar.append(f"{identificador_alfa[:3]}-{identificador_alfa[3:]}")
            formatos_para_testar.append(identificador_alfa)
        if identificador not in formatos_para_testar:
            formatos_para_testar.append(identificador)

        close_session = False
        if session is None:
            session = aiohttp.ClientSession()
            close_session = True

        try:
            seriais_encontrados = []
            for formato in formatos_para_testar:
                url_device = f"{cls.BASE_URL}/device/"
                params_device = {
                    "includes": "last_position,last_position.position,last_position.last_driver,last_position.position.driver,gprs_simcard,device_model,vehicle,vehicle.vehicle_category,customer,accessories",
                    "general": formato
                }

                async with session.get(url_device, params=params_device, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        dados = await resp.json()
                        lista_devs = dados if isinstance(dados, list) else dados.get('data', [])
                        for dev in lista_devs:
                            veiculo = dev.get('vehicle', {})
                            if veiculo and '*' in veiculo.get('plate', ''):
                                continue
                            serial = dev.get('serial')
                            if serial and serial not in seriais_encontrados:
                                seriais_encontrados.append(serial)

                if seriais_encontrados:
                    break

            if not seriais_encontrados:
                return {
                    "identificador": identificador,
                    "sucesso": False,
                    "erro": "Identificador não encontrado ou sem dispositivo vinculado."
                }

            detalhes_seriais = []
            for serial in seriais_encontrados:
                url_os = f"{cls.BASE_URL}/maintener/order/"
                params_os = {
                    "aggregated_field": "maintener",
                    "serial": serial,
                    "free_service_orders_search": "true",
                    "includes": "vehicle,vehicle_replace,vehicle_replace.vehicle_category,upload_file,vehicle.vehicle_category,device,device.device_model,device.accessory,device.accessories,device.accessories.accessory_type,device_replace,device_replace.device_model,device_replace.accessories,device_replace.accessories.accessory_type,customer,maintener,maintener.bank_accounts,maintener.bank_accounts.bank_account,maintener.address,maintener.address.city,maintener_order_reason,license,user_executor,vehicle.vehicle_model,vehicle.vehicle_model.vehicle_model_manufacturer,vehicle.license_device_model_vehicle,vehicle.license_device_model_vehicle.device_model,contact_history,vehicle.license_accessories_vehicle,vehicle.license_accessories_vehicle.license_accessory,vehicle.license_accessories_vehicle.license_accessory.accessory_type"
                }

                async with session.get(url_os, params=params_os, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp_os:
                    if resp_os.status == 200:
                        dados_os = await resp_os.json()
                        lista_os = dados_os if isinstance(dados_os, list) else dados_os.get('data', [])

                        os_filtradas = [
                            os_item for os_item in lista_os
                            if os_item.get('status') in ('E', 'F')
                            and os_item.get('date_execution')
                            and os_item.get('type') != 'T'
                            and (os_item.get('local') or '').strip() not in ('', '-')
                        ]

                        if os_filtradas:
                            os_filtradas.sort(key=lambda x: x.get('date_execution'), reverse=True)
                            ultima_os = os_filtradas[0]
                            detalhes_seriais.append({
                                "serial": serial,
                                "local": ultima_os.get('local', 'Local não especificado'),
                                "data_execucao": ultima_os.get('date_execution'),
                                "status": ultima_os.get('status'),
                                "possui_os": True
                            })
                        else:
                            detalhes_seriais.append({
                                "serial": serial,
                                "local": "Sem OS válida (status E/F ou local preenchido)",
                                "data_execucao": None,
                                "status": None,
                                "possui_os": False
                            })
                    else:
                        detalhes_seriais.append({
                            "serial": serial,
                            "local": f"Erro na consulta da OS (Status {resp_os.status})",
                            "data_execucao": None,
                            "status": None,
                            "possui_os": False
                        })

            return {
                "identificador": identificador,
                "sucesso": True,
                "seriais": detalhes_seriais
            }
        except Exception as e:
            return {
                "identificador": identificador,
                "sucesso": False,
                "erro": f"Erro ao consultar local: {str(e)}"
            }
        finally:
            if close_session:
                await session.close()

    @classmethod
    async def consultar_locais_em_massa(cls, identificadores: List[str]) -> List[Dict[str, Any]]:
        """
        Consulta locais de instalação para múltiplos identificadores/placas.
        """
        resultados = []
        async with aiohttp.ClientSession() as session:
            for ident in identificadores:
                res = await cls.consultar_local_instalacao(ident, session=session)
                resultados.append(res)
                await asyncio.sleep(0.2)

        return resultados

    @classmethod
    async def ranking_diario(cls, data_referencia: Optional[str] = None) -> Dict[str, Any]:
        """
        Consulta o ranking de execuções de OS para uma data específica (padrão: hoje no fuso BRT).
        """
        token = await cls.obter_token()
        if not token:
            return {
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota. Verifique as credenciais no .env."
            }

        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        if data_referencia:
            try:
                data_dt = datetime.datetime.strptime(data_referencia, "%Y-%m-%d").replace(tzinfo=tz_brt)
            except ValueError:
                data_dt = datetime.datetime.now(tz_brt)
        else:
            data_dt = datetime.datetime.now(tz_brt)

        amanha_dt = data_dt + datetime.timedelta(days=1)
        start_date = f"{data_dt.strftime('%Y-%m-%d')}T03:00:00.000Z"
        end_date = f"{amanha_dt.strftime('%Y-%m-%d')}T02:59:59.000Z"

        url_os = f"{cls.BASE_URL}/maintener/order/"
        params = {
            "aggregated_field": "maintener",
            "date_execution_start": start_date,
            "date_execution_end": end_date,
            "free_service_orders_search": "true",
            "includes": "vehicle,user_executor,maintener"
        }
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url_os, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=25)) as resp:
                    if resp.status == 200:
                        dados = await resp.json()
                        lista_os = dados if isinstance(dados, list) else dados.get('data', [])

                        contagem = {}
                        for os_item in lista_os:
                            executor_data = os_item.get('user_executor')
                            if executor_data:
                                nome = executor_data.get('name', 'Desconhecido').strip().title()
                                contagem[nome] = contagem.get(nome, 0) + 1

                        ranking = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
                        total_os = sum(contagem.values())

                        itens_ranking = []
                        for idx, (nome, qtd) in enumerate(ranking):
                            percentual = round((qtd / total_os * 100), 1) if total_os > 0 else 0
                            itens_ranking.append({
                                "posicao": idx + 1,
                                "nome": nome,
                                "quantidade": qtd,
                                "percentual": percentual
                            })

                        return {
                            "sucesso": True,
                            "data": data_dt.strftime("%d/%m/%Y"),
                            "data_iso": data_dt.strftime("%Y-%m-%d"),
                            "total_os": total_os,
                            "ranking": itens_ranking
                        }
                    else:
                        return {
                            "sucesso": False,
                            "erro": f"Erro na API WebRota. Código: {resp.status}"
                        }
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Falha ao consultar ranking diário: {str(e)}"
            }

    @classmethod
    async def ranking_mensal(
        cls,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        tecnicos_custom: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Consulta o ranking de execuções do mês (comparativo Túlio x Kaio e geral).
        """
        token = await cls.obter_token()
        if not token:
            return {
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota. Verifique credenciais no .env."
            }

        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        agora_brt = datetime.datetime.now(tz_brt)

        ano_sel = ano or agora_brt.year
        mes_sel = mes or agora_brt.month

        primeiro_dia = datetime.datetime(ano_sel, mes_sel, 1, tzinfo=tz_brt)
        # Se for o mês atual, vai até hoje + 1 dia. Se for mês passado, vai até o último dia do mês.
        if ano_sel == agora_brt.year and mes_sel == agora_brt.month:
            fim_periodo = agora_brt + datetime.timedelta(days=1)
            periodo_texto = f"{primeiro_dia.strftime('%d/%m/%Y')} a {agora_brt.strftime('%d/%m/%Y')}"
        else:
            proximo_mes = primeiro_dia.replace(day=28) + datetime.timedelta(days=4)
            ultimo_dia = proximo_mes - datetime.timedelta(days=proximo_mes.day)
            fim_periodo = ultimo_dia + datetime.timedelta(days=1)
            periodo_texto = f"{primeiro_dia.strftime('%d/%m/%Y')} a {ultimo_dia.strftime('%d/%m/%Y')}"

        start_date = f"{primeiro_dia.strftime('%Y-%m-%d')}T03:00:00.000Z"
        end_date = f"{fim_periodo.strftime('%Y-%m-%d')}T02:59:59.000Z"

        tecnicos_alvo = tecnicos_custom or [
            {"nome_exibicao": "Tulio Albuquerque Freitas", "busca": "Tulio Albuquerque Freitas (TÉCNICO WEBROTA) - Nível(3)"},
            {"nome_exibicao": "Kaio Gabriel de Freitas", "busca": "Kaio Gabriel de Freitas (TÉCNICO WEBROTA) - Nível(3)"}
        ]

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        url_os = f"{cls.BASE_URL}/maintener/order/"
        ranking_resultados = []

        try:
            async with aiohttp.ClientSession() as session:
                for tec in tecnicos_alvo:
                    params_os = {
                        "aggregated_field": "maintener",
                        "date_execution_start": start_date,
                        "date_execution_end": end_date,
                        "free_service_orders_search": "true",
                        "general": tec["busca"],
                        "includes": "maintener,user_executor"
                    }

                    total_executado = 0
                    async with session.get(url_os, params=params_os, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp_os:
                        if resp_os.status == 200:
                            dados_os = await resp_os.json()
                            lista_os = dados_os if isinstance(dados_os, list) else dados_os.get('data', [])

                            for os_item in lista_os:
                                maintener_obj = os_item.get('maintener') or {}
                                nome_maintener = maintener_obj.get('name', '')
                                primeiro_nome = tec["nome_exibicao"].split()[0].lower()

                                if primeiro_nome in nome_maintener.lower():
                                    if os_item.get('date_execution') or os_item.get('status') in ('E', 'F'):
                                        total_executado += 1

                    ranking_resultados.append({
                        "nome": tec["nome_exibicao"],
                        "total": total_executado
                    })
                    await asyncio.sleep(0.5)

            ranking_ordenado = sorted(ranking_resultados, key=lambda x: x["total"], reverse=True)
            total_geral = sum(r["total"] for r in ranking_ordenado)

            itens = []
            for idx, item in enumerate(ranking_ordenado):
                pct = round((item["total"] / total_geral * 100), 1) if total_geral > 0 else 0
                itens.append({
                    "posicao": idx + 1,
                    "nome": item["nome"],
                    "total": item["total"],
                    "percentual": pct
                })

            return {
                "sucesso": True,
                "periodo": periodo_texto,
                "mes": mes_sel,
                "ano": ano_sel,
                "total_comparativo": total_geral,
                "ranking": itens
            }
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Falha ao gerar ranking mensal: {str(e)}"
            }

