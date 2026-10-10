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
    }
]


# Dicionário de sinônimos e mapeamentos de termos técnicos para normalização
TECHNICAL_TERMS_MAP = {
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
