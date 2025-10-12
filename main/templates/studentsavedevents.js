document.addEventListener("DOMContentLoaded", () => {
  const savedContainer = document.getElementById("saved-events");
  const emptyMessage = document.getElementById("empty-message");
  const key = "studentsSavedEvents";

  // Load saved events
  const savedEvents = JSON.parse(localStorage.getItem(key) || "[]");

  // If no events saved
  if (savedEvents.length === 0) {
    emptyMessage.style.display = "block";
    return;
  }

  // Create event cards
  savedEvents.forEach((event, index) => {
    const card = document.createElement("div");
    card.classList.add("event-card");
    card.innerHTML = `
      <h3>${event.name}</h3>
      <p><strong>Date:</strong> ${event.date}</p>
      <p><strong>Category:</strong> ${event.category}</p>
      <p><strong>Organization:</strong> ${event.organization}</p>
      <p><strong>Location:</strong> ${event.location}</p>
      <p><strong>Capacity:</strong> ${event.capacity}</p>
      <p>${event.description}</p>
      <button class="unsave-btn">Unsave</button>
    `;

    // Unsave button handler
    card.querySelector(".unsave-btn").addEventListener("click", () => {
      if (confirm(`Remove "${event.name}" from saved events?`)) {
        const updated = savedEvents.filter((_, i) => i !== index);
        localStorage.setItem(key, JSON.stringify(updated));
        card.remove();
        if (updated.length === 0) emptyMessage.style.display = "block";
      }
    });

    savedContainer.appendChild(card);
  });
});
