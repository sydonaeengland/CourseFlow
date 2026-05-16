/* ============================================================
   CourseFlow — Shared App Logic
   ============================================================ */

const BASE = '';

// ── STATE ────────────────────────────────────────────────────
const CF = {
  token: localStorage.getItem('cf_token'),
  user: JSON.parse(localStorage.getItem('cf_user') || 'null'),
  courses: [],
};

// ── SVG ICONS ────────────────────────────────────────────────
const SVG_ICONS = {
  cs: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><polyline points="8 21 12 17 16 21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>`,
  math: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="5" x2="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/></svg>`,
  bio: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22C6.477 22 2 17.523 2 12S6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`,
  chem: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6v11l3.3 5.5A1 1 0 0 1 17.4 21H6.6a1 1 0 0 1-.9-1.5L9 14V3z"/><line x1="9" y1="3" x2="15" y2="3"/><path d="M9.5 14.5a5 5 0 0 1 5 0"/></svg>`,
  phys: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg>`,
  eng: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/><path d="M20.66 8A10 10 0 0 1 20.66 16M3.34 8a10 10 0 0 0 0 8"/></svg>`,
  data: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`,
  design: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="13.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="10.5" r="2.5"/><circle cx="8.5" cy="7.5" r="2.5"/><circle cx="6.5" cy="12.5" r="2.5"/><path d="M12 22a4 4 0 0 1-4-4l1-8 7 4-4 8z"/></svg>`,
  net: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>`,
  sec: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
  default: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>`,
};

// ── SUBJECT CLASSIFICATION ───────────────────────────────────
const SUBJECTS = [
  { keywords: ['computer','software','algorithm','data struct','programming','cyber','network','database','web','mobile'], cls: 'subject-cs',     icon: SVG_ICONS.cs,      label: 'Computer Science' },
  { keywords: ['math','calculus','algebra','statistic','numeric','discrete'],                                              cls: 'subject-math',   icon: SVG_ICONS.math,    label: 'Mathematics' },
  { keywords: ['biology','bio','ecology','genetic','microbio','anatomy'],                                                  cls: 'subject-bio',    icon: SVG_ICONS.bio,     label: 'Biology' },
  { keywords: ['chemistry','chem','organic','biochem'],                                                                    cls: 'subject-chem',   icon: SVG_ICONS.chem,    label: 'Chemistry' },
  { keywords: ['physics','phys','mechanics','quantum','thermodynamic'],                                                    cls: 'subject-phys',   icon: SVG_ICONS.phys,    label: 'Physics' },
  { keywords: ['engineering','circuit','electric','mechanic','civil','struct'],                                            cls: 'subject-eng',    icon: SVG_ICONS.eng,     label: 'Engineering' },
  { keywords: ['data science','machine learn','artificial','neural','deep learn','analytics'],                             cls: 'subject-data',   icon: SVG_ICONS.data,    label: 'Data Science' },
  { keywords: ['design','interface','ux','ui','graphic','visual','studio'],                                                cls: 'subject-design', icon: SVG_ICONS.design,  label: 'Design' },
  { keywords: ['network','protocol','tcp','infrastructure'],                                                               cls: 'subject-net',    icon: SVG_ICONS.net,     label: 'Networks' },
  { keywords: ['security','cybersec','cryptograph','forensic'],                                                            cls: 'subject-sec',    icon: SVG_ICONS.sec,     label: 'Security' },
];

function classifyCourse(cname = '', ccode = '') {
  const text = (cname + ' ' + ccode).toLowerCase();
  for (const s of SUBJECTS) {
    if (s.keywords.some(k => text.includes(k))) return s;
  }
  return { cls: 'subject-default', icon: SVG_ICONS.default, label: 'General' };
}

// ── API HELPER ───────────────────────────────────────────────
async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (CF.token) headers['Authorization'] = `Bearer ${CF.token}`;
  try {
    const res = await fetch(BASE + path, { headers, ...opts });
    const data = await res.json().catch(() => ({}));
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    return { ok: false, status: 0, data: { message: 'Network error' } };
  }
}

// ── AUTH HELPERS ─────────────────────────────────────────────
function isLoggedIn() {
  return !!CF.token && !!CF.user;
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = '/auth.html';
    return false;
  }
  return true;
}

function requireRole(...roles) {
  if (!requireAuth()) return false;
  if (!roles.includes(CF.user?.role)) {
    window.location.href = '/dashboard.html';
    return false;
  }
  return true;
}

function saveSession(token, user) {
  CF.token = token;
  CF.user  = user;
  localStorage.setItem('cf_token', token);
  localStorage.setItem('cf_user', JSON.stringify(user));
}

function clearSession() {
  CF.token = null;
  CF.user  = null;
  localStorage.removeItem('cf_token');
  localStorage.removeItem('cf_user');
}

function logout() {
  clearSession();
  window.location.href = '/auth.html';
}

function decodeJWT(token) {
  try {
    return JSON.parse(atob(token.split('.')[1]));
  } catch { return {}; }
}

// ── SVG SHORTCUTS ────────────────────────────────────────────
const _svg = {
  logo:      `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>`,
  dashboard: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>`,
  courses:   `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>`,
  workspace: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>`,
  forums:    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>`,
  events:    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`,
  admin:     `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M4.93 4.93a10 10 0 0 0 0 14.14"/></svg>`,
  chevron:   `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>`,
  signout:   `<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>`,
};

function _navItem(page, icon, label, activePage, hidden = false) {
  const pageMap = { enrolments: 'enrolments.html', grades: 'grades.html', 'admin-courses': 'admin-courses.html', 'admin-users': 'admin-users.html', 'admin-reports': 'admin-reports.html', 'admin-events': 'admin-events.html' };
  const href = pageMap[page] || (page + '.html');
  return `<a class="nav-item${page === activePage ? ' active' : ''}" data-page="${page}" href="/${href}"${hidden ? ' style="display:none"' : ''} title="${label}">
    <span class="nav-icon">${icon}</span><span class="nav-item-label">${label}</span>
  </a>`;
}

// ── SIDEBAR RENDER ───────────────────────────────────────────
function renderSidebar(activePage) {
  if (!CF.user) return;

  const u       = CF.user;
  const displayName = u.fname ? `${u.fname}${u.lname ? ' ' + u.lname : ''}` : u.username;
  const initial = (u.fname || u.username || '?')[0].toUpperCase();
  const isAdmin = u.role === 'admin';

  const sidebar = document.getElementById('sidebar');

  // Restore collapsed state
  if (localStorage.getItem('cf_sidebar') === 'collapsed') {
    sidebar?.classList.add('collapsed');
    document.body.classList.add('sidebar-collapsed');
  }

  if (sidebar) {
    sidebar.innerHTML = `
      <div class="sidebar-header">
        <div class="sidebar-brand">
          <div class="brand-icon">${_svg.logo}</div>
          <span class="sidebar-brand-text">CourseFlow</span>
        </div>
        <button class="sidebar-toggle" onclick="toggleSidebar()" title="Toggle sidebar">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        ${isAdmin ? `
        <div class="nav-section">
          <button class="nav-section-toggle" onclick="toggleNavSection(this)" aria-expanded="true">
            <span>Overview</span>${_svg.chevron}
          </button>
          <div class="nav-section-body">
            ${_navItem('admin',   _svg.dashboard, 'Dashboard',    activePage)}
          </div>
        </div>
        <div class="nav-section">
          <button class="nav-section-toggle" onclick="toggleNavSection(this)" aria-expanded="true">
            <span>Management</span>${_svg.chevron}
          </button>
          <div class="nav-section-body">
            ${_navItem('admin-courses', _svg.courses, 'Courses',  activePage)}
            ${_navItem('admin-users',   _svg.admin,   'Users',    activePage)}
            ${_navItem('admin-events',  _svg.events,  'Events',   activePage)}
            ${_navItem('admin-reports', `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>`, 'Reports', activePage)}
          </div>
        </div>` : `
        ${u.role === 'lecturer' ? `
        <div class="nav-section">
          <button class="nav-section-toggle" onclick="toggleNavSection(this)" aria-expanded="true">
            <span>Teaching</span>${_svg.chevron}
          </button>
          <div class="nav-section-body">
            ${_navItem('dashboard',  _svg.dashboard, 'Dashboard',    activePage)}
            ${_navItem('enrolments', _svg.courses,   'My Courses',   activePage)}
            ${_navItem('courses',    _svg.workspace,  'Course Catalog', activePage)}
          </div>
        </div>
        <div class="nav-section">
          <button class="nav-section-toggle" onclick="toggleNavSection(this)" aria-expanded="true">
            <span>Activity</span>${_svg.chevron}
          </button>
          <div class="nav-section-body">
            ${_navItem('forums', _svg.forums, 'Forums',   activePage)}
            ${_navItem('events', _svg.events, 'Schedule', activePage)}
          </div>
        </div>` : `
        <div class="nav-section">
          <button class="nav-section-toggle" onclick="toggleNavSection(this)" aria-expanded="true">
            <span>Main</span>${_svg.chevron}
          </button>
          <div class="nav-section-body">
            ${_navItem('dashboard',  _svg.dashboard, 'Dashboard',      activePage)}
            ${_navItem('courses',    _svg.courses,   'Course Catalog',  activePage)}
            ${_navItem('enrolments', _svg.workspace, 'My Enrolments',  activePage)}
          </div>
        </div>
        <div class="nav-section">
          <button class="nav-section-toggle" onclick="toggleNavSection(this)" aria-expanded="true">
            <span>Community</span>${_svg.chevron}
          </button>
          <div class="nav-section-body">
            ${_navItem('forums', _svg.forums, 'Academic Forums', activePage)}
            ${_navItem('events', _svg.events, 'Schedule',        activePage)}
          </div>
        </div>
        <div class="nav-section">
          <button class="nav-section-toggle" onclick="toggleNavSection(this)" aria-expanded="true">
            <span>Academic</span>${_svg.chevron}
          </button>
          <div class="nav-section-body">
            ${_navItem('grades', '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>', 'My Grades', activePage)}
          </div>
        </div>`}`}
      </nav>

      <div class="sidebar-user-card">
        <a class="sidebar-user-info" href="/profile.html">
          <div class="user-avatar">${initial}</div>
          <div class="user-details">
            <div class="user-name">${displayName}</div>
            <div class="user-role">${u.role || '—'}</div>
          </div>
        </a>
        <button class="sidebar-logout-btn" onclick="logout()" title="Sign out">
          ${_svg.signout}
        </button>
      </div>`;
  }

  // Topbar
  const tbAvatar = document.getElementById('tb-avatar');
  const tbName   = document.getElementById('tb-username');
  if (tbAvatar) tbAvatar.textContent = initial;
  if (tbName)   tbName.textContent   = displayName;

  // Topbar avatar dropdown (profile + logout)
  const tbBtn = document.querySelector('.topbar-avatar-btn');
  if (tbBtn && !tbBtn.dataset.dropdownReady) {
    tbBtn.dataset.dropdownReady = '1';
    tbBtn.removeAttribute('href');
    tbBtn.style.cursor = 'pointer';
    tbBtn.style.position = 'relative';

    const drop = document.createElement('div');
    drop.id = 'tb-dropdown';
    drop.innerHTML = `
      <a href="/profile.html" style="display:flex;align-items:center;gap:10px;padding:10px 14px;text-decoration:none;color:var(--text);font-size:13px;font-weight:500;border-radius:6px;transition:background 0.12s" onmouseover="this.style.background='var(--bg)'" onmouseout="this.style.background=''">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        View Profile
      </a>
      <div style="height:1px;background:var(--border);margin:4px 0"></div>
      <button onclick="logout()" style="display:flex;align-items:center;gap:10px;padding:10px 14px;width:100%;background:none;border:none;cursor:pointer;color:#ef4444;font-size:13px;font-weight:600;border-radius:6px;transition:background 0.12s" onmouseover="this.style.background='rgba(220,38,38,0.08)'" onmouseout="this.style.background=''">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Sign Out
      </button>`;
    Object.assign(drop.style, {
      position:'absolute', top:'calc(100% + 8px)', right:'0',
      background:'var(--surface)', border:'1px solid var(--border)',
      borderRadius:'10px', boxShadow:'var(--shadow-md)',
      padding:'4px', minWidth:'160px', zIndex:'999',
      display:'none'
    });
    tbBtn.appendChild(drop);

    tbBtn.addEventListener('click', e => {
      e.stopPropagation();
      drop.style.display = drop.style.display === 'none' ? 'block' : 'none';
    });
    document.addEventListener('click', () => { drop.style.display = 'none'; }, { capture: true });
  }

  const chipEl = document.getElementById('tb-role-chip');
  if (chipEl) {
    chipEl.textContent = u.role || '';
    chipEl.className   = `role-chip ${u.role || ''}`;
  }
}

function toggleNavSection(btn) {
  const expanded = btn.getAttribute('aria-expanded') === 'true';
  const body = btn.nextElementSibling;
  if (expanded) {
    // Pin to px first so CSS can animate down to 0
    body.style.maxHeight = body.scrollHeight + 'px';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        body.style.maxHeight = '0';
        btn.setAttribute('aria-expanded', 'false');
      });
    });
  } else {
    btn.setAttribute('aria-expanded', 'true');
    body.style.maxHeight = body.scrollHeight + 'px';
    setTimeout(() => { body.style.maxHeight = 'none'; }, 280);
  }
}

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const collapsed = sidebar.classList.toggle('collapsed');
  document.body.classList.toggle('sidebar-collapsed', collapsed);
  localStorage.setItem('cf_sidebar', collapsed ? 'collapsed' : 'expanded');
}

// ── TOAST ────────────────────────────────────────────────────
function toast(msg, type = 'info') {
  let t = document.getElementById('toast');
  if (!t) {
    t = document.createElement('div');
    t.id = 'toast';
    document.body.appendChild(t);
  }
  t.textContent = msg;
  t.className = `show ${type}`;
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), 3500);
}

// ── MODAL HELPERS ────────────────────────────────────────────
function openModal(id)  { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }

// ── COURSE CARD HTML ─────────────────────────────────────────
function courseCardHTML(c, opts = {}) {
  const sub   = classifyCourse(c.cname, c.ccode);
  const grade = opts.grade || c.grade;
  const due   = opts.due;
  const lecturer = c.fname ? `${c.fname} ${c.lname}` : (c.lecturer || '');

  let gradeHTML = '';
  if (grade) {
    const cls = grade.startsWith('A') ? 'grade-a' : grade.startsWith('B') ? 'grade-b' : grade === 'TBD' ? 'grade-tbd' : 'grade-c';
    gradeHTML = `<span class="grade-badge ${cls}">${grade}</span>`;
  }

  let statusHTML = '';
  if (due > 0) {
    statusHTML = `<span class="course-status due">${due} Due</span>`;
  } else if (due === 0) {
    statusHTML = `<span class="course-status ok">All clear</span>`;
  } else if (due === null) {
    statusHTML = `<span class="course-status tbd">TBD</span>`;
  }

  const lecturerHTML = lecturer
    ? `<span class="course-lecturer"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> ${lecturer}</span>`
    : `<span class="course-lecturer"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg> Unassigned</span>`;

  return `
  <div class="course-card" onclick="viewCourse(${c.courseID}, ${JSON.stringify((c.ccode||'')).replace(/"/g,"'")}, ${JSON.stringify((c.cname||'')).replace(/"/g,"'")})">
    <div class="course-header ${sub.cls}">
      <div class="course-header-icon">${sub.icon}</div>
      <span class="course-header-badge">${sub.label}</span>
    </div>
    <div class="course-body">
      <div class="course-code">${c.ccode || ''} ${gradeHTML}</div>
      <div class="course-name">${c.cname || ''}</div>
      <div class="course-footer">
        ${lecturerHTML}
        ${statusHTML}
      </div>
    </div>
  </div>`;
}

// ── ENROLL MODAL ─────────────────────────────────────────────
async function enrollInCourse(courseID) {
  if (!CF.user || CF.user.role !== 'student') {
    toast('Only students can enroll', 'error');
    return;
  }
  const r = await api(`/courses/${courseID}/enroll`, {
    method: 'POST',
    body: JSON.stringify({ studID: CF.user.userID }),
  });
  toast(r.data.message || (r.ok ? 'Enrolled!' : 'Error'), r.ok ? 'success' : 'error');
}

// ── VIEW COURSE ──────────────────────────────────────────────
function viewCourse(courseID, from) {
  window.location.href = `/course.html?id=${courseID}${from ? '&from=' + from : ''}`;
}


// ── CUSTOM COURSE SELECT ─────────────────────────────────────
function populateSelect(elId, courses, onChangeCb) {
  const native = document.getElementById(elId);
  if (!native) return;

  // Build or find the custom wrapper
  let wrap = document.getElementById(elId + '-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = elId + '-wrap';
    wrap.className = 'cs-wrap';
    native.parentNode.insertBefore(wrap, native);
    native.style.display = 'none';
  }
  if (onChangeCb) wrap._onChangeCb = onChangeCb;

  const searchId  = elId + '-search';
  const listId    = elId + '-list';
  const triggerId = elId + '-trigger';

  wrap.innerHTML = `
    <button type="button" class="cs-trigger" id="${triggerId}" onclick="toggleCourseSelect('${elId}')">
      <span class="cs-trigger-text" id="${elId}-label">All courses</span>
      <svg class="cs-arrow" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
    </button>
    <div class="cs-dropdown" id="${elId}-dropdown">
      <div class="cs-search-wrap">
        <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input class="cs-search" id="${searchId}" type="text" placeholder="Search courses…" oninput="filterCourseSelect('${elId}')" autocomplete="off" />
      </div>
      <div class="cs-list" id="${listId}"></div>
    </div>`;

  // Store courses on element for filtering
  wrap._courses = courses;
  wrap._value   = native.value || '';
  renderCourseList(elId, courses);

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!wrap.contains(e.target)) closeCourseSelect(elId);
  }, { capture: true });
}

function renderCourseList(elId, courses) {
  const listEl  = document.getElementById(elId + '-list');
  const native  = document.getElementById(elId);
  const wrap    = document.getElementById(elId + '-wrap');
  const current = wrap?._value || '';

  const isAllCourses = native.options[0]?.value === '';
  const allOption    = isAllCourses
    ? `<div class="cs-option${current === '' ? ' selected' : ''}" onclick="selectCourseOption('${elId}', '', 'All courses')" data-val="">All courses</div>`
    : '';

  const items = courses.map(c => {
    const label = `${c.ccode} — ${c.cname}`;
    return `<div class="cs-option${current === String(c.courseID) ? ' selected' : ''}" onclick="selectCourseOption('${elId}', '${c.courseID}', '${label.replace(/'/g,"\\'")}', '${(c.ccode||'').replace(/'/g,"\\'")}', '${(c.cname||'').replace(/'/g,"\\'")}')" data-val="${c.courseID}">
      <span class="cs-option-code">${c.ccode}</span>
      <span class="cs-option-name">${c.cname}</span>
    </div>`;
  }).join('');

  listEl.innerHTML = allOption + (items || '<div class="cs-empty">No courses found</div>');
}

function filterCourseSelect(elId) {
  const q     = (document.getElementById(elId + '-search')?.value || '').toLowerCase();
  const wrap  = document.getElementById(elId + '-wrap');
  const all   = wrap?._courses || [];
  const filtered = q ? all.filter(c => (c.ccode||'').toLowerCase().includes(q) || (c.cname||'').toLowerCase().includes(q)) : all;
  renderCourseList(elId, filtered);
}

function selectCourseOption(elId, value, label) {
  const native  = document.getElementById(elId);
  const wrap    = document.getElementById(elId + '-wrap');
  if (!native || !wrap) return;
  native.value  = value;
  wrap._value   = value;
  document.getElementById(elId + '-label').textContent = label;
  renderCourseList(elId, wrap._courses);
  closeCourseSelect(elId);
  if (typeof wrap._onChangeCb === 'function') wrap._onChangeCb();
}

function toggleCourseSelect(elId) {
  const dd = document.getElementById(elId + '-dropdown');
  if (!dd) return;
  const open = dd.classList.toggle('open');
  if (open) setTimeout(() => document.getElementById(elId + '-search')?.focus(), 50);
}

function closeCourseSelect(elId) {
  document.getElementById(elId + '-dropdown')?.classList.remove('open');
}
