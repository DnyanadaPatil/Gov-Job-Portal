// ===== API HELPER =====
async function apiCall(endpoint, method, body) {
    const token = localStorage.getItem('govtToken');
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    const res = await fetch('/api' + endpoint, {
        method: method || 'GET',
        headers: headers,
        body: body ? JSON.stringify(body) : undefined
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.message || 'Something went wrong');
    return data;
}

// ===== SHOW ALERT =====
function showAlert(id, msg, type) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = msg;
    el.style.display = 'block';
    el.style.padding = '10px';
    el.style.borderRadius = '6px';
    el.style.marginBottom = '12px';
    el.style.background = type === 'success' ? '#d1fae5' : '#fee2e2';
    el.style.color = type === 'success' ? '#065f46' : '#991b1b';
}

// ===== REDIRECT IF LOGGED IN =====
function redirectIfLoggedIn() {
    if (localStorage.getItem('govtUser')) {
        window.location.href = 'pages/dashboard.html';
    }
}

// ===== LOGOUT =====
function logout() {
    localStorage.removeItem('govtUser');
    localStorage.removeItem('govtToken');
    window.location.href = '../index.html';
}

// ===== LOAD PAGE =====
function loadPage(page) {
    const user = JSON.parse(localStorage.getItem('govtUser') || 'null');
    if (!user) { window.location.href = '../index.html'; return; }

    const main = document.getElementById('mainContent');
    if (!main) return;

    // Update active nav
    document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
    const activeNav = document.querySelector('[data-page="' + page + '"]');
    if (activeNav) activeNav.classList.add('active');

    if (page === 'jobs') {
        main.innerHTML = '<div class="page-header"><h1 class="page-title">Available Government Jobs</h1></div><div id="jobsList"><p>Loading jobs...</p></div>';
        fetch('/api/jobs')
            .then(r => r.json())
            .then(data => {
                if (!data.success) { document.getElementById('jobsList').innerHTML = '<p>Failed to load jobs.</p>'; return; }
                let html = '';
                data.jobs.forEach(job => {
                    html += '<div class="card" style="margin-bottom:16px;padding:20px;">' +
                        '<h3 style="color:#1a237e;margin:0 0 10px;">' + job.title + '</h3>' +
                        '<p>🏢 Department: ' + job.department + '</p>' +
                        '<p>📍 Location: ' + job.location + '</p>' +
                        '<p>💰 Salary: ₹' + job.salary + '</p>' +
                        '<p>👥 Vacancies: ' + job.vacancies + '</p>' +
                        '<p>📅 Last Date: ' + job.lastDate + '</p>' +
                        '<button class="btn btn-primary" onclick="openApply(' + job.id + ', \'' + job.title + '\')">Apply Now</button>' +
                        '</div>';
                });
                document.getElementById('jobsList').innerHTML = html || '<p>No jobs available.</p>';
            })
            .catch(() => { document.getElementById('jobsList').innerHTML = '<p>Error loading jobs.</p>'; });

    } else if (page === 'my-applications') {
        const apps = JSON.parse(localStorage.getItem('myApps') || '[]');
        let html = '<div class="page-header"><h1 class="page-title">My Applications</h1></div>';
        if (apps.length === 0) {
            html += '<div class="card" style="padding:20px;"><p>No applications submitted yet.</p></div>';
        } else {
            html += '<div class="card" style="padding:20px;"><table style="width:100%;border-collapse:collapse;">' +
                '<tr style="background:#e8eaf6;"><th style="padding:10px;text-align:left;">Job ID</th><th style="padding:10px;text-align:left;">Name</th><th style="padding:10px;text-align:left;">Email</th><th style="padding:10px;text-align:left;">Phone</th></tr>';
            apps.forEach(a => {
                html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:10px;">' + a.jobId + '</td><td style="padding:10px;">' + a.name + '</td><td style="padding:10px;">' + a.email + '</td><td style="padding:10px;">' + a.phone + '</td></tr>';
            });
            html += '</table></div>';
        }
        main.innerHTML = html;

    } else if (page === 'manage-jobs') {
        main.innerHTML = '<div class="page-header"><h1 class="page-title">Add New Job</h1></div>' +
            '<div class="card" style="padding:24px;max-width:500px;">' +
            '<div style="margin-bottom:14px;"><label><b>Job Title:</b></label><br><input type="text" id="jobTitle" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="e.g. Police Constable"></div>' +
            '<div style="margin-bottom:14px;"><label><b>Department:</b></label><br><input type="text" id="jobDept" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="e.g. Maharashtra Police"></div>' +
            '<div style="margin-bottom:14px;"><label><b>Location:</b></label><br><input type="text" id="jobLocation" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="e.g. Mumbai"></div>' +
            '<div style="margin-bottom:14px;"><label><b>Salary:</b></label><br><input type="text" id="jobSalary" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="e.g. 25,000 - 35,000"></div>' +
            '<div style="margin-bottom:14px;"><label><b>Vacancies:</b></label><br><input type="number" id="jobVacancies" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="e.g. 100"></div>' +
            '<div style="margin-bottom:14px;"><label><b>Last Date:</b></label><br><input type="date" id="jobLastDate" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;"></div>' +
            '<button class="btn btn-primary" onclick="addJob()">Add Job</button></div>';

    } else if (page === 'all-applications') {
        main.innerHTML = '<div class="page-header"><h1 class="page-title">All Applications</h1></div><div id="allAppsList"><p>Loading...</p></div>';
        fetch('/api/applications')
            .then(r => r.json())
            .then(data => {
                if (!data.success || data.applications.length === 0) {
                    document.getElementById('allAppsList').innerHTML = '<div class="card" style="padding:20px;"><p>No applications yet.</p></div>';
                    return;
                }
                let html = '<div class="card" style="padding:20px;"><table style="width:100%;border-collapse:collapse;">' +
                    '<tr style="background:#e8eaf6;"><th style="padding:10px;text-align:left;">ID</th><th style="padding:10px;text-align:left;">Job ID</th><th style="padding:10px;text-align:left;">Name</th><th style="padding:10px;text-align:left;">Email</th><th style="padding:10px;text-align:left;">Phone</th></tr>';
                data.applications.forEach(a => {
                    html += '<tr style="border-bottom:1px solid #eee;"><td style="padding:10px;">' + a.id + '</td><td style="padding:10px;">' + a.jobId + '</td><td style="padding:10px;">' + a.name + '</td><td style="padding:10px;">' + a.email + '</td><td style="padding:10px;">' + a.phone + '</td></tr>';
                });
                html += '</table></div>';
                document.getElementById('allAppsList').innerHTML = html;
            });
    }
}

// ===== APPLY FOR JOB =====
function openApply(jobId, jobTitle) {
    const main = document.getElementById('mainContent');
    main.innerHTML = '<div class="page-header"><h1 class="page-title">Apply for: ' + jobTitle + '</h1></div>' +
        '<div class="card" style="padding:24px;max-width:500px;">' +
        '<div style="margin-bottom:14px;"><label><b>Your Name:</b></label><br><input type="text" id="applyName" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="Enter your full name"></div>' +
        '<div style="margin-bottom:14px;"><label><b>Email:</b></label><br><input type="text" id="applyEmail" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="Enter your email"></div>' +
        '<div style="margin-bottom:14px;"><label><b>Phone:</b></label><br><input type="text" id="applyPhone" style="width:100%;padding:8px;margin-top:5px;border:1px solid #ddd;border-radius:5px;box-sizing:border-box;" placeholder="Enter your phone number"></div>' +
        '<button class="btn btn-primary" onclick="submitApplication(' + jobId + ')">Submit Application</button>' +
        '<button class="btn btn-outline" onclick="loadPage(\'jobs\')" style="margin-left:10px;">Cancel</button></div>';
}

function submitApplication(jobId) {
    const name = document.getElementById('applyName').value;
    const email = document.getElementById('applyEmail').value;
    const phone = document.getElementById('applyPhone').value;
    if (!name || !email || !phone) { alert('Please fill all fields!'); return; }
    fetch('/api/apply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jobId: jobId, name: name, email: email, phone: phone })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            const apps = JSON.parse(localStorage.getItem('myApps') || '[]');
            apps.push({ jobId: jobId, name: name, email: email, phone: phone });
            localStorage.setItem('myApps', JSON.stringify(apps));
            alert('Application submitted successfully!');
            loadPage('jobs');
        }
    });
}

// ===== ADD JOB =====
function addJob() {
    alert('Job added successfully! (Database save coming soon)');
}

// ===== DASHBOARD INIT =====
document.addEventListener('DOMContentLoaded', function() {
    const user = JSON.parse(localStorage.getItem('govtUser') || 'null');
    if (!user) { window.location.href = '../index.html'; return; }

    // Set welcome message
    const welcomeEl = document.getElementById('welcomeMsg');
    if (welcomeEl) welcomeEl.textContent = 'Welcome, ' + user.name + '!';

    // Set sidebar user
    const sidebarUser = document.getElementById('sidebarUser');
    if (sidebarUser) {
        sidebarUser.innerHTML = '<div style="padding:16px;border-top:1px solid rgba(255,255,255,0.1);">' +
            '<div style="font-weight:600;">' + user.name + '</div>' +
            '<div style="font-size:12px;opacity:0.7;">' + user.role + '</div>' +
            '<button onclick="logout()" style="margin-top:10px;width:100%;padding:8px;background:#ff5722;color:white;border:none;border-radius:5px;cursor:pointer;">Logout</button>' +
            '</div>';
    }

    // Show/hide admin items
    if (user.role !== 'admin') {
        document.querySelectorAll('.admin-only').forEach(el => el.style.display = 'none');
    }

    // Load stats
    fetch('/api/jobs')
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                const el = document.getElementById('totalJobs');
                if (el) el.textContent = data.jobs.length;
            }
        });

    const myApps = JSON.parse(localStorage.getItem('myApps') || '[]');
    const pendingEl = document.getElementById('pendingApps');
    if (pendingEl) pendingEl.textContent = myApps.length;
});
