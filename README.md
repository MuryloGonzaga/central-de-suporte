# 🛰️ Central de Suporte - Aplicação Web

Aplicação web completa para técnicos e equipe de suporte operacional da **WebRota**, convertida a partir do bot do Discord para uma interface moderna, rápida e responsiva, com suporte a consultas individuais e em lote, gráficos, rankings e guias visuais.

---

## 🚀 Funcionalidades

| Recurso | Descrição |
| :--- | :--- |
| 🚗 **Consulta Placa (AcheCar)** | Consulta dados completos do veículo na base pública (Marca, Modelo, Ano Fabricação/Modelo, Cor, Tipo, Combustível, Município/UF). Suporta consulta em massa com controle de intervalo contra bloqueio. |
| 🛻 **Veículo WebRota** | Busca Marca e Modelo cadastrados diretamente na base do sistema WebRota. |
| 📍 **Local de Instalação (OS)** | Localiza os seriais dos equipamentos e rastreia na última Ordem de Serviço finalizada (`Status E` ou `F`) onde o rastreador foi instalado no veículo ou máquina. |
| 🏆 **Rankings de Execução** | Ranking diário de OS por executor (com pódio 🥇 🥈 🥉, percentuais e filtro por data) e ranking mensal comparativo oficial (Túlio x Kaio). |
| 🔌 **Guia de Cabos** | Diagrama visual com padrão de cores dos chicotes 1 a 5 para instalação rápida no campo. |
| 🚨 **Diagnóstico de LEDs** | Tabela visual e interativa com as contagens de piscadas dos LEDs Azul (GPRS) e Vermelho (GPS) dos rastreadores Suntech. |
| 📋 **Exportação & Cópia** | Botões para copiar tabelas com 1 clique e exportar relatórios diretamente para **CSV/Excel**. |
| 📖 **API REST Documentada** | Documentação Swagger interativa integrada em `/docs`. |

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Aiohttp, Jinja2, Pydantic.
- **Frontend:** HTML5, CSS3 Moderno (Dark Mode), Vanilla JavaScript, FontAwesome.
- **Deploy & Contêineres:** Docker, Docker Compose, Nginx, Systemd.

---

## ⚙️ Pré-requisitos & Configuração (.env)

No diretório do projeto, já existe o arquivo `.env`. Preencha suas credenciais da WebRota:

```env
# Credenciais de Acesso à API da WebRota
WEBROTA_USER=seu_usuario_webrota
WEBROTA_PASS=sua_senha_webrota

# Configurações do Servidor
APP_HOST=0.0.0.0
APP_PORT=8000

# Chave secreta da aplicação
SECRET_KEY=chave_secreta_central_suporte_producao_2026

# Modo de desenvolvimento (false para servidor)
DEBUG=false

# Nome da Aplicação
APP_NAME=Central de Suporte - Rastreamento & WebRota
```

> ⚠️ **Importante:** Mantenha o `APP_HOST=0.0.0.0` para que a aplicação aceite conexões de outros computadores, celulares ou redes externas ao hospedar no servidor.

---

## 💻 Como Rodar Localmente (Windows / Linux / Mac)

### No Windows:
1. Instale as dependências (caso não tenha instalado):
   ```cmd
   pip install -r requirements.txt
   ```
2. Dê dois cliques no arquivo `start.bat` ou execute no terminal:
   ```cmd
   python run.py
   ```
3. Abra seu navegador em:
   - Painel: **`http://localhost:8000`**
   - Documentação Swagger: **`http://localhost:8000/docs`**

---

## 🌐 Como Hospedar em um Servidor (Produção)

Existem 3 formas simples de hospedar sua aplicação:

### Opção 1: Usando Docker & Docker Compose (Mais Recomendado)

Se seu servidor já possui o Docker instalado, basta um único comando para subir tudo em segundo plano:

1. Clone ou transfira a pasta do projeto para o servidor:
   ```bash
   cd "Central de Suporte"
   ```
2. Configure o arquivo `.env` com seu usuário e senha da Webrota.
3. Inicie o contêiner:
   ```bash
   docker compose up -d --build
   ```
4. Pronto! O contêiner irá iniciar automaticamente e se reiniciar em caso de reinicialização do servidor.
5. Para verificar logs:
   ```bash
   docker compose logs -f
   ```

---

### Opção 2: Servidor VPS Linux (Ubuntu / Debian com Systemd)

Se preferir rodar nativamente sem Docker:

1. Conecte-se ao seu servidor via SSH:
   ```bash
   ssh root@seu-ip-ou-dominio
   ```

2. Instale o Python e Git:
   ```bash
   sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
   ```

3. Crie uma pasta e copie o projeto (ex: `/var/www/central-suporte`):
   ```bash
   cd /var/www/central-suporte
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Configure o serviço no **systemd** para que o aplicativo fique sempre ligado:
   ```bash
   sudo nano /etc/systemd/system/central-suporte.service
   ```

   Cole a configuração abaixo:
   ```ini
   [Unit]
   Description=Central de Suporte Web
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/central-suporte
   ExecStart=/var/www/central-suporte/venv/bin/python run.py
   Restart=always
   RestartSec=5
   EnvironmentFile=/var/www/central-suporte/.env

   [Install]
   WantedBy=multi-user.target
   ```

5. Ative e inicie o serviço:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable central-suporte
   sudo systemctl start central-suporte
   sudo systemctl status central-suporte
   ```

6. *(Opcional)* Configurar **Nginx com SSL (HTTPS)**:
   ```nginx
   server {
       server_name suporte.seusite.com.br;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
   E para certificado SSL gratuito:
   ```bash
   sudo certbot --nginx -d suporte.seusite.com.br
   ```

---

### Opção 3: Hospedagem Gratuita/Nuvem (Render, Railway, Fly.io)

O projeto já inclui o arquivo `Procfile`.
1. Suba o código em um repositório GitHub (privado).
2. No [Render.com](https://render.com) ou [Railway.app](https://railway.app), selecione **New Web Service** apontando para o seu repositório.
3. Nas variáveis de ambiente do painel, defina:
   - `WEBROTA_USER`
   - `WEBROTA_PASS`
   - `APP_PORT=8000`
4. A plataforma cuidará da instalação e fornecerá uma URL pública HTTPS automaticamente.

---

## 📡 Endpoints da API REST

A aplicação também disponibiliza uma API REST completa para integrações:

- `GET /api/status`: Verifica integridade e status de conexão com a WebRota.
- `GET /api/consulta/placa/{placa}`: Consulta unitária na base pública AcheCar.
- `POST /api/consulta/placa`: Consulta em lote com parâmetros de intervalo suave.
- `GET /api/consulta/veiculo/{placa}`: Consulta unitária de veículo na WebRota.
- `POST /api/consulta/veiculo`: Consulta de veículos em lote na WebRota.
- `GET /api/consulta/local/{identificador}`: Rastreia serial e local de instalação da última OS.
- `POST /api/consulta/local`: Rastreia locais de instalação em lote.
- `GET /api/ranking/diario?data=AAAA-MM-DD`: Ranking diário de ordens de serviço.
- `GET /api/ranking/mensal`: Ranking mensal comparativo dos técnicos.
- `GET /api/guias/cabos`: Guia JSON das cores dos cabos.
- `GET /api/guias/leds`: Guia JSON de piscadas dos LEDs Suntech.

---

## 🔒 Segurança

- O arquivo `.env` está adicionado ao `.gitignore` e `.dockerignore` para não vazar credenciais.
- Caching de token JWT da WebRota para evitar logins repetitivos desnecessários.
- Intervalo seguro aleatório entre consultas em lote na base AcheCar para prevenir bloqueio por IP.

