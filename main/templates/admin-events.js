document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector("#eventsTable tbody");
  const events = JSON.parse(localStorage.getItem("eventsList") || "[]");

  if (events.length === 0) {
    tbody.innerHTML = "<tr><td colspan='4' style='text-align:center;'>No events found</td></tr>";
  } else {
    events.forEach((ev, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${idx + 1}</td><td>${ev.title}</td><td>${ev.category}</td><td>${ev.date}</td>`;
      tbody.appendChild(tr);
    });
  }
});
