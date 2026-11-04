# -*- coding: utf-8 -*-
"""
Serviço de Autenticação Real WebRota
Autentica diretamente contra a API oficial da WebRota (https://api.webrota.com.br/auth/login/)
utilizando as credenciais individuais de cada colaborador/técnico.
Suporta sessões stateless assinadas com HMAC-SHA256 (compatíveis com Vercel Serverless).
"""

import aiohttp
import secrets
import datetime
import hmac
import hashlib
import base64
import json
from typing import Optional, Dict, Any
from app.config import SECRET_KEY


class AuthService:
    URL_LOGIN_WEBROTA = "https://api.webrota.com.br/auth/login/"
    _duracao_sessao_horas = 12

    # Usuários com permissão para acessar TODAS as funções do sistema
    USUARIOS_ACESSO_TOTAL = {
        "william.lopes",
        "pamela.stender",
        "murylo.gonzaga"
    }

    # Cache em memória para instâncias ativas: token -> { ... }
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
                        token = (
                            dados.get("token")
                            or dados.get("access_token")
                            or (dados.get("data") and isinstance(dados.get("data"), dict) and dados["data"].get("token"))
                            or ""
                        )

                        if not token:
                            return None

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
        """
        Cria um token seguro e assinado criptograficamente (HMAC-SHA256).
        Funciona de forma totalmente stateless (Vercel Serverless, multi-processos)
        e também armazena em cache na memória para respostas instantâneas.
        """
        agora = datetime.datetime.now(datetime.timezone.utc)
        expira = agora + datetime.timedelta(hours=cls._duracao_sessao_horas)
        exp_ts = int(expira.timestamp())

        username = dados_usuario["username"]
        acesso_total = cls.eh_usuario_total(username)
        nome = dados_usuario.get("nome", username)
        perfil = "Administrador" if acesso_total else dados_usuario.get("perfil", "Colaborador")
        webrota_token = dados_usuario.get("webrota_token") or ""

        payload = {
            "u": username,
            "n": nome,
            "p": perfil,
            "wt": webrota_token,
            "exp": exp_ts,
            "rnd": secrets.token_hex(8)
        }

        payload_json = json.dumps(payload, separators=(',', ':')).encode('utf-8')
        payload_b64 = base64.urlsafe_b64encode(payload_json).decode('utf-8').rstrip('=')
        sig = hmac.new(SECRET_KEY.encode('utf-8'), payload_b64.encode('utf-8'), hashlib.sha256).hexdigest()
        token = f"{payload_b64}.{sig}"

        cls._sessoes[token] = {
            "username": username,
            "nome": nome,
            "perfil": perfil,
            "webrota_token": webrota_token,
            "acesso_total": acesso_total,
            "criada_em": agora,
            "expira": expira
        }
        return token

    @classmethod
    def validar_sessao(cls, token: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Verifica se o token de sessão é válido e não expirou.
        Valida tanto via cache local em memória quanto via assinatura criptográfica stateless.
        """
        if not token or not isinstance(token, str):
            return None

        token = token.strip()
        agora = datetime.datetime.now(datetime.timezone.utc)

        # 1. Verifica cache rápido em memória
        if token in cls._sessoes:
            sessao = cls._sessoes[token]
            if agora <= sessao.get("expira", agora):
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
            else:
                cls.encerrar_sessao(token)
                return None

        # 2. Se não está em memória (novo container Vercel Serverless), valida a assinatura HMAC
        if "." in token:
            partes = token.rsplit(".", 1)
            if len(partes) == 2:
                payload_b64, sig = partes
                expected_sig = hmac.new(
                    SECRET_KEY.encode('utf-8'),
                    payload_b64.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()

                if hmac.compare_digest(sig, expected_sig):
                    rem = len(payload_b64) % 4
                    padded_b64 = payload_b64 + ("=" * (4 - rem) if rem else "")
                    try:
                        data = json.loads(base64.urlsafe_b64decode(padded_b64).decode('utf-8'))
                        exp_ts = data.get("exp", 0)
                        if int(agora.timestamp()) <= exp_ts:
                            username = data.get("u", "")
                            acesso_total = cls.eh_usuario_total(username)
                            webrota_token = data.get("wt", "")
                            if webrota_token:
                                from app.services.webrota_service import WebrotaService
                                WebrotaService.set_token_ativo(webrota_token)

                            sessao_dict = {
                                "username": username,
                                "nome": data.get("n", username),
                                "perfil": "Administrador" if acesso_total else data.get("p", "Colaborador"),
                                "webrota_token": webrota_token,
                                "acesso_total": acesso_total,
                                "is_admin": acesso_total,
                                "expira": datetime.datetime.fromtimestamp(exp_ts, tz=datetime.timezone.utc)
                            }
                            # Armazena em cache para requisições subsequentes nesta mesma instância
                            cls._sessoes[token] = sessao_dict
                            return sessao_dict
                    except Exception as e:
                        print(f"[Auth] Falha ao ler payload de sessão assinada: {e}")

        return None

    @classmethod
    def encerrar_sessao(cls, token: Optional[str]) -> bool:
        """Encerra a sessão do usuário (Logout)."""
        if token and token in cls._sessoes:
            del cls._sessoes[token]
            return True
        return False
