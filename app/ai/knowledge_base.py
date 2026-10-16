# -*- coding: utf-8 -*-
"""
Base de Conhecimento Especializada dos Manuais Suntech
Compilação estruturada e exaustiva dos manuais:
- Suntech ST4305 / ST8300 / ST8300R / ST8300H
- Suntech ST340UR
- Suntech Linha ST310 (ST310U, ST310UC, ST310UC2, ST310ULC)
- Suntech ST8310UM / ST8210
"""

from typing import List, Dict, Any

KNOWLEDGE_CHUNKS: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. LINHA ST4305 / ST8300 / ST8300R / ST8300H
    # =========================================================================
    {
        "id": "st4305_st8300_geral",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "especificacoes",
        "title": "Visão Geral e Especificações Técnicas (ST4305, ST8300, ST8300R, ST8300H)",
        "keywords": ["st4305", "st8300", "st8300r", "st8300h", "4g", "lte", "gsm", "especificacoes", "bateria", "tensao", "memoria", "ip"],
        "pages": "Págs. 1, 5, 6, 7",
        "summary": "Dispositivos híbridos de rastreamento com GPS e 4G/2G para gestão de frotas e telemetria avançada.",
        "content": """
O ST4305, ST8300, ST8300R e ST8300H são rastreadores de alta tecnologia com posicionamento GPS e comunicação celular híbrida:
- ST4305: LTE Cat M1 / NB-IoT (Bandas 1 [2100MHz], 3 [1800MHz], 5 [850MHz], 28 [700MHz]) + GPRS 2G (850/900/1800/1900MHz).
- ST8300 / ST8300R / ST8300H: LTE Cat 1 (Bandas 1, 3, 5, 7 [2600MHz], 28 [700MHz]) + GPRS 2G.
- Dimensões: 90 x 58 x 26 mm | Peso: 115g (com cabo).
- Tensão de Operação: DC 8V a 33V (compatível com veículos 12V e 24V).
- Bateria Backup interna: 3.6V, Ni-MH 450mAh.
- Consumo Típico: 40mA a 50mA. Modo Sleep < 5mA @12V (ST8300) / < 7mA (ST4305). Deep Sleep < 3mA @12V (ST8300) / < 4mA (ST4305).
- Capacidade de Memória: 10.000 posições FIFO.
- Entradas e Saídas: 3 Entradas digitais configuráveis. No ST4305/ST8300/ST8300H são 3 saídas digitais (GND max 500mA). No ST8300R são 2 saídas digitais (GND max 500mA).
- Comunicação Externa: 1 porta serial RS232 e interface 1-Wire (para iButton ou sensor de temperatura DS28EA00).
- Servidores Padrão do Fabricante:
  * AGPS (GPS Assistido): http://agps.stdobrasil.com.br
  * Manutenção/FOTA: scuti.stdobrasil.com.br na porta 9000
- Homologado pela ANATEL.
"""
    },
    {
        "id": "st4305_st8300_chicote",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "fios_chicote",
        "title": "Chicote e Pinagem de Fios - ST8300 / ST8300H / ST4305",
        "keywords": ["chicote", "pinagem", "fios", "cores", "st4305", "st8300", "st8300h", "ignicao", "positivo", "negativo", "saidas", "entradas", "1-wire"],
        "pages": "Pág. 11",
        "summary": "Pinagem detalhada do chicote principal de 8 vias e chicote auxiliar RS232 de 4 vias.",
        "content": """
Chicote Principal de 8 Vias (ST8300, ST8300H, ST4305):
- Fio Vermelho: Positivo (+) (Alimentação 8 a 33 Vcc)
- Fio Preto: Negativo (-) GND
- Fio Azul: Ignição (8 a 33 Vcc - detecção de pós-chave)
- Fio Branco: Entrada 1 (GND - configurável, ex: botão antifurto/pânico)
- Fio Amarelo: 1-Wire (Leitor iButton DS9092+ ou Sensor de Temperatura DS28EA00)
- Fio Verde: Entrada 3 ADC (Entrada Analógica 0 a 30V com resolução 0.01V)
- Fio Cinza: Entrada 4 (GND)
- Fio Laranja: Saída 1 (GND / Max 300mA - bloqueio/relé)
- Fio Marrom: Saída 2 (GND / Max 300mA - buzzer/sirene)
- Fio Roxo: Saída 3 (GND / Max 300mA)

Chicote Secundário de 4 Vias (Serial RS232):
- Fio Branco: RS232 RX
- Fio Verde: RS232 TX
- Fio Preto: Terra (GND)
- Fio Marrom: Alimentação 4,5V para equipamento externo (Corrente máxima 200mA).
"""
    },
    {
        "id": "st8300r_diferencas_chicote",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "fios_chicote",
        "title": "Diferenças de Pinagem do Modelo ST8300R (Áudio / Voz)",
        "keywords": ["st8300r", "chicote", "audio", "microfone", "speaker", "alto-falante", "voz", "chamada", "diferenca"],
        "pages": "Pág. 12",
        "summary": "Chicote do ST8300R inclui conexões para microfone e alto-falante (speaker) e 2 saídas digitais.",
        "content": """
O modelo ST8300R possui suporte a comunicação de voz bidirecional (microfone e speaker). Por isso, sua pinagem é diferente:
Chicote Principal do ST8300R:
- Fio Vermelho: Positivo (+) (8 a 33 Vcc)
- Fio Preto: Negativo (-) GND
- Fio Azul: Ignição (8 a 33 Vcc)
- Fio Branco: Entrada 1 (GND)
- Fio Amarelo: 1-Wire (iButton ou Sensor de Temperatura)
- Fio Verde: Entrada 3 ADC (0 a 30V)
- Fio Cinza: RS232 TX
- Fio Laranja: Saída 1 (GND / Max 300mA)
- Fio Marrom: Saída 2 (GND / Max 300mA)
- Fio Roxo: RS232 RX

Chicote de 4 Vias de Áudio (ST8300R):
- Fio Branco: Microfone
- Fio Verde: Speaker + (Alto-falante positivo)
- Fio Preto: Terra
- Fio Marrom: Speaker - (Alto-falante negativo)

Observação: O ST8300R conta com 2 saídas digitais (ao invés de 3 saídas dos modelos ST8300/ST4305).
"""
    },
    {
        "id": "st4305_st8300_sim_chip",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "chip_sim",
        "title": "Instalação do Chip SIM Card no ST4305 / ST8300 / ST8300R / ST8300H",
        "keywords": ["chip", "sim card", "micro sim", "como colocar", "inserir chip", "bateria backup", "3ff"],
        "pages": "Págs. 8, 9",
        "summary": "Procedimento de inserção do Micro SIM Card (3FF) com contatos metálicos para baixo.",
        "content": """
Como inserir o cartão SIM no ST4305 / ST8300 / ST8300R / ST8300H:
1. Pressione a tampa traseira para baixo e deslize para ter acesso ao compartimento da bateria e chip.
2. Desloque a bateria interna para fora com cuidado.
3. Insira o Micro SIM Card (formato 3FF) no slot conforme a orientação da imagem do manual.
Atenção Crítica:
- O SIM Card Micro (3FF) deve ser colocado com a base de metal para baixo, encostando na placa para garantir a conectividade.
- É contraindicado o uso de adaptadores de chip ou formatos cortados manualmente, pois podem amassar os pinos internos e causar perda de garantia.
"""
    },
    {
        "id": "st4305_st8300_leds",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "leds_diagnostico",
        "title": "Diagnóstico de LEDs (Vermelho GPS e Azul GPRS/LTE) - ST4305 / ST8300",
        "keywords": ["led", "leds", "piscadas", "led vermelho", "led azul", "diagnostico", "gps", "gprs", "lte", "piscando"],
        "pages": "Págs. 13, 14",
        "summary": "Tabela de piscadas dos LEDs indicador GPS e indicador celular/GPRS/LTE.",
        "content": """
LED VERMELHO - GPS:
- 1 Piscada: Normal (Sinal GPS fixado e operando normalmente).
- 2 Piscadas: Sem Sinal GPS (Buscando sinal, mau posicionamento ou barreira de rede temporária).
- 4 Piscadas: Erro no Chipset ou Erro na Antena de GPS.

LED AZUL - GPRS / LTE:
- 1 Piscada: Normal (Conectado à rede celular e transmitindo).
- 2 Piscadas: Erro no Servidor (IP/porta incorretos, servidor fechado ou bloqueado).
- 3 Piscadas: Erro na Comunicação GPRS/CAT-M1 (Parâmetros errados, SIM card sem dados ou sinal fraco).
- 4 Piscadas: Sem Rede GPRS (Antena WWAN desconectada ou quebrada).
- 5 Piscadas: PIN Bloqueado (O PIN do SIM Card está ativado e precisa ser desbloqueado ou informado).
- 6 Piscadas: Sem Conexão com a Rede (Sinal de operadora fraco ou sem cobertura).
- 7 Piscadas: Sem SIM Card (Chip ausente, mal encaixado ou soquete quebrado).
- 8 Piscadas: Cartão SIM Bloqueado (Necessário código PUK).
"""
    },
    {
        "id": "st4305_st8300_calibracao_dpa",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "calibracao_dpa",
        "title": "Calibração DPA (Driver Pattern Analysis - Análise de Condução)",
        "keywords": ["dpa", "calibracao", "analise motorista", "ignicao", "freada", "aceleracao", "curva", "como calibrar", "start dpa calibration", "7 ignicoes"],
        "pages": "Págs. 25, 57, 58",
        "summary": "Dois métodos de calibração: via comando do configurador ou manualmente pela chave de ignição.",
        "content": """
O DPA analisa a condução do motorista detectando acelerações bruscas, curvas acentuadas e frenagens bruscas (G-Force).

Método 1: Calibração DPA por Comando
1. No parâmetro Acelerômetro, ative a função DPA (parâmetro 1910 = 01).
2. Envie o comando: 'Start DPA Calibration'.
3. Os LEDs GPS e GPRS piscarão a cada 0.5s continuamente indicando modo calibração.
4. Dirija o veículo a mais de 10 km/h e realize:
   * 3 freadas normais;
   * 3 acelerações normais;
   * 3 curvas normais.
5. Envie o comando: 'Stop DPA Calibration'.
6. Os LEDs voltam ao ritmo fixo/normal e o rastreador enviará o evento de calibração concluída.

Método 2: Calibração DPA por Ignição (Sem Computador)
1. Certifique-se de que a ignição está configurada como Física (fio azul) e DPA (1910) está habilitado.
2. Realize uma sequência de 7 ignições OFF (cada ciclo em até 3 segundos):
   OFF (0) > ON > OFF (1) > ON > OFF (2) > ON > OFF (3) > ON > OFF (4) > ON > OFF (5) > ON > OFF (6) > ON > OFF (7) > ON (8) (manter ligado na 8ª).
3. Os LEDs GNSS e LTE piscarão a 0.5s continuamente.
4. Dirija acima de 10 km/h e realize 3 freadas, 3 acelerações e 3 curvas em ritmos normais.
5. Desligue a ignição para finalizar a calibração.
6. Os LEDs voltam ao estado normal e o evento é gerado.
"""
    },
    {
        "id": "st8300_jornada_trabalho",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "jornada_trabalho",
        "title": "Funcionalidade de Jornada de Trabalho (ST8300)",
        "keywords": ["jornada", "jornada de trabalho", "st8300", "horario", "hora extra", "bloqueio fora de horario", "fuso utc", "1630", "1637", "1638", "1639", "1640", "188"],
        "pages": "Págs. 59, 60",
        "summary": "Controle de horários permitidos de operação do veículo, fuso horário UTC, bloqueio e hora extra.",
        "content": """
A funcionalidade de Jornada de Trabalho (disponível no ST8300) permite controlar o uso do veículo por horários e dias da semana através do menu 'Config. Modos de Operação':
- Parâmetro 1630 (Jornada de Trabalho): Habilitar / Desabilitar.
- Parâmetro 1637 (Envio de posições apenas na Jornada): Quando habilitado, posições STT só são enviadas dentro da jornada de trabalho.
- Parâmetro 1638 (Início da Jornada): Faixa de 0h a 23h em fuso UTC.
  * ATENÇÃO AO FUSO: Em horário de Brasília (UTC -3), adicione 3 horas! Exemplo: para iniciar às 08:00, configure 8 + 3 = 11h.
- Parâmetro 1639 (Fim da Jornada): Faixa de 1h a 24h em fuso UTC. Exemplo: para encerrar às 17:00, configure 17 + 3 = 20h. Padrão: 24.
- Parâmetro 1640 (Dias da Semana): Padrão de 7 caracteres com 'Y' (trabalho) e 'N' (folga).
  * Exemplo de Segunda a Sexta: 'NYYYYYN' (Domingo folga, Seg a Sex trabalho, Sábado folga). Todos os dias: 'YYYYYYY'.
- Parâmetro 1631 (Delay para ignição após jornada): Minutos permitidos para acionamento único fora da jornada.
- Parâmetro 1632 (Ativação de saída): Escolha a saída digital para efetuar o bloqueio do veículo fora da jornada.
- Alerta de Violação de Jornada: Habilitar em Configuração de Alertas 2 -> Violação de Jornada de Trabalho (ALERT_ID 188).
- Comandos para Horas Extras:
  * Ativação de hora extra (permite uso após o horário): CMD;ESN;06;76
  * Desativação de hora extra (bloqueia o uso): CMD;ESN;06;77
"""
    },
    {
        "id": "st8300_saida_modo_idle",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "modo_idle",
        "title": "Ativação de Saída em Modo Idle / Ocioso (ST8300)",
        "keywords": ["idle", "modo idle", "ocioso", "veiculo parado ligado", "saida idle", "1615", "1668", "1669"],
        "pages": "Pág. 61",
        "summary": "Aciona uma saída configurada (como buzzer ou bloqueio) quando o veículo permanece ocioso em excesso.",
        "content": """
No ST8300 é possível acionar uma saída física quando o veículo fica ligado sem sair do lugar (Modo Idle / Ocioso):
- Acesse o menu 'Config. Modos de Operação'.
- Parâmetro 1615 (Tempo limite 1 em modo idle): Tempo em segundos para considerar tempo ocioso excedido e gerar alerta.
- Parâmetro 1668 (Ativação da saída modo Idle): Seleciona qual saída (Saída 1, 2 ou 3) será acionada quando o tempo limite 1 for atingido.
- Parâmetro 1669 (Tempo de Ativação da saída no modo Idle):
  * Se configurado como 0: A saída permanecerá ativada continuamente até o veículo sair do modo ocioso ou receber comando de desbloqueio.
  * Se configurado entre 1s e 43200s: A saída ficará ativada temporariamente pelo tempo programado em segundos.
"""
    },
    {
        "id": "st4305_st8300_comandos_rs232",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "comandos",
        "title": "Comandos pela Porta Serial RS232 - ST4305 / ST8300",
        "keywords": ["rs232", "comandos serial", "sttreq", "cmd", "habilitar saida serial", "reboot serial", "imobilizador serial"],
        "pages": "Pág. 21",
        "summary": "Protocolo e comandos ASCII aceitos pela interface RS232 do rastreador.",
        "content": """
Equipamentos externos conectados à RS232 podem solicitar dados e enviar comandos para o rastreador:
a) Requisitar dados de posição:
   Comando: CMD;1610009909;03;1 ou SttReq
   Resposta: Retorna mensagem de posição STT idêntica à enviada ao servidor.
b) Habilitar Saída 1:
   Comando: CMD;1610009909;04;1 -> Resposta: RES;1610009909;04;01
c) Desabilitar Saída 1:
   Comando: CMD;1610009909;04;02 -> Resposta: RES;1610009909;04;02
d) Habilitar Saída 2:
   Comando: CMD;1610009909;04;03 -> Resposta: RES;1610009909;04;03
e) Desabilitar Saída 2:
   Comando: CMD;1610009909;04;04 -> Resposta: RES;1610009909;04;04
f) Habilitar Saída 3:
   Comando: CMD;1610009909;04;09 -> Resposta: RES;1610009909;04;09
g) Desabilitar Saída 3:
   Comando: CMD;1610009909;04;10 -> Resposta: RES;1610009909;04;10
h) Reiniciar / Reboot do rastreador:
   Comando: CMD;1610009909;03;03 -> Resposta: RES;1610009909;03;03
i) Configurar tempos dos ciclos do imobilizador (T1 e T2 em segundos):
   Comando: CMD;4309999001;04;22;T1,T2
j) Iniciar ciclo do imobilizador:
   Comando: CMD;1610009909;04;23
"""
    },
    {
        "id": "st4305_st8300_comandos_gerais",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "comandos",
        "title": "Lista de Comandos Disponíveis no Configurador / GPRS / SMS",
        "keywords": ["comandos", "preset", "reboot", "reset", "statusreq", "enable1", "disable1", "eraseall", "setodometer", "sethmeter", "initcirclegeo"],
        "pages": "Págs. 39, 40, 41, 42",
        "summary": "Comandos de controle remoto, limpeza de memória, configuração de hodômetro e saídas.",
        "content": """
Lista de Comandos Disponíveis no ST4305/ST8300/ST8300R/ST8300H:
- Preset: Solicita as configurações atuais do rastreador.
- PresetP: Apresenta as configurações do parâmetro solicitado.
- StatusReq: Solicita a posição atual instantânea do dispositivo.
- Reset: Reinicia o dispositivo para padrões de fábrica.
- Reboot: Reinicia o equipamento sem perder as configurações gravadas.
- ReqVer: Solicita a versão de firmware (usar valor 1 no campo Option).
- Enable1 / Disable1: Ativa / Desativa a Saída 1.
- Enable2 / Disable2: Ativa / Desativa a Saída 2.
- Enable3 / Disable3: Ativa / Desativa a Saída 3.
- EraseAll: Apaga todas as posições armazenadas na memória interna do rastreador.
- SetOdometer: Ajusta/configura o hodômetro do veículo (em metros).
- SetHMeter: Ajusta/configura o horímetro do veículo (em minutos).
- InitCircleGeo: Apaga todas as cercas circulares cadastradas.
- InitAllPolygonGeo: Apaga todas as cercas poligonais cadastradas.
- ReqIMSI / ReqICCID: Requisita o IMSI e ICCID do chip SIM.
- ReqConNtw: Requisita em qual tecnologia de rede o módulo está conectado (0=GSM, 8=LTE Cat M1, 9=LTE Cat NB1).
- SetGoogleMap / ReqGoogleMap: Configura e consulta o link do Google Maps para localização via SMS.
- ActivateAntiTheft: Ativa manualmente a função antifurto.
"""
    },
    {
        "id": "st4305_st8300_antifurto",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "antifurto",
        "title": "Funcionamento do Antifurto por Ignição e por Porta",
        "keywords": ["antifurto", "botao segredo", "buzzer", "imobilizador", "porta", "ignicao", "tempo antifurto", "1050", "1051"],
        "pages": "Págs. 10, 11, 22, 23",
        "summary": "Lógica de funcionamento do sistema antifurto com botão segredo e sensor de porta.",
        "content": """
Antifurto por Ignição:
1. Ao desligar a ignição do veículo estacionado, inicia-se uma contagem automática de 20 segundos para armar o antifurto.
2. Quando a ignição for ligada novamente, o motorista precisa pressionar o botão segredo dentro do tempo estipulado no parâmetro 1050 (padrão recomendado: 30 segundos).
3. Se o botão segredo NÃO for pressionado no prazo, a saída configurada (imobilizador e/ou buzzer) é acionada e o evento de alerta é transmitido para a central após o tempo do parâmetro 1051 (padrão: 0s).
4. Para desarmar a qualquer momento: basta pressionar o botão segredo.

Antifurto por Sensor de Porta:
1. Requer uma entrada configurada como 'Sensor de porta' e outra como 'Botão Antifurto'.
2. Ao desligar a ignição e abrir/fechar a porta, após 20 segundos o módulo arma o antifurto e emite um breve bipe sonoro (se a saída estiver em Buzzer).
3. Ao reabrir a porta, o condutor deve pressionar o botão antifurto dentro do tempo do 'Intervalo para acionar o botão Antifurto'. Caso contrário, inicia o bloqueio de emergência.
"""
    },
    {
        "id": "st4305_st8300_synctrak_conexao",
        "device_family": "ST4305 / ST8300 / ST8300R / ST8300H",
        "topic": "configuracao_synctrak",
        "title": "Como Conectar ao Synctrak e Senha Padrão",
        "keywords": ["synctrak", "como configurar", "cabo usb", "senha", "st5656", "aberta", "fechada", "3001", "3002"],
        "pages": "Págs. 15, 51",
        "summary": "Procedimento obrigatório de ligação USB e senha de fábrica st5656.",
        "content": """
Procedimento para conexão via PC no software Synctrack©:
1. Remova a bateria backup do rastreador.
2. Conecte o cabo micro USB entre o rastreador e o computador.
3. Alimente o rastreador em uma fonte externa regulada de 12V ou 24V.
4. Abra o software Synctrack© e clique no botão 'Aberta'.
Senha Padrão do Synctrak:
- Senha de fábrica da Suntech: 'st5656'.
- Para alterar ou desabilitar: menu 'Change Password' (parâmetro 3000 habilitar/desabilitar, 3001 senha atual, 3002 nova senha).
- A senha deve ter no mínimo 6 dígitos e no máximo 18 dígitos.
"""
    },

    # =========================================================================
    # 2. SUNTECH ST340UR
    # =========================================================================
    {
        "id": "st340ur_geral",
        "device_family": "ST340UR",
        "topic": "especificacoes",
        "title": "Visão Geral e Especificações Técnicas - Suntech ST340UR",
        "keywords": ["st340ur", "ip67", "moto", "barco", "trator", "maquina", "especificacoes", "bateria", "rs232", "1-wire", "ibutton"],
        "pages": "Págs. 1, 4, 5, 6, 7",
        "summary": "Rastreador estanque IP67 ideal para motocicletas, jet skis, embarcações e máquinas pesadas.",
        "content": """
O ST340UR é um rastreador veicular fixo de alta resistência:
- Grau de Proteção: Case estanque IP67 (total proteção contra poeira e imersão temporária em água).
- Aplicações Recomendadas: Motocicletas, motos aquáticas (jet ski), embarcações, tratores, máquinas agrícolas e ambientes severos/hostis.
- Comunicação Celular: GSM/GPRS 2G Quadriband (850/900/1800/1900 MHz - módulo MTK 2503).
- Posicionamento GPS: Módulo MT3333, 36 canais, sensibilidade -165 dBm, CEP < 2.5m.
- Bateria Backup: Li-Ion 4.1V / 450mAh.
- Dimensões: 77 x 47 x 19.5 mm | Peso: 95g.
- Alimentação: 8 a 33 VDC. Consumo típico: 40mAh ~ 60mAh (Sleep < 6mAh, Deep Sleep ~ 2mAh).
- Entradas/Saídas: 2 entradas digitais e 1 saída digital (GND max 500mA).
- Interfaces: 1 porta Serial RS232 (teclados, leitor código de barras) e 1-Wire (iButton, suporta até 5.000 motoristas embarcados).
- Memória Interna: 2.000 posições.
- Cercas Virtuais: 200 cercas circulares embarcadas com limite de velocidade.
- Homologado pela ANATEL.
"""
    },
    {
        "id": "st340ur_chicote",
        "device_family": "ST340UR",
        "topic": "fios_chicote",
        "title": "Cores e Funções dos Fios do Chicote - ST340UR",
        "keywords": ["st340ur", "chicote", "fios", "cores", "pinagem", "vermelho", "preto", "branco", "amarelo", "verde", "marrom", "roxo", "laranja"],
        "pages": "Pág. 12",
        "summary": "Tabela completa de cores de fios e sinais do chicote de 8 condutores do ST340UR.",
        "content": """
Chicote de 8 Fios do Suntech ST340UR:
- Fio Vermelho: Positivo (+) (Alimentação 9 a 30 VDC - VCC com fusível de 5A)
- Fio Branco: Entrada 1 ou Ignição (GND/VCC - detecção de pós-chave)
- Fio Amarelo: Entrada 2 (GND - ex: botão de pânico ou sensor de porta)
- Fio Verde: RX (RS232 - comunicação de dados)
- Fio Marrom: TX (RS232 - comunicação de dados)
- Fio Roxo/Amarelo: 1-Wire (Leitor iButton Dallas)
- Fio Laranja: Saída 1 (GND - bloqueio / relé de corte)
- Fio Preto: Negativo (GND - terra na lataria)
"""
    },
    {
        "id": "st340ur_sim_card",
        "device_family": "ST340UR",
        "topic": "chip_sim",
        "title": "Como Inserir o Chip SIM Card no ST340UR (Vedação IP67)",
        "keywords": ["st340ur", "chip", "sim card", "micro sim", "vedacao", "parafusos", "tampa", "ip67"],
        "pages": "Pág. 8",
        "summary": "Passos para abrir a carcaça vedada por 6 parafusos e inserir o Micro SIM Card.",
        "content": """
Procedimento para inserção do chip no ST340UR:
1. Remova a tampa plástica desparafusando os 6 parafusos de fixação.
2. Posicione e insira o Micro SIM Card no soquete interno.
3. Certifique-se de que a borracha de vedação preta está devidamente encaixada na canaleta para preservar a vedação IP67.
4. Recoloque a tampa plástica e aperte firmemente os 6 parafusos de maneira uniforme.
"""
    },
    {
        "id": "st340ur_calibracao_dpa",
        "device_family": "ST340UR",
        "topic": "calibracao_dpa",
        "title": "Calibração DPA (Análise de Motorista) no ST340UR",
        "keywords": ["st340ur", "dpa", "calibracao", "7 vezes", "meia chave", "ignicao", "freadas", "aceleracoes", "curvas"],
        "pages": "Pág. 11",
        "summary": "Processo de calibração do sensor DPA através de 7 giros da ignição e trajeto de teste.",
        "content": """
Procedimento de Calibração DPA no ST340UR:
1. Ligar e desligar a ignição 7 vezes na sequência:
   On (1ª) – Off (2ª) – On (3ª) – Off (4ª) – On (5ª) – Off (6ª) – On (7ª).
   * IMPORTANTE: As seis primeiras ignições são apenas de 'meia chave' (acessório). Na sétima (7ª), gire a chave totalmente ligando a ignição.
2. Aguarde 5 segundos.
3. Os LEDs vermelho e azul piscarão ininterruptamente a cada 0,5 segundos.
4. Dirija o veículo normalmente em velocidade superior a 10 km/h:
   * Realize no mínimo 3 freadas normais;
   * Realize no mínimo 3 acelerações normais;
   * Realize no mínimo 3 curvas em ritmo considerado normal.
5. Desligue a ignição e ligue novamente.
6. Os LEDs voltam a piscar no ritmo padrão, confirmando a calibração com sucesso.
"""
    },
    {
        "id": "st340ur_instalacao_eletrica",
        "device_family": "ST340UR",
        "topic": "instalacao_eletrica",
        "title": "Guia Prático de Instalação Elétrica (Alimentação, Ignição e Terra) - ST340UR",
        "keywords": ["instalacao", "instalacao eletrica", "st340ur", "pos chave", "gnd", "vcc", "fusivel", "scotchlok", "emenda", "multimetro"],
        "pages": "Págs. 57, 58, 59, 60, 61, 62, 63",
        "summary": "Métodos práticos de medição com multímetro, derivação de cabos e instalação segura.",
        "content": """
Recomendações e Passo a Passo da Instalação Elétrica:
Atenção: A Suntech recomenda obrigatoriamente a utilização de fusível de 5A na alimentação VCC para proteção contra curto-circuito.

1. Alimentação Positiva (VCC - Fio Vermelho):
   - Fio geralmente vermelho de maior bitola, localizado na caixa de fusíveis ou comutador.
   - Medição: Ponta vermelha do multímetro no fio e ponta preta no terra (GND da lataria). Deve indicar 12V ou 24VDC com ignição ligada ou desligada.
   - Métodos de Conexão: Conector original do veículo (Caso 1), Conector Scotchlok 3M (Caso 2), ou desencape dividindo o condutor em duas metades com isolamento e cinta plástica (Caso 3).

2. Ignição / Pós-Chave (Fio Branco):
   - Localizado no tambor de ignição ou caixa de fusíveis.
   - Medição com multímetro: Ignição ligada = 12V ou 24V; Ignição desligada = 0V.

3. Negativo (GND - Fio Preto):
   - Deve ser retirado em parafuso específico de aterramento fixado diretamente na lataria do veículo.
   - Teste: Ponta vermelha no VCC e preta no parafuso; deve acusar 12V ou 24VDC.

4. Acabamento:
   - Toda a fiação deve ser revestida com espaguete corrugado/isolante e fita isolante de alta qualidade. Fixe o chicote do rastreador ao chicote original com cintas plásticas, longe de partes móveis como articuladores de pedais ou limpador de para-brisa.

5. Antena de GPS:
   - Deve ser posicionada sob o painel, em local oculto, com a inscrição GPS voltada para o céu e NUNCA embaixo de superfícies metálicas que bloqueiem os satélites.
"""
    },
    {
        "id": "st340ur_bloqueio_rele",
        "device_family": "ST340UR",
        "topic": "instalacao_eletrica",
        "title": "Esquema de Ligação do Bloqueio com Relé de 5 Pinos (Bomba de Combustível)",
        "keywords": ["bloqueio", "rele", "5 pinos", "bomba de combustivel", "corte", "30", "87a", "87", "85", "86", "esquema"],
        "pages": "Págs. 64, 65",
        "summary": "Ligação correta dos pinos 30, 87a, 85 e 86 do relé automotivo de bloqueio.",
        "content": """
Esquema de Ligação do Bloqueio Automotivo (Relé de 5 Pinos na Bomba de Combustível):
Corte o fio positivo da bomba de combustível ou da ignição. As duas pontas cortadas serão ligadas ao relé:
- Pino 30 do relé: Conectado a uma das pontas do fio cortado.
- Pino 87A do relé: Conectado à outra ponta do fio cortado (quando a lógica de saída estiver configurada como 1 / normal, contato normalmente fechado NF).
  * (Obs: se utilizar lógica invertida 0, use o pino 87).
- Pino 85 do relé: Conectado ao Fio Laranja do rastreador (Saída 1 configurada como bloqueio/imobilizador, acionamento por GND).
- Pino 86 do relé: Conectado ao Pós-Chave (Ignição 12V / 24VDC).

Esquema de Ligação da Sirene / Buzzer:
- Fio positivo da sirene (+) ligado ao 12/24VDC.
- Fio negativo da sirene (-) ligado à saída do rastreador (configurada como Buzzer).
"""
    },
    {
        "id": "st340ur_comandos",
        "device_family": "ST340UR",
        "topic": "comandos",
        "title": "Comandos Disponíveis no ST340UR",
        "keywords": ["st340ur", "comandos", "statusreq", "reset", "preset", "ackemerg", "enable1", "disable1", "reqver", "setgooglemap", "reqgooglemap"],
        "pages": "Págs. 49, 50, 51, 52",
        "summary": "Comandos de consulta, teste de saída, hodômetro, horímetro e link de mapa.",
        "content": """
Comandos Principais do ST340UR:
- StatusReq: Solicita a posição atual instantânea.
- Reset: Retorna o equipamento às configurações de fábrica.
- Preset: Solicita a configuração embarcada atual.
- AckEmerg: Desativa o estado de emergência quando o módulo estiver transmitindo em emergência.
- Enable1 / Disable1: Habilita / Desabilita a Saída 1 (aciona ou cancela bloqueio).
- ReqIMSI / ReqICCID: Requisita o IMSI e o ICCID do chip SIM.
- ReqVer: Requisita a versão de hardware e firmware do rastreador.
- EraseAll: Apaga todas as posições salvas na memória interna e reinicia contadores.
- InitDist: Inicializa/zera o odômetro.
- SetHMeter: Configura o valor do horímetro (valor em minutos).
- SetOdometer: Configura o odômetro (valor em metros).
- SetGoogleMap: Define o formato do link do Google Maps.
- ReqGoogleMap: Requisita o formato do link do Google Maps. O link é enviado para o smartphone via SMS ao enviar o comando 'Where are you'.
- ReqShortTest: Ativa a saída digital por 30 segundos para teste de bancada.
- ReqTest: Ativa a saída por 1 minuto para teste de bancada.
- ImproveBatteryLife (0 desabilita, 1 habilita): Otimiza a vida útil da bateria backup quando a alimentação principal for desconectada.
"""
    },

    # =========================================================================
    # 3. LINHA ST310 (ST310U / ST310UC / ST310UC2 / ST310ULC)
    # =========================================================================
    {
        "id": "st310_diferencas_modelos",
        "device_family": "Linha ST310 (U / UC / UC2 / ULC)",
        "topic": "diferencas_modelos",
        "title": "Comparativo e Diferenças Cruciais entre os Modelos ST310 (U, UC, UC2, ULC)",
        "keywords": ["st310", "st310u", "st310uc", "st310uc2", "st310ulc", "diferencas", "comparativo", "qual a diferenca", "entradas", "ip67", "chip", "jammer"],
        "pages": "Págs. 4, 5, 7, 13",
        "summary": "Tabela comparativa detalhada de carcaça IP67, chicote, tipo de chip, entradas e limitações de cada modelo.",
        "content": """
Comparativo Completo da Linha ST310 (Suntech 2G):
1. ST310U:
   - Grau de Proteção: Case IP67 (resistente à água e poeira).
   - Entradas / Saídas: 2 Entradas digitais e 1 Saída digital.
   - Chicote: 50 cm com acabamento externo.
   - Tipo de SIM Card: SIM Card Padrão (Mini-SIM grande).
   - Memória: 1.000 STT, 50 ALT/EVT, 50 EMG.
   - Recursos: Detecção de Jammer, Antifurto por ignição e porta, Acelerômetro 3 eixos.

2. ST310UC:
   - Grau de Proteção: NÃO possui certificação IP67 (uso interno em painel de carros/caminhões).
   - Entradas / Saídas: 1 Entrada digital e 1 Saída digital (NÃO possui Entrada 2).
   - Chicote: 30 cm sem acabamento.
   - Tipo de SIM Card: Nano SIM Card.
   - Memória: 1.000 STT, 50 ALT/EVT, 50 EMG.
   - Não suporta antifurto por porta (pois necessita de 2 entradas).

3. ST310UC2:
   - Grau de Proteção: Case IP67 (resistente à água e poeira).
   - Entradas / Saídas: 2 Entradas digitais e 1 Saída digital.
   - Chicote: 50 cm com acabamento.
   - Tipo de SIM Card: Nano SIM Card.
   - Memória: 1.000 STT, 50 ALT/EVT, 50 EMG.
   - Suporta todos os recursos, incluindo antifurto por porta e jammer.

4. ST310ULC (Versão Low-Cost):
   - Grau de Proteção: Case IP67.
   - Entradas / Saídas: 1 Entrada digital e 1 Saída digital (NÃO possui Entrada 2).
   - Chicote: 50 cm com acabamento.
   - Tipo de SIM Card: Nano SIM Card.
   - Memória Reduzida: 500 STT (metade dos outros modelos), 50 ALT/EVT, 50 EMG.
   - DIFERENÇAS CRÍTICAS DO ST310ULC:
     * NÃO possui funções de detecção de Jamming!
     * NÃO suporta a função Antifurto quando utilizada ignição física!
     * NÃO suporta Antifurto por sensor de porta.
"""
    },
    {
        "id": "st310_chicote",
        "device_family": "Linha ST310 (U / UC / UC2 / ULC)",
        "topic": "fios_chicote",
        "title": "Chicote e Cores dos Fios - Linha ST310",
        "keywords": ["st310", "chicote", "cores", "fios", "vermelho", "preto", "branco", "amarelo", "laranja", "ignicao st310"],
        "pages": "Pág. 13",
        "summary": "Identificação dos fios Positivo, Negativo, Entrada 1, Entrada 2 e Saída 1 da linha ST310.",
        "content": """
Chicote de Fios da Linha ST310:
- Fio Vermelho: Positivo (+) (Alimentação 8 a 33 VDC - VCC) -> Presente em todos (U, UC, UC2, ULC)
- Fio Preto: Negativo (-) (GND / Terra) -> Presente em todos
- Fio Branco: Entrada 1 (Ignição Física GND / VCC) -> Presente em todos
- Fio Amarelo: Entrada 2 (GND) -> Presente APENAS no ST310U e ST310UC2. (NÃO EXISTE no ST310UC e ST310ULC)
- Fio Laranja: Saída 1 (GND / Max 500mA - bloqueio ou buzzer) -> Presente em todos

Dimensões do Chicote:
- ST310U e ST310UC2 / ST310ULC: 50 cm com acabamento isolante.
- ST310UC: 30 cm sem acabamento.
"""
    },
    {
        "id": "st310_abrir_chip",
        "device_family": "Linha ST310 (U / UC / UC2 / ULC)",
        "topic": "chip_sim",
        "title": "Como Abrir o Case e Inserir o Chip na Linha ST310",
        "keywords": ["st310", "abrir case", "inserir chip", "travas", "borracha de vedacao", "trilho", "nano sim", "sim padrao"],
        "pages": "Págs. 6, 7, 8, 9, 10",
        "summary": "Instruções passo a passo para desmontar e remontar o case com vedação e trilhos guia.",
        "content": """
Procedimento para Inserir Chip na Linha ST310:
1. Solte as 4 travas laterais e desloque ligeiramente a tampa.
2. CUIDADO COM A VEDAÇÃO: Antes de soltar a tampa totalmente, segure a borracha de vedação para evitar que ela saia ou seja danificada. Caso saia, use uma pinça fina para reposicioná-la na canaleta.
3. Localize o slot na placa:
   - ST310U: SIM Card Padrão (grande).
   - ST310UC, ST310UC2 e ST310ULC: Nano SIM Card.
4. Conecte a bateria interna no conector da placa (Passos 4 e 5).
5. FECHAMENTO CORRETO: Antes de fechar, certifique-se de que a placa de circuito impresso está devidamente encaixada nos trilhos guia internos da tampa plástica.
6. Encaixe a borracha de vedação na tampa e pressione até que todas as 4 travas emitam clique de fechamento seguro.
"""
    },
    {
        "id": "st310_ignicao_config",
        "device_family": "Linha ST310 (U / UC / UC2 / ULC)",
        "topic": "configuracao_synctrak",
        "title": "Configuração da Ignição Física (Fio Branco) no Synctrak - Linha ST310",
        "keywords": ["st310", "ignicao fisica", "fio branco", "synctrak", "parametros de eventos", "nao usar linha de ignicao"],
        "pages": "Págs. 19, 20, 22",
        "summary": "Como habilitar a leitura de ignição física no fio branco no configurador da linha ST310.",
        "content": """
Como configurar a Ignição Física na linha ST310:
1. No Synctrak, vá até a aba 'Parâmetros de Eventos'.
2. No campo 'Ignição', selecione: 'Não usar linha de Ignição' (pois a opção 'Usar linha de Ignição' não é aplicável a estes modelos).
3. No campo 'Tipo de Entrada 1', selecione: 'Ignição'.
4. Desta forma, o Fio Branco passa a operar como sensor de ignição física (detectando 12V/24V como ligado e 0V como desligado).
5. Defina também os tempos de 'Tempo para entrada em modo repouso' (desligado) e 'Tempo para entrada em modo ativo' (ligado).
"""
    },
    {
        "id": "st310_battery_shutdown",
        "device_family": "Linha ST310 (U / UC / UC2 / ULC)",
        "topic": "bateria_consumo",
        "title": "Proteção de Bateria Backup (Battery Shutdown Parameter) - Linha ST310",
        "keywords": ["st310", "bateria backup", "desligamento", "battery shutdown", "tensao minima", "3.4v", "preservar bateria"],
        "pages": "Pág. 38",
        "summary": "Configuração para desligar o rastreador e proteger a bateria backup contra descarga profunda.",
        "content": """
Battery Shutdown Parameter (Proteção contra Descarga Total):
Este parâmetro é acionado quando a alimentação principal do veículo é desconectada ou cortada:
- 'Use low battery Shutdown':
  * Desabilitado: O dispositivo permanece ligado consumindo a bateria backup até esgotar totalmente.
  * Habilitado: Desliga o dispositivo com segurança quando a bateria do veículo está desconectada e a tensão da bateria de backup atinge o limite crítico.
- 'Low battery Threshold':
  * Limite de tensão para desligamento de proteção: de 3.4V a 3.8V (Recomendado: 3.4V).
"""
    },

    # =========================================================================
    # 4. SUNTECH ST8310UM / ST8210
    # =========================================================================
    {
        "id": "st8310um_geral",
        "device_family": "ST8310UM / ST8210",
        "topic": "especificacoes",
        "title": "Visão Geral e Especificações Técnicas - ST8310UM / ST8210",
        "keywords": ["st8310um", "st8210", "4g", "lte cat 1", "cat1-bis", "especificacoes", "ip67", "dimensoes", "memoria", "sem 1-wire", "sem rs232"],
        "pages": "Págs. 1, 4, 5, 6, 50",
        "summary": "Rastreador ultracompacto 4G LTE Cat 1 com redundância 2G, proteção IP67 e alta memória.",
        "content": """
O ST8310UM e o ST8210 são rastreadores veiculares compactos e modernos:
- Tecnologias de Comunicação:
  * ST8310UM: LTE Cat 1 (4G) com redundância para GSM/GPRS (2G). Bandas 4G: 1 (2100MHz), 3 (1800MHz), 5 (850MHz), 7 (2600MHz), 28 (700MHz).
  * ST8210: LTE Cat 1-Bis (4G).
- Dimensões Ultracompactas: 61.2 x 53.2 x 20.8 mm | Peso: apenas 76g.
- Grau de Proteção: IP67 (à prova d'água e poeira).
- Bateria Backup interna: Li-Íon 3.7V / 220mAh.
- Alimentação: DC 8V a 33VDC. Consumo típico: 30 a 50mA @12V (Sleep ~5mA, Deep Sleep ~3mA).
- Memória Interna: 10.000 posições FIFO.
- Cercas Virtuais: 999 cercas circulares e 30 cercas poligonais (de 3 a 70 pontos cada).
- SIM Card: Tipo Nano SIM (4FF).
- Entradas e Saídas: 2 Entradas digitais e 1 Saída digital (GND max 300mA).
- OBSERVAÇÃO IMPORTANTE: O ST8310UM NÃO possui recursos de 1-Wire (iButton/temperatura) nem interface RS232! Todas as configurações de 1-Wire e RS232 no Synctrak devem permanecer desmarcadas para este aparelho.
"""
    },
    {
        "id": "st8310um_chicote",
        "device_family": "ST8310UM / ST8210",
        "topic": "fios_chicote",
        "title": "Chicote e Pinagem de Fios - ST8310UM / ST8210",
        "keywords": ["st8310um", "st8210", "chicote", "pinagem", "fios", "vermelho", "preto", "branco", "amarelo", "laranja", "5 fios"],
        "pages": "Pág. 10",
        "summary": "Chicote simplificado de 5 fios do ST8310UM e ST8210.",
        "content": """
Chicote de 5 Fios do ST8310UM / ST8210:
- Fio Vermelho: Positivo (+) (8 a 30 VCC - alimentação principal, utilizar fusível 5A)
- Fio Preto: Negativo (-) GND (terra na lataria)
- Fio Branco: Entrada 1 ou Ignição (GND / VCC - pós-chave físico)
- Fio Amarelo: Entrada 2 (GND - botão de pânico ou sensor de porta)
- Fio Laranja: Saída 1 (GND / Corrente máxima 300mA - bloqueio/relé)

Observações do Modelo:
- Não possui Saída 2 nem Saída 3.
- Não possui Entrada 3 nem Entrada 4.
- Para usar o fio branco como ignição física, configure a Entrada 1 no Synctrak para 'Ignição'.
"""
    },
    {
        "id": "st8310um_calibracao_dpa",
        "device_family": "ST8310UM / ST8210",
        "topic": "calibracao_dpa",
        "title": "Calibração DPA no ST8310UM (8 Ignições ON)",
        "keywords": ["st8310um", "calibracao", "dpa", "8 ignicoes", "diferenca dpa", "freadas", "curvas", "aceleracoes"],
        "pages": "Pág. 53",
        "summary": "Sequência específica do ST8310UM: 8 ignições ON seguidas por teste de direção.",
        "content": """
Calibração DPA por Ignição no ST8310UM (Atenção à quantidade de ignições!):
1. Verifique se a Entrada 1 (fio branco) está configurada como Ignição e DPA (1910) está habilitado.
2. Realize a sequência de 8 IGNIÇÕES ON (contando pela ignição OFF, cada sequência em até 3 segundos):
   OFF > ON (1) > OFF > ON (2) > OFF > ON (3) > OFF > ON (4) > OFF > ON (5) > OFF > ON (6) > OFF > ON (7) > OFF > ON (8) (MANTER LIGADO NA 8ª).
3. Os LEDs GPS e GPRS piscarão a 0.5s continuamente.
4. Dirija o veículo em velocidade acima de 10 km/h e realize:
   * 3 freadas normais;
   * 3 acelerações normais;
   * 3 curvas normais.
5. Desligue a ignição para finalizar a calibração.
6. Os LEDs voltam a piscar no ritmo padrão normal e o evento de calibração concluída é gerado.

Calibração por Comando:
- Envie 'Start DPA Calibration' -> LEDs piscam 0.5s -> dirija > 10 km/h com 3 freadas, acelerações e curvas -> Envie 'Stop DPA Calibration'.
"""
    },
    {
        "id": "st8310um_jornada_trabalho",
        "device_family": "ST8310UM / ST8210",
        "topic": "jornada_trabalho",
        "title": "Jornada de Trabalho e Horas Extras no ST8310UM",
        "keywords": ["st8310um", "jornada", "jornada de trabalho", "horas extras", "1630", "1638", "1639", "188", "cmd;esn;06;76"],
        "pages": "Págs. 54, 55, 56",
        "summary": "Controle de horários de circulação com fuso horário UTC e comandos de liberação de horas extras.",
        "content": """
Jornada de Trabalho no ST8310UM:
- Parâmetro 1630: Habilita/Desabilita a função.
- Parâmetro 1637: Envio de posições (STT) apenas dentro do período da jornada.
- Parâmetro 1638: Horário de início em formato UTC (Brasília UTC-3: somar 3 horas. Ex: 08:00h da manhã -> 11h).
- Parâmetro 1639: Horário de término em formato UTC (Brasília UTC-3: somar 3 horas. Ex: 18:00h da tarde -> 21h).
- Parâmetro 1640: Dias da semana ('NYYYYYN' = Seg a Sex; 'YYYYYYY' = Todos os dias).
- Parâmetro 1631: Minutos permitidos para ligar o veículo fora da jornada.
- Parâmetro 1632: Saída digital para bloqueio do veículo fora do horário.
- Alerta de Violação de Jornada: Habilitar em Alertas 2 -> Violação de Jornada de Trabalho (ALERT_ID 188).
- Comandos de Hora Extra:
  * Ativação da hora extra: CMD;ESN;06;76
  * Desativação da hora extra: CMD;ESN;06;77
"""
    },
    {
        "id": "st8310um_nota_bateria_backup",
        "device_family": "ST8310UM / ST8210",
        "topic": "bateria_consumo",
        "title": "Alerta de Versão de Firmware - Falha de Bateria Interna no ST8310UM",
        "keywords": ["st8310um", "firmware", "versao 1.0.20", "parametro 1932", "bateria backup", "perfil de configuracao"],
        "pages": "Pág. 22",
        "summary": "Nota técnica sobre remoção do parâmetro 1932 a partir da versão de firmware 1.0.20.",
        "content": """
Nota Técnica de Firmware no ST8310UM:
- No ST8310UM versão 1.0.20 ou superior, o parâmetro 1932 (Falha na bateria interna / remoção de bateria backup) foi removido do perfil de configuração.
- Se você estiver atualizando ou carregando um perfil antigo em um aparelho com firmware recente, é necessário criar ou sincronizar um novo perfil de configuração sem esse campo para evitar incompatibilidade.
"""
    },

    # =========================================================================
    # 5. REGRAS DE INSTALAÇÃO ELÉTRICA E BOAS PRÁTICAS GERAIS (TODOS OS MODELOS)
    # =========================================================================
    {
        "id": "geral_instalacao_fusivel_seguranca",
        "device_family": "Geral / Todos os Modelos",
        "topic": "instalacao_eletrica",
        "title": "Aviso Crucial de Segurança: Fusível de 5A e Instalação Elétrica",
        "keywords": ["fusivel", "5a", "5 amperes", "seguranca", "curto circuito", "garantia", "todos aparelhos", "atencao"],
        "pages": "ST4305 pág. 62 | ST340UR pág. 57 | ST8310UM pág. 56",
        "summary": "Recomendação obrigatória expressa pelo fabricante Suntech em todos os manuais.",
        "content": """
ATENÇÃO IMPORTANTE DO FABRICANTE (SUNTECH DO BRASIL):
"A Suntech do Brasil não é responsável pela instalação elétrica nos veículos. Cada cliente tem seu padrão de instalação. Por isso recomendamos a utilização de fusível (5 A) na alimentação VCC para proteção do veículo em caso de curto-circuito causado pela instalação elétrica."

Boas práticas de instalação:
1. Sempre instale o porta-fusível com fusível de 5A na perna do fio positivo (vermelho), o mais próximo possível do ponto de derivação.
2. Certifique-se de que a emenda seja firme (utilizando Scotchlok 3M ou trança com solda/cinta plástica bem isolada).
3. Não conecte em fios que alimentem sistemas críticos de segurança do veículo (ex: módulo de injeção eletrônica direta, freios ABS ou airbags).
4. O aterramento (GND) deve ser feito diretamente na carcaça metálica (lataria) com terminal olhal e parafuso limpo de tinta.
"""
    },
    {
        "id": "geral_antena_gps_posicionamento",
        "device_family": "Geral / Todos os Modelos",
        "topic": "instalacao_eletrica",
        "title": "Posicionamento e Fixação Correta da Antena de GPS",
        "keywords": ["antena gps", "onde instalar", "posicionamento", "orientacao", "lataria", "painel", "parabrisa"],
        "pages": "ST340UR pág. 63 | ST310 pág. 56",
        "summary": "Como posicionar o rastreador e antena para evitar perda de sinal GPS.",
        "content": """
Fixação da Antena de GPS (ou Módulos com Antena Interna como ST310, ST340UR, ST8310UM):
1. Deve ser instalada sob o painel, em local não visível e de difícil acesso.
2. A face superior (com indicação 'THIS SIDE UP' ou etiqueta GPS) deve estar voltada para o céu.
3. NUNCA fixe o aparelho diretamente embaixo de vigas, chapas metálicas ou estruturas de aço, pois o metal cria uma Gaiola de Faraday e bloqueia a recepção de satélites GPS.
4. Mantenha distância de chicotes elétricos de alta corrente, relés e motores para evitar interferência eletromagnética (EMI).
"""
    },
    {
        "id": "geral_cercas_eletronicas",
        "device_family": "Geral / Todos os Modelos",
        "topic": "cercas",
        "title": "Cercas Virtuais (Circular e Poligonal) no Configurador Synctrak",
        "keywords": ["cerca", "cerca circular", "cerca poligonal", "geofence", "geo id", "raio", "limite de velocidade na cerca", "alerta de entrada", "alerta de saida", "buzzer"],
        "pages": "ST4305 Págs. 35-38 | ST340UR Págs. 47-48 | ST8310UM Págs. 36-39",
        "summary": "Como desenhar e configurar cercas circulares e poligonais com controle de velocidade e bloqueio.",
        "content": """
Configuração de Cercas Virtuais no Synctrak:

1. Cerca Eletrônica Circular:
   - Suporte: Até 999 cercas no ST8310UM, 200 no ST340UR / ST310, 30 no ST4305.
   - Como cadastrar:
     1. Na aba 'Cerca Eletrônica Circular', clique em 'Adicionar'.
     2. Escolha o 'GEO ID' (número da cerca).
     3. Selecione os alertas desejados: 'Alerta de entrada' e/ou 'Alerta de saída'.
     4. (Opcional) 'Ativar saída': Selecione a Saída (1 a 3) para acionar ao entrar na cerca (com opção de desativar ao sair ou manter acionada).
     5. (Opcional) 'Limite de velocidade na cerca' (0 a 200 km/h) e 'Buzzer para limite de velocidade'.
     6. Clique em 'Next / Próximo'.
     7. No mapa: clique com o BOTÃO ESQUERDO no centro da cerca (marcador vermelho).
     8. Clique com o BOTÃO DIREITO na borda externa para definir o raio (marcador azul).
     9. Clique em 'Enviar' para gravar a cerca no rastreador.

2. Cerca Eletrônica Poligonal (3 a 70 pontos):
   - Suporte: ST8300, ST4305, ST8310UM (até 30 cercas poligonais).
   - Como cadastrar:
     1. Na aba 'Cerca Eletrônica Poligonal', clique em 'Adicionar'.
     2. Defina o ID da cerca (1 a 30), alertas de entrada e saída, e limite de velocidade (KM/h).
     3. Clique em 'Próximo'.
     4. Com o BOTÃO ESQUERDO do mouse, clique nos pontos do mapa para desenhar o polígono.
     5. Clique em 'Enviar' para gravar no equipamento.
"""
    },
    # =========================================================================
    # 7. QUECLINK GV50CG (GSM / GPRS / LTE CAT 1 GNSS TRACKER)
    # =========================================================================
    {
        "id": "gv50cg_geral",
        "device_family": "Queclink GV50CG",
        "topic": "especificacoes",
        "title": "Visão Geral e Especificações Técnicas (Queclink GV50CG)",
        "keywords": ["queclink", "gv50cg", "gv50", "4g", "lte", "cat1", "cat 1", "gsm", "especificacoes", "tensao", "bateria", "9v a 90v", "antena", "anatel"],
        "pages": "Págs. 1, 5, 6, 7",
        "summary": "Micro rastreador GNSS e LTE Cat 1 com ampla faixa de tensão (9V a 90V) e antena interna de alto ganho.",
        "content": """
O Queclink GV50CG é um micro rastreador veicular de alta sensibilidade com tecnologia GNSS e comunicação celular LTE Cat 1 com fallback GSM/GPRS:
- Tecnologia Celular: LTE Cat 1 (Bandas B1, B2, B3, B4, B5, B7, B8, B28, B66) com fallback EGPRS 850/900/1800/1900 MHz.
- Tensão de Alimentação Contínua: DC 9V a 90V (compatível com motocicletas, veículos leves 12V, caminhões 24V e máquinas pesadas até 90V).
- Bateria Backup Interna: Li-Polymer 190mAh / 3.7V recarregável com chave física interna liga/desliga (Power Switch).
- Dimensões e Peso: 87.0 x 37.0 x 12.0 mm | Peso: ~48g.
- Conector Principal: Cabo chicote tipo Pitch com conector de 5 pinos.
- Entradas e Saídas:
  * 1 Entrada de Ignição dedicada (Pós-Chave trigger positivo 5.0V a 32V).
  * 1 Entrada Configurável (AIN/IN1): Analógica (0 a 16V) ou Digital negativa (trigger GND para botão de pânico).
  * 1 Saída Digital Open-Drain (OUT): Negativo com corrente máxima de 150mA para acionamento de relé de bloqueio.
- Antenas: Antena GNSS interna de alto ganho e antena celular LTE interna.
- Orientação de Instalação: O lado sem LEDs possui a gravação 'THIS SIDE TOWARDS SKY' e DEVE ficar apontado para o céu.
- Certificações: ANATEL, FCC, CE.
"""
    },
    {
        "id": "gv50cg_chicote",
        "device_family": "Queclink GV50CG",
        "topic": "fios_chicote",
        "title": "Chicote e Pinagem de Fios - Queclink GV50CG (Conector 5 Vias)",
        "keywords": ["queclink", "gv50cg", "gv50", "chicote", "pinagem", "fios", "cores", "laranja", "vermelho", "preto", "marrom", "branco", "ignicao", "bloqueio", "panico"],
        "pages": "Págs. 10, 11",
        "summary": "Pinagem completa do chicote de 5 vias do Queclink GV50CG.",
        "content": """
Chicote do Queclink GV50CG (Conector de 5 Vias):
- Pino 1 - Fio Laranja: AIN / IN1 (Entrada Analógica 0 a 16V OU Entrada Digital 1 negativa GND). Usado tipicamente para Botão de Pânico / Emergência (ativo em 0 a 0.8V, inativo circuito aberto).
- Pino 2 - Fio Vermelho: VIN (Alimentação Positiva Contínua DC 9V a 90V). Ligar à bateria permanente do veículo com fusível recomendado de 2A a 5A.
- Pino 3 - Fio Preto: GND (Negativo / Terra). Ligar diretamente ao chassi metálico ou borne negativo da bateria.
- Pino 4 - Fio Marrom: OUT (Saída Digital 1 de Bloqueio - Open-Drain GND, corrente máxima 150mA). Conectar ao pino 85 do relé de bloqueio. OBRIGATÓRIO utilizar relé com diodo de roda livre (ex: 1N4004) em paralelo com 85 e 86.
- Pino 5 - Fio Branco: IGN (Entrada de Ignição / Pós-Chave - Trigger positivo). Conectar à linha 15 (pós-chave do veículo). Tensão de ativação: 5.0V a 32V (ativo), 0 a 3V ou circuito aberto (inativo).
"""
    },
    {
        "id": "gv50cg_bloqueio_rele",
        "device_family": "Queclink GV50CG",
        "topic": "bloqueio_rele",
        "title": "Ligação do Relé de Bloqueio com Diodo (Queclink GV50CG)",
        "keywords": ["queclink", "gv50cg", "rele", "bloqueio", "corte", "marrom", "diodo", "1n4004", "bomba", "combustivel", "ignicao"],
        "pages": "Pág. 12",
        "summary": "Esquema elétrico de bloqueio com Fio Marrom e diodo 1N4004 obrigatório na bobina do relé.",
        "content": """
Ligação do Relé de Bloqueio no Queclink GV50CG:
A saída digital do GV50CG é o Fio Marrom (Open Drain / terra comutado, máx 150mA).
IMPORTANTE: É OBRIGATÓRIO instalar um diodo de roda livre (ex: 1N4004) em paralelo com a bobina do relé (pinos 85 e 86) para absorver o pico de contratensão indutiva e proteger o circuito do rastreador contra queima.

Esquema de Ligação nos Pinos do Relé (Padrão Automotivo 12V/24V):
- Pino 85 do Relé: Conectar ao Fio Marrom do GV50CG (Saída OUT) e ao ÂNODO do diodo 1N4004 (lado sem listra).
- Pino 86 do Relé: Conectar ao Pós-Chave (+12V/+24V) e ao CÁTODO do diodo 1N4004 (lado com a listra prateada/branca).
- Pino 30 do Relé: Conectar em uma das pontas do fio cortado da bomba de combustível ou ignição.
- Pino 87A do Relé (Normal Fechado - NF): Conectar na outra ponta do fio cortado da bomba de combustível ou ignição.
- Pino 87 (Normal Aberto): Deixar isolado (não utilizado).

Funcionamento: Enquanto o rastreador estiver em estado normal (desbloqueado), o contato entre 30 e 87A permanece fechado, permitindo o fluxo de corrente e partida do motor. Quando o comando de bloqueio é enviado, a saída Fio Marrom aterra o pino 85, a bobina atraca e abre o circuito entre 30 e 87A, cortando a bomba.
"""
    },
    {
        "id": "gv50cg_leds",
        "device_family": "Queclink GV50CG",
        "topic": "leds_diagnostico",
        "title": "Diagnóstico dos LEDs Celular e GNSS (Queclink GV50CG)",
        "keywords": ["queclink", "gv50cg", "led", "leds", "verde", "azul", "pisca", "piscando", "celular", "gnss", "gps", "pin", "fix"],
        "pages": "Págs. 7, 8",
        "summary": "Padrão de piscadas e diagnósticos dos LEDs Verde (Celular) e Azul (GNSS).",
        "content": """
O Queclink GV50CG possui 2 LEDs indicadores frontais de diagnóstico:

1. LED CELULAR (Verde / Green):
- Piscando Rápido (100ms Ligado / 800ms Desligado): Buscando sinal da rede celular (LTE Cat 1 / 2G).
- Piscando Lento (100ms Ligado / 2000ms Desligado): Registrado na rede celular com sucesso (Conectado / Operação Normal).
- Aceso Fixo (Continuously ON): Chip SIM bloqueado por PIN (o cartão SIM exige senha PIN para liberar). Solução: Coloque o chip em um smartphone e desative a trava de PIN nas configurações de segurança.
- Apagado: Modem celular desligado ou rastreador sem alimentação elétrica.

2. LED GNSS / GPS (Azul / Blue):
- Aceso Fixo (Continuously ON): Fix GNSS obtido com sucesso (Posição GPS calculada e precisa).
- Piscando Rápido (100ms Ligado / 100ms Desligado): Buscando sinal de satélites GNSS (sem posição fixada ainda).
- Piscando Lento (600ms Ligado / 600ms Desligado): GNSS sem sinal ou erro nos dados de satélite.
- Apagado: Receptor GNSS desligado.
"""
    },
    {
        "id": "gv50cg_instalacao_antena",
        "device_family": "Queclink GV50CG",
        "topic": "instalacao_eletrica",
        "title": "Posicionamento da Antena e Instalação Física (Queclink GV50CG)",
        "keywords": ["queclink", "gv50cg", "antena", "posicionamento", "this side towards sky", "instalacao", "ceu", "orientacao"],
        "pages": "Págs. 14, 15",
        "summary": "O lado sem LEDs com a gravação 'THIS SIDE TOWARDS SKY' deve apontar para o céu.",
        "content": """
Orientações de Instalação e Posicionamento do Queclink GV50CG:
- Orientação da Antena Interna: O lado liso do rastreador (oposto aos LEDs) possui a gravação:
  'THIS SIDE TOWARDS SKY' (Este lado voltado para o céu).
  Este lado DEVE obrigatoriamente ficar apontado para cima (para o céu) para recepção adequada dos sinais GNSS.
- Barreiras e Blindagens: Não instale o equipamento diretamente sob chapas metálicas, estruturas de aço ou blindagens térmicas metálicas do vidro. Superfícies plásticas do painel, carpete ou estofamento não bloqueiam o sinal.
- Fixação: Utilize fita dupla-face automotiva de alta resistência (3M) ou abraçadeiras plásticas (enforca-gato) presas ao chicote fixo do veículo, garantindo que o aparelho não sofra vibração mecânica excessiva.
- Fusível de Proteção: Sempre instale porta-fusível com fusível de 2A a 5A na linha de alimentação positiva (Fio Vermelho) o mais próximo possível do ponto de derivação da bateria.
"""
    },
    {
        "id": "gv50cg_sim_card",
        "device_family": "Queclink GV50CG",
        "topic": "chip_sim",
        "title": "Instalação do Micro-SIM Card e Chave de Bateria (Queclink GV50CG)",
        "keywords": ["queclink", "gv50cg", "sim", "chip", "micro sim", "bateria", "switch", "abrir", "chave", "pin"],
        "pages": "Págs. 8, 9",
        "summary": "Procedimento de inserção do Micro-SIM (3FF) e acionamento da chave interna da bateria.",
        "content": """
Instalação do Chip SIM Card e Chave Interna no Queclink GV50CG:
1. Tamanho do Chip: O GV50CG utiliza padrão Micro-SIM (3FF).
2. Abertura do Gabinete: Solte os parafusos da tampa traseira e abra a carcaça com cuidado para não danificar o anel de vedação.
3. Inserção do SIM Card: Encaixe o chip Micro-SIM no slot correspondente com os contatos dourados voltados para baixo e empurre a trava metálica até travar com clique.
4. Chave da Bateria Interna (Power Switch):
   - Por padrão de fábrica para transporte, a chave da bateria interna vem na posição 'OFF'.
   - Mude a chave da bateria para a posição 'ON'. Isso permite que a bateria de backup funcione caso a alimentação principal seja desconectada.
5. Fechamento: Encaixe a carcaça superior na inferior e aperte os parafusos firmemente de forma homogênea.
6. Validação do Chip: Certifique-se de que a senha/código PIN do chip esteja desativada e que haja plano de dados M2M/IoT ativo com APN configurada.
"""
    },

    # =========================================================================
    # 8. COMANDOS OPERACIONAIS E TEMPLATES POR EQUIPAMENTO
    # =========================================================================
    {
        "id": "st310_st340_comandos_operacionais",
        "device_family": "ST310 / ST340",
        "topic": "comandos",
        "title": "Comandos Operacionais e Templates - Suntech ST310 e ST340",
        "keywords": [
            "st310", "st340", "st310u", "st340ur", "ignicao virtual", "ignicao fisica",
            "ignicao por deslocamento", "deslocamento", "beep de velocidade", "alterar beep",
            "buzzer enable", "buzzer disable", "buzzer st310u", "buzzer st340",
            "deep sleep", "habilitar deep sleep", "desabilitar deep sleep", "st300evt", "st300svc", "st300cmd"
        ],
        "pages": "Tabela de Comandos de Configuração Suntech ST310 / ST340",
        "summary": "Templates de comandos para ST310 e ST340: ignição virtual por tensão, física, deslocamento, controle de buzzer, beep de velocidade e deep sleep.",
        "content": """
Tabela de Comandos Operacionais - Suntech ST310 / ST340:

1. Ignição Virtual por Tensão (310):
- Template: ST300EVT;SERIAL;02;2;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0
- Descrição: Configura ignição virtual baseada na elevação de tensão da bateria do veículo no modelo ST310. Substitua SERIAL pelo serial de 9 ou 10 dígitos do aparelho.

2. Ignição Virtual por Tensão (340):
- Template: ST300EVT;SERIAL;02;2;10;0;2;20;9;20;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3
- Descrição: Configura ignição virtual por tensão da bateria especificamente para o modelo ST340 / ST340UR.

3. Ignição Física (310):
- Template: ST300EVT;SERIAL;02;3;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0
- Descrição: Configura a detecção física de ignição através do fio de entrada pós-chave (linha 15) no ST310.

4. Ignição Física (340):
- Template: ST300EVT;SERIAL;02;0;10;0;12;13;9;30;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3
- Descrição: Configura detecção física de ignição via fio pós-chave no modelo ST340.

5. Ignição por Deslocamento (ST310U):
- Template: ST300EVT;SERIAL;02;3;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0
- Descrição: Ativa a ignição virtual quando o GPS do ST310U detectar deslocamento/movimento do veículo.

6. Ignição por Deslocamento (ST340UR):
- Template: ST300EVT;SERIAL;02;3;10;0;2;20;9;20;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3
- Descrição: Ativa ignição virtual por movimentação/deslocamento no modelo estanque ST340UR.

7. Alterar Beep de Velocidade (ST340):
- Template: ST300SVC;SERIAL;02;1;VELOCIDADE;0;0;0;1;1;0;1;0;0;0;1;1
- Descrição: Altera a velocidade de corte/aviso sonoro do buzzer no ST340. Substitua VELOCIDADE pelo limite numérico em km/h (ex: 80, 100, 110) e SERIAL pelo serial do rastreador.

8. Buzzer Enable 1:
- Template: ST300CMD;SERIAL;02;Enable1
- Descrição: Aciona e liga a Saída 1 do ST310/ST340, ativando imediatamente o buzzer ou sirene conectada.

9. Buzzer Disable 1:
- Template: ST300CMD;SERIAL;02;Disable1
- Descrição: Desativa e desliga a Saída 1 do ST310/ST340, silenciando o buzzer sonoro.

10. Buzzer ST310U:
- Template: ST300SVC;SERIAL;02;1;110;0;0;0;0;0;1;0;0;0;0
- Descrição: Configura os parâmetros e limites padrão de operação do buzzer no ST310U (limite de 110 km/h).

11. Buzzer ST340:
- Template: ST300SVC;SERIAL;02;1;120;0;0;0;1;1;0;1;0;0;0;1;1
- Descrição: Configura os parâmetros e limites do buzzer no ST340 (limite de 120 km/h).

12. Habilitar Deep Sleep:
- Template: ST300SVC;SERIAL;02;0;200;1;0;0;0;1;0;1;0;0;0;1;1
- Descrição: Habilita o modo de economia profunda (Deep Sleep) no ST310 / ST340 para reduzir o consumo de bateria do veículo enquanto desligado.

13. Desabilitar Deep Sleep / Qualquer Sleep:
- Template: ST300SVC;SERIAL;02;0;200;0;0;0;0;0;1;0;1;0;0;0;1
- Descrição: Desativa qualquer modo sleep no ST310 / ST340, forçando o equipamento a operar em regime contínuo 100% acordado.
"""
    },
    {
        "id": "st8310_st8300_st4315_st4305_comandos_prg",
        "device_family": "ST8310 / ST8300 / ST4315 / ST4305",
        "topic": "comandos",
        "title": "Comandos PRG de Configuração 4G - ST8310, ST8300, ST4315 e ST4305",
        "keywords": [
            "st8310", "st8300", "st4315", "st4305", "prg", "ignicao acelerometro", "ignicao tensao",
            "ignicao fisica", "pos chave", "beep velocidade 4g", "buzzer habilitar", "buzzer desabilitar",
            "sleep desabilitado", "sleep profundo", "sleep baixo consumo", "driving behavior"
        ],
        "pages": "Tabela de Comandos PRG Linha 4G Suntech",
        "summary": "Templates de comandos no formato PRG para a linha 4G Suntech (ignição por acelerômetro/tensão/física, buzzer, sleep e driving behavior).",
        "content": """
Tabela de Comandos PRG (Linha 4G Suntech - ST8310 / ST8300 / ST4315 / ST4305):

1. Ignição Virtual por Acelerômetro:
- Template: PRG;SERIAL;17;00#03
- Descrição: Configura a ignição virtual através do sensor de movimento/acelerômetro interno (G-sensor).

2. Ignição Virtual por Tensão:
- Template: PRG;SERIAL;17;00#02
- Descrição: Configura a ignição virtual monitorando o aumento da voltagem da bateria do veículo.

3. Ignição Física (Pós Chave):
- Template: PRG;SERIAL;17;00#01
- Descrição: Configura a detecção convencional de ignição pelo Fio Azul conectado ao pós-chave (linha 15).

4. Alterar Beep de Velocidade (4G):
- Template: PRG;SERIAL;16;21#VELOCIDADE
- Descrição: Define a velocidade de disparo do alerta sonoro nos rastreadores 4G. Substitua VELOCIDADE pelo valor em km/h (ex: 80, 100, 120) e SERIAL pelo serial do aparelho.

5. Buzzer Habilitar:
- Template: PRG;SERIAL;10;64#01
- Descrição: Habilita a função do buzzer sonoro na saída configurada.

6. Buzzer Desabilitar:
- Template: PRG;SERIAL;10;64#00
- Descrição: Desabilita o buzzer sonoro do rastreador.

7. Modo Sleep Desabilitado (Consumo normal):
- Template: PRG;SERIAL;19;30#00
- Descrição: Desativa o modo econômico de repouso. O equipamento opera com consumo padrão o tempo todo.

8. Sleep Profundo / Ultra-baixo consumo:
- Template: PRG;SERIAL;19;30#01
- Descrição: Ativa o modo Deep Sleep (consumo ultrabaixo <3mA) desligando módulos não essenciais com a ignição desligada.

9. Sleep Baixo consumo (GPRS Mantido):
- Template: PRG;SERIAL;19;30#02
- Descrição: Ativa o modo sleep econômico mantendo o modem GPRS/LTE conectado na rede celular para recepção instantânea de comandos.

10. Driving Behavior (Habilitar Função):
- Template: PRG;SERIAL;19;10#01
- Descrição: Habilita a função de telemetria de condução (Driving Behavior / Eco-Driving).

11. Driving Behavior Completo:
- Template: PRG;SERIAL;19;10#01;12#40.0;13#45.0;14#60.0;21#20.0;22#20.0;23#20.0
- Descrição: Configura telemetria detalhada de condução agressiva:
  * 12#40.0: Limiar de aceleração brusca
  * 13#45.0: Limiar de frenagem brusca
  * 14#60.0: Limiar de curva brusca
  * 21#20.0, 22#20.0, 23#20.0: Limiares complementares de impactos e choques
"""
    },
    {
        "id": "queclink_gv50_comandos_bloqueio",
        "device_family": "Queclink GV50CG",
        "topic": "comandos",
        "title": "Comandos de Bloqueio e Desbloqueio - Queclink GV50 4G (GV50CG)",
        "keywords": [
            "gv50 4g", "gv50cg", "queclink", "bloquear veiculo", "desbloquear veiculo",
            "at+gtdos", "bloqueio gv50", "desbloqueio gv50", "ignicao ligada", "rele"
        ],
        "pages": "Tabela de Comandos de Operação Queclink GV50 4G",
        "summary": "Comandos AT+GTDOS de bloqueio e desbloqueio para o Queclink GV50 4G com aviso obrigatório de ignição ligada.",
        "content": """
Comandos de Bloqueio e Desbloqueio - Queclink GV50 4G (GV50CG):

1. Bloquear Veículo:
- Template: AT+GTDOS=gv50cg,0,1,1,1,0,0,,,0,0,5,,,,FFFF$
- ⚠️ AVISO OBRIGATÓRIO: EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!
- Descrição: Envia o comando de bloqueio via protocolo @Tracker para acionar a saída digital (Pino 4 - Fio Marrom / OUT) conectada à bobina do relé automotivo de corte.

2. Desbloquear Veículo:
- Template: AT+GTDOS=gv50cg,0,1,1,0,0,0,,,0,0,5,,,,FFFF$
- ⚠️ AVISO OBRIGATÓRIO: EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!
- Descrição: Envia o comando de desbloqueio desativando a saída digital e restabelecendo o circuito da bomba de combustível ou ignição.

Regra Importante de Execução:
Para que o Queclink GV50 4G processe e execute com sucesso o comando de bloqueio ou desbloqueio, o veículo e o equipamento DEVEM estar com a ignição ligada.
"""
    },
    {
        "id": "identificador_motorista_rfid_comandos",
        "device_family": "Identificador de Motorista",
        "topic": "comandos",
        "title": "Comandos para Identificador de Motorista (RFID GET, SGBRAS e Teclado)",
        "keywords": [
            "identificador de motorista", "rfid", "sgbras", "teclado", "matricula", "getscale",
            "timeout", "st300dex", "dex", "gtsl", "sgbt", "passageiro", "leitor de cartao"
        ],
        "pages": "Tabela de Comandos de Periféricos e Acessórios",
        "summary": "Templates de comandos DEX e ST300DEX para configuração de RFID GET, SGBRAS 09.2/04.8, teclado de matrícula e timeout GetScale.",
        "content": """
Tabela de Comandos para Identificador de Motorista (RFID / Teclado / Periféricos):

1. RFID GET - 1. IDENTIFICAÇÃO DE MOTORISTA/PASSAGEIRO (RFID - GET):
- Template: ST300DEX;02;6;718|1|;C9
- Descrição: Configura a identificação de motorista/passageiro via leitor RFID GET no protocolo ST300DEX.

2. RFID GET - IDENTIFICAÇÃO DE MOTORISTA/PASSAGEIRO (RFID - SGBRAS):
- Template: ST300DEX;SERIAL;02;19;GTSL|7|1|2|719|0|1|;3
- Descrição: Configura a identificação de motorista/passageiro para leitores RFID SGBRAS. Substitua SERIAL pelo serial do rastreador.

3. RFID GET (DEX 0009):
- Template: DEX;SERIAL;0009;718|1|;C9;80
- Descrição: Comando DEX padrão de comunicação para leitor RFID GET com o serial do rastreador.

4. RFID SGBRAS (09.2):
- Template: ST300DEX;SERIAL;02;10;SGBT|09.2|;F1
- Descrição: Configura e calibra o leitor RFID SGBRAS versão de firmware 09.2.

5. RFID SGBRAS (04.8):
- Template: ST300DEX;SERIAL;02;10;SGBT|04.8|;F2
- Descrição: Configura o leitor RFID SGBRAS versão de firmware 04.8.

6. TECLADO SGBRAS (Ativar RFID):
- Template: DEX;SERIAL;0008;SGBT|18|;91
- Descrição: Habilita o leitor de cartões RFID embutido no teclado SGBRAS.

7. TECLADO SGBRAS (Ativar Matrícula):
- Template: DEX;SERIAL;0008;SGBT|17|;90
- Descrição: Habilita a digitação manual de matrícula/código do motorista através do teclado numérico SGBRAS.

8. Timeout ID GetScale:
- Template: DEX;SERIAL;0006;709|0|;C8
- Descrição: Configura o tempo de espera (timeout) para leitura de identificação do sistema GetScale.
"""
    },
    {
        "id": "tabela_geral_comandos_equipamentos",
        "device_family": "Geral / Todos os Modelos",
        "topic": "comandos",
        "title": "Tabela Completa de Comandos por Modelo de Equipamento",
        "keywords": [
            "tabela de comandos", "todos os comandos", "lista de comandos", "comandos de configuracao",
            "comandos por modelo", "st310", "st340", "st8300", "st4305", "st8310", "gv50 4g", "rfid"
        ],
        "pages": "Tabela Operacional Centralizada de Comandos",
        "summary": "Compilação de todos os comandos organizados por modelo: Suntech ST310/ST340, Suntech 4G PRG, Queclink GV50 4G e Identificadores de Motorista.",
        "content": """
Tabela Geral de Comandos por Equipamento:

--- LINHA ST310 / ST340 ---
• Ignição Virtual por Tensão (310): ST300EVT;SERIAL;02;2;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0
• Ignição Virtual por Tensão (340): ST300EVT;SERIAL;02;2;10;0;2;20;9;20;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3
• Ignição Física (310): ST300EVT;SERIAL;02;3;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0
• Ignição Física (340): ST300EVT;SERIAL;02;0;10;0;12;13;9;30;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3
• Ignição por Deslocamento (ST310U): ST300EVT;SERIAL;02;3;10;0;2;13;9;2;20;0;5;7;1;1;0;0;0;0;0;0;9;9;0;0;0
• Ignição por Deslocamento (ST340UR): ST300EVT;SERIAL;02;3;10;0;2;20;9;20;20;0;5;7;1;0;0;0;0;0;0;0;9;9;0;0;3
• Alterar Beep de Velocidade (ST340): ST300SVC;SERIAL;02;1;VELOCIDADE;0;0;0;1;1;0;1;0;0;0;1;1
• Buzzer Enable 1: ST300CMD;SERIAL;02;Enable1
• Buzzer Disable 1: ST300CMD;SERIAL;02;Disable1
• Buzzer ST310U: ST300SVC;SERIAL;02;1;110;0;0;0;0;0;1;0;0;0;0
• Buzzer ST340: ST300SVC;SERIAL;02;1;120;0;0;0;1;1;0;1;0;0;0;1;1
• Habilitar Deep Sleep: ST300SVC;SERIAL;02;0;200;1;0;0;0;1;0;1;0;0;0;1;1
• Desabilitar Deep Sleep / Qualquer Sleep: ST300SVC;SERIAL;02;0;200;0;0;0;0;0;1;0;1;0;0;0;1

--- LINHA ST8310 / ST8300 / ST4315 / ST4305 (4G PRG) ---
• Ignição Virtual por Acelerômetro: PRG;SERIAL;17;00#03
• Ignição Virtual por Tensão: PRG;SERIAL;17;00#02
• Ignição Física (Pós Chave): PRG;SERIAL;17;00#01
• Alterar Beep de Velocidade (4G): PRG;SERIAL;16;21#VELOCIDADE
• Buzzer Habilitar: PRG;SERIAL;10;64#01
• Buzzer Desabilitar: PRG;SERIAL;10;64#00
• Modo Sleep Desabilitado (Consumo normal): PRG;SERIAL;19;30#00
• Sleep Profundo / Ultra-baixo consumo: PRG;SERIAL;19;30#01
• Sleep Baixo consumo (GPRS Mantido): PRG;SERIAL;19;30#02
• Driving Behavior (Habilitar Função): PRG;SERIAL;19;10#01
• Driving Behavior Completo: PRG;SERIAL;19;10#01;12#40.0;13#45.0;14#60.0;21#20.0;22#20.0;23#20.0

--- QUECLINK GV50 4G (GV50CG) ---
• Bloquear Veículo: AT+GTDOS=gv50cg,0,1,1,1,0,0,,,0,0,5,,,,FFFF$
  [AVISO: EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!]
• Desbloquear Veículo: AT+GTDOS=gv50cg,0,1,1,0,0,0,,,0,0,5,,,,FFFF$
  [AVISO: EQUIPAMENTO DEVE ESTAR COM A IGNIÇÃO LIGADA!]

--- IDENTIFICADOR DE MOTORISTA (RFID / TECLADO) ---
• RFID GET - 1. IDENTIFICAÇÃO DE MOTORISTA/PASSAGEIRO (RFID - GET): ST300DEX;02;6;718|1|;C9
• RFID GET - IDENTIFICAÇÃO DE MOTORISTA/PASSAGEIRO (RFID - SGBRAS): ST300DEX;SERIAL;02;19;GTSL|7|1|2|719|0|1|;3
• RFID GET (DEX 0009): DEX;SERIAL;0009;718|1|;C9;80
• RFID SGBRAS (09.2): ST300DEX;SERIAL;02;10;SGBT|09.2|;F1
• RFID SGBRAS (04.8): ST300DEX;SERIAL;02;10;SGBT|04.8|;F2
• TECLADO SGBRAS (Ativar RFID): DEX;SERIAL;0008;SGBT|18|;91
• TECLADO SGBRAS (Ativar Matrícula): DEX;SERIAL;0008;SGBT|17|;90
• Timeout ID GetScale: DEX;SERIAL;0006;709|0|;C8
"""
    }
]


# Dicionário de sinônimos e mapeamentos de termos técnicos para normalização
TECHNICAL_TERMS_MAP = {
    "queclink": "gv50cg_geral",
    "gv50cg": "gv50cg_geral",
    "gv50": "gv50cg_geral",
    "gv 50": "gv50cg_geral",
    "diodo 1n4004": "bloqueio_rele",
    "1n4004": "bloqueio_rele",
    "diodo de roda livre": "bloqueio_rele",
    "diodo rele": "bloqueio_rele",
    "this side towards sky": "instalacao_eletrica",
    "towards sky": "instalacao_eletrica",
    "chave bateria": "chip_sim",
    "power switch": "chip_sim",
    "micro sim": "chip_sim",
    "micro-sim": "chip_sim",
    "pos chave": "ignicao",
    "pos-chave": "ignicao",
    "poschave": "ignicao",
    "desliga chave": "ignicao",
    "corta corrente": "bloqueio",
    "corte de combustivel": "bloqueio",
    "rele": "bloqueio_rele",
    "rele de 5 pinos": "bloqueio_rele",
    "5 pinos": "bloqueio_rele",
    "bomba de combustivel": "bloqueio_rele",
    "piscando": "leds_diagnostico",
    "led": "leds_diagnostico",
    "leds": "leds_diagnostico",
    "luz vermelha": "leds_diagnostico",
    "luz azul": "leds_diagnostico",
    "calibrar": "calibracao_dpa",
    "calibracao": "calibracao_dpa",
    "dpa": "calibracao_dpa",
    "freadas": "calibracao_dpa",
    "curvas": "calibracao_dpa",
    "aceleracoes": "calibracao_dpa",
    "cor do fio": "fios_chicote",
    "cores": "fios_chicote",
    "chicote": "fios_chicote",
    "pinagem": "fios_chicote",
    "fio branco": "fios_chicote",
    "fio amarelo": "fios_chicote",
    "fio laranja": "fios_chicote",
    "fio azul": "fios_chicote",
    "fio verde": "fios_chicote",
    "fio vermelho": "fios_chicote",
    "fio preto": "fios_chicote",
    "chip": "chip_sim",
    "simcard": "chip_sim",
    "sim card": "chip_sim",
    "jornada": "jornada_trabalho",
    "hora extra": "jornada_trabalho",
    "fuso": "jornada_trabalho",
    "utc": "jornada_trabalho",
    "idle": "modo_idle",
    "ocioso": "modo_idle",
    "senha": "configuracao_synctrak",
    "synctrak": "configuracao_synctrak",
    "synctrack": "configuracao_synctrak",
    "st5656": "configuracao_synctrak",
    "fusivel": "instalacao_eletrica",
    "5a": "instalacao_eletrica",
    "ip67": "especificacoes",
    "diferenca": "diferencas_modelos",
    "diferencas": "diferencas_modelos",
    "comparar": "diferencas_modelos",
    "comando": "comandos",
    "comandos": "comandos",
    "template": "comandos",
    "templates": "comandos",
    "st300evt": "comandos",
    "st300svc": "comandos",
    "st300cmd": "comandos",
    "st300dex": "comandos",
    "prg": "comandos",
    "at+gtdos": "comandos",
    "gtdos": "comandos",
    "rfid": "comandos",
    "sgbras": "comandos",
    "teclado sgbras": "comandos",
    "getscale": "comandos",
    "matricula": "comandos",
    "beep": "comandos",
    "buzzer": "comandos",
    "deep sleep": "comandos",
    "driving behavior": "comandos",
    "bloquear veiculo": "comandos",
    "desbloquear veiculo": "comandos",
    "ignicao virtual": "comandos",
    "ignicao fisica": "comandos",
    "rs232": "comandos_rs232",
    "ibutton": "especificacoes",
    "1-wire": "especificacoes",
    "jammer": "especificacoes",
    "antifurto": "antifurto",
    "botao segredo": "antifurto",
    "cerca": "cercas",
    "cerca circular": "cercas",
    "cerca poligonal": "cercas",
    "geofence": "cercas",
}

INTENTS_LIST = [
    "fios_chicote",
    "calibracao_dpa",
    "leds_diagnostico",
    "instalacao_eletrica",
    "bloqueio_rele",
    "antifurto",
    "jornada_trabalho",
    "modo_idle",
    "comandos",
    "comandos_rs232",
    "diferencas_modelos",
    "especificacoes",
    "chip_sim",
    "configuracao_synctrak",
    "bateria_consumo",
    "cercas"
]
