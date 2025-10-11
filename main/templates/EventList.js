// JavaScript
document.addEventListener("DOMContentLoaded", async () => {
  const searchInput = document.getElementById("tableSearchInput");
  const tableBody = document.querySelector("#EventTable tbody");
  const overlay = document.getElementById("contentOverlay");
  const contentArea = document.getElementById("contentArea");
  const closeBtn = document.querySelector("#contentPanel .close-btn");
  let selectedRow = null;

  // Fetch events from API
  let events = [];
  try {
    const response = await fetch("http://127.0.0.1:8000/api/events/");
    if (!response.ok) throw new Error("Failed to fetch events");
    events = await response.json();
  } catch (err) {
    console.error(err);
    tableBody.innerHTML = `<tr><td colspan="5">Failed to load events</td></tr>`;
    return;
  }

  // Populate table
  function populateTable(events) {
    tableBody.innerHTML = ""; // clear existing rows
    events.forEach(event => {
      const organizerName = event.organizer?.name || "Unknown";
      const tr = document.createElement("tr");

      tr.dataset.id = event.id;
      tr.dataset.title = event.title;
      tr.dataset.date = event.date;
      tr.dataset.time = event.time;
      tr.dataset.location = event.location;
      tr.dataset.capacity = event.capacity;
      tr.dataset.ticket_type = event.ticket_type;
      tr.dataset.status = event.status;
      tr.dataset.organizer = organizerName;

      tr.innerHTML = `
        <td>${event.title}</td>
        <td>${organizerName}</td>
        <td>${event.date}</td>
        <td>${event.time}</td>
        <td>${event.ticket_type}</td>
      `;

      // Row click event
      tr.addEventListener("click", () => {
        if (selectedRow === tr) {
          tr.classList.remove("selected");
          overlay.style.display = "none";
          selectedRow = null;
          return;
        }

        // Deselect previous
        tableBody.querySelectorAll("tr").forEach(r => r.classList.remove("selected"));
        tr.classList.add("selected");
        selectedRow = tr;

        const { id, title, date, time, location, capacity, ticket_type, status, organizer } = tr.dataset;

        contentArea.innerHTML = `
          <h2><strong>${title}</strong></h2>
          <p><strong>Date:</strong> ${date} ${time}</p>
          <p><strong>Location:</strong> ${location}</p>
          <p><strong>Organizer:</strong> ${organizer}</p>
          <p><strong>Ticket Type:</strong> ${ticket_type}</p>
          <p><strong>Capacity:</strong> ${capacity}</p>
          <div class="action-buttons" style="margin-top:10px;">
            <button class="register-btn">Register</button>
            <button class="unregister-btn">Unregister</button>
          </div>
        `;

        // Show overlay
        overlay.style.display = "flex";

        // Register/Unregister actions
        contentArea.querySelector(".register-btn").addEventListener("click", async () => {
          try {
            const res = await fetch(`http://127.0.0.1:8000/api/events/${id}/register/`, { method: "POST", credentials: "include" });
            const data = await res.json();
            alert(data.message || "Registered successfully");
          } catch {
            alert("Error registering for event");
          }
        });

        contentArea.querySelector(".unregister-btn").addEventListener("click", async () => {
          try {
            const res = await fetch(`http://127.0.0.1:8000/api/events/${id}/unregister/`, { method: "POST", credentials: "include" });
            const data = await res.json();
            alert(data.message || "Unregistered successfully");
          } catch {
            alert("Error unregistering from event");
          }
        });
      });

      tr.style.cursor = "pointer";
      tableBody.appendChild(tr);
    });
  }

  populateTable(events);

  // Live table filter
  searchInput.addEventListener("keyup", () => {
    const query = searchInput.value.toLowerCase();
    tableBody.querySelectorAll("tr").forEach(row => {
      const rowText = row.textContent.toLowerCase();
      row.style.display = rowText.includes(query) ? "" : "none";
    });
  });

  // Close overlay
  closeBtn.addEventListener("click", () => {
    overlay.style.display = "none";
    if (selectedRow) selectedRow.classList.remove("selected");
    selectedRow = null;
  });

  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) { // Only if clicked outside the panel
      overlay.style.display = "none";
      if (selectedRow) selectedRow.classList.remove("selected");
      selectedRow = null;
    }
  });
});
