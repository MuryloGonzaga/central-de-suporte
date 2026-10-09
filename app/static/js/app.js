// ====================================================================
// CENTRAL DE SUPORTE - JAVASCRIPT FRONTEND
// ====================================================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMobileMenu();
    verificarStatusWebrota();

    // Define data padrão de hoje no seletor de rankings
    const dataFiltro = document.getElementById('data-filtro-ranking');
    if (dataFiltro) {
        const hoje = new Date().toISOString().split('T')[0];
        dataFiltro.value = hoje;
    }
});

// --------------------------------------------------------------------
// NAVEGAÇÃO ENTRE ABAS
// --------------------------------------------------------------------
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const pageTitle = document.getElementById('page-title');

    const titulos = {
        'tab-placa': 'Consulta de Placa (Base Pública AcheCar)',
        'tab-veiculo': 'Consulta de Veículo no Cadastro WebRota',
        'tab-local': 'Rastreamento de Local de Instalação (Última OS)',
        'tab-ranking': 'Rankings de Execução de Ordens de Serviço',
        'tab-cabos': 'Guia de Cabos & Cores de Instalação',
        'tab-leds': 'Diagnóstico de LEDs Suntech'
    };

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.getAttribute('data-tab');

            navItems.forEach(n => n.classList.remove('active'));
            tabPanes.forEach(t => t.classList.remove('active'));

            item.classList.add('active');
            const targetPane = document.getElementById(tabId);
            if (targetPane) {
                targetPane.classList.add('active');
            }

            if (titulos[tabId] && pageTitle) {
                pageTitle.textContent = titulos[tabId];
            }

            // Carrega dados automáticos ao entrar na aba de Rankings
            if (tabId === 'tab-ranking') {
                carregarRankingDiario();
                carregarRankingMensal();
            }

            // Fecha menu no mobile após clique
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) sidebar.classList.remove('mobile-open');
        });
    });

    // Botão de refresh de status
    const btnRefresh = document.getElementById('btn-refresh-status');
    if (btnRefresh) {
        btnRefresh.addEventListener('click', () => {
            verificarStatusWebrota();
        });
    }
}

function initMobileMenu() {
    const toggle = document.getElementById('mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('mobile-open');
        });
    }
}

// --------------------------------------------------------------------
// VERIFICAÇÃO DE STATUS DA WEBROTA
// --------------------------------------------------------------------
async function verificarStatusWebrota() {
    const dot = document.querySelector('#webrota-status-badge .status-dot');
    const text = document.getElementById('webrota-status-text');

    if (!dot || !text) return;

    dot.className = 'status-dot warning';
    text.textContent = 'Verificando...';

    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();

        if (data.webrota && data.webrota.conectado) {
            dot.className = 'status-dot success';
            text.textContent = 'Conectado (' + (data.webrota.usuario || 'Ativo') + ')';
        } else if (data.webrota && data.webrota.configurado === false) {
            dot.className = 'status-dot warning';
            text.textContent = 'Credenciais não configuradas (.env)';
        } else {
            dot.className = 'status-dot danger';
            text.textContent = 'Falha de Login';
        }
    } catch (err) {
        dot.className = 'status-dot danger';
        text.textContent = 'Servidor Offline';
    }
}

// --------------------------------------------------------------------
// TAB 1: CONSULTA ACHECAR (BASE PÚBLICA)
// --------------------------------------------------------------------
async function consultarAcheCar() {
    const input = document.getElementById('input-placas-achecar');
    const intervalo = document.getElementById('check-intervalo-achecar').checked;
    const btn = document.getElementById('btn-consultar-achecar');
    const resultCard = document.getElementById('resultado-achecar');
    const tbody = document.getElementById('tbody-achecar');
    const countSpan = document.getElementById('count-achecar');

    const texto = input.value.trim();
    if (!texto) {
        showToast('Por favor, informe ao menos uma placa.', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Consultando...';
    resultCard.style.display = 'block';
    tbody.innerHTML = '<tr><td colspan="7" class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Consultando placas na base pública...</td></tr>';

    try {
        const resp = await fetch('/api/consulta/placa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ placas: texto, intervalo_seguro: intervalo })
        });
        const data = await resp.json();

        if (!data.sucesso && (!data.resultados || data.resultados.length === 0)) {
            tbody.innerHTML = `<tr><td colspan="7" class="empty-state">${data.mensagem || 'Nenhum resultado encontrado.'}</td></tr>`;
            countSpan.textContent = '0';
            showToast(data.mensagem || 'Erro na consulta.', 'error');
            return;
        }

        tbody.innerHTML = '';
        const resultados = data.resultados || [];
        countSpan.textContent = resultados.length;

        resultados.forEach(item => {
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
        });

        if (data.bloqueio_detectado) {
            showToast('Aviso: Limite de requisições atingido na API pública.', 'warning');
        } else {
            showToast(`${resultados.length} placa(s) processada(s) com sucesso!`, 'success');
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Erro de comunicação com o servidor: ${err.message}</td></tr>`;
        showToast('Erro de conexão ao consultar placas.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-search"></i> Consultar Placas';
    }
}

// --------------------------------------------------------------------
// TAB 2: CONSULTA WEBROTA (VEÍCULO)
// --------------------------------------------------------------------
async function consultarVeiculosWebrota() {
    const input = document.getElementById('input-placas-webrota');
    const btn = document.getElementById('btn-consultar-webrota');
    const resultCard = document.getElementById('resultado-webrota');
    const tbody = document.getElementById('tbody-webrota');
    const countSpan = document.getElementById('count-webrota');

    const texto = input.value.trim();
    if (!texto) {
        showToast('Informe ao menos uma placa para consultar na WebRota.', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Consultando...';
    resultCard.style.display = 'block';
    tbody.innerHTML = '<tr><td colspan="4" class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Consultando cadastro da WebRota...</td></tr>';

    try {
        const resp = await fetch('/api/consulta/veiculo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ placas: texto })
        });
        const data = await resp.json();

        if (!data.sucesso && (!data.resultados || data.resultados.length === 0)) {
            tbody.innerHTML = `<tr><td colspan="4" class="empty-state">${data.mensagem || 'Nenhum veículo localizado.'}</td></tr>`;
            countSpan.textContent = '0';
            showToast(data.mensagem || 'Falha na busca.', 'error');
            return;
        }

        tbody.innerHTML = '';
        const resultados = data.resultados || [];
        countSpan.textContent = resultados.length;

        resultados.forEach(item => {
            const tr = document.createElement('tr');
            if (item.sucesso) {
                tr.innerHTML = `
                    <td><span class="tag-placa">${item.placa}</span></td>
                    <td><strong>${item.marca || 'Desconhecida'}</strong></td>
                    <td>${item.modelo || 'Desconhecido'}</td>
                    <td><span class="badge badge-success"><i class="fa-solid fa-check"></i> Cadastrado</span></td>
                `;
            } else {
                tr.innerHTML = `
                    <td><span class="tag-placa">${item.placa}</span></td>
                    <td colspan="2" style="color: #94A3B8;">${item.erro || 'Não localizado no cadastro.'}</td>
                    <td><span class="badge badge-warning"><i class="fa-solid fa-question"></i> Não Cadastrado</span></td>
                `;
            }
            tbody.appendChild(tr);
        });

        showToast(`${resultados.length} veículo(s) consultado(s)!`, 'success');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="empty-state">Erro ao comunicar com a WebRota: ${err.message}</td></tr>`;
        showToast('Erro de comunicação.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-search"></i> Consultar no WebRota';
    }
}

// --------------------------------------------------------------------
// TAB 3: CONSULTA LOCAL DE INSTALAÇÃO (ORDEM DE SERVIÇO)
// --------------------------------------------------------------------
async function consultarLocalInstalacao() {
    const input = document.getElementById('input-locais');
    const btn = document.getElementById('btn-consultar-local');
    const resultCard = document.getElementById('resultado-local');
    const tbody = document.getElementById('tbody-local');

    const texto = input.value.trim();
    if (!texto) {
        showToast('Informe as placas ou identificadores de equipamentos.', 'warning');
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Rastreando OS...';
    resultCard.style.display = 'block';
    tbody.innerHTML = '<tr><td colspan="5" class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Localizando seriais e histórico de OS na WebRota...</td></tr>';

    try {
        const resp = await fetch('/api/consulta/local', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ identificadores: texto })
        });
        const data = await resp.json();

        if (!data.sucesso || !data.resultados || data.resultados.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="empty-state">${data.mensagem || 'Nenhum registro encontrado.'}</td></tr>`;
            showToast(data.mensagem || 'Falha na busca.', 'error');
            return;
        }

        tbody.innerHTML = '';
        data.resultados.forEach(item => {
            if (item.sucesso && item.seriais && item.seriais.length > 0) {
                item.seriais.forEach(ser => {
                    const tr = document.createElement('tr');
                    const dataFormatada = ser.data_execucao ? formatarDataIso(ser.data_execucao) : 'Sem data';
                    const badgeClass = ser.possui_os ? 'badge-success' : 'badge-warning';
                    const statusText = ser.status ? `Status (${ser.status})` : 'Sem OS Válida';

                    tr.innerHTML = `
                        <td><span class="tag-placa">${item.identificador}</span></td>
                        <td><code style="color: #60A5FA;">${ser.serial}</code></td>
                        <td><strong>${ser.local}</strong></td>
                        <td>${dataFormatada}</td>
                        <td><span class="badge ${badgeClass}">${statusText}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><span class="tag-placa">${item.identificador}</span></td>
                    <td colspan="3" style="color: #94A3B8;">${item.erro || 'Sem dispositivo vinculado ou não encontrado.'}</td>
                    <td><span class="badge badge-danger"><i class="fa-solid fa-ban"></i> Não Localizado</span></td>
                `;
                tbody.appendChild(tr);
            }
        });

        showToast('Consulta de locais finalizada com sucesso!', 'success');
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">Erro: ${err.message}</td></tr>`;
        showToast('Erro ao consultar locais de instalação.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-location-crosshairs"></i> Buscar Locais de Instalação';
    }
}

// --------------------------------------------------------------------
// TAB 4: RANKINGS DE EXECUÇÃO
// --------------------------------------------------------------------
async function carregarRankingDiario() {
    const container = document.getElementById('lista-ranking-diario');
    const totalSpan = document.getElementById('total-os-diario');
    const dataLabel = document.getElementById('data-label-diario');
    const dataInput = document.getElementById('data-filtro-ranking');

    container.innerHTML = '<div class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Carregando ranking do dia...</div>';

    const dataSel = dataInput ? dataInput.value : '';
    const url = dataSel ? `/api/ranking/diario?data=${dataSel}` : '/api/ranking/diario';

    try {
        const resp = await fetch(url);
        const data = await resp.json();

        if (!data.sucesso) {
            container.innerHTML = `<div class="empty-state">${data.erro || 'Não foi possível carregar o ranking.'}</div>`;
            totalSpan.textContent = '0';
            dataLabel.textContent = '--';
            return;
        }

        totalSpan.textContent = `${data.total_os} OS`;
        dataLabel.textContent = data.data || '--';

        if (!data.ranking || data.ranking.length === 0) {
            container.innerHTML = '<div class="empty-state">Nenhuma Ordem de Serviço executada nesta data até o momento.</div>';
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
                        <strong style="color: #60A5FA;">${item.quantidade} OS <small style="color: var(--text-muted); font-weight: normal;">(${item.percentual}%)</small></strong>
                    </div>
                    <div class="ranking-bar-container">
                        <div class="ranking-bar-fill" style="width: ${item.percentual}%;"></div>
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
    const totalSpan = document.getElementById('total-os-mensal');
    const periodoLabel = document.getElementById('periodo-label-mensal');

    container.innerHTML = '<div class="loading-state"><i class="fa-solid fa-spinner fa-spin"></i> Carregando comparativo mensal...</div>';

    try {
        const resp = await fetch('/api/ranking/mensal');
        const data = await resp.json();

        if (!data.sucesso) {
            container.innerHTML = `<div class="empty-state">${data.erro || 'Não foi possível carregar o ranking mensal.'}</div>`;
            totalSpan.textContent = '0';
            periodoLabel.textContent = '--';
            return;
        }

        totalSpan.textContent = `${data.total_comparativo} OS`;
        periodoLabel.textContent = data.periodo || '--';

        if (!data.ranking || data.ranking.length === 0) {
            container.innerHTML = '<div class="empty-state">Nenhum dado registrado para o período.</div>';
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
                        <strong style="color: #38BDF8;">${item.total} OS <small style="color: var(--text-muted); font-weight: normal;">(${item.percentual}%)</small></strong>
                    </div>
                    <div class="ranking-bar-container">
                        <div class="ranking-bar-fill" style="width: ${item.percentual}%;"></div>
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

