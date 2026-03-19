// ================================================================
// 📄 FILE: app.js
// 📂 FOLDER: frontend/js/
// 🎯 YEH KYA HAI?
//    Pura frontend ka JavaScript.
//    Browser mein chalta hai — server pe nahi.
//    Yeh backend (Python Flask) se baat karta hai
//    fetch() ke zariye — jaise phone call karna server ko.
//
// 🔤 IMPORTANT: Backend change hua (Node → Python Flask)
//    Lekin JavaScript bilkul same hai!
//    Kyunki JavaScript browser mein chalta hai
//    aur backend se sirf API calls karta hai.
//    API ka format same hai — JSON in, JSON out.
// ================================================================

// Hamare Python Flask server ka address
// Flask bhi port 3000 pe chal raha hai
const API = 'http://localhost:3000/api';


// ---- UTILITY FUNCTIONS ----

// Toast notification dikhao (bottom-right popup)
function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `show ${type}`;
  setTimeout(() => { toast.className = ''; }, 4000);
}

// Form ke andar alert box dikhao
function showAlert(id, message, type = 'error') {
  const el = document.getElementById(id);
  if (el) {
    el.textContent = message;
    el.className = `alert ${type} show`;
    setTimeout(() => { el.className = 'alert'; }, 5000);
  }
}

// Date ko readable format mein badlo
// "2025-08-31T00:00:00Z" → "31 Aug 2025"
function formatDate(dateStr) {
  if (!dateStr) return '-';
  const d = new Date(dateStr);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}


// ---- AUTH HELPERS ----

function getUser() {
  const u = localStorage.getItem('govtUser');
  return u ? JSON.parse(u) : null;
}

function getToken() {
  return localStorage.getItem('govtToken');
}

function requireAuth() {
  const user = getUser();
  if (!user) window.location.href = '../index.html';
  return user;
}

function redirectIfLoggedIn() {
  if (getUser()) window.location.href = 'pages/dashboard.html';
}

function logout() {
  localStorage.removeItem('govtUser');
  localStorage.removeItem('govtToken');
  window.location.href = '../index.html';
}


// ---- API HELPER ----
// Yeh function sab API calls karta hai
// Ek hi jagah likhna padta hai — DRY principle!
async function apiCall(endpoint, method = 'GET', body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' }
  };

  const token = getToken();
  if (token) options.headers['Authorization'] = token;

  if (body) options.body = JSON.stringify(body);

  const res = await fetch(API + endpoint, options);
  const data = await res.json();

  if (!res.ok) throw new Error(data.message || 'Kuch galat hua');
  return data;
}


// ---- NAVIGATION ----
function showPage(pageId) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

  const page = document.getElementById(pageId);
  if (page) page.classList.add('active');

  const nav = document.querySelector(`[data-page="${pageId}"]`);
  if (nav) nav.classList.add('active');

  const titles = {
    'page-dashboard':  { t: 'Dashboard',        s: 'Aapka overview yahan hai' },
    'page-jobs':       { t: 'Job Listings',      s: 'Sarkari jobs dhundho' },
    'page-status':     { t: 'Meri Applications', s: 'Apni applications track karo' },
    'page-admin-jobs': { t: 'Jobs Manage Karo',  s: 'Job add, edit, delete karo' },
    'page-admin-apps': { t: 'Sab Applications',  s: 'Status update karo' },
    'page-users':      { t: 'Users',             s: 'Registered users' },
  };

  const info = titles[pageId];
  if (info) {
    document.getElementById('header-title').textContent = info.t;
    document.getElementById('header-sub').textContent = info.s;
  }

  if (pageId === 'page-dashboard')  loadDashboard();
  if (pageId === 'page-jobs')       loadJobs();
  if (pageId === 'page-status')     loadMyApplications();
  if (pageId === 'page-admin-jobs') loadAdminJobs();
  if (pageId === 'page-admin-apps') loadAdminApplications();
  if (pageId === 'page-users')      loadUsers();
}


// ---- DASHBOARD ----
let chartInstance = null;

async function loadDashboard() {
  const user = getUser();
  if (!user) return;

  try {
    if (user.role === 'admin') {
      const stats = await apiCall('/applications/stats');

      document.getElementById('stat-jobs').textContent       = stats.totalJobs;
      document.getElementById('stat-applicants').textContent = stats.totalApplicants;
      document.getElementById('stat-approved').textContent   = stats.approved;
      document.getElementById('stat-pending').textContent    = stats.pending;

      document.getElementById('recent-jobs-body').innerHTML = stats.recentJobs.map(j => `
        <tr>
          <td><strong>${j.title}</strong></td>
          <td>${j.department}</td>
          <td>${formatDate(j.lastDate)}</td>
          <td>${j.vacancies}</td>
        </tr>`).join('') || '<tr><td colspan="4" class="text-center text-muted">Koi job nahi</td></tr>';

      document.getElementById('recent-apps-body').innerHTML = stats.recentApplications.map(a => `
        <tr>
          <td>${a.applicantName}</td>
          <td>${a.jobTitle}</td>
          <td>${formatDate(a.appliedAt)}</td>
          <td><span class="badge badge-${a.status.toLowerCase()}">${a.status}</span></td>
        </tr>`).join('') || '<tr><td colspan="4" class="text-center text-muted">Koi application nahi</td></tr>';

      drawChart(stats.approved, stats.pending, stats.rejected);

    } else {
      const [jobs, myApps] = await Promise.all([
        apiCall('/jobs'),
        apiCall('/applications/my')
      ]);

      document.getElementById('stat-jobs').textContent       = jobs.length;
      document.getElementById('stat-applicants').textContent = myApps.length;
      document.getElementById('stat-approved').textContent   = myApps.filter(a => a.status === 'Approved').length;
      document.getElementById('stat-pending').textContent    = myApps.filter(a => a.status === 'Pending').length;

      document.getElementById('recent-jobs-body').innerHTML = jobs.slice(0, 5).map(j => `
        <tr>
          <td><strong>${j.title}</strong></td>
          <td>${j.department}</td>
          <td>${formatDate(j.lastDate)}</td>
          <td>${j.vacancies}</td>
        </tr>`).join('') || '<tr><td colspan="4" class="text-center text-muted">Koi job nahi</td></tr>';

      document.getElementById('recent-apps-body').innerHTML = myApps.slice(0, 5).map(a => `
        <tr>
          <td>${a.applicantName}</td>
          <td>${a.jobTitle}</td>
          <td>${formatDate(a.appliedAt)}</td>
          <td><span class="badge badge-${a.status.toLowerCase()}">${a.status}</span></td>
        </tr>`).join('') || '<tr><td colspan="4" class="text-center text-muted">Koi application nahi</td></tr>';

      const ap = myApps.filter(a => a.status === 'Approved').length;
      const pe = myApps.filter(a => a.status === 'Pending').length;
      const re = myApps.filter(a => a.status === 'Rejected').length;
      drawChart(ap, pe, re);
    }
  } catch (err) {
    console.error('Dashboard error:', err.message);
  }
}

function drawChart(approved, pending, rejected) {
  const ctx = document.getElementById('statusChart');
  if (!ctx) return;
  if (chartInstance) chartInstance.destroy();
  chartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Approved', 'Pending', 'Rejected'],
      datasets: [{ data: [approved, pending, rejected], backgroundColor: ['#0e9f6e', '#e3a008', '#e02424'], borderWidth: 0, hoverOffset: 6 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom', labels: { padding: 15, font: { size: 12 } } } },
      cutout: '65%'
    }
  });
}


// ---- JOBS PAGE ----
let allJobs = [];

async function loadJobs() {
  const container = document.getElementById('jobs-container');
  container.innerHTML = '<p class="text-muted">Jobs load ho rahi hain...</p>';
  try {
    allJobs = await apiCall('/jobs');
    renderJobs(allJobs);

    const depts = [...new Set(allJobs.map(j => j.department))];
    const filterEl = document.getElementById('dept-filter');
    if (filterEl) {
      filterEl.innerHTML = '<option value="all">Sab Departments</option>' +
        depts.map(d => `<option value="${d}">${d}</option>`).join('');
    }
  } catch (err) {
    container.innerHTML = '<p class="text-muted">Jobs load nahi huin. Server chalu hai?</p>';
  }
}

function renderJobs(jobs) {
  const container = document.getElementById('jobs-container');
  if (!jobs.length) {
    container.innerHTML = `<div class="empty-state"><div class="empty-icon">📋</div><h3>Koi job nahi mili</h3><p>Doosra search try karo.</p></div>`;
    return;
  }
  container.innerHTML = `<div class="jobs-grid">${jobs.map(job => `
    <div class="job-card" onclick="viewJob('${job.id}')">
      <div class="job-card-header">
        <div>
          <h3>${job.title}</h3>
          <span class="dept-name">🏛 ${job.department}</span>
        </div>
        <div class="job-dept-icon">💼</div>
      </div>
      <div class="job-meta">
        <span class="job-meta-item">🎓 ${job.qualification.substring(0,30)}...</span>
        <span class="job-meta-item">💰 ₹${job.salary}</span>
        <span class="job-meta-item">📍 ${job.location}</span>
        <span class="job-meta-item">👥 ${job.vacancies} Posts</span>
      </div>
      <div class="job-card-footer">
        <span class="last-date">⏰ Last Date: ${formatDate(job.lastDate)}</span>
        <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); openApplyModal('${job.id}')">Apply Karo</button>
      </div>
    </div>`).join('')}</div>`;
}

function searchJobs() {
  const query = document.getElementById('job-search').value.toLowerCase();
  const dept  = document.getElementById('dept-filter').value;
  let filtered = allJobs;
  if (query) filtered = filtered.filter(j => j.title.toLowerCase().includes(query) || j.department.toLowerCase().includes(query));
  if (dept !== 'all') filtered = filtered.filter(j => j.department === dept);
  renderJobs(filtered);
}

let selectedJob = null;

function viewJob(jobId) {
  selectedJob = allJobs.find(j => j.id === jobId);
  if (!selectedJob) return;
  document.getElementById('job-detail-content').innerHTML = `
    <div style="margin-bottom:20px">
      <span class="dept-name">🏛 ${selectedJob.department}</span>
      <h2 style="font-size:22px;font-weight:800;margin:8px 0">${selectedJob.title}</h2>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:20px">
      <div style="background:#f3f6fb;padding:14px;border-radius:10px"><div style="font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase">Salary</div><div style="font-weight:700;margin-top:4px">₹${selectedJob.salary}</div></div>
      <div style="background:#f3f6fb;padding:14px;border-radius:10px"><div style="font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase">Vacancies</div><div style="font-weight:700;margin-top:4px">${selectedJob.vacancies}</div></div>
      <div style="background:#f3f6fb;padding:14px;border-radius:10px"><div style="font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase">Last Date</div><div style="font-weight:700;color:#e02424;margin-top:4px">${formatDate(selectedJob.lastDate)}</div></div>
      <div style="background:#f3f6fb;padding:14px;border-radius:10px"><div style="font-size:11px;color:#6b7280;font-weight:700;text-transform:uppercase">Location</div><div style="font-weight:700;margin-top:4px">${selectedJob.location}</div></div>
    </div>
    <div style="margin-bottom:16px"><div style="font-weight:700;margin-bottom:6px">📚 Qualification</div><p style="color:#6b7280;font-size:13px">${selectedJob.qualification}</p></div>
    <div><div style="font-weight:700;margin-bottom:6px">📋 Description</div><p style="color:#6b7280;font-size:13px;line-height:1.7">${selectedJob.description}</p></div>`;
  document.getElementById('job-detail-modal').classList.add('show');
}

function closeJobDetail() { document.getElementById('job-detail-modal').classList.remove('show'); }
function applyFromDetail() { closeJobDetail(); if (selectedJob) openApplyModal(selectedJob.id); }


// ---- APPLY MODAL ----
function openApplyModal(jobId) {
  const user = getUser();
  if (!user) { showToast('Pehle login karo', 'error'); return; }
  const job = allJobs.find(j => j.id === jobId);
  if (!job) return;
  document.getElementById('apply-job-id').value = jobId;
  document.getElementById('apply-job-title').textContent = job.title;
  document.getElementById('apply-dept').textContent = job.department;
  document.getElementById('apply-modal').classList.add('show');
}

function closeApplyModal() {
  document.getElementById('apply-modal').classList.remove('show');
  document.getElementById('apply-form').reset();
}

async function submitApplication() {
  const btn = document.getElementById('apply-submit-btn');
  btn.innerHTML = '<span class="spinner"></span> Submit ho raha hai...';
  btn.disabled = true;

  const data = {
    jobId:         document.getElementById('apply-job-id').value,
    phone:         document.getElementById('apply-phone').value,
    dob:           document.getElementById('apply-dob').value,
    qualification: document.getElementById('apply-qualification').value,
    experience:    document.getElementById('apply-experience').value,
    address:       document.getElementById('apply-address').value,
  };

  try {
    await apiCall('/applications/apply', 'POST', data);
    closeApplyModal();
    showToast('✅ Application submit ho gayi!');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.innerHTML = 'Submit Karo';
    btn.disabled = false;
  }
}


// ---- MY APPLICATIONS ----
async function loadMyApplications() {
  const container = document.getElementById('my-apps-container');
  container.innerHTML = '<p class="text-muted">Load ho rahi hain...</p>';
  try {
    const apps = await apiCall('/applications/my');
    if (!apps.length) {
      container.innerHTML = `<div class="empty-state"><div class="empty-icon">📭</div><h3>Abhi tak apply nahi kiya</h3><p>Jobs dekho aur apply karo!</p></div>`;
      return;
    }
    container.innerHTML = `<div class="table-responsive"><table><thead><tr><th>Job</th><th>Department</th><th>Apply Kiya</th><th>Status</th></tr></thead><tbody>${
      apps.map(a => `<tr><td><strong>${a.jobTitle}</strong></td><td>${a.department}</td><td>${formatDate(a.appliedAt)}</td><td><span class="badge badge-${a.status.toLowerCase()}">${a.status}</span></td></tr>`).join('')
    }</tbody></table></div>`;
  } catch (err) {
    container.innerHTML = '<p class="text-muted">Load nahi hua.</p>';
  }
}


// ---- ADMIN JOBS ----
async function loadAdminJobs() {
  const container = document.getElementById('admin-jobs-body');
  container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Load ho raha hai...</td></tr>';
  try {
    const jobs = await apiCall('/jobs');
    if (!jobs.length) { container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Koi job nahi. Add karo!</td></tr>'; return; }
    container.innerHTML = jobs.map(j => `<tr>
      <td><strong>${j.title}</strong></td>
      <td>${j.department}</td>
      <td>${j.vacancies}</td>
      <td>${formatDate(j.lastDate)}</td>
      <td>₹${j.salary}</td>
      <td><div style="display:flex;gap:6px">
        <button class="btn btn-outline btn-sm" onclick="editJob('${j.id}')">✏️ Edit</button>
        <button class="btn btn-danger btn-sm" onclick="deleteJob('${j.id}')">🗑 Delete</button>
      </div></td>
    </tr>`).join('');
  } catch (err) { container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Error.</td></tr>'; }
}

function openAddJobModal() {
  document.getElementById('job-modal-title').textContent = 'Naya Job Add Karo';
  document.getElementById('job-form').reset();
  document.getElementById('job-id-field').value = '';
  document.getElementById('job-modal').classList.add('show');
}

function closeJobModal() { document.getElementById('job-modal').classList.remove('show'); }

async function editJob(id) {
  try {
    const job = await apiCall(`/jobs/${id}`);
    document.getElementById('job-modal-title').textContent = 'Job Edit Karo';
    document.getElementById('job-id-field').value       = job.id;
    document.getElementById('job-title-field').value    = job.title;
    document.getElementById('job-dept-field').value     = job.department;
    document.getElementById('job-qual-field').value     = job.qualification;
    document.getElementById('job-salary-field').value   = job.salary;
    document.getElementById('job-vacancies-field').value = job.vacancies;
    document.getElementById('job-location-field').value = job.location;
    document.getElementById('job-lastdate-field').value = job.lastDate;
    document.getElementById('job-desc-field').value     = job.description;
    document.getElementById('job-modal').classList.add('show');
  } catch (err) { showToast('Job load nahi hua', 'error'); }
}

async function saveJob() {
  const jobId = document.getElementById('job-id-field').value;
  const data = {
    title:         document.getElementById('job-title-field').value,
    department:    document.getElementById('job-dept-field').value,
    qualification: document.getElementById('job-qual-field').value,
    salary:        document.getElementById('job-salary-field').value,
    vacancies:     document.getElementById('job-vacancies-field').value,
    location:      document.getElementById('job-location-field').value,
    lastDate:      document.getElementById('job-lastdate-field').value,
    description:   document.getElementById('job-desc-field').value,
  };

  const btn = document.getElementById('job-save-btn');
  btn.innerHTML = '<span class="spinner"></span> Save ho raha hai...';
  btn.disabled = true;

  try {
    if (jobId) {
      await apiCall(`/jobs/${jobId}`, 'PUT', data);
      showToast('✅ Job update ho gayi!');
    } else {
      await apiCall('/jobs', 'POST', data);
      showToast('✅ Job post ho gayi!');
    }
    closeJobModal();
    loadAdminJobs();
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    btn.innerHTML = 'Save Karo';
    btn.disabled = false;
  }
}

async function deleteJob(id) {
  if (!confirm('Pakka delete karna hai?')) return;
  try {
    await apiCall(`/jobs/${id}`, 'DELETE');
    showToast('Job delete ho gayi.');
    loadAdminJobs();
  } catch (err) { showToast(err.message, 'error'); }
}


// ---- ADMIN APPLICATIONS ----
async function loadAdminApplications() {
  const container = document.getElementById('admin-apps-body');
  container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Load ho raha hai...</td></tr>';
  try {
    const apps = await apiCall('/applications/all');
    if (!apps.length) { container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Koi application nahi.</td></tr>'; return; }
    container.innerHTML = apps.map(a => `<tr>
      <td><strong>${a.applicantName}</strong><br><span class="text-muted">${a.applicantEmail}</span></td>
      <td>${a.jobTitle}</td>
      <td>${a.phone}</td>
      <td>${formatDate(a.appliedAt)}</td>
      <td><span class="badge badge-${a.status.toLowerCase()}">${a.status}</span></td>
      <td>
        <select class="status-select" onchange="updateStatus('${a.id}', this.value)">
          <option value="Pending"  ${a.status==='Pending'  ? 'selected':''}>Pending</option>
          <option value="Approved" ${a.status==='Approved' ? 'selected':''}>Approved</option>
          <option value="Rejected" ${a.status==='Rejected' ? 'selected':''}>Rejected</option>
        </select>
      </td>
    </tr>`).join('');
  } catch (err) { container.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Load nahi hua.</td></tr>'; }
}

async function updateStatus(appId, status) {
  try {
    await apiCall(`/applications/status/${appId}`, 'PUT', { status });
    showToast(`Status ${status} kar diya!`);
    loadAdminApplications();
  } catch (err) { showToast(err.message, 'error'); }
}


// ---- USERS ----
async function loadUsers() {
  const container = document.getElementById('users-body');
  try {
    const apps = await apiCall('/applications/all');
    const unique = {};
    apps.forEach(a => {
      if (!unique[a.userId]) unique[a.userId] = { name: a.applicantName, email: a.applicantEmail, phone: a.phone, apps: 0 };
      unique[a.userId].apps++;
    });
    const users = Object.values(unique);
    if (!users.length) { container.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Koi user nahi.</td></tr>'; return; }
    container.innerHTML = users.map(u => `<tr>
      <td><div style="display:flex;align-items:center;gap:10px"><div class="user-avatar" style="width:32px;height:32px;font-size:12px">${u.name.charAt(0)}</div><strong>${u.name}</strong></div></td>
      <td>${u.email}</td>
      <td>${u.phone}</td>
      <td>${u.apps} application${u.apps !== 1 ? 's' : ''}</td>
    </tr>`).join('');
  } catch (err) { container.innerHTML = '<tr><td colspan="4" class="text-center text-muted">Load nahi hua.</td></tr>'; }
}


// ---- MOBILE SIDEBAR ----
function toggleSidebar() {
  document.querySelector('.sidebar').classList.toggle('open');
}
