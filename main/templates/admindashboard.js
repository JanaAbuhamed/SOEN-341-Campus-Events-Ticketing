// ---- helpers ----
function statusKey(email) { return `organizerStatus:${email}`; }
function profileKey(email) { return `organizerProfile:${email}`; }

// Build one row (ID, Name, Email, Actions)
function makeRow(idx, name, email) {
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td>${idx}</td>
    <td>${name || '(no name)'}</td>
    <td>${email}</td>
    <td>
      <button class="btn approve">Approve</button>
      <button class="btn reject">Reject</button>
    </td>
  `;
  return tr;
}

// Attach click handlers for approve/reject
function attachRowActions(tbody) {
  tbody.querySelectorAll('.approve').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('tr');
      const name = row.children[1].textContent.trim();
      const email = row.children[2].textContent.trim();
      localStorage.setItem(statusKey(email), 'approved');
      alert(`${name} has been approved as an organizer!`);
      row.remove();
    });
  });

  tbody.querySelectorAll('.reject').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      const row = e.target.closest('tr');
      const name = row.children[1].textContent.trim();
      const email = row.children[2].textContent.trim();
      localStorage.setItem(statusKey(email), 'rejected');
      alert(`${name}'s organizer request has been rejected.`);
      row.remove();
    });
  });
}

// Load pending organizers from localStorage and render table
function loadPending() {
  const tbody = document.querySelector('#pendingTable tbody');
  if (!tbody) return;

  // Optional: keep any hardcoded rows already in HTML? -> clear them to avoid duplicates.
  tbody.innerHTML = '';

  const pendings = [];
  for (let i = 0; i < localStorage.length; i++) {
    const k = localStorage.key(i);
    if (!k.startsWith('organizerStatus:')) continue;
    const email = k.split(':')[1];
    const status = localStorage.getItem(k);
    if (status !== 'pending') continue;

    // Try to read saved profile for nicer display
    let name = '';
    try {
      const profRaw = localStorage.getItem(profileKey(email));
      if (profRaw) {
        const prof = JSON.parse(profRaw);
        name = prof.name || '';
      }
    } catch (_) {}

    pendings.push({ email, name });
  }

  // Render rows
  pendings.forEach((p, idx) => {
    const tr = makeRow(idx + 1, p.name, p.email);
    tbody.appendChild(tr);
  });

  attachRowActions(tbody);
}

document.addEventListener('DOMContentLoaded', loadPending);
