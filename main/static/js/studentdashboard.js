// Server-backed student tickets with responsive, in-card QR and per-card PNG download.

async function loadTicketsFromAPI() {
  try {
    const res = await fetch('/api/tickets/mine/', { credentials: 'include' });
    if (!res.ok) return [];
    return await res.json();
  } catch {
    return [];
  }
}

function el(tag, attrs = {}, children = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else e.setAttribute(k, v);
  }
  children.forEach(c => e.appendChild(c));
  return e;
}

function downloadCanvasAsPNG(canvas, filename) {
  const a = document.createElement('a');
  a.download = filename;
  a.href = canvas.toDataURL('image/png');
  a.click();
}

// Keep references so we can re-render QRs on resize responsively
const qrRegistry = [];

/**
 * Render a QR that fits within the card.
 * Size = min( cardWidth - padding, 280 ) with a sensible floor.
 */
function renderResponsiveQR(holder, text) {
  if (!window.QRCode) {
    holder.textContent = 'QR library missing';
    return;
  }
  const card = holder.closest('.card');
  const cardWidth = card ? card.clientWidth : 300;
  // 40px accounts for card padding; clamp between 120 and 280
  const side = Math.max(120, Math.min(280, cardWidth - 40));

  // clear and render
  holder.innerHTML = '';
  new QRCode(holder, {
    text,
    width: side,
    height: side,
    correctLevel: QRCode.CorrectLevel.M
  });
}

function reflowAllQRs() {
  qrRegistry.forEach(({ holder, text }) => renderResponsiveQR(holder, text));
}

// Simple debounce for resize
let resizeTimer = null;
window.addEventListener('resize', () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(reflowAllQRs, 120);
});

document.addEventListener('DOMContentLoaded', async () => {
  const grid = document.getElementById('ticketsGrid');
  const empty = document.getElementById('emptyState');

  const tickets = await loadTicketsFromAPI();

  grid.innerHTML = '';
  if (!tickets.length) { empty.classList.remove('hidden'); return; }
  empty.classList.add('hidden');

  tickets.forEach((t, idx) => {
    const card = el('div', { class: 'card' });

    card.appendChild(el('h4', { text: t.event_title }));
    card.appendChild(el('div', { class: 'meta', text: `Date: ${t.event_date}` }));
    card.appendChild(el('div', { class: 'meta', text: `Time: ${t.event_time}` }));
    card.appendChild(el('div', { class: 'meta', text: `Location: ${t.event_location}` }));
    card.appendChild(el('div', { class: 'meta', text: `Status: ${t.status}` }));

    const qrWrap = el('div', { class: 'qr' });
    const qrHolder = el('div', { id: `qr-${idx}`, class: 'qr-box' });
    qrWrap.appendChild(qrHolder);
    card.appendChild(qrWrap);

    // Render responsive QR & register for future reflows
    renderResponsiveQR(qrHolder, t.qr_text);
    qrRegistry.push({ holder: qrHolder, text: t.qr_text });

    // Download button
    const actions = el('div', { class: 'card-actions' });
    const dl = el('button', { class: 'btn', text: 'Download PNG' });
    dl.addEventListener('click', () => {
      const canvas = qrHolder.querySelector('canvas');
      const img = qrHolder.querySelector('img');
      const fname = `${t.event_title.replace(/\s+/g,'_')}_ticket.png`;
      if (canvas) downloadCanvasAsPNG(canvas, fname);
      else if (img) { const a = document.createElement('a'); a.href = img.src; a.download = fname; a.click(); }
    });
    actions.appendChild(dl);
    card.appendChild(actions);

    grid.appendChild(card);
  });
});
