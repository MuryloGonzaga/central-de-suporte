import asyncio
import re
import datetime
from typing import List, Dict, Any, Optional, AsyncGenerator
import aiohttp
from app.config import WEBROTA_USER, WEBROTA_PASS, WEBROTA_RANKING_USER, WEBROTA_RANKING_PASS
from app.services.ranking_cache import RankingCacheManager

class WebrotaService:
    BASE_URL = "https://api.webrota.com.br"
    _token: Optional[str] = None
    _token_time: Optional[datetime.datetime] = None
    _lock = asyncio.Lock()

    # Credenciais e Token ISOLADOS para o Ranking de OS (usa usuário do .env / Vercel)
    _ranking_token: Optional[str] = None
    _ranking_token_time: Optional[datetime.datetime] = None
    _ranking_auth_lock = asyncio.Lock()
    _ranking_query_lock = asyncio.Lock()

    @classmethod
    def set_token_ativo(cls, token: str):
        """Define o token ativo autenticado pelo usuário logado (usado apenas em consultas de usuário)."""
        if token:
            cls._token = token
            cls._token_time = datetime.datetime.now(datetime.timezone.utc)

    @classmethod
    async def obter_token_ranking(cls, forcar_renovacao: bool = False) -> Optional[str]:
        """
        Obtém ou renova o token JWT exclusivo para o Ranking de OS.
        Utiliza ESTRITAMENTE as credenciais do .env ou variáveis do Vercel
        (WEBROTA_RANKING_USER / WEBROTA_RANKING_PASS).
        Não altera nem sofre interferência de logins de outros usuários.
        """
        async with cls._ranking_auth_lock:
            agora = datetime.datetime.now(datetime.timezone.utc)
            if (
                not forcar_renovacao
                and cls._ranking_token
                and cls._ranking_token_time
                and (agora - cls._ranking_token_time).total_seconds() < 14400
            ):
                return cls._ranking_token

            from app.config import get_env_flexible
            usuario_ranking = get_env_flexible("WEBROTA_RANKING_USER", "WEBROTA_RANKING_USUARIO", "WEBROTA_USER", "WEBROTA_USUARIO", "WEBROTA_LOGIN", default=WEBROTA_RANKING_USER)
            senha_ranking = get_env_flexible("WEBROTA_RANKING_PASS", "WEBROTA_RANKING_PASSWORD", "WEBROTA_RANKING_SENHA", "WEBROTA_PASS", default=WEBROTA_RANKING_PASS)

            if not usuario_ranking or not senha_ranking:
                print("[Ranking WebRota] Aviso: WEBROTA_USER/WEBROTA_PASS não configurados no .env ou Vercel.")
                return None

            url_login = f"{cls.BASE_URL}/auth/login/"
            payload = {"username": usuario_ranking, "password": senha_ranking}
            headers = {"Content-Type": "application/json", "Accept": "application/json, text/plain, */*"}

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url_login, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                        if resp.status in (200, 201):
                            dados = await resp.json()
                            token = (
                                dados.get('token')
                                or dados.get('access_token')
                                or (dados.get('data') and isinstance(dados.get('data'), dict) and dados['data'].get('token'))
                                or ""
                            )
                            if token:
                                cls._ranking_token = token
                                cls._ranking_token_time = agora
                                return cls._ranking_token
                        else:
                            print(f"[Ranking WebRota] Falha de login para '{usuario_ranking}': HTTP {resp.status}")
            except Exception as e:
                print(f"[Ranking WebRota] Erro de conexão ao autenticar para ranking: {e}")

            return cls._ranking_token

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
                        ]

                        if os_filtradas:
                            os_filtradas.sort(key=lambda x: x.get('date_execution'), reverse=True)
                            ultima_os = os_filtradas[0]
                            local_instalacao = ultima_os.get('local')
                            if local_instalacao is None or not str(local_instalacao).strip():
                                local_instalacao = "-"
                            else:
                                local_instalacao = str(local_instalacao).strip()

                            detalhes_seriais.append({
                                "numero_equipamento": idx_eq + 1,
                                "serial": serial,
                                "local": local_instalacao,
                                "data_execucao": ultima_os.get('date_execution'),
                                "status": ultima_os.get('status'),
                                "possui_os": True
                            })
                        else:
                            detalhes_seriais.append({
                                "numero_equipamento": idx_eq + 1,
                                "serial": serial,
                                "local": "Sem OS válida (status E ou F)",
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
    async def ranking_diario(cls, data_referencia: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
        """
        Consulta o ranking de execuções de OS para uma data específica.
        REGRAS RÍGIDAS DE CACHE E HORÁRIO:
        - Autenticação: Utiliza ESTRITAMENTE as credenciais do .env ou variáveis do Vercel
          (WEBROTA_RANKING_USER / WEBROTA_RANKING_PASS). Não depende e não altera sessões de outros usuários.
        - Horário operacional: Consultas externas à API permitidas APENAS entre 08:00 e 18:00 (horário de Brasília).
        - Frequência: No máximo 1 consulta por hora. O resultado é salvo em cache de memória e persistido em arquivo JSON.
        - Fora do horário (antes das 08h ou a partir das 18h): NUNCA dispara requisições para a API WebRota;
          retorna o snapshot congelado do cache persistente.
        """
        cache = RankingCacheManager.get_instance()
        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        agora_brt = datetime.datetime.now(tz_brt)
        hora_atual = agora_brt.hour
        dia_hoje_iso = agora_brt.strftime("%Y-%m-%d")

        janela_ativa = (8 <= hora_atual <= 18)

        if data_referencia:
            try:
                data_dt = datetime.datetime.strptime(data_referencia, "%Y-%m-%d").replace(tzinfo=tz_brt)
            except ValueError:
                data_dt = agora_brt
        else:
            data_dt = agora_brt

        dia_iso = data_dt.strftime("%Y-%m-%d")
        eh_hoje = (dia_iso == dia_hoje_iso)

        # ------------------------------------------------------------------
        # CASO 1: Consulta para DATA PASSADA (histórico fechado)
        # ------------------------------------------------------------------
        if not eh_hoje:
            cache_key_fechado = f"{dia_iso}_fechado"
            cached = cache.get_diario(cache_key_fechado)
            if cached:
                cached["janela_ativa"] = False
                return cached

            # Tenta encontrar qualquer snapshot já existente deste dia
            snap = cache.obter_ultimo_snapshot_diario(dia_iso)
            if snap and snap.get("data_iso") == dia_iso:
                snap["janela_ativa"] = False
                cache.set_diario(cache_key_fechado, snap)
                return snap

            # Se nunca foi consultado antes no histórico, busca uma única vez via API
            token = await cls.obter_token_ranking()
            if not token:
                return {
                    "sucesso": False,
                    "erro": "Credenciais de ranking não configuradas no .env ou variáveis do Vercel (WEBROTA_USER / WEBROTA_PASS).",
                    "janela_ativa": False
                }
            res_passado = await cls._executar_consulta_os_dia(data_dt, dia_iso, token, janela_ativa=False)
            if res_passado.get("sucesso"):
                cache.set_diario(cache_key_fechado, res_passado)
            return res_passado

        # ------------------------------------------------------------------
        # CASO 2: Consulta para o DIA DE HOJE
        # ------------------------------------------------------------------
        cache_key_hora = f"{dia_iso}_{hora_atual}"

        # 1. Se já temos snapshot desta hora em cache (persistente ou memória), retorna imediatamente
        if not force:
            cached = cache.get_diario(cache_key_hora)
            if cached:
                cached["janela_ativa"] = janela_ativa
                return cached

        # 2. Se estiver FORA da janela operacional (antes das 08h ou a partir das 18h)
        # NUNCA executa requisição na WebRota!
        if not janela_ativa:
            snap_hoje = cache.obter_ultimo_snapshot_diario(dia_iso)
            if snap_hoje and snap_hoje.get("data_iso") == dia_iso:
                snap_hoje["janela_ativa"] = False
                snap_hoje["mensagem_horario"] = "Ranking congelado fora do horário operacional. Atualizações automáticas ocorrem de 1 em 1 hora entre 08:00 e 18:00."
                return snap_hoje

            # Se for antes das 08:00 da manhã e ainda não houver nenhum snapshot de hoje
            return {
                "sucesso": True,
                "data": data_dt.strftime("%d/%m/%Y"),
                "data_iso": dia_iso,
                "total_os": 0,
                "ranking": [],
                "janela_ativa": False,
                "mensagem_horario": "Ranking congelado fora do horário operacional. As consultas iniciam às 08:00.",
                "proxima_atualizacao": "08:00 (Início do expediente)",
                "regra_atualizacao": "Atualização automática de 1 em 1 hora entre 08:00 e 18:00"
            }

        # 3. Está DENTRO da janela (08:00 às 18:00) e AINDA NÃO CONSULTADO NESTA HORA
        # Utiliza lock para evitar concorrência caso múltiplos usuários acessem simultaneamente
        async with cls._ranking_query_lock:
            # Dupla checagem sob lock
            if not force:
                cached = cache.get_diario(cache_key_hora)
                if cached:
                    cached["janela_ativa"] = True
                    return cached

            token = await cls.obter_token_ranking()
            if not token:
                return {
                    "sucesso": False,
                    "erro": "Credenciais de ranking não configuradas no .env ou variáveis do Vercel (WEBROTA_USER / WEBROTA_PASS).",
                    "janela_ativa": True
                }

            resultado = await cls._executar_consulta_os_dia(data_dt, dia_iso, token, janela_ativa=True, hora_atual=hora_atual)
            if resultado.get("sucesso"):
                cache.set_diario(cache_key_hora, resultado)
            return resultado

    @classmethod
    async def _executar_consulta_os_dia(
        cls,
        data_dt: datetime.datetime,
        dia_iso: str,
        token: str,
        janela_ativa: bool,
        hora_atual: Optional[int] = None
    ) -> Dict[str, Any]:
        """Rotina interna que consulta a API WebRota para ordens de serviço do dia."""
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

                        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
                        agora_brt = datetime.datetime.now(tz_brt)
                        h = hora_atual if hora_atual is not None else agora_brt.hour
                        proxima_hora_str = f"{(h + 1):02d}:00" if h < 18 else "08:00 (próximo ciclo)"
                        ultima_hora_str = agora_brt.strftime(f"%d/%m/%Y às {h:02d}:00")

                        return {
                            "sucesso": True,
                            "data": data_dt.strftime("%d/%m/%Y"),
                            "data_iso": dia_iso,
                            "total_os": total_os,
                            "ranking": itens_ranking,
                            "janela_ativa": janela_ativa,
                            "ultima_atualizacao": ultima_hora_str,
                            "proxima_atualizacao": proxima_hora_str,
                            "regra_atualizacao": "Atualização automática de 1 em 1 hora entre 08:00 e 18:00"
                        }
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
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Consulta o ranking de execuções do mês (comparativo Túlio x Kaio e geral).
        REGRAS RÍGIDAS DE CACHE E HORÁRIO:
        - Autenticação: Utiliza ESTRITAMENTE as credenciais do .env ou variáveis do Vercel
          (WEBROTA_RANKING_USER / WEBROTA_RANKING_PASS). Não depende e não altera sessões de outros usuários.
        - Horário operacional: Consultas externas à API permitidas APENAS entre 08:00 e 18:00 (horário de Brasília).
        - Frequência: No máximo 1 consulta por hora. O resultado é salvo em cache de memória e persistido em arquivo JSON.
        - Fora do horário (antes das 08h ou a partir das 18h): NUNCA dispara requisições para a API WebRota;
          retorna o snapshot congelado do cache persistente.
        """
        cache = RankingCacheManager.get_instance()
        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        agora_brt = datetime.datetime.now(tz_brt)
        hora_atual = agora_brt.hour

        janela_ativa = (8 <= hora_atual <= 18)

        ano_sel = ano or agora_brt.year
        mes_sel = mes or agora_brt.month
        eh_mes_atual = (ano_sel == agora_brt.year and mes_sel == agora_brt.month)

        prefixo_mes = f"{ano_sel}_{mes_sel}"

        # ------------------------------------------------------------------
        # CASO 1: MÊS PASSADO (histórico fechado)
        # ------------------------------------------------------------------
        if not eh_mes_atual:
            cache_key_fechado = f"{prefixo_mes}_fechado"
            cached = cache.get_mensal(cache_key_fechado)
            if cached:
                cached["janela_ativa"] = False
                return cached

            snap_m = cache.obter_ultimo_snapshot_mensal(prefixo_mes)
            if snap_m:
                snap_m["janela_ativa"] = False
                cache.set_mensal(cache_key_fechado, snap_m)
                return snap_m

            token = await cls.obter_token_ranking()
            if not token:
                return {
                    "sucesso": False,
                    "erro": "Credenciais de ranking não configuradas no .env ou variáveis do Vercel (WEBROTA_USER / WEBROTA_PASS).",
                    "janela_ativa": False
                }
            res_m = await cls._executar_consulta_os_mensal(ano_sel, mes_sel, token, tecnicos_custom, janela_ativa=False)
            if res_m.get("sucesso"):
                cache.set_mensal(cache_key_fechado, res_m)
            return res_m

        # ------------------------------------------------------------------
        # CASO 2: MÊS ATUAL
        # ------------------------------------------------------------------
        cache_key_hora = f"{prefixo_mes}_{hora_atual}"

        # 1. Se já calculou nesta hora, retorna do cache imediatamente
        if not force:
            cached = cache.get_mensal(cache_key_hora)
            if cached:
                cached["janela_ativa"] = janela_ativa
                return cached

        # 2. Se fora da janela operacional (antes das 08h ou a partir das 18h)
        # NUNCA executa requisição na WebRota!
        if not janela_ativa:
            snap_mes = cache.obter_ultimo_snapshot_mensal(prefixo_mes)
            if snap_mes:
                snap_mes["janela_ativa"] = False
                snap_mes["mensagem_horario"] = "Ranking mensal congelado fora do horário operacional (08:00 às 18:00)."
                return snap_mes

            return {
                "sucesso": True,
                "periodo": f"Mês {mes_sel}/{ano_sel}",
                "mes": mes_sel,
                "ano": ano_sel,
                "total_comparativo": 0,
                "ranking": [],
                "janela_ativa": False,
                "mensagem_horario": "Ranking mensal congelado fora do horário operacional (08:00 às 18:00).",
                "proxima_atualizacao": "08:00 (Início do expediente)",
                "regra_atualizacao": "Atualização automática de 1 em 1 hora entre 08:00 e 18:00"
            }

        # 3. Está DENTRO da janela (08:00 às 18:00) e AINDA NÃO CONSULTADO NESTA HORA
        async with cls._ranking_query_lock:
            cached = cache.get_mensal(cache_key_hora)
            if cached:
                cached["janela_ativa"] = True
                return cached

            token = await cls.obter_token_ranking()
            if not token:
                return {
                    "sucesso": False,
                    "erro": "Credenciais de ranking não configuradas no .env ou variáveis do Vercel (WEBROTA_USER / WEBROTA_PASS).",
                    "janela_ativa": True
                }

            resultado_m = await cls._executar_consulta_os_mensal(ano_sel, mes_sel, token, tecnicos_custom, janela_ativa=True, hora_atual=hora_atual)
            if resultado_m.get("sucesso"):
                cache.set_mensal(cache_key_hora, resultado_m)
            return resultado_m

    @classmethod
    async def _executar_consulta_os_mensal(
        cls,
        ano_sel: int,
        mes_sel: int,
        token: str,
        tecnicos_custom: Optional[List[Dict[str, str]]],
        janela_ativa: bool,
        hora_atual: Optional[int] = None
    ) -> Dict[str, Any]:
        """Rotina interna que consulta a API WebRota para o ranking mensal dos técnicos."""
        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        agora_brt = datetime.datetime.now(tz_brt)

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
                    await asyncio.sleep(0.3)

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

            h = hora_atual if hora_atual is not None else agora_brt.hour
            proxima_hora_str = f"{(h + 1):02d}:00" if h < 18 else "08:00 (próximo ciclo)"
            ultima_hora_str = agora_brt.strftime(f"%d/%m/%Y às {h:02d}:00")

            return {
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
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Falha ao gerar ranking mensal: {str(e)}",
                "janela_ativa": janela_ativa
            }


    @classmethod
    async def executar_atualizacao_segundo_plano(cls, force: bool = False) -> Dict[str, Any]:
        """
        Executa a atualizacao proativa de segundo plano dos rankings diario e mensal.
        Projetado para ser chamado por:
        - Vercel Cron Jobs (GET /api/cron/ranking a cada hora entre 08:00 e 18:00 BRT)
        - Background Worker interno em servidor continuo (FastAPI lifespan/task)
        """
        tz_brt = datetime.timezone(datetime.timedelta(hours=-3))
        agora_brt = datetime.datetime.now(tz_brt)
        hora_atual = agora_brt.hour
        janela_ativa = (8 <= hora_atual <= 18)

        if not janela_ativa and not force:
            return {
                "sucesso": True,
                "executado": False,
                "motivo": f"Fora do horario operacional (08:00 as 18:00 BRT). Hora atual: {hora_atual:02d}h.",
                "horario_brt": agora_brt.strftime("%d/%m/%Y %H:%M:%S"),
                "janela_ativa": False
            }

        res_diario = await cls.ranking_diario(force=force)
        res_mensal = await cls.ranking_mensal(force=force)

        return {
            "sucesso": True,
            "executado": True,
            "horario_brt": agora_brt.strftime("%d/%m/%Y %H:%M:%S"),
            "janela_ativa": janela_ativa,
            "diario": {
                "sucesso": res_diario.get("sucesso", False),
                "total_os": res_diario.get("total_os", 0),
                "erro": res_diario.get("erro")
            },
            "mensal": {
                "sucesso": res_mensal.get("sucesso", False),
                "total_geral": res_mensal.get("total_comparativo", {}).get("total_geral", 0) if isinstance(res_mensal.get("total_comparativo"), dict) else 0,
                "erro": res_mensal.get("erro")
            }
        }
