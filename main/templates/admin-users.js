document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.querySelector("#usersTable tbody");
  const users = JSON.parse(localStorage.getItem("usersList") || "[]");

  if (users.length === 0) {
    tbody.innerHTML = "<tr><td colspan='3' style='text-align:center;'>No users found</td></tr>";
  } else {
    users.forEach((u, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${idx + 1}</td><td>${u.name}</td><td>${u.email}</td>`;
      tbody.appendChild(tr);
    });
  }
});
