// Key helpers
function statusKey(email) { return `organizerStatus:${email}`; }
const DASHBOARD = 'organizerdashboard.html';

document.addEventListener('DOMContentLoaded', () => {
  const emailSpan = document.getElementById('orgEmail');
  const refreshBtn = document.getElementById('refreshBtn');

  // We store the "current" organizer email at signup time for the pending page to read
  const email = localStorage.getItem('currentOrganizerEmail') || '';

  if (emailSpan) emailSpan.textContent = email || 'unknown';

  const check = () => {
    if (!email) return;
    const status = localStorage.getItem(statusKey(email));
    if (status === 'approved') {
      // small UX pause
      setTimeout(() => { window.location.href = DASHBOARD; }, 300);
    }
  };

  // Manual check button
  refreshBtn?.addEventListener('click', check);

  // Auto-check every 3 seconds
  check();
  setInterval(check, 3000);
});
