/**
 * kb-widget.js — Widget de Recomendação BodyScan KB
 *
 * Integra a API do KB ao frontend existente do BodyScan.
 * Lê métricas do localStorage (peso, IMC calculado) e envia para a API.
 *
 * Uso: incluir após app.js e chamar BodyScanKB.init()
 */

const BodyScanKB = (() => {
  const API_BASE = window.BODYSCAN_KB_API || 'http://localhost:8000';

  // -----------------------------------------------------------------------
  // Utilitários
  // -----------------------------------------------------------------------

  function getPseudonimoUsuario() {
    let id = localStorage.getItem('bodyscan_uid');
    if (!id) {
      id = 'user_' + Math.random().toString(36).slice(2, 10);
      localStorage.setItem('bodyscan_uid', id);
    }
    return id;
  }

  function calcularIMC(pesoKg, alturaM) {
    if (!pesoKg || !alturaM || alturaM <= 0) return null;
    return pesoKg / (alturaM * alturaM);
  }

  function calcularRCA(circunferenciaAbdominal, altura) {
    if (!circunferenciaAbdominal || !altura || altura <= 0) return null;
    return circunferenciaAbdominal / altura;
  }

  function obterMetricasDoLocalStorage() {
    const metricas = [];

    // Peso atual (salvo pelo app.js)
    const pesoRaw = localStorage.getItem('bodyscan_peso_atual');
    const peso = pesoRaw ? parseFloat(pesoRaw) : null;

    // Altura (pode ser configurada pelo usuário)
    const alturaRaw = localStorage.getItem('bodyscan_altura_cm');
    const altura = alturaRaw ? parseFloat(alturaRaw) / 100 : null;

    // Circunferência abdominal
    const caRaw = localStorage.getItem('bodyscan_ca_cm');
    const ca = caRaw ? parseFloat(caRaw) : null;

    if (peso) metricas.push({ biomarcador: 'peso', valor: peso });

    if (peso && altura) {
      const imc = calcularIMC(peso, altura);
      if (imc) metricas.push({ biomarcador: 'imc', valor: Math.round(imc * 10) / 10 });
    }

    if (ca && altura) {
      const rca = calcularRCA(ca, altura * 100);
      if (rca) metricas.push({ biomarcador: 'rca', valor: Math.round(rca * 100) / 100 });
    }

    return metricas;
  }

  function inferirContextoClinico() {
    // Infere contexto com base nos dados do localStorage
    const tipoCircurgia = localStorage.getItem('bodyscan_tipo_cirurgia');
    const diasPosCirurgia = parseInt(localStorage.getItem('bodyscan_dias_pos_cirurgia') || '0');

    if (tipoCircurgia === 'rygb') {
      return diasPosCirurgia <= 365 ? 'pos_rygb_0_12m' : 'pos_rygb_12m_plus';
    }
    if (tipoCircurgia === 'sleeve') {
      return diasPosCirurgia <= 365 ? 'pos_sleeve_0_12m' : null;
    }

    // Verifica se está em perda acelerada (> 1% do peso por semana)
    const perdaSemana = parseFloat(localStorage.getItem('bodyscan_perda_semana_pct') || '0');
    if (perdaSemana > 1) return 'perda_acelerada';

    return null;
  }

  // -----------------------------------------------------------------------
  // Chamadas à API
  // -----------------------------------------------------------------------

  async function perguntarKB(pergunta, opcoesExtra = {}) {
    const metricas = obterMetricasDoLocalStorage();
    const contexto = inferirContextoClinico();
    const pseudonimo = getPseudonimoUsuario();

    const payload = {
      pseudonimo,
      pergunta,
      metricas,
      contexto_clinico: contexto,
      incluir_supervisao: false,
      k: 6,
      ...opcoesExtra,
    };

    const resp = await fetch(`${API_BASE}/v1/recomendacoes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!resp.ok) {
      throw new Error(`API KB retornou ${resp.status}`);
    }
    return resp.json();
  }

  async function enviarFeedback(logId, util, comentario = '') {
    const resp = await fetch(`${API_BASE}/v1/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ log_id: logId, util, comentario }),
    });
    return resp.json();
  }

  // -----------------------------------------------------------------------
  // Renderização do widget
  // -----------------------------------------------------------------------

  function criarWidgetHTML() {
    return `
    <div id="kb-widget" class="kb-widget section-card" style="margin-top:16px;">
      <h3 class="section-title" style="display:flex;align-items:center;gap:8px;">
        <span>🧠</span> Assistente BodyScan KB
        <span style="font-size:11px;background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:12px;font-weight:500;">Educativo</span>
      </h3>

      <!-- Configuração de métricas -->
      <div id="kb-config" class="kb-config" style="margin-bottom:12px;padding:10px;background:#f9f9f9;border-radius:8px;font-size:13px;">
        <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
          <label style="display:flex;align-items:center;gap:4px;">
            Altura (cm):
            <input type="number" id="kb-altura" placeholder="170" min="100" max="230"
              style="width:70px;padding:4px;border:1px solid #ddd;border-radius:4px;"
              onchange="BodyScanKB.salvarAltura(this.value)">
          </label>
          <label style="display:flex;align-items:center;gap:4px;">
            CA (cm):
            <input type="number" id="kb-ca" placeholder="90" min="50" max="200"
              style="width:70px;padding:4px;border:1px solid #ddd;border-radius:4px;"
              onchange="BodyScanKB.salvarCA(this.value)">
          </label>
          <label style="display:flex;align-items:center;gap:4px;">
            Cirurgia:
            <select id="kb-cirurgia" style="padding:4px;border:1px solid #ddd;border-radius:4px;"
              onchange="BodyScanKB.salvarCirurgia(this.value)">
              <option value="">Nenhuma</option>
              <option value="rygb">RYGB</option>
              <option value="sleeve">Sleeve</option>
            </select>
          </label>
        </div>
      </div>

      <!-- Campo de pergunta -->
      <div style="display:flex;gap:8px;margin-bottom:8px;">
        <input
          type="text"
          id="kb-pergunta"
          placeholder="Pergunte sobre nutrição, exercício, metabolismo..."
          style="flex:1;padding:10px 14px;border:1px solid #ddd;border-radius:8px;font-size:14px;"
          onkeydown="if(event.key==='Enter') BodyScanKB.perguntar()"
        >
        <button
          onclick="BodyScanKB.perguntar()"
          style="padding:10px 18px;background:#4CAF50;color:white;border:none;border-radius:8px;cursor:pointer;font-weight:600;"
        >
          Perguntar
        </button>
      </div>

      <!-- Sugestões rápidas -->
      <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;">
        <button class="kb-sugestao" onclick="BodyScanKB.perguntaRapida('Como preservar massa muscular durante a perda de peso?')">💪 Massa muscular</button>
        <button class="kb-sugestao" onclick="BodyScanKB.perguntaRapida('O que causa o platô na perda de peso?')">📊 Platô</button>
        <button class="kb-sugestao" onclick="BodyScanKB.perguntaRapida('Como cuidar da pele durante a perda de peso?')">🧴 Pele</button>
        <button class="kb-sugestao" onclick="BodyScanKB.perguntaRapida('Como a gordura é queimada no organismo?')">🔥 Lipólise</button>
      </div>

      <!-- Área de resposta -->
      <div id="kb-resposta" style="display:none;"></div>
    </div>

    <style>
      .kb-widget { font-family: inherit; }
      .kb-sugestao {
        padding: 5px 10px;
        background: #f0f4ff;
        border: 1px solid #c5cae9;
        border-radius: 16px;
        cursor: pointer;
        font-size: 12px;
        color: #3949ab;
        transition: background 0.2s;
      }
      .kb-sugestao:hover { background: #e8eaf6; }
      .kb-resposta-box {
        background: #f8fff8;
        border: 1px solid #c8e6c9;
        border-radius: 8px;
        padding: 14px;
        font-size: 14px;
        line-height: 1.6;
      }
      .kb-escalonamento-box {
        background: #fff8e1;
        border: 1px solid #ffe082;
        border-radius: 8px;
        padding: 14px;
        font-size: 14px;
      }
      .kb-aviso {
        font-size: 11px;
        color: #666;
        margin-top: 8px;
        padding: 6px 10px;
        background: #f5f5f5;
        border-radius: 4px;
        border-left: 3px solid #bbb;
      }
      .kb-feedback-bar {
        display: flex;
        gap: 8px;
        margin-top: 10px;
        align-items: center;
        font-size: 12px;
        color: #666;
      }
      .kb-feedback-btn {
        padding: 3px 10px;
        border: 1px solid #ddd;
        border-radius: 12px;
        cursor: pointer;
        background: white;
        font-size: 13px;
      }
      .kb-feedback-btn:hover { background: #f5f5f5; }
      .kb-recomendacoes {
        margin-top: 10px;
        padding: 8px 12px;
        background: #e8f5e9;
        border-radius: 6px;
        font-size: 13px;
      }
      .kb-spinner {
        display: inline-block;
        width: 16px; height: 16px;
        border: 2px solid #ccc;
        border-top-color: #4CAF50;
        border-radius: 50%;
        animation: kb-spin 0.8s linear infinite;
        vertical-align: middle;
        margin-right: 6px;
      }
      @keyframes kb-spin { to { transform: rotate(360deg); } }
    </style>
    `;
  }

  function renderizarResposta(data) {
    const el = document.getElementById('kb-resposta');
    if (!el) return;
    el.style.display = 'block';

    if (data.escalonar) {
      el.innerHTML = `
        <div class="kb-escalonamento-box">
          <strong>⚠️ Atenção — Orientação Profissional Necessária</strong>
          <p style="margin:8px 0 0;">${data.mensagem}</p>
        </div>
      `;
      return;
    }

    if (data.coberto === false) {
      el.innerHTML = `
        <div class="kb-escalonamento-box">
          <strong>ℹ️ Informação não disponível</strong>
          <p style="margin:8px 0 0;">${data.mensagem}</p>
        </div>
      `;
      return;
    }

    const recsHTML = data.recomendacoes && data.recomendacoes.length > 0
      ? `<div class="kb-recomendacoes">
          <strong>📋 Recomendações relacionadas:</strong>
          <ul style="margin:4px 0 0;padding-left:18px;">
            ${data.recomendacoes.map(r =>
              `<li>${r.titulo} <em style="color:#666;font-size:11px;">(${r.forca.replace(/_/g,' ')})</em></li>`
            ).join('')}
          </ul>
        </div>`
      : '';

    const fontesHTML = data.fontes && data.fontes.length > 0
      ? `<p style="font-size:11px;color:#666;margin-top:6px;">📚 Fontes: ${data.fontes.join(', ')}</p>`
      : '';

    el.innerHTML = `
      <div class="kb-resposta-box">
        <div style="white-space:pre-wrap;">${escapeHTML(data.resposta)}</div>
        ${fontesHTML}
        ${recsHTML}
        <div class="kb-aviso">
          ⚕️ ${data.aviso || 'Esta informação é educativa e não substitui avaliação médica ou nutricional.'}
        </div>
        <div class="kb-feedback-bar">
          <span>Esta resposta foi útil?</span>
          <button class="kb-feedback-btn" onclick="BodyScanKB.feedback('${data.log_id}', true)">👍 Sim</button>
          <button class="kb-feedback-btn" onclick="BodyScanKB.feedback('${data.log_id}', false)">👎 Não</button>
          <span id="kb-feedback-status-${data.log_id}"></span>
        </div>
      </div>
    `;
  }

  function escapeHTML(str) {
    return (str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function mostrarCarregando() {
    const el = document.getElementById('kb-resposta');
    if (el) {
      el.style.display = 'block';
      el.innerHTML = `<div style="padding:12px;color:#666;"><span class="kb-spinner"></span> Consultando base de conhecimento...</div>`;
    }
  }

  // -----------------------------------------------------------------------
  // API pública
  // -----------------------------------------------------------------------

  async function perguntar() {
    const input = document.getElementById('kb-pergunta');
    if (!input) return;
    const pergunta = input.value.trim();
    if (!pergunta) return;

    mostrarCarregando();
    try {
      const data = await perguntarKB(pergunta);
      renderizarResposta(data);
    } catch (err) {
      const el = document.getElementById('kb-resposta');
      if (el) {
        el.innerHTML = `<div style="padding:12px;color:#c62828;">Erro ao consultar o assistente: ${err.message}. Verifique se o servidor KB está em execução.</div>`;
      }
    }
  }

  async function perguntaRapida(texto) {
    const input = document.getElementById('kb-pergunta');
    if (input) input.value = texto;
    await perguntar();
  }

  async function feedback(logId, util) {
    const statusEl = document.getElementById(`kb-feedback-status-${logId}`);
    try {
      await enviarFeedback(logId, util);
      if (statusEl) statusEl.textContent = util ? '✓ Obrigado!' : '✓ Registrado';
    } catch (e) {
      if (statusEl) statusEl.textContent = '(erro ao salvar)';
    }
  }

  function salvarAltura(val) {
    localStorage.setItem('bodyscan_altura_cm', val);
  }

  function salvarCA(val) {
    localStorage.setItem('bodyscan_ca_cm', val);
  }

  function salvarCirurgia(val) {
    localStorage.setItem('bodyscan_tipo_cirurgia', val);
  }

  function init() {
    // Injeta o widget antes do footer
    const footer = document.querySelector('.footer');
    if (footer) {
      const container = document.createElement('div');
      container.innerHTML = criarWidgetHTML();
      footer.parentNode.insertBefore(container, footer);
    } else {
      // Fallback: adiciona ao final do body
      document.body.insertAdjacentHTML('beforeend', criarWidgetHTML());
    }

    // Restaura valores salvos
    const altura = localStorage.getItem('bodyscan_altura_cm');
    const ca = localStorage.getItem('bodyscan_ca_cm');
    const cirurgia = localStorage.getItem('bodyscan_tipo_cirurgia');

    if (altura) {
      const el = document.getElementById('kb-altura');
      if (el) el.value = altura;
    }
    if (ca) {
      const el = document.getElementById('kb-ca');
      if (el) el.value = ca;
    }
    if (cirurgia) {
      const el = document.getElementById('kb-cirurgia');
      if (el) el.value = cirurgia;
    }

    console.log('[BodyScan KB] Widget inicializado. API:', API_BASE);
  }

  return { init, perguntar, perguntaRapida, feedback, salvarAltura, salvarCA, salvarCirurgia };
})();

// Auto-init quando o DOM estiver pronto
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => BodyScanKB.init());
} else {
  BodyScanKB.init();
}
