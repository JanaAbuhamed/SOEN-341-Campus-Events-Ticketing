const monthEl = document.getElementById("month");
const yearEl = document.getElementById("year");
const daysEl = document.getElementById("calendar-days");
const todayText = document.getElementById("today-text");

const months = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

let currentDate = new Date();
const today = new Date();

function renderCalendar() {
  const month = currentDate.getMonth();
  const year = currentDate.getFullYear();

  monthEl.textContent = months[month];
  yearEl.textContent = year;
  daysEl.innerHTML = "";

  // Dates for previous and current month
  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const prevLastDay = new Date(year, month, 0).getDate();

  const firstDayIndex = firstDayOfMonth.getDay();
  const lastDayIndex = lastDayOfMonth.getDay();
  const nextDays = 6 - lastDayIndex;

  // Add previous month's ending days
  for (let x = firstDayIndex; x > 0; x--) {
    const div = document.createElement("div");
    div.textContent = prevLastDay - x + 1;
    div.classList.add("inactive");
    daysEl.appendChild(div);
  }

  // Add current month's days
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
    // Highlight days that have events
const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;

events.forEach(event => {
  if (event.date === dateString) {
    div.classList.add("event-day");  // add CSS style
    div.title = `${event.title} (${event.time})`;  // tooltip
  }
});

  }

  // Add next month's starting days
  for (let j = 1; j <= nextDays; j++) {
    const div = document.createElement("div");
    div.textContent = j;
    div.classList.add("inactive");
    daysEl.appendChild(div);
  }

  // Update footer text
  todayText.textContent = `Today is ${months[today.getMonth()]} ${today.getDate()}, ${today.getFullYear()}`;
}

// Navigation
document.getElementById("prev-month").addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() - 1);
  renderCalendar();
});

document.getElementById("next-month").addEventListener("click", () => {
  currentDate.setMonth(currentDate.getMonth() + 1);
  renderCalendar();
});

renderCalendar();