# -*- coding: utf-8 -*-
"""
Gerenciador de Cache Persistente para Rankings de Ordens de Serviço (WebRota)
Armazena snapshots horários em memória e persiste em arquivo JSON.
Suporta fallback automático para /tmp em ambientes somente-leitura (como Vercel).
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List

class RankingCacheManager:
    _instance: Optional['RankingCacheManager'] = None

    def __init__(self):
        self._cache_diario: Dict[str, Any] = {}
        self._cache_mensal: Dict[str, Any] = {}
        self._cache_file: Path = self._descobrir_caminho_arquivo()
        self._carregar_disco()

    @classmethod
    def get_instance(cls) -> 'RankingCacheManager':
        if cls._instance is None:
            cls._instance = RankingCacheManager()
        return cls._instance

    def _descobrir_caminho_arquivo(self) -> Path:
        """
        Determina o melhor local para persistir o cache JSON.
        Tenta a pasta 'data/' do projeto; caso seja somente-leitura (Vercel),
        faz fallback para a pasta temporária do sistema operacional.
        """
        # Raiz do projeto: .../Central de Suporte
        base_dir = Path(__file__).resolve().parent.parent.parent
        data_dir = base_dir / "data"

        try:
            data_dir.mkdir(parents=True, exist_ok=True)
            teste_path = data_dir / ".write_test"
            teste_path.write_text("test", encoding="utf-8")
            teste_path.unlink(missing_ok=True)
            return data_dir / "rankings_cache.json"
        except Exception:
            # Fallback para Vercel Serverless (/tmp)
            return Path(tempfile.gettempdir()) / "central_suporte_rankings_cache.json"

    def _carregar_disco(self):
        """Carrega snapshots salvos anteriormente no disco para a memória."""
        try:
            if self._cache_file.exists():
                conteudo = self._cache_file.read_text(encoding="utf-8")
                dados = json.loads(conteudo)
                if isinstance(dados, dict):
                    self._cache_diario = dados.get("diario", {})
                    self._cache_mensal = dados.get("mensal", {})
        except Exception as e:
            print(f"[RankingCache] Aviso ao carregar cache do disco ({self._cache_file}): {e}")

    def _salvar_disco(self):
        """Salva atomicamente o estado do cache no arquivo JSON."""
        try:
            payload = {
                "diario": self._cache_diario,
                "mensal": self._cache_mensal
            }
            # Gravação direta com encoding utf-8
            self._cache_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[RankingCache] Aviso ao salvar cache no disco ({self._cache_file}): {e}")

    # ----------------------------------------------------------------
    # MÉTODOS DE CONSULTA E ARMAZENAMENTO - RANKING DIÁRIO
    # ----------------------------------------------------------------

    def get_diario(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera um snapshot diário específico pela chave (ex: '2026-10-17_14')."""
        item = self._cache_diario.get(key)
        return item.copy() if item else None

    def set_diario(self, key: str, valor: Dict[str, Any]):
        """Armazena um snapshot diário em memória e persiste em disco."""
        self._cache_diario[key] = valor
        self._salvar_disco()

    def obter_ultimo_snapshot_diario(self, dia_iso: str) -> Optional[Dict[str, Any]]:
        """
        Retorna o snapshot mais recente já registrado para o dia (ex: 18h, 17h, 16h...),
        ou de dias anteriores caso o dia atual ainda não possua consultas.
        """
        snapshots_dia = [v for k, v in self._cache_diario.items() if k.startswith(dia_iso)]
        if snapshots_dia:
            return snapshots_dia[-1].copy()

        # Se não houver snapshot para a data exata, tenta o último disponível no cache geral
        if self._cache_diario:
            chaves_ordenadas = sorted(self._cache_diario.keys())
            if chaves_ordenadas:
                return self._cache_diario[chaves_ordenadas[-1]].copy()

        return None

    # ----------------------------------------------------------------
    # MÉTODOS DE CONSULTA E ARMAZENAMENTO - RANKING MENSAL
    # ----------------------------------------------------------------

    def get_mensal(self, key: str) -> Optional[Dict[str, Any]]:
        """Recupera um snapshot mensal específico pela chave (ex: '2026_10_14')."""
        item = self._cache_mensal.get(key)
        return item.copy() if item else None

    def set_mensal(self, key: str, valor: Dict[str, Any]):
        """Armazena um snapshot mensal em memória e persiste em disco."""
        self._cache_mensal[key] = valor
        self._salvar_disco()

    def obter_ultimo_snapshot_mensal(self, prefixo_ano_mes: str) -> Optional[Dict[str, Any]]:
        """
        Retorna o snapshot mais recente já registrado para o mês selecionado.
        """
        snapshots_mes = [v for k, v in self._cache_mensal.items() if k.startswith(prefixo_ano_mes)]
        if snapshots_mes:
            return snapshots_mes[-1].copy()

        if self._cache_mensal:
            chaves_ordenadas = sorted(self._cache_mensal.keys())
            if chaves_ordenadas:
                return self._cache_mensal[chaves_ordenadas[-1]].copy()

        return None

