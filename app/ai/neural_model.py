# -*- coding: utf-8 -*-
"""
Motor Neural de Compreensão e Atendimento dos Manuais Suntech
Implementa:
- Normalização Semântica Canônica e Expansão de Sinônimos
- Invariância à Ordem das Palavras (Bag-of-Canonical-Tokens + Shuffled Augmentation)
- Rede Neural Multicamadas (Multi-Layer Perceptron - MLP) para classificação de intenção
- Mapeamento Denso de Espaço Semântico Latente (LSA / SVD)
- Detector Neural de Aparelhos (ST4305, ST8300, ST8300R/H, ST340UR, Linha ST310, ST8310UM, ST8210)
- Ranqueador Híbrido Neural (Similaridade Cosseno + Sobreposição Canônica Jaccard)
- Sintetizador Especialista com Resposta Direta Imediata e Referências Oficiais
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
    "st8210": "mod_st8210"
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
    # Substitui expressões compostas em ordem decrescente de tamanho
    for k, v in sorted(SYNONYMS_CANONICAL.items(), key=lambda x: len(x[0]), reverse=True):
        texto_norm = re.sub(r'\b' + re.escape(k) + r'\b', v, texto_norm)
    tokens = {t for t in texto_norm.split() if len(t) > 1 and t not in STOPWORDS_BR}
    return sorted(list(tokens))


def gerar_representacao_invariante(texto: str) -> str:
    """
    Gera representação dual:
    Frase normalizada + Coleção ordenada de tokens canônicos únicos.
    Garante que 'st340ur pos chave fio cor' e 'qual a cor do fio pos chave no st340ur'
    gerem representações semânticas fortemente alinhadas na Rede Neural.
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

    # Intenção: antifurto
    ("como funciona o antifurto por ignicao", "antifurto"),
    ("como desarmar o antifurto com botao segredo", "antifurto"),
    ("antifurto por sensor de porta", "antifurto"),
    ("tempo para acionar o botao antifurto 1050", "antifurto"),
    ("quanto tempo o antifurto espera antes de bloquear", "antifurto"),
    ("como desativar o antifurto segurando 10 segundos", "antifurto"),
    ("bipe da sirene ao ativar antifurto", "antifurto"),

    # Intenção: jornada_trabalho
    ("como configurar a jornada de trabalho", "jornada_trabalho"),
    ("horario de jornada fuso utc", "jornada_trabalho"),
    ("como liberar hora extra no st8300", "jornada_trabalho"),
    ("comando cmd esn 06 76 hora extra", "jornada_trabalho"),
    ("bloquear veiculo fora do horario de trabalho", "jornada_trabalho"),
    ("alerta de violacao de jornada alert id 188", "jornada_trabalho"),
    ("dias da semana jornada nyyyyyn", "jornada_trabalho"),
    ("parametro 1638 inicio e 1639 fim", "jornada_trabalho"),
    ("hora extra comando ativar desativar", "jornada_trabalho"),

    # Intenção: modo_idle
    ("como acionar saida em modo idle ocioso", "modo_idle"),
    ("veiculo ligado parado modo ocioso", "modo_idle"),
    ("tempo limite idle parametro 1615", "modo_idle"),
    ("acionamento da saida no modo ocioso 1668", "modo_idle"),
    ("buzzer quando o carro ficar ligado sem andar", "modo_idle"),

    # Intenção: comandos
    ("qual o comando para reiniciar o aparelho", "comandos"),
    ("comando reboot e reset", "comandos"),
    ("comando statusreq pegar posicao", "comandos"),
    ("como ativar a saida 1 enable1", "comandos"),
    ("como apagar a memoria interna eraseall", "comandos"),
    ("ajustar hodometro setodometer", "comandos"),
    ("ajustar horimetro sethmeter", "comandos"),
    ("solicitar imsi e iccid do chip", "comandos"),
    ("link do google maps setgooglemap", "comandos"),
    ("lista de comandos do rastreador", "comandos"),

    # Intenção: comandos_rs232
    ("comandos pela serial rs232", "comandos_rs232"),
    ("sttreq comando serial", "comandos_rs232"),
    ("como habilitar saida 1 pela rs232", "comandos_rs232"),
    ("cmd 1610009909 04 1", "comandos_rs232"),
    ("comunicacao rs232 modo normal e rfid", "comandos_rs232"),

    # Intenção: diferencas_modelos
    ("qual a diferenca entre st310u e st310uc", "diferencas_modelos"),
    ("o st310ulc tem jammer", "diferencas_modelos"),
    ("diferenca entre st8300 e st8300r", "diferencas_modelos"),
    ("qual modelo e a prova d agua ip67", "diferencas_modelos"),
    ("diferenca de memoria da linha st310", "diferencas_modelos"),
    ("qual a diferenca do st8310um para o st8210", "diferencas_modelos"),
    ("comparativo entre os modelos de rastreadores", "diferencas_modelos"),
    ("st310u st310ulc comparacao diferenca", "diferencas_modelos"),

    # Intenção: especificacoes
    ("quais sao as bandas 4g do st8300", "especificacoes"),
    ("o st340ur tem leitor de ibutton", "especificacoes"),
    ("quantos motoristas cabem no st340ur", "especificacoes"),
    ("consumo de bateria e modo sleep", "especificacoes"),
    ("qual a tensao de alimentacao suportada", "especificacoes"),
    ("o st8310um tem 1-wire ou rs232", "especificacoes"),
    ("especificacoes tecnicas gerais", "especificacoes"),
    ("o st340ur aguenta agua e chuva", "especificacoes"),
    ("o aparelho e a prova d agua ip67", "especificacoes"),
    ("pode molhar o rastreador", "especificacoes"),
    ("dimensoes e tamanho do aparelho", "especificacoes"),
    ("st340ur agua resistente chuva ip67", "especificacoes"),

    # Intenção: cercas
    ("como criar cerca circular", "cercas"),
    ("como desenhar cerca poligonal", "cercas"),
    ("configuracao de cercas virtuais no synctrak", "cercas"),
    ("limite de velocidade dentro da cerca", "cercas"),
    ("ativar saida ao entrar na cerca circular", "cercas"),
    ("geo id da cerca como configurar", "cercas"),
    ("quantas cercas virtuais suporta", "cercas"),

    # Intenção: chip_sim
    ("como colocar o chip no st4305", "chip_sim"),
    ("qual o tamanho do chip no st340ur", "chip_sim"),
    ("qual o tamanho do chip no st8310um nano sim", "chip_sim"),
    ("como abrir a tampa do st310 para colocar chip", "chip_sim"),
    ("cuidado com a borracha de vedacao do chip", "chip_sim"),
    ("o micro sim deve ficar com metal para baixo", "chip_sim"),

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
    Data Augmentation: Para cada exemplo, cria variações invertidas e embaralhadas
    de palavras para treinar a rede a ser 100% agnóstica à ordem dos termos.
    """
    expandidas = []
    for frase, intent in samples:
        expandidas.append((frase, intent))
        palavras = frase.split()
        if len(palavras) > 2:
            # Versão invertida
            expandidas.append((" ".join(reversed(palavras)), intent))
            # Versão tokens ordenados
            expandidas.append((" ".join(sorted(palavras)), intent))
            # Versão canônica ordenada
            tokens_c = extrair_tokens_canonicos(frase)
            if tokens_c:
                expandidas.append((" ".join(tokens_c), intent))
    return expandidas


class NeuralManualBrain:
    """Rede Neural e Motor de Inteligência Artificial para os Manuais Suntech"""

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

        # 1. Prepara base de conhecimento e conjuntos de tokens canônicos
        chunk_texts = []
        self.chunk_token_sets = []
        for c in KNOWLEDGE_CHUNKS:
            raw_text = f"{c['title']} {c['summary']} {c['content']} {' '.join(c['keywords'])}"
            inv_text = gerar_representacao_invariante(raw_text)
            chunk_texts.append(inv_text)
            self.chunk_token_sets.append(set(extrair_tokens_canonicos(raw_text)))

        # 2. Expansão com data augmentation das amostras de treino
        amostras_expandidas = expandir_amostras_invariantes(BASE_TRAINING_SAMPLES)
        sample_texts = [gerar_representacao_invariante(s[0]) for s in amostras_expandidas]
        sample_labels = [s[1] for s in amostras_expandidas]

        todos_textos = chunk_texts + sample_texts

        # 3. Vetorizador Híbrido N-gram com sublinear TF
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            analyzer="word",
            sublinear_tf=True,
            min_df=1
        )
        tfidf_matrix = self.vectorizer.fit_transform(todos_textos)

        # 4. Projeção Latente Densa (Neural Embedding Layer)
        n_features = min(64, tfidf_matrix.shape[1] - 1)
        self.svd = TruncatedSVD(n_components=n_features, random_state=42)
        dense_space = self.svd.fit_transform(tfidf_matrix)

        self.chunk_embeddings = dense_space[:len(KNOWLEDGE_CHUNKS)]

        # 5. Treinamento do Classificador Neural Multicamadas (MLP)
        X_train = dense_space[len(KNOWLEDGE_CHUNKS):]
        y_train = np.array(sample_labels)

        self.mlp = MLPClassifier(
            hidden_layer_sizes=(128, 64),
            activation='relu',
            solver='adam',
            alpha=0.0005,
            max_iter=600,
            random_state=42,
            early_stopping=False
        )
        self.mlp.fit(X_train, y_train)

        # 6. Salva modelo compilado
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

        if "st4305" in q:
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

        # 1. Transforma query na representação dual invariante
        q_invariante = gerar_representacao_invariante(query)
        q_tfidf = self.vectorizer.transform([q_invariante])
        q_dense = self.svd.transform(q_tfidf)

        # 2. Predição Neural Multicamadas (MLP)
        probs = self.mlp.predict_proba(q_dense)[0]
        max_idx = np.argmax(probs)
        pred_intent = self.mlp.classes_[max_idx]
        intent_confidence = float(probs[max_idx])

        # 3. Similaridade Cosseno no Espaço Latente Denso
        norm_q = np.linalg.norm(q_dense)
        if norm_q > 0:
            similaridades = np.dot(self.chunk_embeddings, q_dense.T).flatten() / (
                np.linalg.norm(self.chunk_embeddings, axis=1) * norm_q + 1e-9
            )
        else:
            similaridades = np.zeros(len(KNOWLEDGE_CHUNKS))

        # 4. Ranqueamento Combinado (Similaridade + MLP + Overlap Canônico + Aparelho)
        scored_chunks = []
        for i, chunk in enumerate(KNOWLEDGE_CHUNKS):
            sim_score = float(similaridades[i])
            bonus_intent = 0.35 if chunk["topic"] == pred_intent else 0.0

            # Bônus de Sobreposição Canônica Jaccard (Agnóstico à ordem)
            overlap_ratio = 0.0
            if query_tokens and self.chunk_token_sets:
                inter = query_tokens.intersection(self.chunk_token_sets[i])
                overlap_ratio = len(inter) / len(query_tokens)

            bonus_device = 0.0
            if aparelho_detectado:
                dev_norm = normalizar_texto(aparelho_detectado)
                chunk_family_norm = normalizar_texto(chunk["device_family"])
                if dev_norm in chunk_family_norm or chunk_family_norm in dev_norm:
                    bonus_device = 0.45
                elif "geral" in chunk_family_norm:
                    bonus_device = 0.15
                else:
                    bonus_device = -0.20

            final_score = (
                (sim_score * 0.35) +
                (bonus_intent * 0.25) +
                (overlap_ratio * 0.20) +
                (bonus_device * 0.20)
            )
            scored_chunks.append((final_score, chunk))

        # Ordenação decrescente por relevância final
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
        """Gera a resposta completa estruturada a partir da análise da Rede Neural"""
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
                    "Não encontrei informações correspondentes nos manuais dos aparelhos "
                    "Suntech com base na sua pergunta. Por favor, especifique o modelo do rastreador "
                    "(ex: **ST340UR**, **ST4305/ST8300**, **ST310U/UC**, **ST8310UM**) e o tópico "
                    "(ex: chicote, calibração DPA, LEDs, relé de corte, comandos ou jornada de trabalho)."
                ),
                "intencao": intencao,
                "aparelho_detectado": aparelho,
                "confianca": confianca,
                "fontes": [],
                "sugestoes": [
                    "Qual a pinagem do chicote do ST340UR?",
                    "Como calibrar o DPA por ignição no ST8300?",
                    "Quais as diferenças entre ST310U e ST310ULC?"
                ],
                "tempo_ms": tempo_ms
            }

        chunk_principal = chunks[0]
        fontes = [f"{c['device_family']} ({c['pages']})" for c in chunks]

        # Montagem inteligente da resposta estruturada com resposta direta
        resposta_md = self._sintetizar_conteudo(query, chunk_principal, chunks, aparelho, intencao)
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

    def _extrair_resposta_direta(self, query: str, aparelho: Optional[str], intencao: str) -> Optional[str]:
        """
        Extrai resposta direta e inequívoca para a dúvida do instalador,
        apresentando imediatamente o resultado antes dos detalhes completos.
        """
        q = normalizar_texto(query)
        dev = (aparelho or "").upper()

        # Dúvida de Ignição / Pós-Chave
        if "ignicao" in q or "pos" in q or "chave" in q:
            if "st340" in q or "ST340" in dev:
                return "👉 **Resposta Direta:** No **ST340UR**, o pós-chave / ignição é o **Fio Branco** (Entrada 1 ou Ignição - GND/VCC)."
            elif "st8300" in q or "st4305" in q or "ST8300" in dev or "ST4305" in dev:
                return "👉 **Resposta Direta:** No **ST4305 / ST8300 / ST8300H / ST8300R**, a ignição física é o **Fio Azul** (8 a 33 Vcc)."
            elif "st310" in q or "ST310" in dev:
                return "👉 **Resposta Direta:** Na linha **ST310 (U/UC/UC2/ULC)**, a ignição física é o **Fio Branco** (Entrada 1 - GND/VCC)."
            elif "st8310" in q or "st8210" in q or "ST8310" in dev:
                return "👉 **Resposta Direta:** No **ST8310UM / ST8210**, a ignição física é o **Fio Branco** (Entrada 1 ou Ignição - GND/VCC)."

        # Dúvida de Relé de 5 Pinos / Bomba
        if "rele" in q or "5 pinos" in q or "bomba" in q:
            return (
                "👉 **Resposta Direta (Relé 5 Pinos):**\n"
                "• **Pino 30 e 87A:** Ligados em série nas duas pontas do fio cortado da bomba (lógica normal 1)\n"
                "• **Pino 85:** Conectado ao **Fio Laranja** do rastreador (Saída 1 GND de bloqueio)\n"
                "• **Pino 86:** Conectado ao **Pós-Chave (12V/24V)**"
            )

        # Dúvida de Calibração DPA por Ignição (Quantas ignições?)
        if "calibrar" in q or "dpa" in q or "ignicoes" in q:
            if "st8310" in q or "ST8310" in dev:
                return "👉 **Resposta Direta:** No **ST8310UM**, a calibração por ignição requer **8 ignições ON** (mantendo ligado na 8ª). LEDs piscam a 0.5s. Dirija >10km/h com 3 freadas, 3 acelerações e 3 curvas normais."
            elif "st340" in q or "ST340" in dev:
                return "👉 **Resposta Direta:** No **ST340UR**, ligue e desligue a ignição **7 vezes** (as 6 primeiras 'meia chave', na 7ª chave total). LEDs piscam a 0.5s. Dirija >10km/h com 3 freadas, 3 acelerações e 3 curvas normais."
            elif "st8300" in q or "st4305" in q or "ST8300" in dev:
                return "👉 **Resposta Direta:** No **ST8300 / ST4305**, realize a sequência de **7 ignições OFF** e ligue na 8ª (OFF>ON>...OFF(7)>ON(8)). LEDs piscam a 0.5s. Dirija >10km/h com 3 freadas, acelerações e curvas normais."

        # Dúvida de Piscadas de LEDs
        if "4" in q and ("led" in q or "pisca" in q or "vermelho" in q):
            return "👉 **Resposta Direta:** **LED Vermelho piscando 4 vezes** indica **Erro no Chipset de GPS ou Erro na Antena de GPS** (antena desconectada ou conector danificado)."
        if "2" in q and ("led" in q or "pisca" in q or "vermelho" in q):
            return "👉 **Resposta Direta:** **LED Vermelho piscando 2 vezes** indica **Sem Sinal GPS** (buscando satélites, mau posicionamento sob metal ou sem visada direta)."
        if "7" in q and ("led" in q or "pisca" in q or "azul" in q or "sim" in q):
            return "👉 **Resposta Direta:** **LED Azul piscando 7 vezes** indica **Sem SIM Card** (chip não inserido, mal encaixado ou conector quebrado)."

        # Dúvida de Senha Synctrak
        if "senha" in q and "synctrak" in q:
            return "👉 **Resposta Direta:** A senha de fábrica padrão da Suntech no software Synctrak é **`st5656`**."

        # Dúvida de Resistência à Água / IP67
        if "agua" in q or "chuva" in q or "molhar" in q or "ip67" in q:
            if "st340" in q or "ST340" in dev:
                return "👉 **Resposta Direta:** **Sim!** O **ST340UR** possui certificação **IP67** com carcaça estanque e borracha de vedação com 6 parafusos, resistente a chuva e jatos d'água, ideal para motos, jet skis e barcos."
            if "st310" in q or "ST310" in dev:
                return "👉 **Resposta Direta:** **ST310U, ST310UC2 e ST310ULC possuem IP67**. Já o modelo **ST310UC NÃO possui certificação IP67** e deve ser instalado somente no interior do painel de veículos fechados."

        return None

    def _sintetizar_conteudo(
        self,
        query: str,
        principal: Dict[str, Any],
        todos_chunks: List[Dict[str, Any]],
        aparelho: Optional[str],
        intencao: str
    ) -> str:
        """Produz texto em Markdown rico, técnico e diretamente aplicável"""
        nome_aparelho = aparelho if aparelho else principal["device_family"]

        cabecalho = f"### 📘 {principal['title']}\n"
        cabecalho += f"**Aparelho:** `{nome_aparelho}` | **Referência no Manual Oficial:** {principal['pages']}\n\n"

        # Extração de Resposta Direta em Destaque
        resposta_direta = self._extrair_resposta_direta(query, aparelho, intencao)
        bloco_direto = ""
        if resposta_direta:
            bloco_direto = f"> {resposta_direta}\n\n"

        corpo = principal["content"].strip()

        # Adiciona complemento somente se for exatamente do mesmo tópico ou boas práticas de instalação
        complemento = ""
        if len(todos_chunks) > 1 and todos_chunks[1]["id"] != principal["id"]:
            segundo = todos_chunks[1]
            if segundo["topic"] == principal["topic"]:
                complemento = f"\n\n---\n#### 🔍 Informações Adicionais ({segundo['title']}):\n{segundo['content'].strip()}"
            elif principal["topic"] in ("fios_chicote", "instalacao_eletrica", "bloqueio_rele") and segundo["topic"] == "instalacao_eletrica":
                complemento = f"\n\n---\n#### 🔍 Boas Práticas de Instalação ({segundo['title']}):\n{segundo['content'].strip()}"

        rodape = (
            "\n\n> 💡 **Nota Técnica Suntech:** Lembre-se sempre de utilizar fusível de proteção (5A) "
            "no fio de alimentação VCC e validar as medições de tensão com multímetro antes de finalizar a emenda."
        )

        return cabecalho + bloco_direto + corpo + complemento + rodape

    def _gerar_sugestoes_contextuais(self, intencao: str, aparelho: str) -> List[str]:
        """Gera perguntas de continuação contextualizadas"""
        if intencao in ("fios_chicote", "bloqueio_rele"):
            return [
                f"Como ligar o relé de 5 pinos para corte na bomba de combustível?",
                f"Qual a função do fio branco (ignição) no {aparelho}?",
                f"Onde conectar a sirene ou buzzer no {aparelho}?"
            ]
        elif intencao == "calibracao_dpa":
            return [
                f"Como calibrar o DPA por comando no Synctrak?",
                f"Quantas ignições são necessárias para calibrar o DPA no {aparelho}?",
                f"O que significa os LEDs piscando a cada 0.5s?"
            ]
        elif intencao == "leds_diagnostico":
            return [
                "O que significa o LED vermelho piscando 4 vezes?",
                "O que significa o LED azul piscando 3 vezes (comunicação)?",
                "Como testar se o chip SIM card está conectado e com dados?"
            ]
        elif intencao == "jornada_trabalho":
            return [
                "Como calcular o fuso horário UTC na jornada de trabalho?",
                "Qual comando SMS/GPRS para liberar hora extra no veículo?",
                "Como configurar o alerta de violação de jornada (ALERT 188)?"
            ]
        elif intencao == "diferencas_modelos":
            return [
                "Quais modelos da linha ST310 possuem proteção estanque IP67?",
                "Qual a diferença do ST8300R para o ST8300 comum?",
                "O modelo ST310ULC possui função de bloqueio por Jammer?"
            ]
        else:
            return [
                f"Qual a pinagem completa do chicote do {aparelho}?",
                f"Qual a senha de fábrica padrão para conectar no Synctrak?",
                f"Como ligar o bloqueio na bomba de combustível com relé?"
            ]


# Instância Singleton global do cérebro neural
neural_brain = NeuralManualBrain()
