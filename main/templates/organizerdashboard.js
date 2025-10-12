// Navigation functionality
function showSection(sectionId) {
  // Hide all sections
  document.querySelectorAll('.dashboard-section').forEach(section => {
    section.classList.remove('active');
  });
  
  // Remove active class from all nav links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
  });
  
  // Show selected section
  document.getElementById(sectionId).classList.add('active');
  
  // Activate corresponding nav link
  document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
}

// Add click listeners to nav links
document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    const section = link.getAttribute('data-section');
    showSection(section);
  });
});

// Logout functionality
document.querySelector('.logout-btn').addEventListener('click', () => {
  if (confirm('Are you sure you want to logout?')) {
    // Redirect to login page
    window.location.href = 'login.html';
  }
});

console.log("Organizer Dashboard loaded");
