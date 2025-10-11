document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("event-search");
  const eventCards = document.querySelectorAll(".event-card");
  const modal = document.getElementById("event-modal");
  const closeBtn = document.getElementById("modal-close");
  const claimBtn = document.getElementById("claimBtn");
  const saveBtn  = document.getElementById("saveBtn");

  // live search
  searchInput.addEventListener("input", () => {
    const q = searchInput.value.toLowerCase();
    eventCards.forEach(card => {
      const t = card.dataset.title.toLowerCase();
      const c = card.dataset.category.toLowerCase();
      const o = card.dataset.org.toLowerCase();
      card.style.display = (t.includes(q) || c.includes(q) || o.includes(q)) ? "block" : "none";
    });
  });

  // current event selected in modal
  let current = null;

  // open modal on card click
  eventCards.forEach(card => {
    card.addEventListener("click", () => {
      current = {
        name: card.dataset.title,
        date: card.dataset.date,
        category: card.dataset.category,
        organization: card.dataset.org,
        location: card.dataset.location,
        capacity: card.dataset.capacity,
        description: card.dataset.description
      };
      document.getElementById("modal-title").textContent = current.name;
      document.getElementById("modal-date").textContent = current.date;
      document.getElementById("modal-category").textContent = current.category;
      document.getElementById("modal-org").textContent = current.organization;
      document.getElementById("modal-location").textContent = current.location;
      document.getElementById("modal-capacity").textContent = current.capacity;
      document.getElementById("modal-description").textContent = current.description;
      modal.classList.add("active");
    });
  });

  // claim: push to localStorage.studentTickets (de-dupe)
  claimBtn.addEventListener("click", () => {
    if (!current) return;
    const key = 'studentTickets';
    const list = JSON.parse(localStorage.getItem(key) || '[]');
    const sig = `${current.name}|${current.date}|${current.organization}`;
    const exists = list.some(t => `${t.name}|${t.date}|${t.organization}` === sig);
    if (!exists) {
      list.push({
        ticketId: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        name: current.name,
        category: current.category,
        organization: current.organization,
        date: current.date,
        claimedAt: new Date().toISOString()
      });
      localStorage.setItem(key, JSON.stringify(list));
    }
    alert('Ticket claimed! See it under My Tickets.');
    modal.classList.remove("active");
  }, { passive: true });

  // save: optional list (does not affect tickets)
  saveBtn.addEventListener("click", () => {
    if (!current) return;
    const key = 'studentsSavedEvents';
    const list = JSON.parse(localStorage.getItem(key) || '[]');
    const sig = `${current.name}|${current.date}|${current.organization}`;
    if (!list.some(e => `${e.name}|${e.date}|${e.organization}` === sig)) {
      list.push(current);
      localStorage.setItem(key, JSON.stringify(list));
    }
    alert('Event saved.');
  }, { passive: true });

  // close modal
  closeBtn.addEventListener("click", () => modal.classList.remove("active"));
  modal.addEventListener("click", (e) => { if (e.target === modal) modal.classList.remove("active"); });
});
