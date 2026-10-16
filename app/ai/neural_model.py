# -*- coding: utf-8 -*-
"""
Motor Neural de Compreensão e Atendimento dos Manuais Suntech e Queclink
Implementa:
- Normalização Semântica Canônica e Expansão de Sinônimos
- Invariância à Ordem das Palavras (Bag-of-Canonical-Tokens + Shuffled Augmentation)
- Rede Neural Multicamadas (Multi-Layer Perceptron - MLP) para classificação de intenção
- Mapeamento Denso de Espaço Semântico Latente (LSA / SVD)
- Detector Neural de Aparelhos (Suntech ST4305, ST8300, ST8300R/H, ST340UR, ST310, ST8310UM, ST8210 e Queclink GV50CG)
- Ranqueador Híbrido Neural (Similaridade Cosseno + Sobreposição Canônica Jaccard)
- Sintetizador Especialista com Respostas Personalizadas, Concisas e Diretas
"""

import os
import re
import pickle
import unicodedata
import time
from typing import List, Dict, Any, Tuple, Optional, Set
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.decomposition import TruncatedSVD

from app.ai.knowledge_base import KNOWLEDGE_CHUNKS, TECHNICAL_TERMS_MAP, INTENTS_LIST
from app.config import BASE_DIR

MODEL_DIR = BASE_DIR / "app" / "models"
MODEL_FILE = MODEL_DIR / "neural_brain.pkl"

# Stopwords em português para filtrar ruído e focar no significado
STOPWORDS_BR: Set[str] = {
    "de", "do", "da", "dos", "das", "no", "na", "nos", "nas", "em", "para", "pra", "pro",
    "com", "por", "que", "qual", "quais", "como", "onde", "quando", "quanto", "quantos",
    "quem", "um", "uma", "uns", "umas", "o", "a", "os", "as", "se", "ou", "e", "eh", "ser",
    "isso", "esse", "essa", "esta", "este", "esses", "essas", "meu", "minha", "seu", "sua",
    "dizer", "fazer", "saber", "favor", "pode", "consigo", "quero", "gostaria", "ajuda"
}

# Dicionário de Sinônimos e Normalizações Canônicas Técnicas
SYNONYMS_CANONICAL: Dict[str, str] = {
    # Ignição / Pós-Chave
    "pos chave": "ignicao",
    "pos-chave": "ignicao",
    "poschave": "ignicao",
    "linha 15": "ignicao",
    "pos": "ignicao",
    "chave": "ignicao",
    "ign": "ignicao",
    "ignicao": "ignicao",

    # Corte / Bloqueio / Relé
    "rele de 5 pinos": "rele_5_pinos",
    "rele 5 pinos": "rele_5_pinos",
    "5 pinos": "rele_5_pinos",
    "rele bloqueio": "rele_5_pinos",
    "rele": "rele_5_pinos",
    "bomba de combustivel": "bomba_combustivel",
    "bomba combustivel": "bomba_combustivel",
    "bomba": "bomba_combustivel",
    "combustivel": "bomba_combustivel",
    "bloqueio": "bloqueio",
    "bloquear": "bloqueio",
    "bloqueia": "bloqueio",
    "corte": "bloqueio",
    "cortar": "bloqueio",
    "imobilizador": "bloqueio",
    "diodo 1n4004": "diodo_1n4004",
    "1n4004": "diodo_1n4004",
    "diodo": "diodo_1n4004",
    "roda livre": "diodo_1n4004",

    # DPA e Condução
    "dpa": "calibrar_dpa",
    "calibrar": "calibrar_dpa",
    "calibracao": "calibrar_dpa",
    "calibra": "calibrar_dpa",
    "calibrando": "calibrar_dpa",
    "freadas": "freada",
    "frenagem": "freada",
    "freada": "freada",
    "curvas": "curva",
    "curva": "curva",
    "aceleracoes": "aceleracao",
    "aceleracao": "aceleracao",

    # LEDs e Sinalizações
    "piscadas": "piscada",
    "piscada": "piscada",
    "piscando": "piscada",
    "pisca": "piscada",
    "piscou": "piscada",
    "led": "led",
    "leds": "led",
    "luz": "led",

    # Cores
    "vermelho": "cor_vermelho",
    "verm": "cor_vermelho",
    "preto": "cor_preto",
    "pto": "cor_preto",
    "branco": "cor_branco",
    "branc": "cor_branco",
    "azul": "cor_azul",
    "amarelo": "cor_amarelo",
    "amar": "cor_amarelo",
    "laranja": "cor_laranja",
    "lar": "cor_laranja",
    "verde": "cor_verde",
    "verd": "cor_verde",
    "marrom": "cor_marrom",
    "roxo": "cor_roxo",
    "cinza": "cor_cinza",

    # Fios e Chicotes
    "fio": "fio",
    "fios": "fio",
    "chicote": "chicote",
    "pinagem": "chicote",
    "pinos": "pinos",
    "pino": "pinos",

    # Senhas e Synctrak
    "synctrak": "synctrak",
    "synctrack": "synctrak",
    "senha": "senha",
    "password": "senha",
    "st5656": "senha_st5656",

    # Água e IP67
    "ip67": "ip67_agua",
    "agua": "ip67_agua",
    "chuva": "ip67_agua",
    "estanque": "ip67_agua",
    "molhar": "ip67_agua",
    "resistente": "ip67_agua",

    # Jornada e Horas Extras
    "jornada": "jornada_trabalho",
    "jornada de trabalho": "jornada_trabalho",
    "hora extra": "hora_extra",
    "horas extras": "hora_extra",
    "fuso": "fuso_utc",
    "utc": "fuso_utc",

    # Ocioso / Idle
    "idle": "modo_idle",
    "ocioso": "modo_idle",

    # Comandos e Memória
    "eraseall": "eraseall",
    "apagar memoria": "eraseall",
    "statusreq": "statusreq",
    "posicao": "statusreq",
    "reboot": "reboot",
    "reiniciar": "reboot",
    "reset": "reset",

    # Cercas
    "cerca": "cerca",
    "cercas": "cerca",
    "geofence": "cerca",
    "poligonal": "cerca_poligonal",
    "circular": "cerca_circular",

    # Modelos de Aparelho
    "queclink": "mod_gv50cg",
    "gv50cg": "mod_gv50cg",
    "gv50": "mod_gv50cg",
    "gv 50": "mod_gv50cg",
    "gv-50": "mod_gv50cg",
    "towards sky": "antena_sky",
    "this side towards sky": "antena_sky",
    "power switch": "chave_bateria",
    "micro sim": "micro_sim",
    "micro-sim": "micro_sim",
    "st340ur": "mod_st340ur",
    "st340": "mod_st340ur",
    "st4305": "mod_st4305",
    "st8300r": "mod_st8300r",
    "st8300h": "mod_st8300h",
    "st8300": "mod_st8300",
    "st310u": "mod_st310u",
    "st310uc2": "mod_st310uc2",
    "st310uc": "mod_st310uc",
    "st310ulc": "mod_st310ulc",
    "st310": "mod_st310",
    "st8310um": "mod_st8310um",
    "st8310": "mod_st8310um",
    "st8210": "mod_st8210",
    "st4315": "mod_st4305",
    "rfid": "perif_rfid",
    "sgbras": "perif_sgbras",
    "getscale": "perif_getscale",
    "teclado": "perif_teclado",
    "st300evt": "cmd_st300evt",
    "st300svc": "cmd_st300svc",
    "st300cmd": "cmd_st300cmd",
    "st300dex": "cmd_st300dex",
    "prg": "cmd_prg",
    "at+gtdos": "cmd_gtdos",
    "gtdos": "cmd_gtdos",
    "template": "cmd_template",
    "templates": "cmd_template",
    "beep": "cmd_beep",
    "buzzer": "cmd_buzzer",
    "deep sleep": "cmd_deep_sleep",
    "driving behavior": "cmd_driving_behavior",
    "bloquear veiculo": "cmd_bloquear",
    "desbloquear veiculo": "cmd_desbloquear"
}


def normalizar_texto(texto: str) -> str:
    """Remove acentos, pontuação e converte para minúsculas"""
    if not texto:
        return ""
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto)
    texto = "".join([c for c in texto if not unicodedata.combining(c)])
    texto = re.sub(r'[^a-z0-9\s\-_+]', ' ', texto)
    return re.sub(r'\s+', ' ', texto).strip()


def extrair_tokens_canonicos(texto: str) -> List[str]:
    """Extrai conjunto ordenado de tokens canônicos (Invariante à ordem da frase)"""
    texto_norm = normalizar_texto(texto)
    for k, v in sorted(SYNONYMS_CANONICAL.items(), key=lambda x: len(x[0]), reverse=True):
        texto_norm = re.sub(r'\b' + re.escape(k) + r'\b', v, texto_norm)
    tokens = {t for t in texto_norm.split() if len(t) > 1 and t not in STOPWORDS_BR}
    return sorted(list(tokens))


def gerar_representacao_invariante(texto: str) -> str:
    """
    Gera representação dual:
    Frase normalizada + Coleção ordenada de tokens canônicos únicos.
    """
    norm = normalizar_texto(texto)
    canon_tokens = extrair_tokens_canonicos(texto)
    return f"{norm} {' '.join(canon_tokens)}"


# Amostras originais de treinamento
BASE_TRAINING_SAMPLES: List[Tuple[str, str]] = [
    # Intenção: fios_chicote
    ("qual a cor do fio de ignicao no st340", "fios_chicote"),
    ("onde ligo o pos chave do st340ur", "fios_chicote"),
    ("cores do chicote do st8300", "fios_chicote"),
    ("para que serve o fio branco no st310", "fios_chicote"),
    ("qual fio e o negativo gnd", "fios_chicote"),
    ("chicote do st4305 pinagem completa", "fios_chicote"),
    ("qual a cor do fio positivo vcc", "fios_chicote"),
    ("fio amarelo no st310u", "fios_chicote"),
    ("fio laranja saida 1 de bloqueio", "fios_chicote"),
    ("chicote do st8310um quantos fios tem", "fios_chicote"),
    ("pinagem do chicote de 4 vias da rs232", "fios_chicote"),
    ("fios do chicote de audio do st8300r", "fios_chicote"),
    ("como ligar o leitor de ibutton no chicote", "fios_chicote"),
    ("o que ligar no fio azul do st8300", "fios_chicote"),
    ("qual a diferenca dos fios do chicote", "fios_chicote"),
    ("fio verde adc sinal analogico", "fios_chicote"),
    ("st340ur pos chave fio cor", "fios_chicote"),
    ("fio cor ignicao st340ur", "fios_chicote"),
    ("ignicao pos chave qual fio st8300", "fios_chicote"),
    ("cor do fio de corte bloqueio saida", "fios_chicote"),
    ("qual a cor do fio de ignicao no queclink gv50cg", "fios_chicote"),
    ("onde ligo o pos chave no gv50cg", "fios_chicote"),
    ("cores do chicote do queclink gv50cg", "fios_chicote"),
    ("pinagem do chicote de 5 vias gv50cg", "fios_chicote"),
    ("qual a funcao do fio laranja no gv50cg", "fios_chicote"),
    ("fio marrom gv50cg saida de corte", "fios_chicote"),
    ("gv50cg pos chave fio cor", "fios_chicote"),
    ("fio branco ignicao gv50cg", "fios_chicote"),

    # Intenção: calibracao_dpa
    ("como calibrar o dpa", "calibracao_dpa"),
    ("calibracao da analise de motorista", "calibracao_dpa"),
    ("quantas ignicoes para calibrar o st8300", "calibracao_dpa"),
    ("calibrar dpa por ignicao no st340ur", "calibracao_dpa"),
    ("como fazer 7 ignicoes para o dpa", "calibracao_dpa"),
    ("no st8310 sao 8 ignicoes para dpa", "calibracao_dpa"),
    ("comando start dpa calibration", "calibracao_dpa"),
    ("leds piscando 0 5s calibra dpa", "calibracao_dpa"),
    ("fazer 3 freadas 3 curvas 3 aceleracoes", "calibracao_dpa"),
    ("calibrar acelerometro aceleracao brusca curva acentuada", "calibracao_dpa"),
    ("procedimento de calibracao do dpa passo a passo", "calibracao_dpa"),
    ("dpa calibrar chave ignicao st8300", "calibracao_dpa"),
    ("st8310um calibrar dpa 8 vezes chave", "calibracao_dpa"),
    ("calibracao dpa st340 7 vezes meia chave", "calibracao_dpa"),

    # Intenção: leds_diagnostico
    ("led vermelho piscando 4 vezes", "leds_diagnostico"),
    ("o que significa led azul 2 piscadas", "leds_diagnostico"),
    ("led piscando 7 vezes sem sim card", "leds_diagnostico"),
    ("led gps sem sinal", "leds_diagnostico"),
    ("led azul com 3 piscadas erro de comunicacao", "leds_diagnostico"),
    ("led vermelho piscando normal uma vez", "leds_diagnostico"),
    ("led piscando 8 vezes puk bloqueado", "leds_diagnostico"),
    ("pin bloqueado led azul pisca 5 vezes", "leds_diagnostico"),
    ("tabela de piscadas dos leds suntech", "leds_diagnostico"),
    ("diagnostico visual dos leds do rastreador", "leds_diagnostico"),
    ("4 piscadas led vermelho gps erro antena", "leds_diagnostico"),
    ("led azul pisca 2 vezes erro servidor", "leds_diagnostico"),
    ("piscando 7 vezes led azul chip sim", "leds_diagnostico"),
    ("led verde piscando rapido gv50cg", "leds_diagnostico"),
    ("led verde piscando lento queclink gv50cg", "leds_diagnostico"),
    ("led verde fixo gv50cg sim pin bloqueado", "leds_diagnostico"),
    ("led azul gv50cg buscando gnss gps", "leds_diagnostico"),
    ("led azul fixo gv50cg fix gps ok", "leds_diagnostico"),
    ("diagnostico dos leds do queclink gv50cg", "leds_diagnostico"),

    # Intenção: instalacao_eletrica
    ("como instalar o rastreador no carro", "instalacao_eletrica"),
    ("onde colocar o fusivel de 5a", "instalacao_eletrica"),
    ("posicionamento correto da antena de gps", "instalacao_eletrica"),
    ("posso instalar o modulo embaixo de lata", "instalacao_eletrica"),
    ("como usar o conector scotchlok 3m", "instalacao_eletrica"),
    ("medir pos chave com multimetro", "instalacao_eletrica"),
    ("dicas para fazer a instalacao eletrica", "instalacao_eletrica"),
    ("onde achar o terra gnd na lataria", "instalacao_eletrica"),
    ("antena virada para cima this side up", "instalacao_eletrica"),
    ("curto circuito protecao de 5 amperes", "instalacao_eletrica"),
    ("posicionamento da antena do queclink gv50cg", "instalacao_eletrica"),
    ("this side towards sky gv50cg virado para cima", "instalacao_eletrica"),
    ("como posicionar o queclink gv50cg no veiculo", "instalacao_eletrica"),

    # Intenção: bloqueio_rele
    ("como ligar o rele de 5 pinos", "bloqueio_rele"),
    ("esquema de corte da bomba de combustivel", "bloqueio_rele"),
    ("qual pino do rele liga no rastreador", "bloqueio_rele"),
    ("onde ligar o pino 30 e 87a no rele de bloqueio", "bloqueio_rele"),
    ("ligacao do pino 85 e 86 do rele", "bloqueio_rele"),
    ("fazer bloqueio com rele automotivo", "bloqueio_rele"),
    ("como bloquear o veiculo com o fio laranja", "bloqueio_rele"),
    ("esquema de ligacao de sirene buzzer", "bloqueio_rele"),
    ("5 pinos rele ligar corte bomba", "bloqueio_rele"),
    ("bomba corte pino 30 87a rele", "bloqueio_rele"),
    ("como ligar o rele de bloqueio no queclink gv50cg", "bloqueio_rele"),
    ("qual diodo usar no rele do gv50cg 1n4004", "bloqueio_rele"),
    ("fio marrom corte bomba rele gv50cg", "bloqueio_rele"),
    ("esquema de bloqueio do gv50cg com diodo 1n4004", "bloqueio_rele"),
    ("pino 85 86 diodo rele queclink gv50cg", "bloqueio_rele"),

    # Intenção: antifurto
    ("como funciona o antifurto por ignicao", "antifurto"),
    ("como desarmar o antifurto com botao segredo", "antifurto"),
    ("antifurto por sensor de porta", "antifurto"),
    ("tempo para acionar o botao antifurto 1050", "antifurto"),
    ("quanto tempo o antifurto espera antes de bloquear", "antifurto"),
    ("como desativar o antifurto segurando 10 segundos", "antifurto"),

    # Intenção: jornada_trabalho
    ("como funciona a jornada de trabalho", "jornada_trabalho"),
    ("alerta de violacao de jornada 188", "jornada_trabalho"),
    ("tabela de fuso horario utc brasil", "jornada_trabalho"),
    ("como calcular hora extra no veiculo", "jornada_trabalho"),
    ("liberar hora extra por comando gprs", "jornada_trabalho"),
    ("configuracao de jornada de trabalho e descanso", "jornada_trabalho"),

    # Intenção: modo_idle
    ("o que e modo idle ocioso", "modo_idle"),
    ("como funciona o alerta de idle", "modo_idle"),
    ("motor ligado parado carro ocioso", "modo_idle"),
    ("configurar tempo de idle no veiculo", "modo_idle"),

    # Intenção: comandos
    ("quais sao os comandos sms gprs", "comandos"),
    ("como reiniciar o rastreador por comando reboot", "comandos"),
    ("comando eraseall apagar memoria", "comandos"),
    ("comando statusreq pedir posicao", "comandos"),
    ("estrutura de comandos st300cmd", "comandos"),
    ("comando de ignicao virtual por tensao st310", "comandos"),
    ("comando de ignicao virtual por tensao st340", "comandos"),
    ("comando de ignicao fisica st310", "comandos"),
    ("comando de ignicao fisica st340", "comandos"),
    ("comando ignicao por deslocamento st310u", "comandos"),
    ("comando ignicao por deslocamento st340ur", "comandos"),
    ("alterar beep de velocidade st340", "comandos"),
    ("comando buzzer enable st310 st340", "comandos"),
    ("comando buzzer disable st310 st340", "comandos"),
    ("comando buzzer st310u", "comandos"),
    ("comando buzzer st340", "comandos"),
    ("comando habilitar deep sleep st310 st340", "comandos"),
    ("comando desabilitar deep sleep st310", "comandos"),
    ("comando ignicao virtual acelerometro st8300 st4305", "comandos"),
    ("comando ignicao virtual tensao st8310", "comandos"),
    ("comando ignicao fisica pos chave st8300 st4305", "comandos"),
    ("alterar beep de velocidade 4g st8300 st4305 st8310", "comandos"),
    ("comando buzzer habilitar st8300", "comandos"),
    ("comando buzzer desabilitar st8300", "comandos"),
    ("modo sleep desabilitado st8300", "comandos"),
    ("comando sleep profundo st8300 st4305", "comandos"),
    ("comando sleep baixo consumo gprs mantido st8310", "comandos"),
    ("comando driving behavior st8300", "comandos"),
    ("comando driving behavior completo st8310 st4305", "comandos"),
    ("comando de bloquear veiculo gv50 4g", "comandos"),
    ("comando de desbloquear veiculo gv50 4g queclink", "comandos"),
    ("comando rfid get identificacao de motorista", "comandos"),
    ("comando rfid sgbras 09.2", "comandos"),
    ("comando rfid sgbras 04.8", "comandos"),
    ("comando teclado sgbras ativar rfid", "comandos"),
    ("comando teclado sgbras ativar matricula", "comandos"),
    ("comando timeout id getscale", "comandos"),
    ("tabela de comandos dos equipamentos", "comandos"),
    ("template de comandos por modelo", "comandos"),

    # Intenção: comandos_rs232
    ("comandos para porta serial rs232", "comandos_rs232"),
    ("como ler parametros pela rs232", "comandos_rs232"),
    ("conectar cabo serial 4 vias rs232", "comandos_rs232"),

    # Intenção: diferencas_modelos
    ("qual a diferenca entre st310u e st310ulc", "diferencas_modelos"),
    ("o st340ur aguenta agua e chuva", "diferencas_modelos"),
    ("quais modelos sao a prova de agua ip67", "diferencas_modelos"),
    ("st8300r tem comunicacao de voz microfone", "diferencas_modelos"),
    ("diferenca entre st8300 e st4305 cat m1", "diferencas_modelos"),
    ("st310uc nao tem ip67", "diferencas_modelos"),

    # Intenção: especificacoes
    ("quais as especificacoes tecnicas do st8300", "especificacoes"),
    ("tensao de alimentacao suportada 8v a 33v", "especificacoes"),
    ("qual a capacidade da bateria backup interna", "especificacoes"),
    ("quantas posicoes salva na memoria fifo", "especificacoes"),
    ("tensao de alimentacao do queclink gv50cg 9v a 90v", "especificacoes"),
    ("especificacoes tecnicas do queclink gv50cg", "especificacoes"),
    ("bateria backup do queclink gv50cg", "especificacoes"),

    # Intenção: chip_sim
    ("como colocar o chip sim card", "chip_sim"),
    ("tamanho do sim card micro sim nano", "chip_sim"),
    ("como destravar o chip com pin", "chip_sim"),
    ("qual o tamanho do chip no queclink gv50cg", "chip_sim"),
    ("onde fica a chave da bateria do gv50cg power switch", "chip_sim"),
    ("como abrir o gv50cg para colocar o micro sim", "chip_sim"),

    # Intenção: configuracao_synctrak
    ("como conectar no synctrak", "configuracao_synctrak"),
    ("qual a senha padrao do synctrak", "configuracao_synctrak"),
    ("senha de fabrica st5656", "configuracao_synctrak"),
    ("procedimento para abrir no computador cabo usb", "configuracao_synctrak"),
    ("tirar bateria antes de ligar o usb synctrak", "configuracao_synctrak"),
    ("como configurar ip e porta do servidor", "configuracao_synctrak"),
    ("servidor agps e servidor scuti suntech", "configuracao_synctrak"),
    ("synctrak senha padrao st5656", "configuracao_synctrak"),

    # Intenção: bateria_consumo
    ("como funciona o desligamento por bateria fraca", "bateria_consumo"),
    ("battery shutdown parameter st310", "bateria_consumo"),
    ("parametro 1930 tipo de baixo consumo", "bateria_consumo"),
    ("modo ultrabaixo consumo e deep sleep", "bateria_consumo"),
    ("tensao de protecao 12v e 24v", "bateria_consumo")
]


def expandir_amostras_invariantes(samples: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Data Augmentation: Cria variações invertidas e ordenadas de palavras
    para treinar a rede a ser 100% agnóstica à ordem dos termos.
    """
    expandidas = []
    for frase, intent in samples:
        expandidas.append((frase, intent))
        palavras = frase.split()
        if len(palavras) > 2:
            expandidas.append((" ".join(reversed(palavras)), intent))
            expandidas.append((" ".join(sorted(palavras)), intent))
            tokens_c = extrair_tokens_canonicos(frase)
            if tokens_c:
                expandidas.append((" ".join(tokens_c), intent))
    return expandidas


class NeuralManualBrain:
    """Rede Neural e Motor de Inteligência Artificial para os Manuais Suntech e Queclink"""

    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.svd: Optional[TruncatedSVD] = None
        self.mlp: Optional[MLPClassifier] = None
        self.chunk_embeddings: Optional[np.ndarray] = None
        self.chunk_token_sets: List[Set[str]] = []
        self.intents: List[str] = INTENTS_LIST
        self.is_trained: bool = False
        self.carregar_ou_treinar()

    def carregar_ou_treinar(self):
        """Carrega modelo treinado do disco ou treina uma nova rede neural"""
        MODEL_DIR.mkdir(parents=True, exist_ok=True)
        if MODEL_FILE.exists():
            try:
                with open(MODEL_FILE, "rb") as f:
                    data = pickle.load(f)
                    self.vectorizer = data["vectorizer"]
                    self.svd = data["svd"]
                    self.mlp = data["mlp"]
                    self.chunk_embeddings = data["chunk_embeddings"]
                    self.chunk_token_sets = data.get("chunk_token_sets", [])
                    self.is_trained = True
                print(">> [Rede Neural] Modelo neural carregado com sucesso do disco!")
                return
            except Exception as e:
                print(f">> [Rede Neural] Falha ao carregar modelo existente ({e}). Retreinando...")

        self.treinar()

    def treinar(self):
        """Treina a Rede Neural Multicamadas (MLP) com representações invariantes"""
        print(">> [Rede Neural] Iniciando treinamento da rede neural com invariância à ordem...")
        start_time = time.time()

        chunk_texts = []
        self.chunk_token_sets = []
        for c in KNOWLEDGE_CHUNKS:
            raw_text = f"{c['title']} {c['summary']} {c['content']} {' '.join(c['keywords'])}"
            inv_text = gerar_representacao_invariante(raw_text)
            chunk_texts.append(inv_text)
            self.chunk_token_sets.append(set(extrair_tokens_canonicos(raw_text)))

        amostras_expandidas = expandir_amostras_invariantes(BASE_TRAINING_SAMPLES)
        sample_texts = [gerar_representacao_invariante(s[0]) for s in amostras_expandidas]
        sample_labels = [s[1] for s in amostras_expandidas]

        todos_textos = chunk_texts + sample_texts

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            analyzer="word",
            sublinear_tf=True,
            min_df=1
        )
        X_tfidf = self.vectorizer.fit_transform(todos_textos)

        n_components = min(48, X_tfidf.shape[1] - 1)
        self.svd = TruncatedSVD(n_components=n_components, random_state=42)
        X_dense = self.svd.fit_transform(X_tfidf)

        num_chunks = len(KNOWLEDGE_CHUNKS)
        self.chunk_embeddings = X_dense[:num_chunks]

        X_train = X_dense[num_chunks:]
        y_train = np.array(sample_labels)

        self.mlp = MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation="relu",
            solver="adam",
            alpha=0.0001,
            batch_size=32,
            learning_rate_init=0.003,
            max_iter=600,
            random_state=42,
            early_stopping=False
        )
        self.mlp.fit(X_train, y_train)

        with open(MODEL_FILE, "wb") as f:
            pickle.dump({
                "vectorizer": self.vectorizer,
                "svd": self.svd,
                "mlp": self.mlp,
                "chunk_embeddings": self.chunk_embeddings,
                "chunk_token_sets": self.chunk_token_sets
            }, f)

        self.is_trained = True
        elapsed = time.time() - start_time
        print(f">> [Rede Neural] Treinamento concluído em {elapsed:.2f}s! Amostras: {len(X_train)} | Classes: {len(self.mlp.classes_)}")

    def detectar_aparelho(self, query: str) -> Optional[str]:
        """Identifica modelo de aparelho mencionado em qualquer posição do texto"""
        q = normalizar_texto(query)

        if "queclink" in q or "gv50cg" in q or "gv50" in q or "gv 50" in q:
            return "Queclink GV50CG"
        if "st4305" in q or "st4315" in q:
            return "ST4305"
        if "st8300r" in q:
            return "ST8300R"
        if "st8300h" in q:
            return "ST8300H"
        if "st8300" in q:
            return "ST8300"
        if "st340ur" in q or "st340" in q:
            return "ST340UR"
        if "st310ulc" in q:
            return "ST310ULC"
        if "st310uc2" in q:
            return "ST310UC2"
        if "st310uc" in q:
            return "ST310UC"
        if "st310u" in q:
            return "ST310U"
        if "st310" in q:
            return "Linha ST310"
        if "st8310um" in q or "st8310" in q:
            return "ST8310UM"
        if "st8210" in q:
            return "ST8210"
        if "rfid" in q or "sgbras" in q or "getscale" in q or "matricula" in q or "identificador" in q:
            return "Identificador de Motorista"

        return None

    def inferir_intencao_e_ranking(
        self,
        query: str,
        filtro_aparelho: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Passa a consulta pela Rede Neural com invariância total à ordem:
        Combina predição MLP + similaridade cosseno densa + overlap canônico Jaccard.
        """
        q_norm = normalizar_texto(query)
        if not q_norm:
            return {
                "intencao": "desconhecida",
                "confianca": 0.0,
                "chunks": [],
                "aparelho_detectado": None
            }

        aparelho_detectado = self.detectar_aparelho(query) or filtro_aparelho
        query_tokens = set(extrair_tokens_canonicos(query))

        q_invariante = gerar_representacao_invariante(query)
        q_tfidf = self.vectorizer.transform([q_invariante])
        q_dense = self.svd.transform(q_tfidf)

        probs = self.mlp.predict_proba(q_dense)[0]
        max_idx = np.argmax(probs)
        pred_intent = self.mlp.classes_[max_idx]
        intent_confidence = float(probs[max_idx])

        norm_q = np.linalg.norm(q_dense)
        if norm_q > 0:
            similaridades = np.dot(self.chunk_embeddings, q_dense.T).flatten() / (
                np.linalg.norm(self.chunk_embeddings, axis=1) * norm_q + 1e-9
            )
        else:
            similaridades = np.zeros(len(KNOWLEDGE_CHUNKS))

        scored_chunks = []
        for i, chunk in enumerate(KNOWLEDGE_CHUNKS):
            sim_score = float(similaridades[i])
            bonus_intent = 0.35 if chunk["topic"] == pred_intent else 0.0

            overlap_ratio = 0.0
            if query_tokens and self.chunk_token_sets:
                inter = query_tokens.intersection(self.chunk_token_sets[i])
                overlap_ratio = len(inter) / len(query_tokens)

            bonus_device = 0.0
            if aparelho_detectado:
                dev_norm = normalizar_texto(aparelho_detectado)
                chunk_family_norm = normalizar_texto(chunk["device_family"])
                if dev_norm in chunk_family_norm or chunk_family_norm in dev_norm:
                    bonus_device = 0.50
                elif "geral" in chunk_family_norm:
                    bonus_device = 0.10
                else:
                    bonus_device = -0.25

            final_score = (
                (sim_score * 0.35) +
                (bonus_intent * 0.25) +
                (overlap_ratio * 0.20) +
                (bonus_device * 0.20)
            )
            scored_chunks.append((final_score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)

        melhores_chunks = [c for score, c in scored_chunks[:3] if score > 0.05]
        if not melhores_chunks and scored_chunks:
            melhores_chunks = [scored_chunks[0][1]]

        return {
            "intencao": pred_intent,
            "confianca": round(intent_confidence * 100, 1),
            "chunks": melhores_chunks,
            "aparelho_detectado": aparelho_detectado
        }

    def gerar_resposta(
        self,
        query: str,
        filtro_aparelho: Optional[str] = None
    ) -> Dict[str, Any]:
        """Gera a resposta completa personalizada e direta a partir da consulta"""
        start_time = time.time()
        analise = self.inferir_intencao_e_ranking(query, filtro_aparelho)
        chunks = analise["chunks"]
        aparelho = analise["aparelho_detectado"]
        intencao = analise["intencao"]
        confianca = analise["confianca"]

        if not chunks:
            tempo_ms = int((time.time() - start_time) * 1000)
            return {
                "resposta": (
                    "Não encontrei informações correspondentes nos manuais técnicos com base na sua pergunta. "
                    "Por favor, especifique o modelo do rastreador (ex: **Queclink GV50CG**, **ST340UR**, **ST4305/ST8300**, "
                    "**ST310U/UC**, **ST8310UM**) e a dúvida exata (ex: fio de pós-chave, relé com diodo, LEDs ou calibração)."
                ),
                "intencao": intencao,
                "aparelho_detectado": aparelho,
                "confianca": confianca,
                "fontes": [],
                "sugestoes": [
                    "Qual o fio pós-chave do Queclink GV50CG?",
                    "Como ligar o relé com diodo 1N4004 no GV50CG?",
                    "Qual a pinagem do chicote do ST340UR?"
                ],
                "tempo_ms": tempo_ms
            }

        chunk_principal = chunks[0]
        fontes = [f"{c['device_family']} ({c['pages']})" for c in chunks]

        # Sintetiza resposta sob medida, respondendo DE FATO o que foi perguntado
        resposta_md = self._sintetizar_conteudo_personalizado(query, chunk_principal, aparelho, intencao)
        sugestoes = self._gerar_sugestoes_contextuais(intencao, aparelho or chunk_principal["device_family"])
        tempo_ms = int((time.time() - start_time) * 1000)

        return {
            "resposta": resposta_md,
            "intencao": intencao,
            "aparelho_detectado": aparelho or chunk_principal["device_family"],
            "confianca": confianca,
            "fontes": list(dict.fromkeys(fontes)),
            "sugestoes": sugestoes,
            "tempo_ms": tempo_ms
        }

    def _sintetizar_conteudo_personalizado(
        self,
        query: str,
        principal: Dict[str, Any],
        aparelho: Optional[str],
        intencao: str
    ) -> str:
        """
        Produz resposta altamente personalizada, respondendo EXATAMENTE o que foi perguntado,
        evitando blocos de textos gigantes e focando no detalhe requisitado pelo instalador.
        """
        q = normalizar_texto(query)
        dev = (aparelho or principal["device_family"]).strip()
        dev_upper = dev.upper()

        # Determina o aparelho ativo
        is_gv50 = "GV50" in dev_upper or "QUECLINK" in dev_upper or "gv50" in q or "queclink" in q
        is_st340 = "ST340" in dev_upper or "st340" in q
        is_st8300 = ("ST8300" in dev_upper or "ST4305" in dev_upper or "st8300" in q or "st4305" in q) and not is_st340
        is_st310 = "ST310" in dev_upper or "st310" in q
        is_st8310 = "ST8310" in dev_upper or "ST8210" in dev_upper or "st8310" in q or "st8210" in q

        # Se não identificou nenhum específico, assume o do chunk principal
        if not (is_gv50 or is_st340 or is_st8300 or is_st310 or is_st8310):
            fam = principal["device_family"].upper()
            if "QUECLINK" in fam or "GV50" in fam:
                is_gv50 = True
            elif "ST340" in fam:
                is_st340 = True
            elif "ST8300" in fam or "ST4305" in fam:
                is_st8300 = True
            elif "ST310" in fam:
                is_st310 = True
            elif "ST8310" in fam:
                is_st8310 = True

        nome_modelo = "Queclink GV50CG" if is_gv50 else (
            "Suntech ST340UR" if is_st340 else (
                "Suntech ST4305 / ST8300" if is_st8300 else (
                    "Suntech Linha ST310" if is_st310 else (
                        "Suntech ST8310UM" if is_st8310 else dev
                    )
                )
            )
        )

        eh_pergunta_completa = any(w in q for w in [
            "completo", "completa", "todos os fios", "todas as cores", "tabela", "pinagem completa", "visao geral"
        ])

        # Flags semânticas precisas com limites de palavras (Word Boundaries)
        tem_led = bool(re.search(r'\b(led|leds|pisca|piscando|piscada|piscadas|luz)\b', q))
        tem_rele = bool(re.search(r'\b(rele|bloqueio|bloquear|corte|cortar|imobilizador|diodo|1n4004)\b', q)) or ("bomba" in q and "combustivel" in q)
        tem_ignicao = bool(re.search(r'\b(pos chave|pos-chave|poschave|ignicao|linha 15)\b', q)) or (bool(re.search(r'\b(pos|chave|ign)\b', q)) and not bool(re.search(r'\b(significa|designar)\b', q)))
        tem_positivo = bool(re.search(r'\b(positivo|vcc|alimentacao|tensao|volts|voltagem|fusivel)\b', q))
        tem_negativo = bool(re.search(r'\b(negativo|gnd|terra)\b', q))
        tem_panico = bool(re.search(r'\b(panico|emergencia|analogic|analogica|analogico|adc|botao segredo)\b', q))
        tem_antena = bool(re.search(r'\b(antena|sky|towards sky|ceu|posicionamento|orientacao)\b', q))
        tem_sim = bool(re.search(r'\b(sim|chip|micro sim|micro-sim|chave|switch|power switch)\b', q))
        tem_dpa = bool(re.search(r'\b(dpa|calibrar|calibracao|calibra)\b', q))
        tem_senha = bool(re.search(r'\b(senha|password|st5656)\b', q))
        tem_ip67 = bool(re.search(r'\b(ip67|agua|chuva|molhar|estanque|vedacao)\b', q))

        # ---------------------------------------------------------------------
        # 0. PERGUNTAS DE COMANDOS / TEMPLATES DE CONFIGURAÇÃO (Prioritário)
        # ---------------------------------------------------------------------
        tem_palavra_comando = bool(re.search(r'\b(comando|comandos|template|templates|st300evt|st300svc|st300cmd|st300dex|prg|gtdos|at\+gtdos|beep|buzzer|rfid|sgbras|matricula|getscale|bloquear|desbloquear|deep sleep|driving behavior)\b', q))
        if (tem_palavra_comando and not ("como ligar" in q or "esquema" in q or "pinagem" in q or "fio" in q)) or intencao == "comandos":
            # 1. Comandos Queclink GV50 4G (Bloqueio / Desbloqueio)
            if is_gv50 or "gv50" in q or "queclink" in q:
                if "desbloque" in q or "liberar" in q:
                    return (
                        f"### 🔓 Comando de Desbloqueio - Queclink GV50 4G (GV50CG)\n"
                        f"**Manual e Tabela Operacional:** Queclink GV50 4G\n\n"
                        f"**Template de Envio:**\n"
                        f"```text\n"
                        f"AT+GTDOS=gv50cg,0,1,1,0,0,0,,,0,0,5,,,,FFFF$\n"
                        f"```\n\n"
                        f"> ⚠️ **AVISO OBRIGATÓRIO:** **EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!**\n"
                        f"> Para que o Queclink GV50 processe e confirme a liberação, a ignição do veículo deve estar obrigatoriamente ligada.\n\n"
                        f"• **Função:** Desativa a saída digital (Pino 4 - Fio Marrom / OUT) restabelecendo a partida do motor."
                    )
                elif "bloque" in q or "corte" in q or "imobiliz" in q:
                    return (
                        f"### 🔒 Comando de Bloqueio - Queclink GV50 4G (GV50CG)\n"
                        f"**Manual e Tabela Operacional:** Queclink GV50 4G\n\n"
                        f"**Template de Envio:**\n"
                        f"```text\n"
                        f"AT+GTDOS=gv50cg,0,1,1,1,0,0,,,0,0,5,,,,FFFF$\n"
                        f"```\n\n"
                        f"> ⚠️ **AVISO OBRIGATÓRIO:** **EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!**\n"
                        f"> Para que o Queclink GV50 processe o comando de bloqueio, o veículo e o rastreador DEVEM estar com a ignição ligada.\n\n"
                        f"• **Função:** Aciona a saída digital (Pino 4 - Fio Marrom / OUT) para atuar no relé e efetuar o corte da bomba/ignição."
                    )
                else:
                    return (
                        f"### 📡 Comandos Queclink GV50 4G (GV50CG)\n\n"
                        f"| Comando | Template | Aviso Obrigatório |\n"
                        f"| :--- | :--- | :--- |\n"
                        f"| **Bloquear Veículo** | `AT+GTDOS=gv50cg,0,1,1,1,0,0,,,0,0,5,,,,FFFF$` | ⚠️ **EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!** |\n"
                        f"| **Desbloquear Veículo** | `AT+GTDOS=gv50cg,0,1,1,0,0,0,,,0,0,5,,,,FFFF$` | ⚠️ **EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!** |"
                    )

            # 2. Identificador de Motorista / RFID / SGBRAS / Teclado / GetScale
            if any(k in q for k in ["rfid", "sgbras", "matricula", "getscale", "identificador", "motorista", "st300dex"]):
                if "teclado" in q:
                    if "matricula" in q:
                        return (
                            f"### ⌨️ Comando TECLADO SGBRAS (Ativar Matrícula)\n\n"
                            f"**Template:**\n"
                            f"```text\n"
                            f"DEX;SERIAL;0008;SGBT|17|;90\n"
                            f"```\n"
                            f"• Habilita a digitação manual de matrícula no teclado numérico SGBRAS. Substitua `SERIAL` pelo serial do rastreador."
                        )
                    elif "rfid" in q:
                        return (
                            f"### ⌨️ Comando TECLADO SGBRAS (Ativar RFID)\n\n"
                            f"**Template:**\n"
                            f"```text\n"
                            f"DEX;SERIAL;0008;SGBT|18|;91\n"
                            f"```\n"
                            f"• Habilita o leitor de cartão RFID integrado ao teclado SGBRAS. Substitua `SERIAL` pelo serial do rastreador."
                        )
                elif "getscale" in q or "timeout" in q:
                    return (
                        f"### ⏱️ Comando Timeout ID GetScale\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"DEX;SERIAL;0006;709|0|;C8\n"
                        f"```\n"
                        f"• Configura o timeout de leitura de identificação GetScale via porta serial DEX. Substitua `SERIAL`."
                    )
                elif "09.2" in q:
                    return (
                        f"### 💳 Comando RFID SGBRAS (09.2)\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"ST300DEX;SERIAL;02;10;SGBT|09.2|;F1\n"
                        f"```\n"
                        f"• Configuração do leitor RFID SGBRAS versão 09.2. Substitua `SERIAL` pelo serial do rastreador."
                    )
                elif "04.8" in q:
                    return (
                        f"### 💳 Comando RFID SGBRAS (04.8)\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"ST300DEX;SERIAL;02;10;SGBT|04.8|;F2\n"
                        f"```\n"
                        f"• Configuração do leitor RFID SGBRAS versão 04.8. Substitua `SERIAL` pelo serial do rastreador."
                    )
                elif "sgbras" in q:
                    return (
                        f"### 💳 Comando RFID GET - Identificação de Motorista / Passageiro (SGBRAS)\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"ST300DEX;SERIAL;02;19;GTSL|7|1|2|719|0|1|;3\n"
                        f"```\n"
                        f"• Configuração do RFID SGBRAS com parâmetro GTSL. Substitua `SERIAL` pelo serial do aparelho."
                    )
                elif "0009" in q:
                    return (
                        f"### 💳 Comando RFID GET (DEX 0009)\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"DEX;SERIAL;0009;718|1|;C9;80\n"
                        f"```\n"
                        f"• Inicialização do leitor RFID GET via DEX. Substitua `SERIAL`."
                    )
                else:
                    return (
                        f"### 💳 Comandos de Identificador de Motorista (RFID / Teclado / GetScale)\n\n"
                        f"| Comando | Template |\n"
                        f"| :--- | :--- |\n"
                        f"| **RFID GET (1. Motorista/Passageiro)** | `ST300DEX;02;6;718|1|;C9` |\n"
                        f"| **RFID GET (SGBRAS GTSL)** | `ST300DEX;SERIAL;02;19;GTSL|7|1|2|719|0|1|;3` |\n"
                        f"| **RFID GET (DEX 0009)** | `DEX;SERIAL;0009;718|1|;C9;80` |\n"
                        f"| **RFID SGBRAS (09.2)** | `ST300DEX;SERIAL;02;10;SGBT|09.2|;F1` |\n"
                        f"| **RFID SGBRAS (04.8)** | `ST300DEX;SERIAL;02;10;SGBT|04.8|;F2` |\n"
                        f"| **TECLADO SGBRAS (Ativar RFID)** | `DEX;SERIAL;0008;SGBT|18|;91` |\n"
                        f"| **TECLADO SGBRAS (Ativar Matrícula)** | `DEX;SERIAL;0008;SGBT|17|;90` |\n"
                        f"| **Timeout ID GetScale** | `DEX;SERIAL;0006;709|0|;C8` |\n\n"
                        f"> 💡 Substitua `SERIAL` pelo serial do rastreador onde o periférico está conectado."
                    )

            # 3. Comandos Suntech ST8310 / ST8300 / ST4315 / ST4305 (PRG)
            if is_st8300 or is_st8310 or "prg" in q or "4g" in q:
                if "acelerometro" in q:
                    return (
                        f"### 📡 Comando de Ignição Virtual por Acelerômetro - Suntech 4G\n"
                        f"**Aparelhos:** ST8310 / ST8300 / ST4315 / ST4305\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"PRG;SERIAL;17;00#03\n"
                        f"```\n"
                        f"• Detecta ignição virtualmente através do acelerômetro interno (G-sensor). Substitua `SERIAL`."
                    )
                elif "tensao" in q or "voltagem" in q:
                    return (
                        f"### 📡 Comando de Ignição Virtual por Tensão - Suntech 4G\n"
                        f"**Aparelhos:** ST8310 / ST8300 / ST4315 / ST4305\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"PRG;SERIAL;17;00#02\n"
                        f"```\n"
                        f"• Detecta ignição virtualmente pela variação da tensão da bateria. Substitua `SERIAL`."
                    )
                elif "fisica" in q or "pos chave" in q:
                    return (
                        f"### 📡 Comando de Ignição Física (Pós-Chave) - Suntech 4G\n"
                        f"**Aparelhos:** ST8310 / ST8300 / ST4315 / ST4305\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"PRG;SERIAL;17;00#01\n"
                        f"```\n"
                        f"• Configura a detecção convencional de ignição pelo Fio Azul conectado ao pós-chave. Substitua `SERIAL`."
                    )
                elif "beep" in q or "velocidade" in q:
                    return (
                        f"### 🔊 Comando Alterar Beep de Velocidade (4G)\n"
                        f"**Aparelhos:** ST8310 / ST8300 / ST4315 / ST4305\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"PRG;SERIAL;16;21#VELOCIDADE\n"
                        f"```\n"
                        f"• Define o limite para disparo do beep sonoro. Substitua `VELOCIDADE` pelo limite em km/h (ex: 80, 100, 120) e `SERIAL` pelo serial."
                    )
                elif "buzzer" in q:
                    return (
                        f"### 🔊 Comandos de Buzzer - Suntech 4G\n"
                        f"**Aparelhos:** ST8310 / ST8300 / ST4315 / ST4305\n\n"
                        f"• **Habilitar Buzzer:** `PRG;SERIAL;10;64#01`\n"
                        f"• **Desabilitar Buzzer:** `PRG;SERIAL;10;64#00`\n"
                        f"Substitua `SERIAL` pelo serial do rastreador."
                    )
                elif "sleep" in q:
                    return (
                        f"### 💤 Comandos de Modo Sleep - Suntech 4G\n"
                        f"**Aparelhos:** ST8310 / ST8300 / ST4315 / ST4305\n\n"
                        f"• **Modo Sleep Desabilitado (Consumo normal):** `PRG;SERIAL;19;30#00`\n"
                        f"• **Sleep Profundo (Ultra-baixo consumo <3mA):** `PRG;SERIAL;19;30#01`\n"
                        f"• **Sleep Baixo consumo (GPRS/LTE Mantido):** `PRG;SERIAL;19;30#02`\n\n"
                        f"> 💡 Substitua `SERIAL` pelo serial do equipamento."
                    )
                elif "driving" in q or "behavior" in q or "telemetria" in q:
                    return (
                        f"### 🏎️ Comandos Driving Behavior (Telemetria) - Suntech 4G\n"
                        f"**Aparelhos:** ST8310 / ST8300 / ST4315 / ST4305\n\n"
                        f"• **Habilitar Função:** `PRG;SERIAL;19;10#01`\n"
                        f"• **Configuração Completa:**\n"
                        f"```text\n"
                        f"PRG;SERIAL;19;10#01;12#40.0;13#45.0;14#60.0;21#20.0;22#20.0;23#20.0\n"
                        f"```\n"
                        f"Parâmetros: `12#40.0` (aceleração brusca), `13#45.0` (frenagem brusca), `14#60.0` (curva brusca), `21#20.0`, `22#20.0`, `23#20.0` (impactos)."
                    )

            # 4. Comandos Suntech ST310 / ST340
            if is_st310 or is_st340 or "st310" in q or "st340" in q:
                if "tensao" in q or ("virtual" in q and not "deslocamento" in q):
                    cmd_310 = "ST300EVT;SERIAL;02;2;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0"
                    cmd_340 = "ST300EVT;SERIAL;02;2;10;0;2;20;9;20;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3"
                    return (
                        f"### ⚡ Comandos de Ignição Virtual por Tensão - ST310 / ST340\n\n"
                        f"• **Para ST310:**\n"
                        f"```text\n"
                        f"{cmd_310}\n"
                        f"```\n\n"
                        f"• **Para ST340 / ST340UR:**\n"
                        f"```text\n"
                        f"{cmd_340}\n"
                        f"```\n\n"
                        f"> 💡 Substitua `SERIAL` pelo serial do rastreador."
                    )
                elif "fisica" in q:
                    cmd_310 = "ST300EVT;SERIAL;02;3;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0"
                    cmd_340 = "ST300EVT;SERIAL;02;0;10;0;12;13;9;30;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3"
                    return (
                        f"### 🔌 Comandos de Ignição Física (Pós-Chave) - ST310 / ST340\n\n"
                        f"• **Para ST310:**\n"
                        f"```text\n"
                        f"{cmd_310}\n"
                        f"```\n\n"
                        f"• **Para ST340 / ST340UR:**\n"
                        f"```text\n"
                        f"{cmd_340}\n"
                        f"```\n\n"
                        f"> 💡 Substitua `SERIAL` pelo serial do rastreador."
                    )
                elif "deslocamento" in q:
                    cmd_310 = "ST300EVT;SERIAL;02;3;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0"
                    cmd_340 = "ST300EVT;SERIAL;02;3;10;0;2;20;9;20;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3"
                    return (
                        f"### 🚗 Comandos de Ignição por Deslocamento (GPS) - ST310 / ST340\n\n"
                        f"• **Para ST310U:**\n"
                        f"```text\n"
                        f"{cmd_310}\n"
                        f"```\n\n"
                        f"• **Para ST340UR:**\n"
                        f"```text\n"
                        f"{cmd_340}\n"
                        f"```\n\n"
                        f"> 💡 Substitua `SERIAL` pelo serial do rastreador."
                    )
                elif "beep" in q or "velocidade" in q:
                    return (
                        f"### 🔊 Comando Alterar Beep de Velocidade - ST340\n\n"
                        f"**Template:**\n"
                        f"```text\n"
                        f"ST300SVC;SERIAL;02;1;VELOCIDADE;0;0;0;1;1;0;1;0;0;0;1;1\n"
                        f"```\n"
                        f"• Substitua `VELOCIDADE` pelo limite em km/h (ex: 80, 100, 110) e `SERIAL` pelo serial do aparelho."
                    )
                elif "buzzer" in q:
                    return (
                        f"### 🔊 Comandos de Buzzer - ST310 / ST340\n\n"
                        f"• **Acionar / Ligar Buzzer (Enable 1):** `ST300CMD;SERIAL;02;Enable1`\n"
                        f"• **Desligar Buzzer (Disable 1):** `ST300CMD;SERIAL;02;Disable1`\n"
                        f"• **Configuração Buzzer ST310U (110 km/h):** `ST300SVC;SERIAL;02;1;110;0;0;0;0;0;1;0;0;0;0`\n"
                        f"• **Configuração Buzzer ST340 (120 km/h):** `ST300SVC;SERIAL;02;1;120;0;0;0;1;1;0;1;0;0;0;1;1`\n\n"
                        f"> 💡 Substitua `SERIAL` pelo serial do rastreador."
                    )
                elif "sleep" in q:
                    return (
                        f"### 💤 Comandos Deep Sleep - ST310 / ST340\n\n"
                        f"• **Habilitar Deep Sleep:** `ST300SVC;SERIAL;02;0;200;1;0;0;0;1;0;1;0;0;0;1;1`\n"
                        f"• **Desabilitar Deep Sleep / Qualquer Sleep:** `ST300SVC;SERIAL;02;0;200;0;0;0;0;0;1;0;1;0;0;0;1`\n\n"
                        f"> 💡 Substitua `SERIAL` pelo serial do rastreador."
                    )

        # ---------------------------------------------------------------------
        # 1. PERGUNTAS DE DIAGNÓSTICO DE LEDS (Prioridade se mencionou LED/Piscada)
        # ---------------------------------------------------------------------
        if tem_led and not tem_dpa:
            if is_gv50:
                if "verde" in q or "celular" in q or "rede" in q or "gsm" in q or "lte" in q:
                    return (
                        f"### 💡 Diagnóstico do LED Celular (Verde) - {nome_modelo}\n"
                        f"**Manual Oficial:** Queclink GV50CG (Págs. 7, 8)\n\n"
                        f"• **Piscando Rápido (100ms Ligado / 800ms Desligado):** Buscando sinal de rede celular LTE Cat 1 / 2G.\n"
                        f"• **Piscando Lento (100ms Ligado / 2000ms Desligado):** Registrado com sucesso na rede celular (Operação Normal / Online).\n"
                        f"• **Aceso Fixo (Continuously ON):** **Cartão SIM bloqueado por código PIN**. Solução: Coloque o chip em um smartphone e desative a senha PIN nas configurações.\n"
                        f"• **Apagado:** Modem celular desligado ou equipamento sem alimentação."
                    )
                elif "azul" in q or "gnss" in q or "gps" in q:
                    return (
                        f"### 💡 Diagnóstico do LED GNSS / GPS (Azul) - {nome_modelo}\n"
                        f"**Manual Oficial:** Queclink GV50CG (Págs. 7, 8)\n\n"
                        f"• **Aceso Fixo (Continuously ON):** **Fix GNSS obtido com sucesso** (localização GPS precisa calculada).\n"
                        f"• **Piscando Rápido (100ms Ligado / 100ms Desligado):** Buscando satélites GNSS (sem posição fixada ainda).\n"
                        f"• **Piscando Lento (600ms Ligado / 600ms Desligado):** GNSS sem sinal ou erro nos dados de satélite.\n"
                        f"• **Apagado:** Receptor GNSS desligado."
                    )
                else:
                    return (
                        f"### 💡 Tabela de LEDs - {nome_modelo}\n"
                        f"**Manual Oficial:** Queclink GV50CG (Págs. 7, 8)\n\n"
                        f"**1. LED Celular (Verde):**\n"
                        f"• *Piscando rápido:* Buscando rede celular LTE/2G\n"
                        f"• *Piscando lento:* Registrado na rede (Online / OK)\n"
                        f"• *Aceso fixo:* Chip SIM bloqueado por PIN (necessário desbloquear)\n\n"
                        f"**2. LED GNSS (Azul):**\n"
                        f"• *Aceso fixo:* GPS Fixado com precisão\n"
                        f"• *Piscando rápido:* Buscando satélites\n"
                        f"• *Piscando lento:* Sem sinal de satélite"
                    )
            else:
                if "4" in q:
                    return (
                        f"### 💡 LED Vermelho com 4 Piscadas - {nome_modelo}\n"
                        f"**Manual Oficial:** Suntech Diagnóstico de LEDs\n\n"
                        f"> 👉 **Significado:** **Erro no Chipset de GPS ou Erro na Antena de GPS**\n\n"
                        f"• **Possíveis Causas:** Antena de GPS desconectada, cabo rompido, conector SMA danificado ou defeito no módulo interno de GPS.\n"
                        f"• **Ação Recomendada:** Verifique a conexão física da antena externa de GPS ou substitua a antena para testar."
                    )
                elif "2" in q and ("vermelho" in q or "gps" in q):
                    return (
                        f"### 💡 LED Vermelho com 2 Piscadas - {nome_modelo}\n"
                        f"> 👉 **Significado:** **Sem Sinal GPS** (buscando satélites).\n\n"
                        f"• **Solução:** Posicione o veículo em local aberto com céu visível. Não posicione a antena sob estruturas metálicas."
                    )
                elif "7" in q:
                    return (
                        f"### 💡 LED Azul com 7 Piscadas - {nome_modelo}\n"
                        f"> 👉 **Significado:** **Sem Cartão SIM Card**\n\n"
                        f"• **Possíveis Causas:** Chip não inserido, mal posicionado no slot ou leitor de chip danificado.\n"
                        f"• **Solução:** Retire o chip, limpe os contatos dourados com álcool isopropílico e reinsira até travar com clique."
                    )
                elif "5" in q:
                    return (
                        f"### 💡 LED Azul com 5 Piscadas - {nome_modelo}\n"
                        f"> 👉 **Significado:** **Cartão SIM Bloqueado por PIN**\n\n"
                        f"• **Solução:** Insira o chip em um smartphone e desative a solicitação de PIN nas opções de segurança do aparelho."
                    )

        # ---------------------------------------------------------------------
        # 2. PERGUNTAS DE BLOQUEIO / CORTE / RELÉ / DIODO 1N4004
        # ---------------------------------------------------------------------
        if tem_rele and not tem_dpa and not ("antifurto" in q):
            if is_gv50:
                return (
                    f"### 📘 Esquema de Bloqueio e Relé - {nome_modelo}\n"
                    f"**Manual Oficial:** Queclink GV50CG (Págs. 11, 12)\n\n"
                    f"> 👉 **Fio de Bloqueio:** Fio Marrom (Pino 4 - OUT / Saída Digital Open-Drain máx 150mA)\n\n"
                    f"#### ⚠️ Atenção Crítica (Diodo de Roda Livre Obrigatório):\n"
                    f"É **obrigatório** instalar um diodo (ex: **1N4004**) em paralelo entre os pinos 85 e 86 da bobina do relé para proteger a saída digital do GV50CG contra queima por pico indutivo.\n\n"
                    f"#### 🔌 Ligação nos Pinos do Relé Automotivo (12V/24V):\n"
                    f"• **Pino 85:** Conecte ao Fio Marrom do GV50CG e ao **Ânodo** do diodo 1N4004 (lado sem faixa)\n"
                    f"• **Pino 86:** Conecte ao **Pós-Chave (+12V/+24V)** e ao **Cátodo** do diodo 1N4004 (lado com a faixa prateada/branca)\n"
                    f"• **Pinos 30 e 87A (Normal Fechado):** Interrompem o fio positivo da bomba de combustível ou ignição (uma ponta cortada no 30 e a outra no 87A)\n"
                    f"• **Pino 87:** Deixe isolado (não utilizado)"
                )
            elif is_st340:
                return (
                    f"### 📘 Esquema de Bloqueio e Relé - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST340UR (Págs. 10, 11)\n\n"
                    f"> 👉 **Fio de Bloqueio:** Fio Verde (Saída 1 - GND máx 200mA)\n\n"
                    f"#### 🔌 Ligação nos Pinos do Relé (Corte na Bomba):\n"
                    f"• **Pino 85:** Conecte ao Fio Verde (Saída 1) do ST340UR\n"
                    f"• **Pino 86:** Conecte ao **Pós-Chave (+12V/+24V)**\n"
                    f"• **Pinos 30 e 87A:** Em série nas duas pontas do fio cortado da bomba de combustível\n"
                    f"• **Pino 87:** Deixe isolado"
                )
            else:
                return (
                    f"### 📘 Esquema de Bloqueio e Relé - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech (Págs. 11, 14)\n\n"
                    f"> 👉 **Fio de Bloqueio:** Fio Laranja (Saída 1 - GND máx 300mA a 500mA)\n\n"
                    f"#### 🔌 Ligação nos Pinos do Relé (Corte na Bomba):\n"
                    f"• **Pino 85:** Conecte ao Fio Laranja (Saída 1) do rastreador\n"
                    f"• **Pino 86:** Conecte ao **Pós-Chave (+12V/+24V)**\n"
                    f"• **Pinos 30 e 87A:** Em série nas duas pontas do fio cortado da bomba de combustível (lógica normal 1)\n"
                    f"• **Pino 87:** Deixe isolado"
                )

        # ---------------------------------------------------------------------
        # 3. PERGUNTAS DE PÓS-CHAVE / IGNIÇÃO / LINHA 15
        # ---------------------------------------------------------------------
        if tem_ignicao and not tem_dpa and not tem_led:
            if is_gv50:
                return (
                    f"### 📘 Pós-Chave / Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Queclink GV50CG (Págs. 10, 11)\n\n"
                    f"> 👉 **Fio de Ignição:** Fio Branco (Pino 5 - IGN)\n\n"
                    f"• **Tipo de Sinal:** Trigger positivo de ignição (ativo de 5.0V a 32V / inativo 0 a 3V ou circuito aberto).\n"
                    f"• **Onde Conectar:** Conecte à linha 15 (pós-chave do veículo), onde há +12V ou +24V com a ignição ligada e 0V com a chave desligada.\n"
                    f"• **Dica de Instalação:** Teste com multímetro durante a partida do motor para certificar-se de que a linha 15 não corta a alimentação temporariamente."
                )
            elif is_st340:
                return (
                    f"### 📘 Pós-Chave / Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST340UR (Pág. 10)\n\n"
                    f"> 👉 **Fio de Ignição:** Fio Branco (Entrada 1 ou Ignição - GND/VCC)\n\n"
                    f"• **Faixa de Tensão Suportada:** 8 a 30 Vcc.\n"
                    f"• **Onde Conectar:** Conecte à linha 15 (pós-chave do veículo).\n"
                    f"• **Dica Técnica:** No ST340UR a Entrada 1 vem pré-configurada de fábrica para detectar nível de pós-chave positivo."
                )
            elif is_st8300:
                return (
                    f"### 📘 Pós-Chave / Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST8300 / ST4305 (Pág. 11)\n\n"
                    f"> 👉 **Fio de Ignição:** Fio Azul (Pino 3 do chicote principal de 8 vias)\n\n"
                    f"• **Faixa de Tensão:** 8 a 33 Vcc.\n"
                    f"• **Onde Conectar:** Conecte diretamente à linha 15 do comutador de partida.\n"
                    f"• **Atenção:** No ST8300/ST4305 a ignição é o Fio Azul (o Fio Branco é a Entrada 1 para botão antifurto/pânico GND)."
                )
            elif is_st310:
                return (
                    f"### 📘 Pós-Chave / Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech Linha ST310 (Págs. 10, 11)\n\n"
                    f"> 👉 **Fio de Ignição:** Fio Branco (Entrada 1 - Ignição GND/VCC)\n\n"
                    f"• **Faixa de Tensão:** 8 a 30 Vcc.\n"
                    f"• **Onde Conectar:** Conecte à linha 15 (pós-chave do veículo)."
                )
            elif is_st8310:
                return (
                    f"### 📘 Pós-Chave / Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST8310UM (Pág. 11)\n\n"
                    f"> 👉 **Fio de Ignição:** Fio Branco (Entrada 1 ou Ignição - GND/VCC)\n\n"
                    f"• **Faixa de Tensão:** 8 a 33 Vcc.\n"
                    f"• **Onde Conectar:** Conecte à linha 15 (pós-chave do veículo)."
                )

        # ---------------------------------------------------------------------
        # 4. PERGUNTAS DE ALIMENTAÇÃO POSITIVA / TENSÃO / FUSÍVEL
        # ---------------------------------------------------------------------
        if tem_positivo and not tem_sim:
            if is_gv50:
                return (
                    f"### 📘 Alimentação Elétrica (Positivo / VCC) - {nome_modelo}\n"
                    f"**Manual Oficial:** Queclink GV50CG (Págs. 6, 10)\n\n"
                    f"> 👉 **Fio Positivo:** Fio Vermelho (Pino 2 - VIN)\n\n"
                    f"• **Tensão de Operação Suportada:** **DC 9V a 90V Contínua** (ampla compatibilidade com motos, veículos 12V, caminhões 24V e máquinas pesadas até 90V).\n"
                    f"• **Proteção Obrigatória:** Instale porta-fusível com fusível de **2A a 5A** o mais próximo possível do borne da bateria.\n"
                    f"• **Bateria Backup Interna:** Li-Polymer 190mAh / 3.7V recarregável com chave física interna liga/desliga."
                )
            else:
                return (
                    f"### 📘 Alimentação Elétrica (Positivo / VCC) - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech (Pág. 11)\n\n"
                    f"> 👉 **Fio Positivo:** Fio Vermelho (Alimentação 8V a 30V/33V DC)\n\n"
                    f"• **Tensão de Operação:** Compatível com veículos 12V e 24V.\n"
                    f"• **Proteção Obrigatória:** Instale fusível de proteção de **5A** na linha positiva próximo à bateria do veículo."
                )

        # ---------------------------------------------------------------------
        # 5. PERGUNTAS DE NEGATIVO / GND / TERRA
        # ---------------------------------------------------------------------
        if tem_negativo:
            pino_str = " (Pino 3 - GND)" if is_gv50 else " (Pino 2)"
            return (
                f"### 📘 Aterramento / Negativo (GND) - {nome_modelo}\n\n"
                f"> 👉 **Fio Negativo:** Fio Preto{pino_str}\n\n"
                f"• **Como Conectar:** Conecte diretamente ao chassi metálico limpo (sem tinta, verniz ou ferrugem) ou no borne negativo da bateria.\n"
                f"• **Recomendação:** Um aterramento deficiente causa oscilações e reinicializações inesperadas no rastreador."
            )

        # ---------------------------------------------------------------------
        # 6. PERGUNTAS DE BOTÃO DE PÂNICO / ENTRADAS ANALÓGICAS
        # ---------------------------------------------------------------------
        if tem_panico:
            if is_gv50:
                return (
                    f"### 📘 Botão de Pânico / Entrada Analógica - {nome_modelo}\n"
                    f"**Manual Oficial:** Queclink GV50CG (Págs. 10, 11)\n\n"
                    f"> 👉 **Fio de Pânico / Entrada 1:** Fio Laranja (Pino 1 - AIN / IN1)\n\n"
                    f"• **Função Entrada Digital (Pânico):** Trigger negativo GND (ativo de 0 a 0.8V, inativo circuito aberto). Ligue entre o Fio Laranja e o terra através do botão normalmente aberto.\n"
                    f"• **Função Entrada Analógica (AIN):** Medição de tensão analógica na faixa de 0 a 16V DC."
                )
            elif is_st8300:
                return (
                    f"### 📘 Botão de Pânico e Entrada Analógica - {nome_modelo}\n\n"
                    f"• **Botão de Pânico:** Fio Branco (Entrada 1 - ativa por terra GND).\n"
                    f"• **Entrada Analógica ADC:** Fio Verde (Entrada 3 - mede tensão de 0 a 30V com resolução 0.01V)."
                )

        # ---------------------------------------------------------------------
        # 7. PERGUNTAS DE ORIENTAÇÃO DA ANTENA (QUECLINK GV50CG)
        # ---------------------------------------------------------------------
        if tem_antena and is_gv50:
            return (
                f"### 📡 Posicionamento e Antena - {nome_modelo}\n"
                f"**Manual Oficial:** Queclink GV50CG (Págs. 14, 15)\n\n"
                f"> 👉 **Orientação Obrigatória:** O lado liso sem LEDs possui a gravação **`THIS SIDE TOWARDS SKY`** (Este lado voltado para o céu).\n\n"
                f"• **Direção:** Este lado DEVE ficar apontado para cima (em direção ao céu) para receber o sinal dos satélites GNSS.\n"
                f"• **Superfícies:** Não instale o equipamento diretamente sob latarias ou vigas metálicas. Painéis plásticos, borrachas e carpetes não afetam o sinal.\n"
                f"• **Fixação:** Utilize fita dupla face 3M automotiva ou abraçadeiras plásticas firmes presas ao chicote fixo do veículo."
            )

        # ---------------------------------------------------------------------
        # 8. PERGUNTAS DE CHIP SIM CARD E CHAVE DE BATERIA (QUECLINK GV50CG)
        # ---------------------------------------------------------------------
        if tem_sim and is_gv50:
            return (
                f"### 📱 Instalação do SIM Card e Chave da Bateria - {nome_modelo}\n"
                f"**Manual Oficial:** Queclink GV50CG (Págs. 8, 9)\n\n"
                f"• **Tamanho do Chip:** Utiliza padrão **Micro-SIM (3FF)** com os contatos dourados voltados para baixo.\n"
                f"• **Chave da Bateria (Power Switch):**\n"
                f"  - De fábrica para transporte, a chave vem em **OFF**.\n"
                f"  - **Mude a chave para a posição ON** após inserir o chip para ativar a bateria de backup interna de 190mAh.\n"
                f"• **Abertura do Gabinete:** Solte os parafusos traseiros, monte o chip e aperte os parafusos firmemente para garantir a vedação contra poeira e umidade."
            )

        # ---------------------------------------------------------------------
        # 9. PERGUNTAS DE CALIBRAÇÃO DPA
        # ---------------------------------------------------------------------
        if tem_dpa:
            if is_st340:
                return (
                    f"### 🎯 Procedimento de Calibração DPA por Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST340UR (Pág. 12)\n\n"
                    f"> 👉 **Sequência de Ignições:** Ligue e desligue a ignição **7 vezes** (as primeiras 6 em 'meia chave', na 7ª ligue o motor).\n\n"
                    f"• **Sinalização:** Os LEDs piscarão rapidamente a cada 0.5 segundos confirmando o modo calibração.\n"
                    f"• **Condução do Veículo:** Dirija a mais de 10 km/h e execute:\n"
                    f"  1. **3 freadas normais**\n"
                    f"  2. **3 acelerações normais**\n"
                    f"  3. **3 curvas normais**\n"
                    f"• **Conclusão:** Os LEDs voltam ao padrão normal quando a calibração do acelerômetro é concluída."
                )
            elif is_st8310:
                return (
                    f"### 🎯 Procedimento de Calibração DPA por Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST8310UM (Pág. 12)\n\n"
                    f"> 👉 **Sequência:** Ligue a ignição **8 vezes seguidas** (mantendo ligada na 8ª).\n\n"
                    f"• **Sinalização:** LEDs piscam a 0.5s.\n"
                    f"• **Percurso:** Dirija >10 km/h realizando 3 freadas, 3 curvas e 3 acelerações normais."
                )
            elif is_st8300:
                return (
                    f"### 🎯 Procedimento de Calibração DPA por Ignição - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST8300 / ST4305 (Págs. 14, 15)\n\n"
                    f"> 👉 **Sequência:** Realize **7 desligamentos da chave (OFF)** e ligue na 8ª (OFF>ON>...OFF(7)>ON(8)).\n\n"
                    f"• **Sinalização:** LEDs piscam a cada 0.5s.\n"
                    f"• **Percurso:** Dirija a >10 km/h com 3 freadas, 3 curvas e 3 acelerações normais."
                )

        # ---------------------------------------------------------------------
        # 10. PERGUNTAS DE SENHA SYNCTRAK
        # ---------------------------------------------------------------------
        if tem_senha:
            return (
                f"### 🔑 Senha Padrão de Fábrica - Synctrak\n\n"
                f"> 👉 A senha de fábrica padrão da Suntech no software Synctrak é: **`st5656`**\n\n"
                f"• Para conectar via USB/Serial, instale o driver CP210x, selecione a porta COM correta e baud rate 115200 bps."
            )

        # ---------------------------------------------------------------------
        # 11. PERGUNTAS DE RESISTÊNCIA À ÁGUA / IP67
        # ---------------------------------------------------------------------
        if tem_ip67:
            if is_st340:
                return (
                    f"### 🛡️ Proteção IP67 Contra Água e Poeira - {nome_modelo}\n"
                    f"**Manual Oficial:** Suntech ST340UR (Págs. 1, 9)\n\n"
                    f"> 👉 **Sim! O ST340UR possui certificação estanque IP67 total.**\n\n"
                    f"• Possui carcaça vedada com anel de borracha de silicone e fechamento por 6 parafusos.\n"
                    f"• É resistente a jatos d'água fortes, chuva torrencial e poeira intensa, sendo ideal para motos, quadriciclos, barcos e jet skis."
                )
            elif is_st310:
                return (
                    f"### 🛡️ Proteção IP67 na Linha ST310\n\n"
                    f"• **ST310U, ST310UC2 e ST310ULC:** Possuem certificação **IP67** estanque.\n"
                    f"• **ST310UC:** **NÃO possui proteção IP67**, devendo ser instalado estritamente no interior protegido do painel."
                )

        # ---------------------------------------------------------------------
        # 12. PERGUNTAS DO CHICOTE COMPLETO
        # ---------------------------------------------------------------------
        if is_gv50 and ("chicote" in q or "fios" in q or "pinagem" in q or eh_pergunta_completa):
            return (
                f"### 📘 Chicote Completo de 5 Vias - {nome_modelo}\n"
                f"**Manual Oficial:** Queclink GV50CG (Págs. 10, 11)\n\n"
                f"| Pino | Cor do Fio | Sinal / Função | Descrição Técnica |\n"
                f"| :--- | :--- | :--- | :--- |\n"
                f"| **1** | Fio Laranja | **AIN / IN1** | Entrada Analógica (0-16V) ou Digital negativa (Pânico) |\n"
                f"| **2** | Fio Vermelho | **VIN** | Alimentação Positiva Contínua (DC 9V a 90V) |\n"
                f"| **3** | Fio Preto | **GND** | Negativo / Terra (Chassi) |\n"
                f"| **4** | Fio Marrom | **OUT** | Saída Digital Open-Drain (Bloqueio máx 150mA, requer diodo) |\n"
                f"| **5** | Fio Branco | **IGN** | Entrada de Ignição / Pós-Chave (5.0V a 32V) |\n\n"
                f"> 💡 **Nota Técnica:** Lembre-se de utilizar diodo de roda livre 1N4004 na bobina do relé ao conectar o Fio Marrom."
            )

        # ---------------------------------------------------------------------
        # 13. FALLBACK: RESPOSTA RESUMIDA E ESTRUTURADA DO CHUNK PRINCIPAL
        # ---------------------------------------------------------------------
        cabecalho = f"### 📘 {principal['title']}\n"
        cabecalho += f"**Aparelho:** `{nome_modelo}` | **Referência no Manual Oficial:** {principal['pages']}\n\n"
        corpo = principal["content"].strip()

        return f"{cabecalho}{corpo}"

    def _gerar_sugestoes_contextuais(self, intencao: str, aparelho: str) -> List[str]:
        """Gera perguntas de continuação contextualizadas"""
        dev = aparelho.upper()
        if "GV50" in dev or "QUECLINK" in dev:
            return [
                "Como ligar o relé com diodo 1N4004 no Queclink GV50CG?",
                "Qual a cor do fio de ignição no Queclink GV50CG?",
                "O que significa o LED celular verde piscando rápido no GV50CG?"
            ]
        elif intencao in ("fios_chicote", "bloqueio_rele"):
            return [
                f"Como ligar o relé de 5 pinos para corte na bomba no {aparelho}?",
                f"Qual o fio de pós-chave no {aparelho}?",
                "Qual a pinagem do chicote do Queclink GV50CG?"
            ]
        elif intencao == "calibracao_dpa":
            return [
                f"Como calibrar o DPA por ignição no {aparelho}?",
                "O que significam os LEDs piscando a cada 0.5s?",
                "Quantas ignições para calibrar o ST340UR?"
            ]
        elif intencao == "leds_diagnostico":
            return [
                "O que significa o LED vermelho piscando 4 vezes?",
                "O que significa o LED verde piscando rápido no GV50CG?",
                "O que significa o LED azul piscando 7 vezes (SIM card)?"
            ]
        else:
            return [
                "Qual o fio de pós-chave no ST340UR?",
                "Como ligar o relé com diodo no Queclink GV50CG?",
                "Qual a senha de fábrica padrão do Synctrak?"
            ]


# Instância Singleton global do cérebro neural
neural_brain = NeuralManualBrain()
