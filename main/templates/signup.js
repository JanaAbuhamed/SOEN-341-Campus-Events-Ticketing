// ---------- CONFIG ----------
const EVENTS_PAGE = 'EventList.html';       // change if your events file name is different
const ORG_PENDING_PAGE = 'organizer-pending.html';

// ---------- UI: toggle between Student / Organizer forms ----------
function showForm(type) {
  const studentForm = document.getElementById('studentForm');
  const organizerForm = document.getElementById('organizerForm');
  const btnStudent = document.getElementById('btnStudent');
  const btnOrganizer = document.getElementById('btnOrganizer');

  if (type === 'student') {
    studentForm?.classList.remove('hidden');
    organizerForm?.classList.add('hidden');
    btnStudent?.classList.add('active');
    btnOrganizer?.classList.remove('active');
  } else {
    organizerForm?.classList.remove('hidden');
    studentForm?.classList.add('hidden');
    btnOrganizer?.classList.add('active');
    btnStudent?.classList.remove('active');
  }
}

// ---------- Helpers ----------
function setLS(key, val) {
  try { localStorage.setItem(key, val); } catch (_) {}
}
function statusKey(email) { return `organizerStatus:${email}`; }

// ---------- Wire up form submits ----------
document.addEventListener('DOMContentLoaded', () => {
  // Student signup -> go to events page
  const studentForm = document.getElementById('studentForm');
  if (studentForm) {
    studentForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name  = document.getElementById('studentName')?.value.trim();
      const sid   = document.getElementById('studentId')?.value.trim();
      const email = document.getElementById('studentEmail')?.value.trim();
      const pass  = document.getElementById('studentPass')?.value.trim();

      if (!name || !sid || !email || !pass) {
        alert('Please fill in all student fields.');
        return;
      }

      // optional: greet later on events page
      setLS('studentName', name);
      setLS('studentEmail', email);

      // redirect to events list
      window.location.href = EVENTS_PAGE; // e.g., 'event-list.html'
    });
  }

  // Organizer signup -> mark as pending and go to waiting page
  const organizerForm = document.getElementById('organizerForm');
  if (organizerForm) {
    organizerForm.addEventListener('submit', (e) => {
      e.preventDefault();

      const name  = document.getElementById('orgName')?.value.trim();
      const oid   = document.getElementById('orgId')?.value.trim();
      const email = document.getElementById('orgEmail')?.value.trim();
      const pass  = document.getElementById('orgPass')?.value.trim();

      if (!name || !oid || !email || !pass) {
        alert('Please fill in all organizer fields.');
        return;
      }

      // store pending status for polling on the waiting page
      setLS('currentOrganizerEmail', email);
      setLS(statusKey(email), 'pending');

      // redirect to pending approval page
      window.location.href = ORG_PENDING_PAGE; // 'organizer-pending.html'
    });
  }
});
