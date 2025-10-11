/**
 * Enables live filtering for an HTML table.
 *
 * @param {HTMLInputElement} inputEl The input element for the search query.
 * @param {HTMLTableElement} tableEl The table element to filter.
 */
function enableTableFilter(inputEl, tableEl) {
    inputEl.addEventListener('keyup', () => {
        const query = inputEl.value.toLowerCase();
        const rows = tableEl.getElementsByTagName('tr');

        // Loop through all table rows, and hide those who don't match the search query
        for (let i = 1; i < rows.length; i++) { // Start at 1 to skip the header row
            const row = rows[i];
            const rowText = row.textContent || row.innerText;
            
            if (rowText.toLowerCase().indexOf(query) > -1) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        }
    });
}

// Initialize the filterable table
const searchInput = document.getElementById('tableSearchInput');
const dataTable = document.getElementById('EventTable');
if(searchInput && dataTable) {
    enableTableFilter(searchInput, dataTable);
}
document.addEventListener("DOMContentLoaded", function () {
    const rows = document.querySelectorAll("#EventTable tbody tr");

    rows.forEach(row => {
        row.addEventListener("click", function () {
            const href = this.getAttribute("data-href");
            if (href) {
                window.location.href = href; // navigate
            }
        });

        // optional: make it look clickable
        row.style.cursor = "pointer";
    });
});

//Table data
const eventData = [
    { name: "Meet your peers*&^&", category: "Career", organization: "Concordia", date: "02/15/25" },
    { name: "Find a Job", category: "Career", organization: "Concordia", date: "08/22/25" },
    { name: "Find your fit!", category: "concordia", organization: "Zellers", date: "12/11/25" }
];

// Detail box
document.addEventListener("DOMContentLoaded", async function () {
    // const rows = document.querySelectorAll("#EventTable tbody tr");
    const contentArea = document.getElementById("contentArea");
    const tableBody = document.querySelector("#EventTable tbody");
    const overlay = document.getElementById("contentOverlay");
    const closeBtn = document.querySelector("#contentPanel .close-btn");

    let events = [];
    try {
        const response = await fetch("http://localhost:8000/api/events/");
        if (!response.ok) throw new Error("Failed to fetch events");
        events = await response.json();
    } catch (error) {
        console.error("Error fetching events:", error);
    }
    // 1️⃣ Fetch data from your Django API
    async function fetchEvents() {
        try {
            const response = await fetch("http://127.0.0.1:8000/api/events/"); // Adjust URL if needed
            if (!response.ok) throw new Error("Failed to fetch events");
            const events = await response.json();
            populateTable(events);
        } catch (error) {
            console.error("Error loading events:", error);
            tableBody.innerHTML = `<tr><td colspan="4">Failed to load events</td></tr>`;
        }
    }
    // Generate table rows from reference data
    tableBody.innerHTML = ""; // clear previous rows
    events.forEach(event => {
        const tr = document.createElement("tr");
        tr.dataset.id = event.id;
        tr.dataset.title = event.title;
        tr.dataset.date = event.date;
        tr.dataset.time = event.time;
        tr.dataset.location = event.location;
        tr.dataset.capacity = event.capacity;
        tr.dataset.ticket_type = event.ticket_type;
        tr.dataset.status = event.status;
        tr.dataset.organizer = event.organizer.name || "Unknown";

        tr.innerHTML = `
            <td>${event.title}</td>
            <td>${event.organizer.name || "Unknown"}</td>
            <td>${event.date}</td>
            <td>${event.time}</td>
            <td>${event.ticket_type}</td>
        `;

        tableBody.appendChild(tr);
    });

    const rows = tableBody.querySelectorAll("tr");
    let selectedRow = null;

    rows.forEach(row => {
        row.addEventListener("click", function () {
            if (selectedRow === this) {
                this.classList.remove("selected");
                overlay.style.display = "none";
                selectedRow = null;
                return;
            }

            rows.forEach(r => r.classList.remove("selected"));
            this.classList.add("selected");
            selectedRow = this;

            const {
                id, title, date, time, location,
                capacity, ticket_type, status, organizer
            } = this.dataset;

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

            const registerBtn = contentArea.querySelector(".register-btn");
            const unregisterBtn = contentArea.querySelector(".unregister-btn");
            registerBtn.addEventListener("click", async () => {
                try {
                    const res = await fetch(`http://localhost:8000/api/events/${id}/register/`, {
                        method: "POST",
                        credentials: "include" // include cookies if auth needed
                    });
                    const data = await res.json();
                    alert(data.message || "Registered successfully");
                } catch (err) {
                    alert("Error registering for event");
                }
            });

            unregisterBtn.addEventListener("click", async () => {
                try {
                    const res = await fetch(`http://localhost:8000/api/events/${id}/unregister/`, {
                        method: "POST",
                        credentials: "include"
                    });
                    const data = await res.json();
                    alert(data.message || "Unregistered successfully");
                } catch (err) {
                    alert("Error unregistering from event");
                }
            });
        });
    });
    closeBtn.addEventListener("click", () => {
        overlay.style.display = "none";
        if (selectedRow) selectedRow.classList.remove("selected");
        selectedRow = null;
    });
    
        // Add action button functionality
        const saveBtn = contentArea.querySelector(".save-btn");
            saveBtn.addEventListener("click", function () {
                alert("Saving ticket for: " + name);
            });

            const claimBtn = contentArea.querySelector(".claim-btn");
            claimBtn.addEventListener("click", function () {
                alert("Claiming ticket for " + name);
            });
        });
        closeBtn.addEventListener("click", () => {
            overlay.style.display = "none";
            if (selectedRow) selectedRow.classList.remove('selected');
            selectedRow = null;
        });
        
        row.style.cursor = "pointer";

        // Close when clicking outside the panel
        overlay.addEventListener("click", (e) => {
         if (e.target === overlay) {
        overlay.style.display = "none";
        if (selectedRow) selectedRow.classList.remove('selected');
        selectedRow = null;
        }
        });
//     });
// });
