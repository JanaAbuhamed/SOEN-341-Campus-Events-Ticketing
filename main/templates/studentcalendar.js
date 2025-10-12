// ----- DOM refs -----
const monthEl = document.getElementById("month");
const yearEl = document.getElementById("year");
const daysEl = document.getElementById("calendar-days");
const todayText = document.getElementById("today-text");

// Your API endpoint (later: drop the email and use the logged-in user)
const API_URL = "/api/my-claimed-events/?email=admin@gmail.com";

const months = [
  "January","February","March","April","May","June",
  "July","August","September","October","November","December"
];

let currentDate = new Date();
const today = new Date();

// cache of tickets loaded from the API
let TICKETS = [];            // [{ date: 'YYYY-MM-DD', name: 'Title', ... }]
let TICKET_MAP = {};         // dateStr -> [tickets]

function pad(n) { return String(n).padStart(2, "0"); }

// Fetch and normalize tickets from API into [{date, name}]
async function fetchClaimedTickets() {
  try {
    const res = await fetch(API_URL, { credentials: "same-origin" });
    const data = await res.json(); // [{id, title, start}]
    return data.map(e => ({
      date: (e.start || "").split("T")[0], // 'YYYY-MM-DD'
      name: e.title || "Event"
    }));
  } catch (e) {
    console.error("Failed to load claimed tickets:", e);
    return [];
  }
}

// Build a date -> events map for quick lookup
function rebuildTicketMap() {
  TICKET_MAP = {};
  for (const t of TICKETS) {
    if (!t.date) continue;
    (TICKET_MAP[t.date] ||= []).push(t);
  }
}

// Add dots + titles to cells that have events
function annotateClaimedDays(year, month /* 0-based */) {
  const cells = Array.from(document.querySelectorAll("#calendar-days > div"));
  cells.forEach(cell => {
    if (cell.classList.contains("inactive")) return;
    const dayNum = parseInt(cell.textContent, 10);
    if (isNaN(dayNum)) return;

    const ds = `${year}-${pad(month + 1)}-${pad(dayNum)}`;
    cell.dataset.date = ds;

    const events = TICKET_MAP[ds] || [];
    if (events.length) {
      cell.classList.add("has-event");
      cell.title = events.map(e => e.name).join(", ");
    } else {
      cell.classList.remove("has-event");
      cell.removeAttribute("title");
    }
  });
}

// Show the list of events under the calendar for a specific date
function showDayEvents(dateStr) {
  const box = document.getElementById("day-events");
  if (!box) return;
  const list = TICKET_MAP[dateStr] || [];
  if (!list.length) {
    box.innerHTML = "";
    return;
  }
  const html = `
    <div style="background:#fff;border:2px solid #000;border-radius:14px;padding:14px;">
      <strong>Events on ${dateStr}</strong>
      <ul style="margin:10px 0 0 18px;">
        ${list.map(e => `<li>${e.name}</li>`).join("")}
      </ul>
    </div>
  `;
  box.innerHTML = html;
}

function renderCalendar() {
  const month = currentDate.getMonth();
  const year = currentDate.getFullYear();

  monthEl.textContent = months[month];
  yearEl.textContent = year;
  daysEl.innerHTML = "";

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const prevLastDay = new Date(year, month, 0).getDate();

  const firstDayIndex = firstDayOfMonth.getDay();
  const lastDayIndex = lastDayOfMonth.getDay();
  const nextDays = 6 - lastDayIndex;

  // Prev month tail
  for (let x = firstDayIndex; x > 0; x--) {
    const div = document.createElement("div");
    div.textContent = prevLastDay - x + 1;
    div.classList.add("inactive");
    daysEl.appendChild(div);
  }

  // Current month
  for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
    const div = document.createElement("div");
    div.textContent = i;

    if (
      i === today.getDate() &&
      month === today.getMonth() &&
      year === today.getFullYear()
    ) {
      div.classList.add("today");
    }
    daysEl.appendChild(div);
  }

  // Next month head
  for (let j = 1; j <= nextDays; j++) {
    const div = document.createElement("div");
    div.textContent = j;
    div.classList.add("inactive");
    daysEl.appendChild(div);
  }

  todayText.textContent = `Today is ${months[today.getMonth()]} ${today.getDate()}, ${today.getFullYear()}`;

  // annotate after cells are placed
  annotateClaimedDays(year, month);
}

// Click a day to show its events
daysEl.addEventListener("click", (e) => {
  const cell = e.target.closest("div");
  if (!cell || cell.classList.contains("inactive")) return;
  const ds = cell.dataset.date;
  if (ds) showDayEvents(ds);
});

// Navigation
document.getElementById("prev-month").addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() - 1);
  renderCalendar();
});
document.getElementById("next-month").addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() + 1);
  renderCalendar();
});

// ----- Initialize -----
(async function init() {
  TICKETS = await fetchClaimedTickets();
  rebuildTicketMap();
  renderCalendar();
})();
