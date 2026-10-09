from typing import List, Dict, Any

CHICOTES_DATA = [
    {
        "id": 1,
        "titulo": "Chicote Nº 1",
        "fios": [
            {"cor_nome": "Vermelho", "cor_hex": "#EF4444", "funcao": "Positivo (+)", "tipo": "positivo"},
            {"cor_nome": "Verde", "cor_hex": "#10B981", "funcao": "Pós-Chave (Ign)", "tipo": "poschave"},
            {"cor_nome": "Azul", "cor_hex": "#3B82F6", "funcao": "Negativo (-)", "tipo": "negativo"}
        ]
    },
    {
        "id": 2,
        "titulo": "Chicote Nº 2",
        "fios": [
            {"cor_nome": "Vermelho", "cor_hex": "#EF4444", "funcao": "Positivo (+)", "tipo": "positivo"},
            {"cor_nome": "Branco", "cor_hex": "#F3F4F6", "texto_escuro": True, "funcao": "Pós-Chave (Ign)", "tipo": "poschave"},
            {"cor_nome": "Preto", "cor_hex": "#1F2937", "funcao": "Negativo (-)", "tipo": "negativo"}
        ]
    },
    {
        "id": 3,
        "titulo": "Chicote Nº 3",
        "fios": [
            {"cor_nome": "Verde", "cor_hex": "#10B981", "funcao": "Positivo (+)", "tipo": "positivo"},
            {"cor_nome": "Preto", "cor_hex": "#1F2937", "funcao": "Negativo (-)", "tipo": "negativo"},
            {"cor_nome": "Branco", "cor_hex": "#F3F4F6", "texto_escuro": True, "funcao": "Pós-Chave (Ign)", "tipo": "poschave"}
        ]
    },
    {
        "id": 4,
        "titulo": "Chicote Nº 4",
        "fios": [
            {"cor_nome": "Verde", "cor_hex": "#10B981", "funcao": "Positivo (+)", "tipo": "positivo"},
            {"cor_nome": "Marrom", "cor_hex": "#92400E", "funcao": "Negativo (-)", "tipo": "negativo"},
            {"cor_nome": "Azul", "cor_hex": "#3B82F6", "funcao": "Pós-Chave (Ign)", "tipo": "poschave"}
        ]
    },
    {
        "id": 5,
        "titulo": "Chicote Nº 5",
        "fios": [
            {"cor_nome": "Vermelho", "cor_hex": "#EF4444", "funcao": "Positivo (+)", "tipo": "positivo"},
            {"cor_nome": "Preto", "cor_hex": "#1F2937", "funcao": "Negativo (-)", "tipo": "negativo"},
            {"cor_nome": "Verde", "cor_hex": "#10B981", "funcao": "Pós-Chave (Ign)", "tipo": "poschave"}
        ]
    }
]

LEDS_DATA = {
    "azul": {
        "nome": "LED Azul (GPRS / Comunicação)",
        "cor": "blue",
        "itens": [
            {"piscadas": 2, "titulo": "Erro no Servidor", "descricao": "Parâmetros errados, servidor fechado ou rede barrada.", "gravidade": "warning"},
            {"piscadas": 3, "titulo": "Erro na Comunicação", "descricao": "Parâmetros errados, SIM bloqueado, rede barrada ou sinal fraco.", "gravidade": "warning"},
            {"piscadas": 4, "titulo": "Sem Rede GPRS", "descricao": "Antena desconectada ou quebrada.", "gravidade": "danger"},
            {"piscadas": 5, "titulo": "PIN Bloqueado", "descricao": "SIM PIN habilitado no chip.", "gravidade": "danger"},
            {"piscadas": 6, "titulo": "Sem Conexão", "descricao": "Sinal GPRS fraco ou oscilante.", "gravidade": "warning"},
            {"piscadas": 7, "titulo": "Sem SIM Card", "descricao": "Chip não inserido, mal encaixado ou danificado.", "gravidade": "danger"}
        ]
    },
    "vermelho": {
        "nome": "LED Vermelho (GPS)",
        "cor": "red",
        "itens": [
            {"piscadas": 1, "titulo": "Normal / Sinal OK", "descricao": "GPS funcionando e sincronizado corretamente.", "gravidade": "success"},
            {"piscadas": 2, "titulo": "Sem Sinal GPS", "descricao": "Buscando sinal, mau posicionamento ou falha na conexão da antena.", "gravidade": "warning"},
            {"piscadas": 4, "titulo": "Erro no Chipset / Antena", "descricao": "Antena desconectada ou conector danificado.", "gravidade": "danger"}
        ]
    }
}

class GuiasService:
    @staticmethod
    def get_cabos() -> List[Dict[str, Any]]:
        return CHICOTES_DATA

    @staticmethod
    def get_leds() -> Dict[str, Any]:
        return LEDS_DATA

