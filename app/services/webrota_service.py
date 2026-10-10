import asyncio
import re
import datetime
from typing import List, Dict, Any, Optional, AsyncGenerator
import aiohttp
from app.config import WEBROTA_USER, WEBROTA_PASS

class WebrotaService:
    BASE_URL = "https://api.webrota.com.br"
    _token: Optional[str] = None
    _token_time: Optional[datetime.datetime] = None
    _lock = asyncio.Lock()

    # Cache de Rankings com regra rígida: 08:00 às 18:00, 1 em 1 hora, sem recarga manual
    _cache_ranking_diario: Dict[str, Any] = {}
    _cache_ranking_mensal: Dict[str, Any] = {}

    @classmethod
    def set_token_ativo(cls, token: str):
        """Define o token ativo autenticado pelo usuário logado."""
        if token:
            cls._token = token
            cls._token_time = datetime.datetime.now(datetime.timezone.utc)

    @classmethod
    async def obter_token(cls, forcar_renovacao: bool = False, token_usuario: Optional[str] = None) -> Optional[str]:
        """
        Obtém ou renova o token JWT de autenticação da WebRota.
        Dá prioridade ao token da sessão do usuário autenticado.
        """
        if token_usuario:
            cls._token = token_usuario
            cls._token_time = datetime.datetime.now(datetime.timezone.utc)
            return token_usuario

        async with cls._lock:
            agora = datetime.datetime.now(datetime.timezone.utc)
            if (
                not forcar_renovacao
                and cls._token
                and cls._token_time
                and (agora - cls._token_time).total_seconds() < 14400
            ):
                return cls._token

            if not WEBROTA_USER or not WEBROTA_PASS:
                # Se não houver credenciais no .env, utiliza o token ativo em memória se existir
                return cls._token

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
                return cls._token

            return cls._token

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
    async def consultar_veiculo(cls, placa: str, session: Optional[aiohttp.ClientSession] = None, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Consulta veículo cadastrado na WebRota pela placa.
        """
        token = await cls.obter_token(token_usuario=token)
        if not token:
            return {
                "placa": placa,
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota. Faça login novamente com suas credenciais."
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
    async def consultar_veiculos_em_massa(cls, placas: List[str], token: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Consulta múltiplos veículos no cadastro da WebRota.
        """
        token = await cls.obter_token(token_usuario=token)
        if not token:
            return [{"placa": p, "sucesso": False, "erro": "Falha na autenticação da WebRota. Faça login novamente."} for p in placas]

        resultados = []
        async with aiohttp.ClientSession() as session:
            for placa in placas:
                res = await cls.consultar_veiculo(placa, session=session, token=token)
                resultados.append(res)
                await asyncio.sleep(0.15)

        return resultados

    @classmethod
    async def consultar_local_instalacao(cls, identificador: str, session: Optional[aiohttp.ClientSession] = None, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Rastreia seriais e busca o local de instalação na última OS finalizada (Status E ou F).
        Em caso de veículos com múltiplos equipamentos (ex: 2 rastreadores), consolida ambos no mesmo bloco.
        """
        token = await cls.obter_token(token_usuario=token)
        if not token:
            return {
                "identificador": identificador,
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota. Faça login com suas credenciais."
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
                    "possui_multiplos_equipamentos": False,
                    "total_equipamentos": 0,
                    "erro": "Identificador não encontrado ou sem dispositivo vinculado."
                }

            detalhes_seriais = []
            for idx_eq, serial in enumerate(seriais_encontrados):
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
                                "numero_equipamento": idx_eq + 1,
                                "serial": serial,
                                "local": ultima_os.get('local', 'Local não especificado'),
                                "data_execucao": ultima_os.get('date_execution'),
                                "status": ultima_os.get('status'),
                                "possui_os": True
                            })
                        else:
                            detalhes_seriais.append({
                                "numero_equipamento": idx_eq + 1,
                                "serial": serial,
                                "local": "Sem OS válida (status E/F ou local preenchido)",
                                "data_execucao": None,
                                "status": None,
                                "possui_os": False
                            })
                    else:
                        detalhes_seriais.append({
                            "numero_equipamento": idx_eq + 1,
                            "serial": serial,
                            "local": f"Erro na consulta da OS (Status {resp_os.status})",
                            "data_execucao": None,
                            "status": None,
                            "possui_os": False
                        })

            return {
                "identificador": identificador,
                "sucesso": True,
                "possui_multiplos_equipamentos": len(detalhes_seriais) > 1,
                "total_equipamentos": len(detalhes_seriais),
                "seriais": detalhes_seriais
            }
        except Exception as e:
            return {
                "identificador": identificador,
                "sucesso": False,
                "possui_multiplos_equipamentos": False,
                "total_equipamentos": 0,
                "erro": f"Erro ao consultar local: {str(e)}"
            }
        finally:
            if close_session:
                await session.close()

    @classmethod
    async def consultar_locais_em_massa(cls, identificadores: List[str], token: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Consulta locais de instalação para múltiplos identificadores/placas.
        """
        token = await cls.obter_token(token_usuario=token)
        resultados = []
        async with aiohttp.ClientSession() as session:
            for ident in identificadores:
                res = await cls.consultar_local_instalacao(ident, session=session, token=token)
                resultados.append(res)
                await asyncio.sleep(0.2)

        return resultados

    @classmethod
    async def consultar_locais_em_massa_stream(
        cls,
        identificadores: List[str],
        token: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streaming em tempo real com barra de progresso para a consulta de locais de instalação.
        """
        token = await cls.obter_token(token_usuario=token)
        if not token:
            yield {
                "tipo": "erro",
                "mensagem": "Falha na autenticação da WebRota. Por favor, faça login novamente com suas credenciais."
            }
            return

        total = len(identificadores)
        yield {
            "tipo": "inicio",
            "total": total,
            "mensagem": f"Iniciando busca de locais de instalação para {total} veículo(s)..."
        }

        resultados = []
        async with aiohttp.ClientSession() as session:
            for idx, ident in enumerate(identificadores):
                numero_atual = idx + 1
                percentual = round((numero_atual / total) * 100, 1)

                yield {
                    "tipo": "consultando",
                    "atual": numero_atual,
                    "total": total,
                    "percentual": percentual,
                    "identificador": ident,
                    "mensagem": f"Buscando histórico de OS para {ident} ({numero_atual} de {total})..."
                }

                res = await cls.consultar_local_instalacao(ident, session=session, token=token)
                resultados.append(res)

                yield {
                    "tipo": "progresso",
                    "atual": numero_atual,
                    "total": total,
                    "percentual": percentual,
                    "identificador": ident,
                    "resultado": res
                }

                if idx < len(identificadores) - 1:
                    await asyncio.sleep(0.25)

        yield {
            "tipo": "concluido",
            "total_consultadas": len(resultados),
            "total_solicitadas": total,
            "mensagem": f"Busca finalizada! {len(resultados)} veículo(s) processados."
        }

    @classmethod
    async def ranking_diario(cls, data_referencia: Optional[str] = None, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Consulta o ranking de execuções de OS para uma data específica.
        REGRAS RIGIDAS:
        - Atualização permitida APENAS entre 08:00 e 18:00 (horário de Brasília).
        - Atualizações ocorrem no máximo de 1 em 1 hora (cache horário).
        - Fora do horário das 08:00 às 18:00, os dados permanecem estáticos (congelados).
        """
        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        agora_brt = datetime.datetime.now(tz_brt)
        hora_atual = agora_brt.hour

        janela_ativa = (8 <= hora_atual < 18)

        if data_referencia:
            try:
                data_dt = datetime.datetime.strptime(data_referencia, "%Y-%m-%d").replace(tzinfo=tz_brt)
            except ValueError:
                data_dt = agora_brt
        else:
            data_dt = agora_brt

        dia_iso = data_dt.strftime("%Y-%m-%d")
        cache_key = f"{dia_iso}_{hora_atual}"

        # 1. Se já calculou nesta hora, retorna o cache imediatamente
        if cache_key in cls._cache_ranking_diario:
            resp_cache = cls._cache_ranking_diario[cache_key].copy()
            resp_cache["janela_ativa"] = janela_ativa
            return resp_cache

        # 2. Se estiver fora da janela (antes das 08h ou a partir das 18h)
        if not janela_ativa:
            # Busca o último snapshot do dia se existir
            snapshots = [v for k, v in cls._cache_ranking_diario.items() if k.startswith(dia_iso)]
            if snapshots:
                ultimo = snapshots[-1].copy()
                ultimo["janela_ativa"] = False
                ultimo["mensagem_horario"] = "Ranking congelado fora do horário operacional. Atualizações automáticas ocorrem de 1 em 1 hora entre 08:00 e 18:00."
                return ultimo

        # 3. Executa a requisição na API da WebRota
        token = await cls.obter_token(token_usuario=token)
        if not token:
            return {
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota. Faça login com suas credenciais.",
                "janela_ativa": janela_ativa
            }

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

                        proxima_hora_str = f"{(hora_atual + 1):02d}:00" if hora_atual < 17 else "08:00 (próximo ciclo)"
                        ultima_hora_str = agora_brt.strftime(f"%d/%m/%Y às {hora_atual:02d}:00")

                        resultado = {
                            "sucesso": True,
                            "data": data_dt.strftime("%d/%m/%Y"),
                            "data_iso": dia_iso,
                            "total_os": total_os,
                            "ranking": itens_ranking,
                            "janela_ativa": janela_ativa,
                            "ultima_atualizacao": ultima_hora_str,
                            "proxima_atualizacao": proxima_hora_str,
                            "regra_atualizacao": "Atualização automática de 1 em 1 hora entre 08:00 e 18:00 (sem forçar atualização)"
                        }

                        # Armazena no cache da hora cheia
                        cls._cache_ranking_diario[cache_key] = resultado
                        return resultado
                    else:
                        return {
                            "sucesso": False,
                            "erro": f"Erro na API WebRota. Código: {resp.status}",
                            "janela_ativa": janela_ativa
                        }
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Falha ao consultar ranking diário: {str(e)}",
                "janela_ativa": janela_ativa
            }

    @classmethod
    async def ranking_mensal(
        cls,
        ano: Optional[int] = None,
        mes: Optional[int] = None,
        tecnicos_custom: Optional[List[Dict[str, str]]] = None,
        token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Consulta o ranking de execuções do mês (comparativo Túlio x Kaio e geral).
        REGRAS RÍGIDAS: Atualização de 1 em 1 hora entre 08:00 e 18:00.
        """
        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        agora_brt = datetime.datetime.now(tz_brt)
        hora_atual = agora_brt.hour

        janela_ativa = (8 <= hora_atual < 18)

        ano_sel = ano or agora_brt.year
        mes_sel = mes or agora_brt.month
        cache_key = f"{ano_sel}_{mes_sel}_{hora_atual}"

        if cache_key in cls._cache_ranking_mensal:
            resp_m = cls._cache_ranking_mensal[cache_key].copy()
            resp_m["janela_ativa"] = janela_ativa
            return resp_m

        if not janela_ativa:
            snapshots = [v for k, v in cls._cache_ranking_mensal.items() if k.startswith(f"{ano_sel}_{mes_sel}")]
            if snapshots:
                ultimo_m = snapshots[-1].copy()
                ultimo_m["janela_ativa"] = False
                ultimo_m["mensagem_horario"] = "Ranking mensal congelado fora do horário operacional (08:00 às 18:00)."
                return ultimo_m

        token = await cls.obter_token(token_usuario=token)
        if not token:
            return {
                "sucesso": False,
                "erro": "Falha na autenticação da WebRota. Faça login com suas credenciais.",
                "janela_ativa": janela_ativa
            }

        primeiro_dia = datetime.datetime(ano_sel, mes_sel, 1, tzinfo=tz_brt)
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
                    await asyncio.sleep(0.4)

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

            proxima_hora_str = f"{(hora_atual + 1):02d}:00" if hora_atual < 17 else "08:00 (próximo ciclo)"
            ultima_hora_str = agora_brt.strftime(f"%d/%m/%Y às {hora_atual:02d}:00")

            resultado_m = {
                "sucesso": True,
                "periodo": periodo_texto,
                "mes": mes_sel,
                "ano": ano_sel,
                "total_comparativo": total_geral,
                "ranking": itens,
                "janela_ativa": janela_ativa,
                "ultima_atualizacao": ultima_hora_str,
                "proxima_atualizacao": proxima_hora_str,
                "regra_atualizacao": "Atualização automática de 1 em 1 hora entre 08:00 e 18:00"
            }

            cls._cache_ranking_mensal[cache_key] = resultado_m
            return resultado_m
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Falha ao gerar ranking mensal: {str(e)}",
                "janela_ativa": janela_ativa
            }
