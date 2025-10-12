// Landing page button redirects - FIXED
const studentBtn = document.getElementById('studentBtn');
const organizerBtn = document.getElementById('organizerBtn');
const adminBtn = document.getElementById('adminBtn');

if(studentBtn) {
  studentBtn.addEventListener('click', () => {
    window.location.href = "/studentlogin/";  // CHANGED
  });
}

if(organizerBtn) {
  organizerBtn.addEventListener('click', () => {
    window.location.href = "/organizerlogin/";  // CHANGED
  });
}

if(adminBtn) {
  adminBtn.addEventListener('click', () => {
    window.location.href = "/adminlogin/";  // CHANGED
  });
}

// Login page image follow effect (this part is fine)
const img = document.querySelector('.login-left img');

if(img) {
  img.addEventListener('mousemove', (e) => {
    const rect = img.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const moveX = (x - rect.width / 2) / 10;
    const moveY = (y - rect.height / 2) / 10;

    img.style.transform = `translate(${moveX}px, ${moveY}px)`;
  });

  img.addEventListener('mouseleave', () => {
    img.style.transform = 'translate(0, 0)';
  });
}

// Simple login alert for student/organizer/admin pages - FIXED
const loginBtn = document.getElementById('loginBtn');
if(loginBtn) {
  loginBtn.addEventListener('click', () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    if(email === "" || password === "") {
      alert("Please enter both email and password.");
    } else {
      // CHANGED ALL THESE REDIRECTS:
      if(window.location.href.includes('studentlogin')) {
        window.location.href = "/studentdashboard/";  // CHANGED
      } else if(window.location.href.includes('organizerlogin')) {
        window.location.href = "/organizerdashboard/";  // CHANGED
      } else if(window.location.href.includes('adminlogin')) {
        window.location.href = "/admindashboard/";  // CHANGED
      }
    }
  });
}