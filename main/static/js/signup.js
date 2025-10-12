function showForm(type) {
      const studentForm = document.getElementById('studentForm');
      const organizerForm = document.getElementById('organizerForm');
      const btnStudent = document.getElementById('btnStudent');
      const btnOrganizer = document.getElementById('btnOrganizer');

      if (type === 'student') {
        studentForm.classList.remove('hidden');
        organizerForm.classList.add('hidden');
        btnStudent.classList.add('active');
        btnOrganizer.classList.remove('active');
      } else {
        organizerForm.classList.remove('hidden');
        studentForm.classList.add('hidden');
        btnOrganizer.classList.add('active');
        btnStudent.classList.remove('active');
      }
    }