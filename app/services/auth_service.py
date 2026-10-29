# -*- coding: utf-8 -*-
"""
Serviço de Autenticação Real WebRota
Autentica diretamente contra a API oficial da WebRota (https://api.webrota.com.br/auth/login/)
utilizando as credenciais individuais de cada colaborador/técnico.
"""

import aiohttp
import secrets
import datetime
from typing import Optional, Dict, Any

class AuthService:
    URL_LOGIN_WEBROTA = "https://api.webrota.com.br/auth/login/"
    _duracao_sessao_horas = 12

    # Usuários com permissão para acessar TODAS as funções do sistema
    USUARIOS_ACESSO_TOTAL = {
        "william.lopes",
        "pamela.stender",
        "murylo.gonzaga"
    }

    # Sessões ativas em memória: token_sessao -> { "username", "nome", "perfil", "webrota_token", "acesso_total", "expira" }
    _sessoes: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def eh_usuario_total(cls, username: Optional[str]) -> bool:
        """Verifica se o usuário possui permissão de acesso a todas as funções."""
        if not username:
            return False
        u = username.strip().lower()
        if "@" in u:
            u = u.split("@")[0].strip()
        return u in cls.USUARIOS_ACESSO_TOTAL

    @classmethod
    async def autenticar(cls, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica as credenciais na API oficial da WebRota.
        Baseado na rotina oficial:
        POST https://api.webrota.com.br/auth/login/
        payload = { "username": username, "password": password }
        """
        if not username or not password:
            return None

        username_limpo = username.strip()
        payload = {
            "username": username_limpo,
            "password": password
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    cls.URL_LOGIN_WEBROTA,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=20)
                ) as response:
                    status = response.status
                    if status in (200, 201):
                        dados = await response.json()
                        # Extrai o token de acordo com os padrões da API WebRota
                        token = (
                            dados.get("token")
                            or dados.get("access_token")
                            or (dados.get("data") and isinstance(dados.get("data"), dict) and dados["data"].get("token"))
                            or ""
                        )

                        if not token:
                            return None

                        # Extrai informações do usuário se disponíveis no retorno
                        user_info = dados.get("user") or dados.get("data") or {}
                        nome = (
                            user_info.get("name")
                            or user_info.get("nome")
                            or user_info.get("first_name")
                            or dados.get("name")
                            or username_limpo.title()
                        )
                        perfil = (
                            user_info.get("profile")
                            or user_info.get("perfil")
                            or user_info.get("role")
                            or "Colaborador WebRota"
                        )

                        # Sincroniza o token ativo no WebrotaService
                        from app.services.webrota_service import WebrotaService
                        WebrotaService.set_token_ativo(token)

                        acesso_total = cls.eh_usuario_total(username_limpo)

                        return {
                            "username": username_limpo,
                            "nome": nome,
                            "perfil": "Administrador" if acesso_total else perfil,
                            "webrota_token": token,
                            "acesso_total": acesso_total,
                            "is_admin": acesso_total
                        }
                    else:
                        print(f"[Auth WebRota] Falha de login para '{username_limpo}': HTTP {status}")
                        return None
        except Exception as e:
            print(f"[Auth WebRota] Erro de conexão ao autenticar '{username_limpo}': {e}")
            return None

    @classmethod
    def criar_sessao(cls, dados_usuario: Dict[str, Any]) -> str:
        """Cria um token seguro de sessão local para o usuário autenticado."""
        token = secrets.token_urlsafe(32)
        agora = datetime.datetime.now(datetime.timezone.utc)
        expira = agora + datetime.timedelta(hours=cls._duracao_sessao_horas)

        username = dados_usuario["username"]
        acesso_total = cls.eh_usuario_total(username)

        cls._sessoes[token] = {
            "username": username,
            "nome": dados_usuario["nome"],
            "perfil": "Administrador" if acesso_total else dados_usuario.get("perfil", "Colaborador"),
            "webrota_token": dados_usuario.get("webrota_token"),
            "acesso_total": acesso_total,
            "criada_em": agora,
            "expira": expira
        }
        return token

    @classmethod
    def validar_sessao(cls, token: Optional[str]) -> Optional[Dict[str, Any]]:
        """Verifica se o token de sessão é válido e não expirou."""
        if not token or token not in cls._sessoes:
            return None

        sessao = cls._sessoes[token]
        agora = datetime.datetime.now(datetime.timezone.utc)

        if agora > sessao["expira"]:
            cls.encerrar_sessao(token)
            return None

        webrota_token = sessao.get("webrota_token")
        if webrota_token:
            from app.services.webrota_service import WebrotaService
            WebrotaService.set_token_ativo(webrota_token)

        username = sessao["username"]
        acesso_total = cls.eh_usuario_total(username)

        return {
            "username": username,
            "nome": sessao["nome"],
            "perfil": "Administrador" if acesso_total else sessao.get("perfil", "Colaborador"),
            "webrota_token": webrota_token,
            "acesso_total": acesso_total,
            "is_admin": acesso_total
        }

    @classmethod
    def encerrar_sessao(cls, token: Optional[str]) -> bool:
        """Encerra a sessão do usuário (Logout)."""
        if token and token in cls._sessoes:
            del cls._sessoes[token]
            return True
        return False
