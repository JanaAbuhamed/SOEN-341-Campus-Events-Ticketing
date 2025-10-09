// Landing page button redirects
const studentBtn = document.getElementById('studentBtn');
const organizerBtn = document.getElementById('organizerBtn');
const adminBtn = document.getElementById('adminBtn');

if(studentBtn) {
  studentBtn.addEventListener('click', () => {
    window.location.href = 'studentlogin.html';
  });
}

if(organizerBtn) {
  organizerBtn.addEventListener('click', () => {
    window.location.href = 'organizerlogin.html';
  });
}

if(adminBtn) {
  adminBtn.addEventListener('click', () => {
    window.location.href = 'adminlogin.html';
  });
}

// Login page image follow effect
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

// Simple login alert for student/organizer/admin pages
const loginBtn = document.getElementById('loginBtn');
if(loginBtn) {
  loginBtn.addEventListener('click', () => {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    if(email === "" || password === "") {
      alert("Please enter both email and password.");
    } else {
      
      if(window.location.href.includes('studentlogin')) {
        window.location.href = 'EventList.html'; // student events page
      } else if(window.location.href.includes('organizerlogin')) {
        window.location.href = 'organizerdashboard.html'; // organizer dashboard
      } else if(window.location.href.includes('adminlogin')) {
        window.location.href = 'admindashboard.html'; // admin dashboard
      }
    }
  });
}


