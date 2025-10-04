// Approve/Reject button alert (no dynamic changes yet)
document.querySelectorAll('.approve').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const row = e.target.closest('tr');
    const name = row.children[1].textContent;
    alert(`${name} has been approved as an organizer!`);
  });
});

document.querySelectorAll('.reject').forEach(btn => {
  btn.addEventListener('click', (e) => {
    const row = e.target.closest('tr');
    const name = row.children[1].textContent;
    alert(`${name}'s organizer request has been rejected.`);
  });
});
