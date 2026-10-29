// ====================================================================
// CENTRAL DE SUPORTE - JAVASCRIPT FRONTEND
// ====================================================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMobileMenu();
    initChatIA();

    // Define data padrão de hoje no seletor de rankings
    const dataFiltro = document.getElementById('data-filtro-ranking');
    if (dataFiltro) {
        const hoje = new Date().toISOString().split('T')[0];
        dataFiltro.value = hoje;
        dataFiltro.addEventListener('change', () => {
            carregarRankingDiario();
        });
    }

    // Se a rota acessada for /chat, ativa automaticamente a aba do chat
    if (window.location.pathname === '/chat') {
        const chatTabBtn = document.querySelector('[data-tab="tab-chat"]');
        if (chatTabBtn) chatTabBtn.click();
    }
});

// --------------------------------------------------------------------
// NAVEGAÇÃO ENTRE ABAS (DESKTOP & MOBILE BOTTOM BAR)
// --------------------------------------------------------------------
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const bottomNavItems = document.querySelectorAll('.bottom-nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const pageTitle = document.getElementById('page-title');
    const sidebar = document.querySelector('.sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');

    const titulos = {
        'tab-home': 'Bem-vindo à Central de Suporte WebRota',
        'tab-chat': 'Assistente Técnico IA - Manuais Suntech',
        'tab-placa': 'Consulta de Placa (Base Pública AcheCar)',
        'tab-local': 'Rastreamento de Local de Instalação (Última OS)',
        'tab-ranking': 'Rankings de Execução de Ordens de Serviço'
    };

    function mudarAba(tabId) {
        if (!tabId) return;

        // Atualiza estado ativo nos botões da sidebar e bottom nav
        navItems.forEach(n => {
            if (n.getAttribute('data-tab') === tabId) {
                n.classList.add('active');
            } else {
                n.classList.remove('active');
            }
        });

        bottomNavItems.forEach(b => {
            if (b.getAttribute('data-tab') === tabId) {
                b.classList.add('active');
            } else {
                b.classList.remove('active');
            }
        });

        // Alterna os painéis de abas
        tabPanes.forEach(t => {
            if (t.id === tabId) {
                t.classList.add('active');
            } else {
                t.classList.remove('active');
            }
        });

        // Atualiza título da topbar
        if (titulos[tabId] && pageTitle) {
            pageTitle.textContent = titulos[tabId];
        }

        // Carrega dados automáticos ao entrar na aba de Rankings
        if (tabId === 'tab-ranking') {
            carregarRankingDiario();
            carregarRankingMensal();
        }

        // Se for no Chat IA e estiver no mobile, foca de forma confortável
        if (tabId === 'tab-chat') {
            const container = document.getElementById('chat-messages-container');
            if (container) {
                setTimeout(() => {
                    container.scrollTop = container.scrollHeight;
                }, 100);
            }
        }

        // Fecha menu lateral e backdrop no mobile
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (backdrop) backdrop.classList.remove('active');
        document.body.classList.remove('sidebar-locked');

        // Scroll suave para o topo
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // Eventos na Sidebar
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');
            mudarAba(tabId);
        });
    });

    // Eventos na Bottom Navigation Bar (Mobile)
    bottomNavItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');
            mudarAba(tabId);
        });
    });

    // Atalhos dos cards na aba de boas-vindas
    document.querySelectorAll('.welcome-action-card').forEach(card => {
        card.addEventListener('click', () => {
            const gotoTab = card.getAttribute('data-goto');
            mudarAba(gotoTab);
        });
    });
}

function initMobileMenu() {
    const toggle = document.getElementById('mobile-toggle');
    const closeBtn = document.getElementById('sidebar-close');
    const backdrop = document.getElementById('sidebar-backdrop');
    const sidebar = document.querySelector('.sidebar');

    function abrirSidebar() {
        if (sidebar) sidebar.classList.add('mobile-open');
        if (backdrop) backdrop.classList.add('active');
    }

    function fecharSidebar() {
        if (sidebar) sidebar.classList.remove('mobile-open');
        if (backdrop) backdrop.classList.remove('active');
        document.body.classList.remove('sidebar-locked');
    }

    if (toggle) {
        toggle.addEventListener('click', (e) => {
            e.stopPropagation();
            if (sidebar && sidebar.classList.contains('mobile-open')) {
                fecharSidebar();
            } else {
                abrirSidebar();
            }
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fecharSidebar();
        });
    }

    if (backdrop) {
        backdrop.addEventListener('click', () => {
            fecharSidebar();
        });
    }

    // Fecha ao pressionar Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            fecharSidebar();
        }
    });
}

// --------------------------------------------------------------------
// TAB 1: CONSULTA ACHECAR (BASE PÚBLICA COM STREAMING & PROGRESSO)
// --------------------------------------------------------------------
let acheCarEventSource = null;
let acheCarResultados = [];

function adicionarLinhaAcheCar(item) {
    const tbody = document.getElementById('tbody-achecar');
    const countSpan = document.getElementById('count-achecar');
    if (!tbody) return;

    const tr = document.createElement('tr');
    if (item.sucesso) {
        tr.innerHTML = `
            <td><span class="tag-placa">${item.placa}</span></td>
            <td><strong>${item.marca || 'N/A'}</strong> ${item.modelo || ''}</td>
            <td>${item.ano_fabricacao || 'N/A'} / ${item.ano_modelo || 'N/A'}</td>
            <td>${item.cor || 'N/A'}</td>
            <td>${item.tipo_veiculo || 'N/A'} - ${item.combustivel || 'N/A'}</td>
            <td>${item.municipio || 'N/A'} / ${item.uf || 'N/A'}</td>
            <td><span class="badge badge-success"><i class="fa-solid fa-check"></i> Encontrado</span></td>
        `;
    } else {
        tr.innerHTML = `
            <td><span class="tag-placa">${item.placa}</span></td>
            <td colspan="5" style="color: #F87171;">${item.erro || 'Não foi possível consultar os dados.'}</td>
            <td><span class="badge badge-danger"><i class="fa-solid fa-xmark"></i> Falha</span></td>
        `;
    }
    tbody.appendChild(tr);

    if (countSpan) {
        const totalLinhas = tbody.querySelectorAll('tr').length;
        countSpan.textContent = totalLinhas;
    }
}

async function consultarAcheCarStream() {
    const input = document.getElementById('input-placas-achecar');
    const btn = document.getElementById('btn-consultar-achecar');
    const resultCard = document.getElementById('resultado-achecar');
    const tbody = document.getElementById('tbody-achecar');
    const countSpan = document.getElementById('count-achecar');

    const progressWrapper = document.getElementById('progress-achecar');
    const progressText = document.getElementById('progress-achecar-text');
    const progressPct = document.getElementById('progress-achecar-pct');
    const progressFill = document.getElementById('progress-achecar-fill');

    const texto = input.value.trim();
    if (!texto) {
        showToast('Por favor, informe ao menos uma placa.', 'warning');
        return;
    }

    if (acheCarEventSource) {
        acheCarEventSource.close();
        acheCarEventSource = null;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Consultando...';
    resultCard.style.display = 'block';
    tbody.innerHTML = '';
    acheCarResultados = [];
    if (countSpan) countSpan.textContent = '0';

    if (progressWrapper) {
        progressWrapper.style.display = 'block';
        if (progressFill) progressFill.style.width = '0%';
        if (progressPct) progressPct.textContent = '0%';
        if (progressText) progressText.textContent = 'Iniciando consulta suave e segura...';
    }

    // Scroll suave para os resultados no mobile
    setTimeout(() => {
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 150);

    try {
        const url = `/api/consulta/placa/stream?placas=${encodeURIComponent(texto)}`;
        acheCarEventSource = new EventSource(url);

        acheCarEventSource.onmessage = (event) => {
            if (!event.data) return;
            try {
                const data = JSON.parse(event.data);

                if (data.tipo === 'inicio') {
                    if (progressText) progressText.textContent = data.mensagem;
                } else if (data.tipo === 'consultando') {
                    if (progressText) progressText.textContent = data.mensagem;
                    if (progressPct) progressPct.textContent = `${data.percentual}%`;
                    if (progressFill) progressFill.style.width = `${data.percentual}%`;
                } else if (data.tipo === 'progresso') {
                    if (progressPct) progressPct.textContent = `${data.percentual}%`;
                    if (progressFill) progressFill.style.width = `${data.percentual}%`;
                    if (data.resultado) {
                        acheCarResultados.push(data.resultado);
                        adicionarLinhaAcheCar(data.resultado);
                    }
                } else if (data.tipo === 'pausa') {
                    if (progressText) progressText.textContent = data.mensagem;
                } else if (data.tipo === 'tentativa') {
                    if (progressText) {
                        progressText.innerHTML = `<i class="fa-solid fa-arrows-rotate fa-spin" style="color: #F59E0B;"></i> ${data.mensagem}`;
                    }
                    showToast(data.mensagem, 'warning');
                } else if (data.tipo === 'alerta') {
                    showToast(data.mensagem, 'warning');
                } else if (data.tipo === 'concluido' || data.tipo === 'erro') {
                    if (progressText) progressText.textContent = data.mensagem;
                    if (progressPct) progressPct.textContent = '100%';
                    if (progressFill) progressFill.style.width = '100%';

                    acheCarEventSource.close();
                    acheCarEventSource = null;
                    btn.disabled = false;
                    btn.innerHTML = '<i class="fa-solid fa-search"></i> Consultar Placas';

                    showToast(data.mensagem, data.tipo === 'erro' ? 'error' : 'success');
                }
            } catch (err) {
                console.error('Erro ao processar evento SSE AcheCar:', err);
            }
        };

        acheCarEventSource.onerror = (err) => {
            console.error('Erro na conexão SSE AcheCar:', err);
            if (acheCarEventSource) {
                acheCarEventSource.close();
                acheCarEventSource = null;
            }
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-search"></i> Consultar Placas';
            if (progressText) progressText.textContent = 'Consulta finalizada.';
        };
    } catch (err) {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-search"></i> Consultar Placas';
        showToast(`Erro ao iniciar consulta: ${err.message}`, 'error');
    }
}
window.consultarAcheCar = consultarAcheCarStream;

// --------------------------------------------------------------------
// TAB 2: CONSULTA LOCAL DE INSTALAÇÃO (COM PROGRESSO & BLOCO ÚNICO PARA 2 EQUIPAMENTOS)
// --------------------------------------------------------------------
let localResultados = [];

function adicionarCardLocal(item) {
    const container = document.getElementById('locais-cards-container');
    if (!container) return;

    const card = document.createElement('div');
    card.className = 'local-result-card';

    if (item.sucesso && item.seriais && item.seriais.length > 0) {
        const badgeMulti = item.possui_multiplos_equipamentos
            ? `<span class="local-multi-badge"><i class="fa-solid fa-layer-group"></i> ${item.total_equipamentos} Equipamentos Vinculados</span>`
            : '';

        let seriaisHtml = '';
        item.seriais.forEach((ser, idx) => {
            const labelEquip = item.possui_multiplos_equipamentos ? `Equipamento ${ser.numero_equipamento || (idx + 1)}` : 'Equipamento Único';
            const dataFormatada = ser.data_execucao ? formatarDataIso(ser.data_execucao) : 'Sem data';
            const badgeClass = ser.possui_os ? 'badge-success' : 'badge-warning';
            const statusText = ser.status ? `Status (${ser.status})` : 'Sem OS Válida';

            seriaisHtml += `
                <div class="local-equip-item">
                    <div class="equip-label">${labelEquip}</div>
                    <div class="equip-serial"><i class="fa-solid fa-microchip"></i> Serial: <strong>${ser.serial}</strong></div>
                    <div class="equip-local"><i class="fa-solid fa-location-dot" style="color: #F97316;"></i> ${ser.local}</div>
                    <div class="equip-meta" style="margin-top: 6px; display: flex; align-items: center; justify-content: space-between;">
                        <span><i class="fa-regular fa-calendar"></i> ${dataFormatada}</span>
                        <span class="badge ${badgeClass}">${statusText}</span>
                    </div>
                </div>
            `;
        });

        card.innerHTML = `
            <div class="local-card-header">
                <div>
                    <span class="tag-placa">${item.identificador}</span>
                </div>
                <div>${badgeMulti}</div>
            </div>
            <div class="local-equipamentos-grid">
                ${seriaisHtml}
            </div>
        `;
    } else {
        card.innerHTML = `
            <div class="local-card-header">
                <span class="tag-placa">${item.identificador}</span>
                <span class="badge badge-danger"><i class="fa-solid fa-ban"></i> Não Localizado</span>
            </div>
            <div class="local-error-text">
                ${item.erro || 'Sem dispositivo vinculado ou não encontrado na base WebRota.'}
            </div>
        `;
    }

    container.appendChild(card);
}

async function consultarLocalInstalacaoStream() {
    const input = document.getElementById('input-locais');
    const btn = document.getElementById('btn-consultar-local');
    const resultCard = document.getElementById('resultado-local');
    const container = document.getElementById('locais-cards-container');

    const progressWrapper = document.getElementById('progress-local');
    const progressText = document.getElementById('progress-local-text');
    const progressPct = document.getElementById('progress-local-pct');
    const progressFill = document.getElementById('progress-local-fill');

    const texto = input.value.trim();
    if (!texto) {
        showToast('Informe as placas ou identificadores de equipamentos.', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Rastreando OS...';
    resultCard.style.display = 'block';
    container.innerHTML = '';
    localResultados = [];

    if (progressWrapper) {
        progressWrapper.style.display = 'block';
        if (progressFill) progressFill.style.width = '0%';
        if (progressPct) progressPct.textContent = '0%';
        if (progressText) progressText.textContent = 'Iniciando busca de locais...';
    }

    // Scroll suave para os resultados no mobile
    setTimeout(() => {
        resultCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 150);

    try {
        const response = await fetch('/api/consulta/local/stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identificadores: texto })
        });

        if (!response.ok) {
            throw new Error(`Erro no servidor: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const linhas = buffer.split('\n\n');
            buffer = linhas.pop() || '';

            for (const linha of linhas) {
                const trimmed = linha.trim();
                if (trimmed.startsWith('data:')) {
                    try {
                        const jsonStr = trimmed.replace(/^data:\s*/, '');
                        const data = JSON.parse(jsonStr);

                        if (data.tipo === 'inicio') {
                            if (progressText) progressText.textContent = data.mensagem;
                        } else if (data.tipo === 'consultando') {
                            if (progressText) progressText.textContent = data.mensagem;
                            if (progressPct) progressPct.textContent = `${data.percentual}%`;
                            if (progressFill) progressFill.style.width = `${data.percentual}%`;
                        } else if (data.tipo === 'tentativa') {
                            if (progressText) {
                                progressText.innerHTML = `<i class="fa-solid fa-arrows-rotate fa-spin" style="color: #F59E0B;"></i> ${data.mensagem}`;
                            }
                            showToast(data.mensagem, 'warning');
                        } else if (data.tipo === 'progresso') {
                            if (progressPct) progressPct.textContent = `${data.percentual}%`;
                            if (progressFill) progressFill.style.width = `${data.percentual}%`;
                            if (data.resultado) {
                                localResultados.push(data.resultado);
                                adicionarCardLocal(data.resultado);
                            }
                        } else if (data.tipo === 'concluido' || data.tipo === 'erro') {
                            if (progressText) progressText.textContent = data.mensagem;
                            if (progressPct) progressPct.textContent = '100%';
                            if (progressFill) progressFill.style.width = '100%';
                            showToast(data.mensagem, data.tipo === 'erro' ? 'error' : 'success');
                        }
                    } catch (parseErr) {
                        console.error('Erro de decodificação no evento:', parseErr);
                    }
                }
            }
        }
    } catch (err) {
        showToast(`Erro na busca de locais: ${err.message}`, 'error');
        if (progressText) progressText.textContent = 'Erro ao consultar.';
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Buscar Locais de Instalação';
    }
}
window.consultarLocalInstalacao = consultarLocalInstalacaoStream;

// --------------------------------------------------------------------
// TAB 4: RANKINGS DE EXECUÇÃO (HORÁRIO RESTRITO 08H ÀS 18H)
// --------------------------------------------------------------------
async function carregarRankingDiario() {
    const container = document.getElementById('lista-ranking-diario');
    if (!container) return;
    const totalSpan = document.getElementById('total-os-diario');
    const dataLabel = document.getElementById('data-label-diario');
    const proximaAtt = document.getElementById('proxima-att-diario');
    const badgeJanela = document.getElementById('badge-janela-diario');
    const dataInput = document.getElementById('data-filtro-ranking');

    container.innerHTML = '<div class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Carregando ranking do dia...</div>';

    const dataSel = dataInput ? dataInput.value : '';
    const url = dataSel ? `/api/ranking/diario?data=${dataSel}` : '/api/ranking/diario';

    try {
        const resp = await fetch(url);
        const data = await resp.json();

        if (badgeJanela) {
            if (data.janela_ativa) {
                badgeJanela.className = 'ranking-janela-badge janela-ativa';
                badgeJanela.innerHTML = '<i class="fa-solid fa-circle-check"></i> Horário Operacional (08h às 18h)';
            } else {
                badgeJanela.className = 'ranking-janela-badge janela-inativa';
                badgeJanela.innerHTML = '<i class="fa-solid fa-clock"></i> Ranking Congelado (Fora de 08h-18h)';
            }
        }

        if (proximaAtt) {
            proximaAtt.textContent = data.proxima_atualizacao || '--';
        }

        if (!data.sucesso) {
            container.innerHTML = `<div class="empty-state">${data.erro || 'Não foi possível carregar o ranking.'}</div>`;
            totalSpan.textContent = '0';
            dataLabel.textContent = '--';
            return;
        }

        totalSpan.textContent = `${data.total_os} OS`;
        dataLabel.textContent = data.data || '--';

        if (!data.ranking || data.ranking.length === 0) {
            const msgVazio = data.mensagem_horario || 'Nenhuma Ordem de Serviço executada nesta data até o momento.';
            container.innerHTML = `<div class="empty-state">${msgVazio}</div>`;
            return;
        }

        container.innerHTML = '';
        data.ranking.forEach(item => {
            let podiumIcon = `<span>${item.posicao}º</span>`;
            if (item.posicao === 1) podiumIcon = '<i class="fa-solid fa-crown text-gold"></i>';
            else if (item.posicao === 2) podiumIcon = '<i class="fa-solid fa-medal text-silver"></i>';
            else if (item.posicao === 3) podiumIcon = '<i class="fa-solid fa-award text-bronze"></i>';

            const row = document.createElement('div');
            row.className = 'ranking-row';
            row.innerHTML = `
                <div class="ranking-podium-icon">${podiumIcon}</div>
                <div class="ranking-info">
                    <div class="ranking-name">
                        <span>${item.nome}</span>
                        <strong style="color: #F97316;">${item.quantidade} OS <small style="color: var(--text-muted); font-weight: normal;">(${item.percentual}%)</small></strong>
                    </div>
                    <div class="ranking-bar-container">
                        <div class="ranking-bar-fill" style="width: ${item.percentual}%; background: linear-gradient(90deg, #F97316, #FB923C);"></div>
                    </div>
                </div>
            `;
            container.appendChild(row);
        });
    } catch (err) {
        container.innerHTML = `<div class="empty-state">Erro ao buscar dados: ${err.message}</div>`;
    }
}

async function carregarRankingMensal() {
    const container = document.getElementById('lista-ranking-mensal');
    if (!container) return;
    const totalSpan = document.getElementById('total-os-mensal');
    const periodoLabel = document.getElementById('periodo-label-mensal');
    const proximaAtt = document.getElementById('proxima-att-mensal');
    const badgeJanela = document.getElementById('badge-janela-mensal');

    container.innerHTML = '<div class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Carregando comparativo mensal...</div>';

    try {
        const resp = await fetch('/api/ranking/mensal');
        const data = await resp.json();

        if (badgeJanela) {
            if (data.janela_ativa) {
                badgeJanela.className = 'ranking-janela-badge janela-ativa';
                badgeJanela.innerHTML = '<i class="fa-solid fa-circle-check"></i> Horário Operacional (08h às 18h)';
            } else {
                badgeJanela.className = 'ranking-janela-badge janela-inativa';
                badgeJanela.innerHTML = '<i class="fa-solid fa-clock"></i> Ranking Congelado (Fora de 08h-18h)';
            }
        }

        if (proximaAtt) {
            proximaAtt.textContent = data.proxima_atualizacao || '--';
        }

        if (!data.sucesso) {
            container.innerHTML = `<div class="empty-state">${data.erro || 'Não foi possível carregar o ranking mensal.'}</div>`;
            totalSpan.textContent = '0';
            periodoLabel.textContent = '--';
            return;
        }

        totalSpan.textContent = `${data.total_comparativo} OS`;
        periodoLabel.textContent = data.periodo || '--';

        if (!data.ranking || data.ranking.length === 0) {
            const msgVazio = data.mensagem_horario || 'Nenhum dado registrado para o período.';
            container.innerHTML = `<div class="empty-state">${msgVazio}</div>`;
            return;
        }

        container.innerHTML = '';
        data.ranking.forEach(item => {
            let medal = `<span>${item.posicao}º</span>`;
            if (item.posicao === 1) medal = '<i class="fa-solid fa-trophy text-gold"></i>';
            else if (item.posicao === 2) medal = '<i class="fa-solid fa-medal text-silver"></i>';

            const row = document.createElement('div');
            row.className = 'ranking-row';
            row.innerHTML = `
                <div class="ranking-podium-icon">${medal}</div>
                <div class="ranking-info">
                    <div class="ranking-name">
                        <span>${item.nome}</span>
                        <strong style="color: #F97316;">${item.total} OS <small style="color: var(--text-muted); font-weight: normal;">(${item.percentual}%)</small></strong>
                    </div>
                    <div class="ranking-bar-container">
                        <div class="ranking-bar-fill" style="width: ${item.percentual}%; background: linear-gradient(90deg, #F97316, #FB923C);"></div>
                    </div>
                </div>
            `;
            container.appendChild(row);
        });
    } catch (err) {
        container.innerHTML = `<div class="empty-state">Erro: ${err.message}</div>`;
    }
}

// --------------------------------------------------------------------
// UTILITÁRIOS (LIMPAR, COPIAR, EXPORTAR CSV, TOASTS)
// --------------------------------------------------------------------
function limparCampo(inputId, resultCardId) {
    const input = document.getElementById(inputId);
    if (input) input.value = '';

    const card = document.getElementById(resultCardId);
    if (card) card.style.display = 'none';

    if (resultCardId === 'resultado-achecar') {
        acheCarResultados = [];
        const tbody = document.getElementById('tbody-achecar');
        if (tbody) tbody.innerHTML = '';
        const countSpan = document.getElementById('count-achecar');
        if (countSpan) countSpan.textContent = '0';
    } else if (resultCardId === 'resultado-local') {
        localResultados = [];
        const container = document.getElementById('locais-cards-container');
        if (container) container.innerHTML = '';
    }

    showToast('Campos e resultados limpos.', 'info');
}

function formatarDataIso(isoStr) {
    try {
        const dt = new Date(isoStr);
        return dt.toLocaleDateString('pt-BR', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    } catch (e) {
        return isoStr;
    }
}

// --------------------------------------------------------------------
// FUNÇÕES DE CÓPIA: MENSAGEM ORGANIZADA & CSV (PLANILHA)
// --------------------------------------------------------------------

/**
 * Copia os resultados de Consulta de Placa (AcheCar) no formato de mensagem organizada
 */
function copiarMensagemAcheCar() {
    if (!acheCarResultados || acheCarResultados.length === 0) {
        showToast('Nenhum dado consultado para copiar.', 'warning');
        return;
    }

    const blocos = acheCarResultados.map(item => {
        if (item.sucesso) {
            const marcaModelo = `${item.marca || 'N/A'} ${item.modelo || ''}`.trim();
            const ano = `${item.ano_fabricacao || 'N/A'} / ${item.ano_modelo || 'N/A'}`;
            const tipoComb = `${item.tipo_veiculo || 'N/A'} - ${item.combustivel || 'N/A'}`;
            const munUf = `${item.municipio || 'N/A'} / ${item.uf || 'N/A'}`;
            return [
                `🚗 *Placa:* ${item.placa}`,
                `• *Marca/Modelo:* ${marcaModelo}`,
                `• *Ano:* ${ano}`,
                `• *Cor:* ${item.cor || 'N/A'}`,
                `• *Tipo/Comb.:* ${tipoComb}`,
                `• *Município/UF:* ${munUf}`,
                `• *Status:* Encontrado`
            ].join('\n');
        } else {
            return [
                `🚗 *Placa:* ${item.placa}`,
                `• *Status:* Falha (${item.erro || 'Não foi possível obter os dados.'})`
            ].join('\n');
        }
    });

    const textoFinal = blocos.join('\n\n' + '─'.repeat(36) + '\n\n');
    navigator.clipboard.writeText(textoFinal).then(() => {
        showToast('Mensagem organizada copiada com sucesso!', 'success');
    }).catch(() => {
        showToast('Não foi possível copiar para a área de transferência.', 'error');
    });
}
window.copiarMensagemAcheCar = copiarMensagemAcheCar;

/**
 * Copia os resultados de Consulta de Placa (AcheCar) no formato de planilha (TSV com cabeçalho)
 */
function copiarCSVAcheCar() {
    if (!acheCarResultados || acheCarResultados.length === 0) {
        showToast('Nenhum dado consultado para copiar.', 'warning');
        return;
    }

    const colunas = ['Placa', 'Marca / Modelo', 'Ano Fab / Modelo', 'Cor', 'Tipo / Combustível', 'Município - UF', 'Status'];
    const linhas = acheCarResultados.map(item => {
        if (item.sucesso) {
            const marcaModelo = `${item.marca || ''} ${item.modelo || ''}`.trim();
            const ano = `${item.ano_fabricacao || ''} / ${item.ano_modelo || ''}`.trim();
            const tipoComb = `${item.tipo_veiculo || ''} - ${item.combustivel || ''}`.trim();
            const munUf = `${item.municipio || ''} - ${item.uf || ''}`.trim();
            return [
                item.placa,
                marcaModelo,
                ano,
                item.cor || '',
                tipoComb,
                munUf,
                'Encontrado'
            ].join('\t');
        } else {
            return [
                item.placa,
                '-',
                '-',
                '-',
                '-',
                '-',
                item.erro || 'Falha'
            ].join('\t');
        }
    });

    const csvFinal = [colunas.join('\t'), ...linhas].join('\n');
    navigator.clipboard.writeText(csvFinal).then(() => {
        showToast('Planilha (CSV) copiada para a área de transferência!', 'success');
    }).catch(() => {
        showToast('Não foi possível copiar os dados.', 'error');
    });
}
window.copiarCSVAcheCar = copiarCSVAcheCar;

/**
 * Copia os resultados de Local de Instalação no formato de mensagem organizada
 */
function copiarMensagemLocal() {
    if (!localResultados || localResultados.length === 0) {
        showToast('Nenhum dado consultado para copiar.', 'warning');
        return;
    }

    const blocos = localResultados.map(item => {
        let texto = `🛠️ *Placa/Identificador:* ${item.identificador}`;
        if (item.sucesso && item.seriais && item.seriais.length > 0) {
            item.seriais.forEach((ser, idx) => {
                const labelEquip = item.possui_multiplos_equipamentos ? ` (Equipamento ${ser.numero_equipamento || (idx + 1)})` : '';
                const dataFormatada = ser.data_execucao ? formatarDataIso(ser.data_execucao) : 'Sem data';
                const statusText = ser.status ? `Status (${ser.status})` : 'Sem OS Válida';
                texto += `\n• *Serial${labelEquip}:* ${ser.serial}`;
                texto += `\n• *Local de Instalação:* ${ser.local || 'Não informado'}`;
                texto += `\n• *Data da OS:* ${dataFormatada}`;
                texto += `\n• *Status da OS:* ${statusText}`;
            });
        } else {
            texto += `\n• *Status:* Não Localizado (${item.erro || 'Sem dispositivo vinculado ou não encontrado'})`;
        }
        return texto;
    });

    const textoFinal = blocos.join('\n\n' + '─'.repeat(36) + '\n\n');
    navigator.clipboard.writeText(textoFinal).then(() => {
        showToast('Mensagem organizada copiada com sucesso!', 'success');
    }).catch(() => {
        showToast('Não foi possível copiar para a área de transferência.', 'error');
    });
}
window.copiarMensagemLocal = copiarMensagemLocal;

/**
 * Copia os resultados de Local de Instalação no formato de planilha (TSV com cabeçalho)
 */
function copiarCSVLocal() {
    if (!localResultados || localResultados.length === 0) {
        showToast('Nenhum dado consultado para copiar.', 'warning');
        return;
    }

    const colunas = ['Placa / Identificador', 'Equipamento', 'Serial', 'Local de Instalação', 'Data da OS', 'Status da OS'];
    const linhas = [];

    localResultados.forEach(item => {
        if (item.sucesso && item.seriais && item.seriais.length > 0) {
            item.seriais.forEach((ser, idx) => {
                const equip = item.possui_multiplos_equipamentos ? `Equipamento ${ser.numero_equipamento || (idx + 1)}` : 'Equipamento Único';
                const dataFormatada = ser.data_execucao ? formatarDataIso(ser.data_execucao) : 'Sem data';
                const statusText = ser.status ? `Status (${ser.status})` : 'Sem OS Válida';
                linhas.push([
                    item.identificador,
                    equip,
                    ser.serial || '',
                    ser.local || '',
                    dataFormatada,
                    statusText
                ].join('\t'));
            });
        } else {
            linhas.push([
                item.identificador,
                '-',
                '-',
                item.erro || 'Não localizado',
                '-',
                'Não Localizado'
            ].join('\t'));
        }
    });

    const csvFinal = [colunas.join('\t'), ...linhas].join('\n');
    navigator.clipboard.writeText(csvFinal).then(() => {
        showToast('Planilha (CSV) copiada para a área de transferência!', 'success');
    }).catch(() => {
        showToast('Não foi possível copiar os dados.', 'error');
    });
}
window.copiarCSVLocal = copiarCSVLocal;

function copiarTabela(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;

    let text = '';
    const rows = table.querySelectorAll('tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('th, td');
        const rowText = Array.from(cells).map(c => c.innerText.trim().replace(/\s+/g, ' ')).join('\t');
        text += rowText + '\n';
    });

    navigator.clipboard.writeText(text).then(() => {
        showToast('Dados copiados para a área de transferência!', 'success');
    }).catch(() => {
        showToast('Não foi possível copiar os dados.', 'error');
    });
}

function exportarCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;

    let csv = [];
    const rows = table.querySelectorAll('tr');

    rows.forEach(row => {
        const rowData = [];
        const cols = row.querySelectorAll('th, td');
        cols.forEach(col => {
            let data = col.innerText.replace(/"/g, '""').trim();
            rowData.push(`"${data}"`);
        });
        csv.push(rowData.join(';'));
    });

    const csvFile = new Blob(["\uFEFF" + csv.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const downloadLink = document.createElement('a');
    downloadLink.download = filename;
    downloadLink.href = window.URL.createObjectURL(csvFile);
    downloadLink.style.display = 'none';
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    showToast(`Arquivo ${filename} exportado com sucesso!`, 'success');
}

function showToast(mensagem, tipo = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${tipo}`;

    const iconMap = {
        success: 'fa-circle-check',
        error: 'fa-circle-xmark',
        warning: 'fa-triangle-exclamation',
        info: 'fa-circle-info'
    };

    toast.innerHTML = `
        <i class="fa-solid ${iconMap[tipo] || 'fa-circle-info'}"></i>
        <span>${mensagem}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ====================================================================
// CHAT IA - ASSISTENTE TÉCNICO DOS MANUAIS SUNTECH (REDE NEURAL)
// ====================================================================

const INTENT_LABELS = {
    'fios_chicote': 'Fios & Chicote',
    'calibracao_dpa': 'Calibração DPA',
    'leds_diagnostico': 'Diagnóstico de LEDs',
    'bloqueio_rele': 'Bloqueio & Relé 5 Pinos',
    'antifurto': 'Sistema Antifurto',
    'jornada_trabalho': 'Jornada de Trabalho',
    'modo_idle': 'Modo Ocioso / Idle',
    'comandos': 'Comandos de Configuração',
    'comandos_rs232': 'Comunicação Serial RS232',
    'diferencas_modelos': 'Comparativo de Modelos',
    'especificacoes': 'Especificações Técnicas',
    'chip_sim': 'Instalação do Chip SIM',
    'configuracao_synctrak': 'Configurador Synctrak',
    'bateria_consumo': 'Bateria & Consumo de Energia',
    'cercas': 'Cercas Virtuais',
    'instalacao_eletrica': 'Instalação Elétrica & Segurança'
};

const INITIAL_WELCOME_HTML = `
    <div class="chat-bubble bot-bubble">
        <div class="bubble-avatar">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="bubble-content">
            <div class="bubble-header">
                <strong>Assistente Técnico IA</strong>
                <span class="meta-tag">Rede Neural Oficial</span>
            </div>
            <div class="bubble-text">
                <p>Olá! Sou seu assistente técnico treinado nos manuais oficiais dos aparelhos <strong>Suntech e Queclink</strong>.</p>
                <p style="margin-top: 6px;">Pergunte qualquer dúvida sobre cores de fios, chicotes, relés de bloqueio, calibração DPA, LEDs ou configurações de rastreadores.</p>
            </div>
        </div>
    </div>
`;

const PROMPT_CATEGORIES_DATA = {
    'frequentes': [
        'Qual o fio pós-chave do Queclink GV50CG?',
        'Como ligar o relé com diodo no Queclink GV50CG?',
        'Qual a cor do fio pós-chave no ST340UR?',
        'Como calibrar o DPA por ignição no ST8300?',
        'LED vermelho piscando 4 vezes o que significa?',
        'Qual a diferença entre ST310U e ST310ULC?',
        'Como ligar o relé de 5 pinos na bomba de combustível?',
        'Qual a senha padrão para conectar no Synctrak?',
        'O ST340UR aguenta água e chuva?'
    ],
    'gv50cg': [
        'Qual o fio de pós-chave do Queclink GV50CG?',
        'Como ligar o relé com diodo 1N4004 no GV50CG?',
        'Chicote completo do Queclink GV50CG 5 pinos',
        'O que significa o LED verde piscando rápido no GV50CG?',
        'O que significa o LED azul GNSS no GV50CG?',
        'Orientação da antena THIS SIDE TOWARDS SKY no GV50CG',
        'Tensão de alimentação do GV50CG 9V a 90V',
        'Como colocar o chip Micro-SIM e ligar a bateria no GV50CG?'
    ],
    'fios': [
        'Chicote do Queclink GV50CG 5 pinos',
        'Chicote do ST340UR pinagem e cores',
        'Qual fio é a ignição no ST8300?',
        'Para que serve o fio branco no ST310?',
        'Chicote do ST8310UM pinagem dos 5 fios',
        'Fios do chicote serial RS232 de 4 vias',
        'Chicote de áudio do ST8300R microfone e speaker'
    ],
    'dpa': [
        'Quantas ignições para calibrar o ST8310UM?',
        'Sequência de 7 ignições meia chave ST340UR',
        'Como calibrar DPA por comando no Synctrak',
        'O que significa LEDs piscando a cada 0.5s?',
        'Calibração DPA por ignição no ST8300'
    ],
    'rele': [
        'Como ligar o relé com diodo 1N4004 no Queclink GV50CG?',
        'Como ligar relé de 5 pinos na bomba',
        'Onde ligar os pinos 85 e 86 do relé de bloqueio?',
        'Qual a saída do rastreador para bloqueio?',
        'Como ligar sirene ou buzzer no rastreador?'
    ],
    'leds': [
        'O que significa o LED verde piscando rápido no GV50CG?',
        'LED vermelho piscando 4 vezes (antena/chipset)',
        'LED vermelho piscando 2 vezes (sem sinal GPS)',
        'LED azul com 2 piscadas (erro no servidor)',
        'LED azul piscando 3 vezes (erro comunicação)',
        'LED azul piscando 7 vezes (sem SIM card)',
        'LED azul com 5 piscadas (PIN bloqueado)'
    ],
    'synctrak': [
        'Senha de fábrica do Synctrak st5656',
        'Como conectar o rastreador no Synctrak via USB',
        'Servidores padrão AGPS e Scuti de manutenção',
        'Como configurar jornada de trabalho no ST8300?',
        'Como configurar modo idle ocioso no ST8300?',
        'Como configurar cerca circular no mapa'
    ]
};

let chatHistorico = [];

function initChatIA() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input-text');
    const chatMessages = document.getElementById('chat-messages-container');
    const btnLimpar = document.getElementById('btn-limpar-chat');
    const inputAparelhoHidden = document.getElementById('chat-filtro-aparelho');
    const btnScrollBottom = document.getElementById('btn-scroll-bottom');

    if (!chatForm || !chatInput || !chatMessages) return;

    // 1. Detecção de Scroll para Botão Flutuante 'Descer'
    chatMessages.addEventListener('scroll', () => {
        if (!btnScrollBottom) return;
        const distFim = chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight;
        if (distFim > 140) {
            btnScrollBottom.classList.add('visible');
        } else {
            btnScrollBottom.classList.remove('visible');
        }
    });

    if (btnScrollBottom) {
        btnScrollBottom.addEventListener('click', () => {
            scrollChatToBottom();
            btnScrollBottom.classList.remove('visible');
        });
    }

    // 5. Ajuste automático de altura do textarea conforme digitação
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // 6. Enviar ao pressionar Enter (sem Shift)
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.requestSubmit();
        }
    });

    // 7. Envio do formulário
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const texto = chatInput.value.trim();
        if (!texto) return;

        const aparelho = inputAparelhoHidden ? inputAparelhoHidden.value : null;

        // Limpa input e reseta altura
        chatInput.value = '';
        chatInput.style.height = 'auto';

        // Adiciona bolha do usuário
        appendUserMessage(texto);

        // Adiciona indicador animado de digitação
        const typingId = appendTypingIndicator();

        try {
            const resp = await fetch('/api/chat/perguntar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    mensagem: texto,
                    aparelho: aparelho || null,
                    historico: chatHistorico
                })
            });

            const data = await resp.json();

            // Remove indicador de digitação
            removeTypingIndicator(typingId);

            if (resp.ok && data.sucesso) {
                appendBotMessage(data);
                // Atualiza histórico na sessão
                chatHistorico.push({ role: 'user', content: texto });
                chatHistorico.push({ role: 'assistant', content: data.resposta });
                if (chatHistorico.length > 10) chatHistorico = chatHistorico.slice(-10);

                // Atualiza indicador de latência no rodapé
                const latencyBadge = document.getElementById('chat-latency-badge');
                if (latencyBadge) {
                    latencyBadge.innerHTML = `<i class="fa-solid fa-bolt"></i> Inferência Neural: ${data.tempo_ms}ms (${data.confianca}% confiança)`;
                }
            } else {
                appendErrorMessage(data.detail || 'Ocorreu um erro ao consultar a rede neural.');
                showToast(data.detail || 'Erro ao processar dúvida', 'error');
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            appendErrorMessage('Falha de conexão com o servidor. Verifique se o sistema está em execução.');
            showToast('Erro de conexão ao consultar a IA', 'error');
        }
    });

    // 8. Botão Limpar Conversa
    if (btnLimpar) {
        btnLimpar.addEventListener('click', () => {
            chatHistorico = [];
            chatMessages.innerHTML = INITIAL_WELCOME_HTML;
            const latencyBadge = document.getElementById('chat-latency-badge');
            if (latencyBadge) {
                latencyBadge.innerHTML = `<i class="fa-solid fa-bolt"></i> Inferência Neural Instantânea`;
            }
            showToast('Histórico do chat reiniciado com sucesso!', 'info');
        });
    }
}

function renderizarChipsCategoria(categoria) {
    const container = document.getElementById('chat-suggestions-chips');
    if (!container) return;

    const lista = PROMPT_CATEGORIES_DATA[categoria] || PROMPT_CATEGORIES_DATA['frequentes'];
    container.innerHTML = lista.map(item => `
        <button type="button" class="chip-btn" data-query="${escapeHtml(item)}" onclick="executarDuvidaRapida('${escapeHtml(item).replace(/'/g, "\\'")}')">
            ${escapeHtml(item)}
        </button>
    `).join('');
}

function appendUserMessage(text) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const agora = new Date();
    const horaFormatada = agora.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble user-bubble';
    bubble.innerHTML = `
        <div class="bubble-avatar">
            <i class="fa-solid fa-user"></i>
        </div>
        <div class="bubble-content">
            <div class="bubble-header" style="justify-content: flex-end;">
                <span class="meta-tag" style="font-size: 11px; opacity: 0.7;">${horaFormatada}</span>
                <strong>Você</strong>
            </div>
            <div class="bubble-text">${escapeHtml(text)}</div>
        </div>
    `;

    container.appendChild(bubble);
    scrollChatToBottom();
}

function appendTypingIndicator() {
    const container = document.getElementById('chat-messages-container');
    if (!container) return null;

    const id = 'typing-' + Date.now();
    const bubble = document.createElement('div');
    bubble.id = id;
    bubble.className = 'chat-bubble bot-bubble';
    bubble.innerHTML = `
        <div class="bubble-avatar">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="bubble-content">
            <div class="bubble-header">
                <strong>Assistente Técnico IA</strong>
                <span class="meta-tag">Processando na Rede Neural...</span>
            </div>
            <div class="bubble-text" style="padding: 12px 18px;">
                <div class="typing-dots">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        </div>
    `;

    container.appendChild(bubble);
    scrollChatToBottom();
    return id;
}

function removeTypingIndicator(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
}

function appendBotMessage(data) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const intentNome = INTENT_LABELS[data.intencao] || data.intencao;
    const htmlResposta = renderMarkdownToHtml(data.resposta);

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble bot-bubble';

    // Monta pills de fontes se houver
    let fontesHtml = '';
    if (data.fontes && data.fontes.length > 0) {
        const pills = data.fontes.map(f => `<span class="source-pill">${escapeHtml(f)}</span>`).join('');
        fontesHtml = `
            <div class="sources-card">
                <strong><i class="fa-solid fa-book-open"></i> Manuais Consultados:</strong>
                <div class="sources-list">${pills}</div>
            </div>
        `;
    }

    // Monta sugestões de continuação clicáveis
    let sugestoesHtml = '';
    if (data.sugestoes && data.sugestoes.length > 0) {
        const botoes = data.sugestoes.map(s => `
            <button class="followup-btn" onclick="executarDuvidaRapida('${escapeHtml(s).replace(/'/g, "\\'")}')">
                <i class="fa-regular fa-comment-dots"></i> ${escapeHtml(s)}
            </button>
        `).join('');

        sugestoesHtml = `
            <div class="bubble-followups">
                <span class="followup-label"><i class="fa-solid fa-lightbulb"></i> Perguntas Relacionadas:</span>
                <div class="followup-chips-row">${botoes}</div>
            </div>
        `;
    }

    bubble.innerHTML = `
        <div class="bubble-avatar">
            <i class="fa-solid fa-robot"></i>
        </div>
        <div class="bubble-content">
            <div class="bubble-header">
                <strong>Assistente Técnico IA</strong>
            </div>

            <div class="meta-badges-row">
                <span class="meta-badge badge-intent" title="Intenção classificada pela Rede Neural">
                    <i class="fa-solid fa-bullseye"></i> ${escapeHtml(intentNome)}
                </span>
                <span class="meta-badge badge-device" title="Aparelho identificado">
                    <i class="fa-solid fa-microchip"></i> ${escapeHtml(data.aparelho_detectado || 'Geral')}
                </span>
                <span class="meta-badge badge-confidence" title="Grau de certeza da inferência neural">
                    <i class="fa-solid fa-shield-check"></i> ${data.confianca}% precisão
                </span>
                <span class="meta-badge badge-speed" title="Tempo de resposta da rede neural">
                    <i class="fa-solid fa-gauge-high"></i> ${data.tempo_ms}ms
                </span>
            </div>

            <div class="bubble-text">
                ${htmlResposta}
                ${fontesHtml}
                ${sugestoesHtml}
                <div class="bubble-actions-row">
                    <button class="btn-copy-bubble" onclick="copiarTextoResposta(this)">
                        <i class="fa-regular fa-copy"></i> Copiar Resposta
                    </button>
                </div>
            </div>
        </div>
    `;

    container.appendChild(bubble);
    scrollChatToBottom();
}

function appendErrorMessage(msg) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return;

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble bot-bubble';
    bubble.innerHTML = `
        <div class="bubble-avatar" style="background: rgba(239, 68, 68, 0.2); color: #EF4444;">
            <i class="fa-solid fa-circle-exclamation"></i>
        </div>
        <div class="bubble-content">
            <div class="bubble-header">
                <strong>Assistente Técnico IA</strong>
                <span class="meta-tag" style="background: rgba(239, 68, 68, 0.15); color: #F87171;">Aviso</span>
            </div>
            <div class="bubble-text" style="border-color: rgba(239, 68, 68, 0.4);">
                <p style="color: #FCA5A5;">${escapeHtml(msg)}</p>
            </div>
        </div>
    `;

    container.appendChild(bubble);
    scrollChatToBottom();
}

function executarDuvidaRapida(query) {
    const chatInput = document.getElementById('chat-input-text');
    const chatForm = document.getElementById('chat-form');
    if (chatInput && chatForm) {
        chatInput.value = query;
        chatForm.requestSubmit();
    }
}

function copiarTextoResposta(botao) {
    const bubbleText = botao.closest('.bubble-text');
    if (!bubbleText) return;

    // Clona para remover botões do texto copiado
    const clone = bubbleText.cloneNode(true);
    const actions = clone.querySelector('.bubble-actions-row');
    if (actions) actions.remove();
    const followups = clone.querySelector('.bubble-followups');
    if (followups) followups.remove();

    const textoLimpo = clone.innerText.trim();
    navigator.clipboard.writeText(textoLimpo).then(() => {
        showToast('Resposta copiada para a área de transferência!', 'success');
        botao.innerHTML = '<i class="fa-solid fa-check"></i> Copiado!';
        setTimeout(() => {
            botao.innerHTML = '<i class="fa-regular fa-copy"></i> Copiar Resposta';
        }, 2000);
    }).catch(() => {
        showToast('Não foi possível copiar automaticamente.', 'warning');
    });
}

function scrollChatToBottom() {
    const container = document.getElementById('chat-messages-container');
    if (container) {
        setTimeout(() => {
            container.scrollTop = container.scrollHeight;
        }, 50);
    }
}

function escapeHtml(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function renderMarkdownToHtml(md) {
    if (!md) return '';

    let html = md;

    // Extrai e estiliza cartões de Resposta Direta (> 👉 **Resposta Direta...**)
    html = html.replace(/^\>\s*👉\s*\*\*Resposta Direta(?:\s*\((.*?)\))?:\*\*\s*(.*?)(?=\n\n|\n[^\>]|$)/gims, (match, sub, conteudo) => {
        const titulo = sub ? `Resposta Direta (${sub})` : 'Resposta Direta ao Instalador';
        return `
            <div class="direct-answer-card">
                <i class="fa-solid fa-circle-check" style="color: #38BDF8; font-size: 18px; margin-top: 2px;"></i>
                <div>
                    <strong>${titulo}:</strong>
                    <div style="margin-top: 4px;">${conteudo.replace(/\n\s*•/g, '<br>•')}</div>
                </div>
            </div>
        `;
    });

    // Formata Títulos
    html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');

    // Negrito e itálico
    html = html.replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/gim, '<em>$1</em>');

    // Código inline
    html = html.replace(/`([^`]+)`/gim, '<code>$1</code>');

    // Linhas horizontais
    html = html.replace(/^---$/gim, '<hr style="border: none; border-top: 1px solid var(--border-color); margin: 12px 0;">');

    // Blockquotes padrão (> texto)
    html = html.replace(/^\>\s*(.*$)/gim, '<blockquote>$1</blockquote>');

    // Formatação de Cores de Fios com Badges Coloridos
    html = html.replace(/\bFio Vermelho\b/g, '<span class="wire-badge wire-red"><i class="fa-solid fa-circle"></i> Fio Vermelho</span>');
    html = html.replace(/\bFio Preto\b/g, '<span class="wire-badge wire-black"><i class="fa-solid fa-circle"></i> Fio Preto</span>');
    html = html.replace(/\bFio Branco\b/g, '<span class="wire-badge wire-white"><i class="fa-solid fa-circle"></i> Fio Branco</span>');
    html = html.replace(/\bFio Azul\b/g, '<span class="wire-badge wire-blue"><i class="fa-solid fa-circle"></i> Fio Azul</span>');
    html = html.replace(/\bFio Amarelo\b/g, '<span class="wire-badge wire-yellow"><i class="fa-solid fa-circle"></i> Fio Amarelo</span>');
    html = html.replace(/\bFio Laranja\b/g, '<span class="wire-badge wire-orange"><i class="fa-solid fa-circle"></i> Fio Laranja</span>');
    html = html.replace(/\bFio Verde\b/g, '<span class="wire-badge wire-green"><i class="fa-solid fa-circle"></i> Fio Verde</span>');
    html = html.replace(/\bFio Marrom\b/g, '<span class="wire-badge wire-brown"><i class="fa-solid fa-circle"></i> Fio Marrom</span>');
    html = html.replace(/\bFio Roxo\b/g, '<span class="wire-badge wire-purple"><i class="fa-solid fa-circle"></i> Fio Roxo</span>');
    html = html.replace(/\bFio Cinza\b/g, '<span class="wire-badge wire-gray"><i class="fa-solid fa-circle"></i> Fio Cinza</span>');

    // Listas não-ordenadas (* ou -)
    html = html.replace(/^\s*[\*\-]\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/gims, '<ul style="margin: 8px 0 10px 20px;">$1</ul>');

    // Parágrafos e quebras de linha
    html = html.replace(/\n\n+/g, '</p><p>');
    html = '<p>' + html + '</p>';

    // Limpeza de tags
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[34]>.*?<\/h[34]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<blockquote>.*?<\/blockquote>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul style=".*?">.*?<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p>(<div class="direct-answer-card">.*?<\/div>)<\/p>/gs, '$1');

    return html;
}

