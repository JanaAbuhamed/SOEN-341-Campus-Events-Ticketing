document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("event-search");
  const eventCards = document.querySelectorAll(".event-card");

  // Live search filter
  searchInput.addEventListener("input", () => {
    const query = searchInput.value.toLowerCase();

    eventCards.forEach(card => {
      const title = card.dataset.title.toLowerCase();
      const category = card.dataset.category.toLowerCase();
      const org = card.dataset.org.toLowerCase();
      const matches = title.includes(query) || category.includes(query) || org.includes(query);
      card.style.display = matches ? "block" : "none";
    });
  });

  // Modal handling
  const modal = document.getElementById("event-modal");
  const closeBtn = document.getElementById("modal-close");

  eventCards.forEach(card => {
    card.addEventListener("click", () => {
      document.getElementById("modal-title").textContent = card.dataset.title;
      document.getElementById("modal-date").textContent = card.dataset.date;
      document.getElementById("modal-category").textContent = card.dataset.category;
      document.getElementById("modal-org").textContent = card.dataset.org;
      document.getElementById("modal-location").textContent = card.dataset.location;
      document.getElementById("modal-capacity").textContent = card.dataset.capacity;
      document.getElementById("modal-description").textContent = card.dataset.description;

      modal.classList.add("active");
    });
  });

  closeBtn.addEventListener("click", () => {
    modal.classList.remove("active");
  });

  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.classList.remove("active");
  });
});

