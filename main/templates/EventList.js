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
document.addEventListener("DOMContentLoaded", function () {
    // const rows = document.querySelectorAll("#EventTable tbody tr");
    const contentArea = document.getElementById("contentArea");
    const tableBody = document.querySelector("#EventTable tbody");
    const overlay = document.getElementById("contentOverlay");
    const closeBtn = document.querySelector("#contentPanel .close-btn");

    // Generate table rows from reference data
    eventData.forEach(event => {
        const tr = document.createElement("tr");
        tr.dataset.name = event.name;
        tr.dataset.category = event.category;
        tr.dataset.organization = event.organization;
        tr.dataset.date = event.date;

        tr.innerHTML = `
            <td>${event.name}</td>
            <td>${event.category}</td>
            <td>${event.organization}</td>
            <td>${event.date}</td>
        `;

        tableBody.appendChild(tr);
    });

    const rows = tableBody.querySelectorAll("tr");
    let selectedRow = null; // track currently selected row
    // Row features
    rows.forEach(row => {
        row.addEventListener("click", function (e) {
            // Toggle off if clicking the same row
            if (selectedRow === this) {
                this.classList.remove('selected');
                contentArea.style.display = "none";
                selectedRow = null;
                return;
            }

            // Highlight row
            rows.forEach(r => r.classList.remove('selected'));
            this.classList.add('selected');
            selectedRow = this;

            // Show details panel
            contentArea.style.display = "block";

            // Populate content from data attributes
            const name = this.dataset.name;
            const category = this.dataset.category;
            const organization = this.dataset.organization;
            const date = this.dataset.date;

            contentArea.innerHTML = `
                <h2><strong>Event Name:</strong> ${name}</h2>
                <p><strong>Category:</strong> ${category}</p>
                <p><strong>Organization:</strong> ${organization}</p>
                <p><strong>Date:</strong> ${date}</p>
                <div class="action-buttons" style="margin-top:10px;">
                    <button class="save-btn">Save</button>
                    <button class="claim-btn">Claim</button>
                </div>
            `;
            // Show overlay
            overlay.style.display = "flex";

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
    });
});
