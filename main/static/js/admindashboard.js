document.addEventListener("DOMContentLoaded", async () => {
    const studentTableBody = document.querySelector("#StudentTable tbody");
    const organizerTableBody = document.querySelector("#OrganizerTable tbody");
    const eventTableBody = document.querySelector("#EventTable tbody");
    const studentSearch = document.getElementById("tableSearchInput");
    const organizerSearch = document.getElementById("organizerSearchInput");
    const eventSearch = document.getElementById("eventSearchInput");
    const overlay = document.getElementById("contentOverlay");
    const contentArea = document.getElementById("contentArea");
    const closeBtn = document.querySelector("#contentPanel .close-btn");
    const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute("content");
    let selectedRow = null;

    // Tabs
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const target = btn.dataset.tab;
            tabButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            btn.classList.add("active");
            document.getElementById(target).classList.add("active");
        });
    });

    // Fetch users
    let users = [];
    try {
        const res = await fetch("/api/users", { credentials: "include" });
        users = await res.json();
    } catch (err) {
        studentTableBody.innerHTML = `<tr><td colspan="3">Failed to load users</td></tr>`;
        organizerTableBody.innerHTML = `<tr><td colspan="4">Failed to load users</td></tr>`;
    }

    // Populate users
    function populateUsers() {
        studentTableBody.innerHTML = "";
        organizerTableBody.innerHTML = "";
        users.forEach(user => {
            if (user.role === 0) {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${user.user_id}</td><td>${user.email}</td><td>${user.name}</td>`;
                studentTableBody.appendChild(tr);
            } else if (user.role === 1) {
                const tr = document.createElement("tr");
                tr.innerHTML = `<td>${user.user_id}</td><td>${user.email}</td><td>${user.name}</td>
                                <td>
                                <button class="activate-btn" data-id="${user.user_id}">${user.status===1?"Deactivate":"Activate"}</button>
                                <button class="remove-btn" data-id="${user.user_id}" style="margin-left:5px;">Remove</button>
                                </td>`;
                organizerTableBody.appendChild(tr);
            }
        });
    }
    populateUsers();

    // Fetch events
    let events = [];
    try {
        const res = await fetch("/api/events/", { credentials: "include" });
        events = await res.json();
    } catch (err) {
        eventTableBody.innerHTML = `<tr><td colspan="9">Failed to load events</td></tr>`;
    }

    // Populate events with overlay
    function populateEvents() {
        eventTableBody.innerHTML = "";
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
            tr.dataset.organizer = event.organizer?.name || "Unknown";

            tr.innerHTML = `<td>${event.id}</td><td>${event.title}</td><td>${tr.dataset.organizer}</td>
                            <td>${event.date}</td><td>${event.time}</td><td>${event.location}</td>
                            <td>${event.ticket_type}</td><td>${event.capacity}</td><td>${event.status}</td>`;

            tr.addEventListener("click", () => {
                if (selectedRow === tr) { overlay.style.display="none"; selectedRow=null; tr.classList.remove("selected"); return; }
                eventTableBody.querySelectorAll("tr").forEach(r=>r.classList.remove("selected"));
                tr.classList.add("selected"); selectedRow=tr;

                contentArea.innerHTML = `
                    <h2><strong>${tr.dataset.title}</strong></h2>
                    <p><strong>Date:</strong> ${tr.dataset.date} ${tr.dataset.time}</p>
                    <p><strong>Location:</strong> ${tr.dataset.location}</p>
                    <p><strong>Organizer:</strong> ${tr.dataset.organizer}</p>
                    <p><strong>Ticket Type:</strong> ${tr.dataset.ticket_type}</p>
                    <p><strong>Capacity:</strong> ${tr.dataset.capacity}</p>
                    <div style="margin-top:10px;">
                        <button class="register-btn">Register</button>
                        <button class="unregister-btn">Unregister</button>
                    </div>
                `;
                overlay.style.display="flex";

                contentArea.querySelector(".register-btn").onclick = async ()=>{
                    await fetch(`/api/events/${tr.dataset.id}/register/`, {method:"POST", credentials:"include", headers:{"X-CSRFToken":csrftoken}});
                    alert("Registered");
                };
                contentArea.querySelector(".unregister-btn").onclick = async ()=>{
                    await fetch(`/api/events/${tr.dataset.id}/unregister/`, {method:"POST", credentials:"include", headers:{"X-CSRFToken":csrftoken}});
                    alert("Unregistered");
                };
            });

            tr.style.cursor="pointer";
            eventTableBody.appendChild(tr);
        });
    }
    populateEvents();

    // Close overlay
    closeBtn.addEventListener("click", () => { overlay.style.display="none"; if(selectedRow) selectedRow.classList.remove("selected"); selectedRow=null; });
    overlay.addEventListener("click", e=>{ if(e.target===overlay){ overlay.style.display="none"; if(selectedRow) selectedRow.classList.remove("selected"); selectedRow=null; } });

    // Search functionality
    studentSearch.addEventListener("keyup", ()=>{ 
        const q=studentSearch.value.toLowerCase();
        studentTableBody.querySelectorAll("tr").forEach(r=>r.style.display=r.textContent.toLowerCase().includes(q)?"":"none"); 
    });
    organizerSearch.addEventListener("keyup", ()=>{ 
        const q=organizerSearch.value.toLowerCase();
        organizerTableBody.querySelectorAll("tr").forEach(r=>r.style.display=r.textContent.toLowerCase().includes(q)?"":"none"); 
    });
    eventSearch.addEventListener("keyup", ()=>{ 
        const q=eventSearch.value.toLowerCase();
        eventTableBody.querySelectorAll("tr").forEach(r=>r.style.display=r.textContent.toLowerCase().includes(q)?"":"none"); 
    });

    // Organizer buttons
    organizerTableBody.addEventListener("click", async e=>{
        const id = e.target.dataset.id;
        if(e.target.classList.contains("activate-btn")){
            const newStatus = e.target.textContent==="Activate"?1:0;
            await fetch(`/api/users/${id}/status`, {method:"POST",credentials:"include",headers:{"Content-Type":"application/json","X-CSRFToken":csrftoken},body:JSON.stringify({status:newStatus})});
            users = users.map(u=>u.user_id===parseInt(id)?{...u,status:newStatus}:u);
            populateUsers();
        }
        if(e.target.classList.contains("remove-btn")){
            if(!confirm("Remove this organizer?")) return;
            await fetch(`/api/users/${id}/`, {method:"DELETE",credentials:"include",headers:{"X-CSRFToken":csrftoken}});
            users = users.filter(u=>u.user_id!==parseInt(id));
            populateUsers();
        }
    });
});
