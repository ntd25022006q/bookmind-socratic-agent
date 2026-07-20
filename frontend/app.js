document.addEventListener('DOMContentLoaded', () => {

    // ── UI Elements ──────────────────────────────────────────────────────────
    const topicInput       = document.getElementById('topic-input');
    const runBtn           = document.getElementById('run-btn');
    const downloadGroup    = document.getElementById('download-group');
    const downloadPdfBtn   = document.getElementById('download-pdf-btn');
    const downloadDiagBtn  = document.getElementById('download-diagram-btn');

    const statTime         = document.getElementById('stat-time');
    const statTokens       = document.getElementById('stat-tokens');
    const statAgents       = document.getElementById('stat-agents');
    const statStatus       = document.getElementById('stat-status');

    const consoleOutput    = document.getElementById('console-output');
    const activeAgentBadge = document.getElementById('active-agent-badge');

    const reportView       = document.getElementById('report-view');
    const mermaidOutput    = document.getElementById('mermaid-render-output');
    const rawMarkdownText  = document.getElementById('raw-markdown-text');
    const copyBtn          = document.getElementById('copy-btn');

    const tabBtns  = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    // Zoom & scale elements
    const zoomOutBtn = document.getElementById('zoom-out-btn');
    const zoomInBtn = document.getElementById('zoom-in-btn');
    const zoomResetBtn = document.getElementById('zoom-reset-btn');
    const zoomLevelEl = document.getElementById('zoom-level');

    // Stop element
    const stopBtn = document.getElementById('stop-btn');

    // Socratic Modal elements
    const socraticModal = document.getElementById('socratic-modal');
    const socraticForm = document.getElementById('socratic-form');
    const socraticQuestionsContainer = document.getElementById('socratic-questions-container');
    let activeStateSnapshot = null;

    // ── Profile Modal Logic ──────────────────────────────────────────────────
    const profileModal = document.getElementById('profile-modal');
    const profileForm = document.getElementById('profile-form');
    const editProfileBtn = document.getElementById('edit-profile-btn');

    const profileInputs = {
        fullname: document.getElementById('prof-fullname'),
        studentId: document.getElementById('prof-student-id'),
        year: document.getElementById('prof-year'),
        school: document.getElementById('prof-school'),
        major: document.getElementById('prof-major'),
        purpose: document.getElementById('prof-purpose'),
        interests: document.getElementById('prof-interests'),
        style: document.getElementById('prof-style'),
        
        // Other input fields
        yearOther: document.getElementById('prof-year-other'),
        schoolOther: document.getElementById('prof-school-other'),
        purposeOther: document.getElementById('prof-purpose-other'),
        interestsOther: document.getElementById('prof-interests-other'),
        styleOther: document.getElementById('prof-style-other')
    };

    // Helper to toggle 'Other' input visibility
    function toggleOtherInput(selectEl, otherInputEl) {
        if (selectEl && otherInputEl) {
            if (selectEl.value === 'Khác') {
                otherInputEl.style.display = 'block';
                otherInputEl.required = true;
            } else {
                otherInputEl.style.display = 'none';
                otherInputEl.required = false;
                otherInputEl.value = '';
            }
        }
    }

    // Register dropdown change events to handle 'Other' options
    const dropdownsToWatch = [
        { select: profileInputs.year, other: profileInputs.yearOther },
        { select: profileInputs.school, other: profileInputs.schoolOther },
        { select: profileInputs.purpose, other: profileInputs.purposeOther },
        { select: profileInputs.interests, other: profileInputs.interestsOther },
        { select: profileInputs.style, other: profileInputs.styleOther }
    ];

    dropdownsToWatch.forEach(item => {
        if (item.select) {
            item.select.addEventListener('change', () => toggleOtherInput(item.select, item.other));
        }
    });

    function getResolvedValue(selectEl, otherInputEl) {
        if (!selectEl) return '';
        if (selectEl.value === 'Khác' && otherInputEl) {
            return `Khác (${otherInputEl.value.trim()})`;
        }
        return selectEl.value;
    }

    function saveUserProfile() {
        const profileData = {
            fullname: profileInputs.fullname ? profileInputs.fullname.value.trim() : '',
            studentId: profileInputs.studentId ? profileInputs.studentId.value.trim() : '',
            
            // Core select values (no hardcoded defaults — user must choose)
            yearRaw: profileInputs.year ? profileInputs.year.value : '',
            schoolRaw: profileInputs.school ? profileInputs.school.value : '',
            purposeRaw: profileInputs.purpose ? profileInputs.purpose.value : '',
            interestsRaw: profileInputs.interests ? profileInputs.interests.value : '',
            styleRaw: profileInputs.style ? profileInputs.style.value : '',
            
            // Raw text inputs for 'Other' options
            yearOtherVal: profileInputs.yearOther ? profileInputs.yearOther.value.trim() : '',
            schoolOtherVal: profileInputs.schoolOther ? profileInputs.schoolOther.value.trim() : '',
            purposeOtherVal: profileInputs.purposeOther ? profileInputs.purposeOther.value.trim() : '',
            interestsOtherVal: profileInputs.interestsOther ? profileInputs.interestsOther.value.trim() : '',
            styleOtherVal: profileInputs.styleOther ? profileInputs.styleOther.value.trim() : '',

            major: profileInputs.major ? profileInputs.major.value.trim() : '',
            
            // Final resolved display values
            year: getResolvedValue(profileInputs.year, profileInputs.yearOther),
            school: getResolvedValue(profileInputs.school, profileInputs.schoolOther),
            purpose: getResolvedValue(profileInputs.purpose, profileInputs.purposeOther),
            interests: getResolvedValue(profileInputs.interests, profileInputs.interestsOther),
            style: getResolvedValue(profileInputs.style, profileInputs.styleOther),
            _schemaVersion: 2
        };
        localStorage.setItem('vnu_bookmind_profile', JSON.stringify(profileData));
        console.log("Saved reader profile:", profileData);
    }

    function loadUserProfile() {
        const stored = localStorage.getItem('vnu_bookmind_profile');
        if (stored) {
            try {
                const data = JSON.parse(stored);
                // Clear stale/legacy cached profiles missing required schema version
                if (!data._schemaVersion || data._schemaVersion < 2) {
                    localStorage.removeItem('vnu_bookmind_profile');
                    return;
                }
                
                if (profileInputs.fullname && data.fullname) profileInputs.fullname.value = data.fullname;
                if (profileInputs.studentId && data.studentId) profileInputs.studentId.value = data.studentId;
                if (profileInputs.major && data.major) profileInputs.major.value = data.major;
                
                // Load select raw choices
                if (profileInputs.year && data.yearRaw) profileInputs.year.value = data.yearRaw;
                if (profileInputs.school && data.schoolRaw) profileInputs.school.value = data.schoolRaw;
                if (profileInputs.purpose && data.purposeRaw) profileInputs.purpose.value = data.purposeRaw;
                if (profileInputs.interests && data.interestsRaw) profileInputs.interests.value = data.interestsRaw;
                if (profileInputs.style && data.styleRaw) profileInputs.style.value = data.styleRaw;

                // Load text input other values
                if (profileInputs.yearOther && data.yearOtherVal) profileInputs.yearOther.value = data.yearOtherVal;
                if (profileInputs.schoolOther && data.schoolOtherVal) profileInputs.schoolOther.value = data.schoolOtherVal;
                if (profileInputs.purposeOther && data.purposeOtherVal) profileInputs.purposeOther.value = data.purposeOtherVal;
                if (profileInputs.interestsOther && data.interestsOtherVal) profileInputs.interestsOther.value = data.interestsOtherVal;
                if (profileInputs.styleOther && data.styleOtherVal) profileInputs.styleOther.value = data.styleOtherVal;

                // Trigger toggle UI displays
                dropdownsToWatch.forEach(item => toggleOtherInput(item.select, item.other));
            } catch (e) {
                console.error("Error loading user profile:", e);
            }
        }
    }

    function isProfileValid() {
        const fullnameVal = profileInputs.fullname ? profileInputs.fullname.value.trim() : '';
        const studentIdVal = profileInputs.studentId ? profileInputs.studentId.value.trim() : '';
        const majorVal = profileInputs.major ? profileInputs.major.value.trim() : '';

        // Require all select fields to be chosen (not empty placeholder '')
        const yearVal = profileInputs.year ? profileInputs.year.value : '';
        const schoolVal = profileInputs.school ? profileInputs.school.value : '';
        const purposeVal = profileInputs.purpose ? profileInputs.purpose.value : '';
        const interestsVal = profileInputs.interests ? profileInputs.interests.value : '';
        const styleVal = profileInputs.style ? profileInputs.style.value : '';

        if (!yearVal) return false;
        if (!schoolVal) return false;
        if (!purposeVal) return false;
        if (!interestsVal) return false;
        if (!styleVal) return false;
        
        // Year check
        if (yearVal === 'Khác') {
            if (!profileInputs.yearOther || !profileInputs.yearOther.value.trim()) return false;
        }
        // School check
        if (schoolVal === 'Khác') {
            if (!profileInputs.schoolOther || !profileInputs.schoolOther.value.trim()) return false;
        }
        // Purpose check
        if (purposeVal === 'Khác') {
            if (!profileInputs.purposeOther || !profileInputs.purposeOther.value.trim()) return false;
        }
        // Interests check
        if (interestsVal === 'Khác') {
            if (!profileInputs.interestsOther || !profileInputs.interestsOther.value.trim()) return false;
        }
        // Style check
        if (styleVal === 'Khác') {
            if (!profileInputs.styleOther || !profileInputs.styleOther.value.trim()) return false;
        }

        return (fullnameVal !== '' && studentIdVal !== '' && majorVal !== '');
    }

    function getUserProfileString() {
        const stored = localStorage.getItem('vnu_bookmind_profile');
        if (!stored) return "";
        try {
            const data = JSON.parse(stored);
            // Labels must exactly match regex patterns in profiler_agent.py
            return [
                'Họ tên: ' + (data.fullname || ''),
                'MSSV: ' + (data.studentId || ''),
                'Sinh viên năm: ' + (data.year || ''),
                'Trường thành viên: ' + (data.school || ''),
                'Ngành học: ' + (data.major || ''),
                'Mục đích đọc sách: ' + (data.purpose || ''),
                'Lĩnh vực quan tâm: ' + (data.interests || ''),
                'Phong cách học: ' + (data.style || '')
            ].join(', ');
        } catch (e) {
            return "";
        }
    }

    // Modal submit event
    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
            if (!isProfileValid()) {
                alert("Vui lòng nhập đầy đủ các trường thông tin bắt buộc!");
                return;
            }
            saveUserProfile();
            if (profileModal) profileModal.style.display = 'none';
        });
    }

    // Edit button click event
    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', () => {
            loadUserProfile();
            if (profileModal) profileModal.style.display = 'flex';
        });
    }

    // First launch mandatory check
    function checkUserProfileOnStartup() {
        const stored = localStorage.getItem('vnu_bookmind_profile');
        if (!stored) {
            if (profileModal) profileModal.style.display = 'flex';
        } else {
            loadUserProfile();
        }
    }

    checkUserProfileOnStartup();

    // Settings panel removed — API prefix auto-detected, no manual config needed

    function getApiPrefix() {
        const host = window.location.hostname;
        if (host === 'localhost' || host === '127.0.0.1' || host.startsWith('192.168.')) {
            return 'http://127.0.0.1:8000';
        }
        if (host.includes('expert')) {
            return 'https://bookmind-expert-agent.onrender.com';
        }
        return 'https://bookmind-socratic-agent-5o4p.onrender.com';
    }

function checkServerConnection() {
        const dot = document.getElementById('connection-status-dot');
        if (!dot) return;

        const url = getApiPrefix() + '/api/report?session_id=' + sessionId;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 15000);

        fetch(url, { method: 'GET', signal: controller.signal })
            .then(res => {
                clearTimeout(timeoutId);
                dot.style.backgroundColor = '#10b981';
                dot.style.boxShadow = '0 0 8px #10b981';
                dot.title = 'Máy chủ đang hoạt động (Online)';
            })
            .catch(err => {
                clearTimeout(timeoutId);
                dot.style.backgroundColor = '#ef4444';
                dot.style.boxShadow = '0 0 8px #ef4444';
                dot.title = 'Không thể kết nối máy chủ (Offline)';
            });
    }

    let currentZoom = 100;

    // Generate or retrieve a persistent session ID for this browser tab.
    // Uses a tab-specific localStorage key so it survives F5 reloads but stays
    // isolated from other tabs (each tab gets its own key via a one-time tabKey in sessionStorage).
    let _tabKey = sessionStorage.getItem('vnu_bookmind_tab_key');
    if (!_tabKey) {
        _tabKey = 'tab_' + Math.random().toString(36).substring(2, 10);
        sessionStorage.setItem('vnu_bookmind_tab_key', _tabKey);
    }
    let sessionId = localStorage.getItem('vnu_bookmind_session_' + _tabKey);
    if (!sessionId) {
        sessionId = 'sess_' + Math.random().toString(36).substring(2, 15) + '_' + Date.now();
        localStorage.setItem('vnu_bookmind_session_' + _tabKey, sessionId);
    }

    let eventSource   = null;
    let hasCompletedSuccessfully = false;
    let sseErrorCount = 0;
    const MAX_SSE_ERRORS = 5;
    let sseReconnectCount = 0;         // How many times SSE has reconnected mid-run
    const MAX_SSE_RECONNECTS = 6;      // After 6 reconnect attempts, fall back to polling
    let sseCurrentUrl = '';            // Remember the SSE URL for reconnecting
    let sseReconnectTimer = null;      // setTimeout handle for scheduled reconnect
    let runStartTime  = null;
    let timerInterval = null;
    let pollingInterval = null;
    let pollCount = 0;
    const MAX_POLLS = 100; // Poll for 5 minutes
    let renderTimeout = null;
    let pendingReportContent = null;
    let expRenderTimeout = null;
    let pendingExpContent = null;

    // Typewriter queue
    let printQueue = [];
    let isPrinting = false;

    // Holds the latest raw markdown content
    let currentMarkdown = '';

    let hasAnalystRun = false;
    let currentDiagramCode = '';
    let hideAnalysisLogText = localStorage.getItem('fpt_hide_analysis_log_text') === 'true';
    let irrelevantDetected = false; // Guard flag: once irrelevant is detected, prevent throttle from overwriting

    // Active real-time stream state
    let activeStream = {
        node: null,
        rawText: '',
        thinkingText: '',
        contentText: '',
        section: 'none',
        logHeaderEl: null,
        thinkingDetailsEl: null,
        thinkingContentEl: null,
        logBodyEl: null
    };

    // ── Tab Switching ────────────────────────────────────────────────────────
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById(btn.getAttribute('data-tab')).classList.add('active');
        });
    });

    if (copyBtn && rawMarkdownText) {
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(rawMarkdownText.value)
                .then(() => {
                    const orig = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Đã sao chép!';
                    copyBtn.style.color = '#16a069';
                    setTimeout(() => { copyBtn.innerHTML = orig; copyBtn.style.color = ''; }, 2000);
                })
                .catch(err => console.error('Clipboard error:', err));
        });
    }

    // ════════════════════════════════════════════════════════════════════════
    //  DOWNLOAD FUNCTIONS
    // ════════════════════════════════════════════════════════════════════════

    // ── Xuất báo cáo chi tiết (tải file HTML) ─────────────────────────────────
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', () => {
            if (!currentMarkdown || currentMarkdown.includes('not generated yet') || currentMarkdown.includes('Báo cáo chưa được tạo') || currentMarkdown.trim().startsWith('# Không áp dụng') || currentMarkdown.trim().startsWith('# IRRELEVANT')) {
                alert('Chưa có báo cáo hợp lệ. Vui lòng chạy quy trình trước!');
                return;
            }

            const topic = topicInput?.value || 'Báo cáo chi tiết chiến lược';
            const safeTopic = topic.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            const now = new Date();

            // Sao chép nội dung báo cáo
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = reportView.innerHTML;

            // Bỏ wrapper tràn bảng — chuyển table ra ngoài
            tempDiv.querySelectorAll('.table-scroll-wrapper').forEach(el => {
                const table = el.querySelector('table');
                if (table) el.replaceWith(table.cloneNode(true));
            });

            // Loại bỏ các phần không cần trong bản xuất
            // Bỏ placeholder-text (chỉ hiển thị khi chưa có báo cáo)
            tempDiv.querySelectorAll('.placeholder-text').forEach(el => el.remove());
            // Bỏ các icon Font Awesome (sẽ không hiển thị trong file xuất)
            tempDiv.querySelectorAll('i.fa-solid, i.fa-regular, i.fa-brands, i.fas, i.far, i.fab').forEach(el => {
                el.remove();
            });

            const htmlContent = `<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${safeTopic} — VNU BookMind</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.css" crossorigin="anonymous">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #ffffff;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #0f172a;
  }

  /* ── Report Container ── */
  .report-page {
    max-width: 960px;
    margin: 0 auto;
    padding: 40px 32px;
  }

  /* ── Markdown Report ── */
  .markdown-report {
    line-height: 1.75;
    color: #1e293b;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    padding: 48px 56px;
    background: #ffffff;
    margin: 0;
    max-width: 100%;
    width: 100%;
    overflow-x: hidden;
  }

  /* ── Headings ── */
  .markdown-report h1 {
    font-size: 24px; margin-bottom: 28px; font-weight: 800;
    text-transform: uppercase; text-align: center; color: #000000;
    letter-spacing: 0.3px;
  }
  .markdown-report h2 {
    font-size: 19px; margin-top: 36px; margin-bottom: 18px; font-weight: 700;
    color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;
  }
  .markdown-report h3 {
    font-size: 16px; margin-top: 26px; margin-bottom: 14px; font-weight: 600;
    color: #1e293b;
  }
  .markdown-report h4 {
    font-size: 14.5px; margin-top: 20px; margin-bottom: 12px; font-weight: 700;
    color: #334155;
  }
  .markdown-report h5 {
    font-size: 13.5px; margin-top: 18px; margin-bottom: 10px; font-weight: 700;
    color: #475569;
  }
  .markdown-report h6 {
    font-size: 13px; margin-top: 16px; margin-bottom: 8px; font-weight: 600;
    font-style: italic; color: #64748b;
  }

  /* ── Paragraphs ── */
  .markdown-report p {
    margin-bottom: 14px; font-size: 14.2px; color: #0f172a; line-height: 1.8;
  }

  /* ── Blockquote ── */
  .markdown-report blockquote {
    border-left: 4px solid #94a3b8; padding: 10px 18px; margin: 18px 28px;
    color: #1e293b; font-style: italic; background: #f1f5f9;
    border-radius: 0 8px 8px 0;
  }

  /* ── Bold ── */
  .markdown-report b, .markdown-report strong {
    color: #000000; font-weight: 700;
  }

  /* ── Lists ── */
  .markdown-report ul, .markdown-report ol {
    margin-left: 24px; margin-bottom: 14px; font-size: 14.2px; color: #0f172a;
  }
  .markdown-report li { margin-bottom: 8px; line-height: 1.7; }
  .markdown-report ul ul, .markdown-report ol ul {
    margin-left: 20px; margin-top: 4px; margin-bottom: 4px; list-style-type: circle;
  }
  .markdown-report ul ul li, .markdown-report ol ul li {
    font-size: 13.5px; color: #1e293b;
  }

  /* ── Tables ── */
  .markdown-report table {
    display: table; width: 100%; table-layout: auto;
    border-collapse: collapse; margin: 20px 0; font-size: 12.5px;
    border-top: 2px solid #0f172a; border-bottom: 2px solid #0f172a;
    word-wrap: normal;
  }
  .markdown-report th, .markdown-report td {
    border: none; padding: 10px 14px; text-align: left;
    white-space: normal; word-wrap: normal; word-break: normal;
    overflow-wrap: break-word; min-width: 60px;
  }
  .markdown-report th {
    border-bottom: 2px solid #0f172a; font-weight: 700; color: #000000;
    background: #f8fafc;
  }
  .markdown-report td {
    border-bottom: 1px solid #e5e7eb; color: #0f172a;
  }
  .markdown-report tr:last-child td { border-bottom: none; }

  /* ── Code ── */
  .markdown-report code {
    background: #f3f4f6; border: 1px solid #e5e7eb; border-radius: 3px;
    padding: 2px 5px; font-family: 'Fira Code', monospace; font-size: 11.5px;
    color: #111827;
  }
  .markdown-report pre {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
    padding: 14px 16px; overflow-x: auto; white-space: pre-wrap;
    word-break: break-all; margin: 18px 0;
  }
  .markdown-report pre code {
    padding: 0; background: transparent; border: none; font-size: 11.5px;
    color: #1e293b;
  }

  /* ── Images ── */
  .markdown-report img {
    max-width: 100%; height: auto; display: block; margin: 18px auto;
  }

  /* ── KaTeX Math Formulas ── */
  .markdown-report .katex-display {
    background: transparent !important;
    border-left: none !important;
    padding: 12px 0 !important;
    margin: 20px 0 !important;
    box-shadow: none !important;
    overflow-x: auto;
  }
  .markdown-report .katex {
    font-size: 1.05em !important;
  }
  .markdown-report .text-danger {
    color: #dc2626; font-family: 'Fira Code', monospace; font-size: 12px;
  }

  /* ── Horizontal Rule ── */
  .markdown-report hr {
    border: none; border-top: 1px solid #e2e8f0; margin: 28px 0;
  }

  /* ── Print Styles ── */
  @media print {
    body { background: #fff; font-size: 12pt; }
    .report-page { padding: 0; max-width: 100%; }
    .markdown-report { padding: 0; box-shadow: none; }
    .markdown-report h1 { font-size: 20pt; }
    .markdown-report h2 { font-size: 15pt; }
    .markdown-report h3 { font-size: 13pt; }
    .markdown-report p { font-size: 11pt; line-height: 1.6; }
    .markdown-report table { font-size: 9pt; }
    .markdown-report .katex-display { margin: 10px 0 !important; }
  }
</style>
</head>
<body>
<div class="report-page">
  <div class="markdown-report">${tempDiv.innerHTML}</div>
</div>
</body>
</html>`;

            const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const safeName = topic.replace(/[^a-zA-Z0-9\u00C0-\u024F\u1E00-\u1EFF\s-]/g, '').replace(/\s+/g, '_').substring(0, 60);
            a.download = `BaoCao_${safeName}_${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}${String(now.getDate()).padStart(2,'0')}.html`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }

    // ── 2. Xuất sơ đồ quy trình (PNG — colorful header/footer) ──────────────
    if (downloadDiagBtn) {
        downloadDiagBtn.addEventListener('click', async () => {
            const svgEl = document.querySelector('#mermaid-render-output svg');
            if (!svgEl) {
                alert('Sơ đồ chưa được vẽ. Vui lòng chạy quy trình và xem tab Sơ Đồ trước!');
                return;
            }

            const origHTML = downloadDiagBtn.innerHTML;
            downloadDiagBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang tạo PNG…';
            downloadDiagBtn.disabled = true;

            const topic = topicInput?.value || 'VNU BookMind';
            const now = new Date();
            const dateStr = now.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });

            try {
                // Serialize SVG
                const cloned = svgEl.cloneNode(true);
                cloned.setAttribute('xmlns', 'http://www.w3.org/2000/svg');

                // Strip pan/zoom transforms to restore native size and center alignment
                cloned.style.transform = 'none';
                cloned.style.transformOrigin = 'unset';
                cloned.style.transition = 'none';
                cloned.style.display = 'block';
                cloned.style.margin = '0 auto';
                cloned.style.width = '100%';

                // Strip the ID prefix (e.g. #mermaid-12345) from selectors in style blocks
                const id = svgEl.getAttribute('id');
                cloned.querySelectorAll('style').forEach(styleEl => {
                    let cssText = styleEl.innerHTML;
                    if (id) {
                        cssText = cssText.replace(new RegExp('#' + id + '(?![a-zA-Z0-9_-])', 'g'), 'svg');
                        styleEl.innerHTML = cssText;
                    }
                });

                // Extract native dimensions from viewBox
                let w = 800;
                let h = 600;
                const viewBoxAttr = svgEl.getAttribute('viewBox');
                if (viewBoxAttr) {
                    const parts = viewBoxAttr.split(/[\s,]+/);
                    if (parts.length === 4) {
                        w = parseFloat(parts[2]) || 800;
                        h = parseFloat(parts[3]) || 600;
                    }
                } else {
                    const bbox = svgEl.getBoundingClientRect();
                    w = bbox.width || 800;
                    h = bbox.height || 600;
                }

                cloned.setAttribute('width', w);
                cloned.setAttribute('height', h);
                cloned.setAttribute('viewBox', viewBoxAttr || `0 0 ${w} ${h}`);

                const svgStr = new XMLSerializer().serializeToString(cloned);
                const svgBlob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
                const svgUrl  = URL.createObjectURL(svgBlob);

                const HEADER_H = 64;
                const FOOTER_H = 36;

                const downloadSvgFallback = () => {
                    try {
                        URL.revokeObjectURL(svgUrl);
                        const fallbackBlob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' });
                        const fallbackUrl = URL.createObjectURL(fallbackBlob);
                        const a = document.createElement('a');
                        a.href     = fallbackUrl;
                        a.download = `VNU BookMind_SoDo_QuyTrinh_${now.toISOString().slice(0,10)}.svg`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        setTimeout(() => URL.revokeObjectURL(fallbackUrl), 10000);
                    } catch (fallbackErr) {
                        console.error('SVG fallback download failed:', fallbackErr);
                        alert(`Không thể tải sơ đồ: ${fallbackErr.message}`);
                    }
                    downloadDiagBtn.innerHTML = origHTML;
                    downloadDiagBtn.disabled = false;
                };

                // Calculate export canvas width — ensure SVG is centered with adequate padding
                const MIN_EXPORT_W = 800;
                const exportW = Math.max(w, MIN_EXPORT_W);
                // Center SVG horizontally within the export canvas
                const svgOffsetX = Math.round((exportW - w) / 2);

                // Draw onto canvas with colorful header & footer
                const img = new Image();
                img.onload = () => {
                    try {
                        const canvas  = document.createElement('canvas');
                        const scale   = 2;
                        const totalH  = HEADER_H + h + FOOTER_H;
                        canvas.width  = exportW * scale;
                        canvas.height = totalH * scale;
                        const ctx = canvas.getContext('2d');
                        if (!ctx) throw new Error("Could not get 2D context");
                        ctx.scale(scale, scale);

                        // ── Colorful header background ──
                        const hdrGrad = ctx.createLinearGradient(0, 0, exportW, 0);
                        hdrGrad.addColorStop(0, '#0054a6');
                        hdrGrad.addColorStop(0.3, '#1a6dc7');
                        hdrGrad.addColorStop(0.6, '#8b5cf6');
                        hdrGrad.addColorStop(1, '#e8621a');
                        ctx.fillStyle = hdrGrad;
                        ctx.fillRect(0, 0, exportW, HEADER_H);

                        // Header accent bar (thin rainbow strip)
                        const accentGrad = ctx.createLinearGradient(0, 0, exportW, 0);
                        accentGrad.addColorStop(0, '#e05577');
                        accentGrad.addColorStop(0.2, '#2f88d4');
                        accentGrad.addColorStop(0.4, '#8b5cf6');
                        accentGrad.addColorStop(0.6, '#d97706');
                        accentGrad.addColorStop(0.8, '#16a069');
                        accentGrad.addColorStop(1, '#0d9488');
                        ctx.fillStyle = accentGrad;
                        ctx.fillRect(0, HEADER_H - 4, exportW, 4);

                        // Header text
                        ctx.fillStyle = '#ffffff';
                        ctx.font = 'bold 16px Inter, system-ui, sans-serif';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('\u{1F4CA}  ' + topic.substring(0, 60), 18, HEADER_H / 2 - 2);

                        ctx.font = '11px Inter, system-ui, sans-serif';
                        ctx.fillStyle = 'rgba(255,255,255,0.8)';
                        ctx.textAlign = 'right';
                        ctx.fillText('VNU BookMind \u2022 Multi-Agent AI System', exportW - 18, HEADER_H / 2 - 2);
                        ctx.textAlign = 'left';

                        // ── Diagram body (centered) ──
                        ctx.fillStyle = '#ffffff';
                        ctx.fillRect(0, HEADER_H, exportW, h);
                        ctx.drawImage(img, svgOffsetX, HEADER_H, w, h);

                        // ── Colorful footer ──
                        const ftrGrad = ctx.createLinearGradient(0, 0, exportW, 0);
                        ftrGrad.addColorStop(0, '#0d9488');
                        ftrGrad.addColorStop(0.5, '#2f88d4');
                        ftrGrad.addColorStop(1, '#0054a6');
                        ctx.fillStyle = ftrGrad;
                        ctx.fillRect(0, HEADER_H + h, exportW, FOOTER_H);

                        ctx.fillStyle = 'rgba(255,255,255,0.85)';
                        ctx.font = '10px Inter, system-ui, sans-serif';
                        ctx.textBaseline = 'middle';
                        ctx.fillText('\u{1F6E1}  VNU BookMind \u00A9 ' + now.getFullYear(), 18, HEADER_H + h + FOOTER_H / 2);
                        ctx.textAlign = 'right';
                        ctx.fillText(dateStr, exportW - 18, HEADER_H + h + FOOTER_H / 2);
                        ctx.textAlign = 'left';

                        URL.revokeObjectURL(svgUrl);

                        canvas.toBlob(blob => {
                            try {
                                if (!blob) throw new Error("Blob creation failed");
                                const pngUrl = URL.createObjectURL(blob);
                                const a = document.createElement('a');
                                a.href     = pngUrl;
                                a.download = `VNU BookMind_SoDo_QuyTrinh_${now.toISOString().slice(0,10)}.png`;
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                setTimeout(() => URL.revokeObjectURL(pngUrl), 10000);
                            } catch (toBlobErr) {
                                console.error('toBlob failed, running SVG fallback:', toBlobErr);
                                downloadSvgFallback();
                            } finally {
                                downloadDiagBtn.innerHTML = origHTML;
                                downloadDiagBtn.disabled = false;
                            }
                        }, 'image/png');
                    } catch (onloadErr) {
                        console.error('img.onload canvas error, running SVG fallback:', onloadErr);
                        downloadSvgFallback();
                    }
                };
                img.onerror = () => {
                    console.warn('img.onerror loaded, running SVG fallback');
                    downloadSvgFallback();
                };
                img.src = svgUrl;

            } catch (err) {
                console.error('Diagram download error:', err);
                alert(`Lỗi tải sơ đồ: ${err.message}`);
                downloadDiagBtn.innerHTML = origHTML;
                downloadDiagBtn.disabled = false;
            }
        });
    }

    // ════════════════════════════════════════════════════════════════════════
    //  PANEL HIGHLIGHT HELPER
    // ════════════════════════════════════════════════════════════════════════
    function highlightPanel(panelKey) {
        document.querySelectorAll('.panel').forEach(p => p.classList.remove('active-section'));
        const consultPanel = document.querySelector('.sidebar-left .panel:first-child');
        const metricsPanel = document.querySelector('.metrics-panel');
        const graphPanel   = document.querySelector('.graph-panel');
        const consolePanel = document.querySelector('.console-panel');
        const tabsPanel    = document.querySelector('.tabs-panel');

        if (panelKey === 'start') {
            consultPanel?.classList.add('active-section');
            metricsPanel?.classList.add('active-section');
        } else if (panelKey === 'guardrail' || panelKey === 'running') {
            consolePanel?.classList.add('active-section');
            graphPanel?.classList.add('active-section');
        } else if (panelKey === 'complete') {
            tabsPanel?.classList.add('active-section');
        }
    }

    // ════════════════════════════════════════════════════════════════════════
    //  UNCREATED PLACEHOLDER CARDS & HISTORY HELPERS
    // ── Metrics Grid: kept visible at all times (including irrelevant queries) ──

    const showIrrelevantReportCard = () => {
        // Cancel any pending throttle render to prevent race condition
        if (renderTimeout) {
            clearTimeout(renderTimeout);
            renderTimeout = null;
        }
        pendingReportContent = null;
        irrelevantDetected = true; // Lock: prevent future throttle renders from overwriting

        reportView.className = 'markdown-report';
        reportView.style.border = '1px solid #fecaca';
        reportView.style.borderRadius = '8px';
        reportView.style.background = '#ffffff';
        reportView.style.padding = '30px 35px';
        reportView.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
        reportView.style.maxWidth = '100%';
        reportView.style.margin = '5px 0';
        reportView.style.minHeight = 'unset';
        reportView.style.maxHeight = 'unset';
        reportView.style.display = 'block';
        reportView.style.position = 'relative';
        reportView.innerHTML = `
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="font-size: 16px; font-weight: 800; color: #dc2626; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 10px 0;">BÁO CÁO KHÔNG ÁP DỤNG</h1>
                <p style="font-size: 13px; color: #475569; line-height: 1.6; max-width: 400px; margin: 0 auto;">
                    Yêu cầu bị từ chối nên không tạo báo cáo chi tiết.
                </p>
            </div>
        `;
    };

    const showUncreatedReportCard = () => {
        reportView.className = 'markdown-report';
        reportView.style.border = '1px solid #e2e8f0';
        reportView.style.borderRadius = '8px';
        reportView.style.background = '#ffffff';
        reportView.style.padding = '30px 35px';
        reportView.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02)';
        reportView.style.maxWidth = '100%';
        reportView.style.margin = '5px 0';
        reportView.innerHTML = `
            <h1 style="font-size: 18px; font-weight: 800; border-bottom: 2px solid #0054a6; padding-bottom: 8px; color: #0054a6; text-transform: uppercase; text-align: center; letter-spacing: 0.5px; margin: 0;">BÁO CÁO CHƯA ĐƯỢC TẠO</h1>
        `;
    };

    const showDiagramOnlyReportCard = () => {
        reportView.className = 'markdown-report';
        reportView.style.border = '1px solid #e2e8f0';
        reportView.style.borderRadius = '8px';
        reportView.style.background = '#ffffff';
        reportView.style.padding = '40px 30px';
        reportView.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02)';
        reportView.style.maxWidth = '100%';
        reportView.style.margin = '5px 0';
        reportView.innerHTML = `
            <div style="text-align: center; color: #94a3b8; padding: 20px 0;">
                <i class="fa-solid fa-file-circle-exclamation" style="font-size: 48px; color: #0054a6; margin-bottom: 16px;"></i>
                <h3 style="margin: 0 0 10px 0; color: #1e293b; font-size: 16px; font-weight: 700;">Nội dung chính là Sơ đồ Quy trình</h3>
                <p style="margin: 0 auto; font-size: 13px; max-width: 420px; line-height: 1.6; color: #64748b;">
                    Yêu cầu của bạn tập trung vào việc mô tả hoặc vẽ sơ đồ quy trình. 
                    Vui lòng chuyển sang tab <strong>Sơ Đồ Quy Trình</strong> ở bên trên để xem trực quan sơ đồ động và bản phân tích kiến trúc chi tiết.
                </p>
            </div>
        `;
    };

    const showIrrelevantDiagramCard = () => {
        const toolbar = document.querySelector('.diagram-toolbar');
        if (toolbar) toolbar.style.display = 'none';
        const exp = document.getElementById('mermaid-explanation-container');
        if (exp) exp.style.display = 'none';

        mermaidOutput.className = 'markdown-report';
        mermaidOutput.style.border = '1px solid #fecaca';
        mermaidOutput.style.borderRadius = '8px';
        mermaidOutput.style.background = '#ffffff';
        mermaidOutput.style.padding = '30px 35px';
        mermaidOutput.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.05)';
        mermaidOutput.style.maxWidth = '100%';
        mermaidOutput.style.margin = '5px 0';
        mermaidOutput.style.minHeight = 'unset';
        mermaidOutput.style.maxHeight = 'unset';
        mermaidOutput.style.display = 'block';
        mermaidOutput.style.position = 'relative';

        mermaidOutput.innerHTML = `
            <div style="text-align: center; padding: 20px 0;">
                <h1 style="font-size: 16px; font-weight: 800; color: #dc2626; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 10px 0;">SƠ ĐỒ KHÔNG ÁP DỤNG</h1>
                <p style="font-size: 13px; color: #475569; line-height: 1.6; max-width: 400px; margin: 0 auto;">
                    Yêu cầu bị từ chối nên không tạo sơ đồ quy trình.
                </p>
            </div>
        `;
    };

    const showUncreatedDiagramCard = () => {
        const toolbar = document.querySelector('.diagram-toolbar');
        if (toolbar) toolbar.style.display = 'none';
        const exp = document.getElementById('mermaid-explanation-container');
        if (exp) exp.style.display = 'none';

        mermaidOutput.className = 'markdown-report';
        mermaidOutput.style.border = '1px solid #e2e8f0';
        mermaidOutput.style.borderRadius = '8px';
        mermaidOutput.style.background = '#ffffff';
        mermaidOutput.style.padding = '30px 35px';
        mermaidOutput.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.03), 0 2px 4px -1px rgba(0, 0, 0, 0.02)';
        mermaidOutput.style.maxWidth = '100%';
        mermaidOutput.style.margin = '5px 0';
        mermaidOutput.style.minHeight = 'unset';
        mermaidOutput.style.maxHeight = 'unset';
        mermaidOutput.style.display = 'block';
        mermaidOutput.style.position = 'relative';

        mermaidOutput.innerHTML = `
            <h1 style="font-size: 18px; font-weight: 800; border-bottom: 2px solid #0054a6; padding-bottom: 8px; color: #0054a6; text-transform: uppercase; text-align: center; letter-spacing: 0.5px; margin: 0;">SƠ ĐỒ CHƯA ĐƯỢC TẠO</h1>
        `;
    };

    function parseDurationText(text) {
        if (!text) return 0;
        const clean = text.trim().toLowerCase();
        const val = parseFloat(clean);
        if (isNaN(val)) return 0;
        if (clean.endsWith('ms')) return val / 1000;
        return val;
    }

    function saveActiveSearchState(status) {
        const topic = topicInput.value.trim();
        if (!topic) {
            localStorage.removeItem('fpt_active_search');
            return;
        }

        const stats = {
            time: statTime.textContent,
            tokens: statTokens.textContent,
            agents: statAgents.textContent,
            status: statStatus.textContent,
            agent_tokens: {},
            agent_durations: {},
            agent_models: {},
            agent_toks_per_sec: {}
        };

        const agentKeys = ['guardrail', 'researcher', 'analyst', 'risk_assessor', 'recommender', 'reporter'];
        agentKeys.forEach(k => {
            const badge = document.getElementById(`metrics-${k}`);
            if (badge) {
                const text = badge.textContent;
                const hasDot = text.includes('·');
                if (hasDot) {
                    const parts = text.split('·').map(p => p.trim());
                    stats.agent_models[k] = badge.title || parts[0] || '';
                    stats.agent_durations[k] = parseDurationText(parts[1]);
                    stats.agent_toks_per_sec[k] = parseFloat(parts[2]) || 0;
                    stats.agent_tokens[k] = parseInt((parts[3] || '').replace(/[^0-9]/g, ''), 10) || 0;
                } else {
                    const parts = text.split('|');
                    stats.agent_durations[k] = parseDurationText(parts[0]);
                    stats.agent_tokens[k] = parseInt((parts[1] || '').replace(/[^0-9]/g, ''), 10) || 0;
                    stats.agent_models[k] = badge.title || '';
                    stats.agent_toks_per_sec[k] = 0;
                }
            }
        });

        let activeNode = null;
        for (const k of agentKeys) {
            const nodeId = agentMappings[k]?.nodeId;
            if (nodeId && document.getElementById(nodeId)?.classList.contains('active')) {
                activeNode = k;
                break;
            }
        }

        const activeSearch = {
            topic,
            status: status || 'running',
            stats,
            hasAnalystRun,
            logs: consoleOutput.innerHTML,
            activeNode,
            timestamp: Date.now(),
            sessionId,                      // persist so reload can reconnect
            stateSnapshot: activeStateSnapshot  // persist so Phase-2 can resume after reload
        };

        localStorage.setItem('fpt_active_search', JSON.stringify(activeSearch));
    }

    // ════════════════════════════════════════════════════════════════════════
    //  RESET UI
    // ════════════════════════════════════════════════════════════════════════
    function resetUI() {
        // Stop any running SSE stream and timers from previous session
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }

        statTime.textContent   = '0.000s';
        statTokens.textContent = '0';
        statAgents.textContent = '0 / 6';
        statStatus.textContent = 'Đang chạy…';
        statStatus.style.color = 'var(--fpt-orange)';

        if (downloadGroup) downloadGroup.style.display = 'none';

        // Reset agent diagram nodes and edges completely
        document.querySelectorAll('.graph-node').forEach(n => {
            n.classList.remove('active');
            n.classList.remove('completed');
            n.classList.remove('node-hidden');
        });
        document.querySelectorAll('.graph-edges line').forEach(l => {
            l.classList.remove('active');
            l.classList.remove('edge-hidden');
        });
        const directEdge = document.getElementById('edge-researcher-reporter');
        if (directEdge) {
            directEdge.style.display = 'none';
        }

        // Reset console output to clean "waiting" state
        consoleOutput.innerHTML = '';
        activeAgentBadge.textContent = 'Chờ lệnh';
        activeAgentBadge.className   = 'agent-badge inactive';

        // Reset report and diagram tabs
        showUncreatedReportCard();
        showUncreatedDiagramCard();
        if (rawMarkdownText) rawMarkdownText.value = 'Báo cáo chưa được tạo';
        currentMarkdown = '';
        currentDiagramCode = '';

        // Reset agent metrics badges
        const agentKeys = ['guardrail', 'researcher', 'analyst', 'risk_assessor', 'recommender', 'reporter'];
        agentKeys.forEach(k => {
            const badge = document.getElementById(`metrics-${k}`);
            if (badge) badge.textContent = '0.000s | 0 tk';
        });

        // Reset typewriter queue
        printQueue = [];
        isPrinting = false;

        // Reset pending render timeouts
        if (renderTimeout) {
            clearTimeout(renderTimeout);
            renderTimeout = null;
        }
        if (expRenderTimeout) {
            clearTimeout(expRenderTimeout);
            expRenderTimeout = null;
        }
        pendingReportContent = null;
        pendingExpContent = null;
        irrelevantDetected = false; // Reset guard flag for new runs

        hasAnalystRun = false;

        // Reset active stream state
        activeStream = {
            node: null,
            rawText: '',
            thinkingText: '',
            contentText: '',
            section: 'none',
            logHeaderEl: null,
            thinkingDetailsEl: null,
            thinkingContentEl: null,
            logBodyEl: null
        };

        // Reset zoom
        currentZoom = 100;
        if (zoomLevelEl) zoomLevelEl.textContent = '100%';

        // Reset mermaid explanation container
        const expContainer = document.getElementById('mermaid-explanation-container');
        const expContent = document.getElementById('mermaid-explanation-content');
        if (expContainer) expContainer.style.display = 'none';
        if (expContent) expContent.innerHTML = '';
    }

    // ════════════════════════════════════════════════════════════════════════
    //  AGENT MAPPINGS
    // ════════════════════════════════════════════════════════════════════════
    const agentMappings = {
        guardrail:    { nodeId: 'node-guardrail',    edgeId: null,                         badgeClass: 'active-guardrail',    name: 'Cảnh Giới' },
        researcher:   { nodeId: 'node-researcher',   edgeId: 'edge-guardrail-researcher',  badgeClass: 'active-researcher',   name: 'Hồ Sơ' },
        analyst:      { nodeId: 'node-analyst',      edgeId: 'edge-researcher-analyst',    badgeClass: 'active-analyst',      name: 'Gợi Ý Sách' },
        risk_assessor:{ nodeId: 'node-risk_assessor',edgeId: 'edge-analyst-risk_assessor', badgeClass: 'active-risk_assessor',name: 'Socrates' },
        recommender:  { nodeId: 'node-recommender',  edgeId: 'edge-risk_assessor-recommender', badgeClass: 'active-recommender', name: 'Phản Biện' },
        reporter:     { nodeId: 'node-reporter',     edgeId: 'edge-recommender-reporter',  badgeClass: 'active-reporter',     name: 'Biên Soạn' }
    };

    function highlightNode(nodeKey) {
        const mapping = agentMappings[nodeKey];
        if (!mapping) return;

        if (nodeKey === 'analyst') {
            hasAnalystRun = true;
        }

        const nodesOrder = ['guardrail', 'researcher', 'analyst', 'risk_assessor', 'recommender', 'reporter'];
        const currentIndex = nodesOrder.indexOf(nodeKey);

        nodesOrder.forEach((nk, idx) => {
            const m = agentMappings[nk];
            const nodeEl = document.getElementById(m.nodeId);
            if (nodeEl) {
                if (idx < currentIndex) {
                    nodeEl.classList.add('completed');
                    nodeEl.classList.remove('active');
                } else if (idx === currentIndex) {
                    nodeEl.classList.remove('completed');
                    nodeEl.classList.add('active');
                } else {
                    nodeEl.classList.remove('completed');
                    nodeEl.classList.remove('active');
                }
            }

            // Handle edge lighting dynamically
            const edgeId = (nk === 'reporter' && !hasAnalystRun) ? 'edge-researcher-reporter' : m.edgeId;
            if (edgeId) {
                const edgeEl = document.getElementById(edgeId);
                if (edgeEl) {
                    if (idx <= currentIndex) {
                        edgeEl.classList.add('active');
                    } else {
                        edgeEl.classList.remove('active');
                    }
                }
            }
        });

        if (nodeKey === 'reporter' && !hasAnalystRun) {
            const directEdge = document.getElementById('edge-researcher-reporter');
            if (directEdge) {
                directEdge.style.display = 'block';
                directEdge.classList.add('active');
            }
        }

        activeAgentBadge.textContent = mapping.name;
        activeAgentBadge.className   = `agent-badge ${mapping.badgeClass}`;
        highlightPanel(nodeKey === 'guardrail' ? 'guardrail' : 'running');

        // Adjust agents count dynamically based on the active flow (simple vs complex)
        const idx = Object.keys(agentMappings).indexOf(nodeKey) + 1;
        if (nodeKey === 'reporter' && !hasAnalystRun) {
            statAgents.textContent = `3 / 3`; // Simple problem has 3 active agents: guardrail, researcher, reporter
        } else {
            statAgents.textContent = `${idx} / 6`;
        }
    }

    // ── Typewriter Effect ────────────────────────────────────────────────────
    function typeText(element, text, speed = 4) {
        element.textContent = text;
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
        return Promise.resolve();
    }

    // ── Vietnamese Text Normalizer ──────────────────────────────────────────
    // Fix broken/stacked diacritics (NFD → NFC) and remove non-Vietnamese CJK characters
    function normalizeVietnameseText(text) {
        if (!text) return '';
        // 1. Normalize Unicode: NFD decomposes, then NFC recomposes properly
        // This fixes cases like "ệ" (e + circumflex + dot below) → "ệ" (precomposed)
        let normalized = text.normalize('NFC');

        // 2. Remove CJK Ideographs (Chinese/Japanese/Korean characters)
        // CJK Unified Ideographs: U+4E00–U+9FFF
        // CJK Unified Ideographs Extension A: U+3400–U+4DBF
        // CJK Compatibility Ideographs: U+F900–U+FAFF
        // CJK Radicals Supplement: U+2E80–U+2EFF
        // CJK Symbols and Punctuation: U+3000–U+303F (keep 。if needed, but remove others)
        // Kangxi Radicals: U+2F00–U+2FDF
        // Hiragana: U+3040–U+309F
        // Katakana: U+30A0–U+30FF
        normalized = normalized.replace(/[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u2E80-\u2EFF\u2F00-\u2FDF\u3040-\u309F\u30A0-\u30FF]/g, '');

        // 3. Remove CJK punctuation that's not Vietnamese (keep standard punctuation)
        // Remove: 、。「」『』【】〔〕〖〗〘〙〚〛
        normalized = normalized.replace(/[\u3001\u3002\u300C-\u300F\u3010-\u3011\u3014-\u301B\u3016-\u301D\u301E-\u301F]/g, '');

        // 4. Clean up any double spaces left after removals
        normalized = normalized.replace(/  +/g, ' ').replace(/\n{3,}/g, '\n\n');

        return normalized.trim();
    }

    // Strip math formulas ($$...$$ and $...$) — for console log display only
    function stripMathFormulas(text) {
        if (!text) return '';
        // Remove display math $$...$$
        let cleaned = text
            .replace(/\*/g, '') // Remove all asterisks globally to prevent ** styling artifacts in console log.replace(/\$\$[\s\S]+?\$\$/g, '');
        // Remove inline math $...$ (but not currency like $100)
        cleaned = cleaned.replace(/\$([^\$\n]{1,}?)\$/g, (match, inner) => {
            // If it looks like a math expression (contains letters, operators, etc.), remove it
            if (/[a-zA-Z\u00C0-\u024F\u1E00-\u1EFF\\\/\^_=+\-*\{\}\[\]()]/.test(inner)) {
                return '';
            }
            return match; // Keep currency-like patterns
        });
        return cleaned;
    }

    // Combined text sanitizer for console log display
    function sanitizeConsoleText(text) {
        if (!text) return '';
        let cleaned = normalizeVietnameseText(text);
        cleaned = stripMathFormulas(cleaned);
        return cleaned;
    }

    function stripMarkdown(text) {
        if (!text) return '';
        let cleaned = text
            .replace(/\*\*([^*]+)\*\*/g, '$1')   // **bold** → bold
            .replace(/\*([^*]+)\*/g, '$1')         // *italic* → italic
            .replace(/\*+/g, '')
            .replace(/\*([^*]+)\*/g, '$1')
            .replace(/`([^`]+)`/g, '$1')
            .replace(/^#+\s+(.+)$/gm, '$1')
            .replace(/^\s*[-*+]\s+/gm, '')
            .replace(/^\s*\d+[\.\-]\s+/gm, '')
            .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
            .replace(/&nbsp;/g, ' ')
            .replace(/_{2,}/g, '')
            .replace(/\*{2,}/g, '');

        // Hide marker lines and section names like CONSOLE MESSAGE, DETAILED REPORT, etc.
        cleaned = cleaned
            .replace(/===?\s*(THINKING|QUÁ TRÌNH TƯ DUY|SUY NGHĨ|TƯ DUY)\s*===?/gi, '')
            .replace(/===?\s*(CONSOLE MESSAGE|THÔNG BÁO CONSOLE|NHẬT KÝ CONSOLE|TÓM TẮT CONSOLE|NHẬT KÝ|TÓM TẮT)\s*===?/gi, '')
            .replace(/===?\s*(DETAILED REPORT|BÁO CÁO CHI TIẾT|BÁO CÁO CỤ THỂ|BÁO CÁO)\s*===?/gi, '')
            .replace(/===?\s*(DIAGRAM EXPLANATION|GIẢI THÍCH CHI TIẾT SƠ ĐỒ|GIẢI THÍCH SƠ ĐỒ|GIẢI THÍCH)\s*===?/gi, '')
            .replace(/===?\s*(MERMAID DIAGRAM|SƠ ĐỒ MERMAID|BIỂU ĐỒ MERMAID)\s*===?/gi, '')
            .replace(/^\s*[-*=]{3,}\s*$/gm, '') // Lines containing only --- or ===
            .replace(/^\s*(THINKING|CONSOLE MESSAGE|DETAILED REPORT|DIAGRAM EXPLANATION|MERMAID DIAGRAM)\s*$/gim, '')
            .replace(/^\s*(QUÁ TRÌNH TƯ DUY|SUY NGHĨ|TƯ DUY|THÔNG BÁO CONSOLE|NHẬT KÝ CONSOLE|TÓM TẮT CONSOLE|NHẬT KÝ|TÓM TẮT)\s*$/gim, '')
            .replace(/^\s*(BÁO CÁO CHI TIẾT|BÁO CÁO CỤ THỂ|BÁO CÁO|GIẢI THÍCH CHI TIẾT SƠ ĐỒ|GIẢI THÍCH SƠ ĐỒ|GIẢI THÍCH|SƠ ĐỒ MERMAID|BIỂU ĐỒ MERMAID)\s*$/gim, '');

        return cleaned.trim();
    }

    const FILENAME_MAP = {
        "agentvista_testvista.md": "Tài liệu Khảo sát AgentVista & TestVista",
        "ai_first_challenges.md": "Báo cáo Thách thức Chiến lược AI-First",
        "codevista_features.md": "Tài liệu Tính năng CodeVista",
        "coding_standards.md": "Quy chuẩn Phát triển Phần mềm VNU BookMind",
        "flezi_foundry_adlc.md": "Báo cáo Quy trình Vận hành Flezi Foundry ADLC",
        "flezipt_architecture.md": "Kiến trúc Nền tảng Flezi Platform (FlezIPT)",
        "fpt_academic_publications.md": "Các Công trình Nghiên cứu Khoa học VNU BookMind",
        "fpt_agentic_ai_2026.md": "Báo cáo Phát triển Agentic AI VNU BookMind 2026",
        "fpt_ai_initiatives_2026.md": "Sáng kiến Chiến lược AI VNU BookMind 2026",
        "fpt_ai_research_lab_2026.md": "Tài liệu Phòng Nghiên cứu Trí tuệ Nhân tạo VNU BookMind AI Research Lab",
        "fpt_ai_strategy_advisory_2026.md": "Báo cáo Tư vấn Chiến lược AI VNU BookMind 2026",
        "fpt_architecture_consulting_2026.md": "Quy trình Tư vấn Kiến trúc Công nghệ VNU BookMind 2026",
        "fpt_enterprise_products_2026.md": "Danh mục Sản phẩm Doanh nghiệp VNU BookMind 2026",
        "fpt_financial_growth_2026.md": "Báo cáo Phát triển Tài chính VNU BookMind 2026",
        "fpt_flezi_ecosystem.md": "Tài liệu Hệ sinh thái Flezi Ecosystem VNU BookMind",
        "fpt_global_presence_2026.md": "Báo cáo Năng lực Toàn cầu VNU BookMind 2026",
        "fpt_global_verticals_2026.md": "Tài liệu Lĩnh vực Kinh doanh Toàn cầu VNU BookMind 2026",
        "fpt_research.md": "Báo cáo Nghiên cứu và Phát triển Công nghệ VNU BookMind",
        "fpt_risk_compliance_2026.md": "Tài liệu Quản trị Rủi ro & Tuân thủ VNU BookMind 2026",
        "fpt_software_overview_2026.md": "Tài liệu Tổng quan VNU BookMind 2026",
        "sdlc_evolution.md": "Tài liệu Tiến trình Phát triển Phần mềm SDLC VNU BookMind",
        "security_best_practices.md": "Quy chuẩn Bảo mật Thông tin VNU BookMind",
    };

    function cleanInternalFilenames(text) {
        if (!text) return '';
        let cleaned = text
            .replace(/\*/g, '') // Remove all asterisks globally to prevent ** styling artifacts in console log;
        
        // 1. Remove RAG prefixes and list of files in parentheses
        const prefixPat = /(?:Truy\s+xuất\s+dữ\s+liệu|Truy\s+xuất\s+tri\s+thức|Nguồn\s+dữ\s+liệu|Tham\s+khảo)\s+từ\s+(?:kho\s+)?(?:tri\s+thức|dữ\s+liệu)\s+nội\s+bộ\s*(?:\([^)]*\)|:[^\n.]*|)/gi;
        cleaned = cleaned.replace(prefixPat, '');
        
        // Remove parenthesized lists of filenames
        const parenPat = /\(\s*[^)]*\.(?:md|txt)[^)]*\)/gi;
        cleaned = cleaned.replace(parenPat, '');
        
        // 2. Fallback translations
        const sortedKeys = Object.keys(FILENAME_MAP).sort((a, b) => b.length - a.length);
        for (const filename of sortedKeys) {
            const title = FILENAME_MAP[filename];
            const escaped = filename.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'gi');
            cleaned = cleaned.replace(regex, title);
        }
        
        for (const filename of sortedKeys) {
            const title = FILENAME_MAP[filename];
            const nameNoExt = filename.split('.').slice(0, -1).join('.');
            const escaped = nameNoExt.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp('\\b' + escaped + '\\b', 'gi');
            cleaned = cleaned.replace(regex, title);
        }
        
        // Strip any remaining raw .md / .txt filenames
        cleaned = cleaned.replace(/\b[a-zA-Z0-9_-]+\.(?:md|txt)\b/g, '');
        
        return cleaned;
    }

    function cleanReportContent(text) {
        if (!text) return '';

        // 0. Second-pass CJK removal (safety net for streamed content)
        text = text.replace(
            /[\u4E00-\u9FFF\u3400-\u4DBF\uF900-\uFAFF\u2E80-\u2EFF\u2F00-\u2FDF\u3040-\u309F\u30A0-\u30FF\u3000-\u303F\u31F0-\u31FF]/g,
            ''
        );
        text = text.replace(/[\u3001\u3002\u300C-\u300F\u3010-\u3011\u300A-\u300B]/g, '');

        let cleaned = text
            // Remove ALL bare ** and *** regardless of context (most critical fix)
            .replace(/\*{3,}/g, '')
            // convert **bold** → plain text — marked.js will render the semantic version
            .replace(/\*\*([^*\n]+)\*\*/g, '$1')
            .replace(/\*([^*\n]+)\*/g, '$1')
            // Remove any remaining orphan asterisks (stray * not wrapping words)
            .replace(/(?<=\s)\*(?=\s|$)/gm, '')
            .replace(/^\*(?=\s)/gm, '')

        // URL sanitization — fix known-broken domains/paths
        cleaned = cleaned
            // cas.vnu.edu.vn → lic.vnu.edu.vn (CAS is internal-only)
            .replace(/https?:\/\/cas\.vnu\.edu\.vn[^\s\)\]'"\u201d]*/g, 'https://lic.vnu.edu.vn/')
            // openlibrary.org/isbn/XXX → worldcat ISBN search (isbn paths often 404)
            .replace(/https?:\/\/openlibrary\.org\/isbn\/(\d+)[^\s\)\]'"\u201d]*/g,
                (_, isbn) => `https://www.worldcat.org/isbn/${isbn}`)
            // openlibrary.org/search?... → worldcat
            .replace(/https?:\/\/openlibrary\.org\/search[^\s\)\]'"\u201d]*/g, 'https://www.worldcat.org/')
            // Made-up OpenLibrary work IDs like OL12345678W
            .replace(/https?:\/\/openlibrary\.org\/works\/OL\d{5,}W[^\s\)\]'"\u201d]*/g, 'https://www.worldcat.org/')

        // Remove any markdown code block of mermaid
        cleaned = cleaned.replace(/```mermaid[\s\S]*?```/gi, '');

        // Remove standard section headers if they leaked into report content
        cleaned = cleaned.replace(/===[\s\S]*?===/g, '');

        // Filter lines that are purely section markers
        const lines = cleaned.split('\n');
        const filteredLines = lines.filter(line => {
            const upper = line.trim().toUpperCase();
            if (upper.includes('MERMAID DIAGRAM') ||
                upper.includes('DIAGRAM EXPLANATION') ||
                upper.includes('GIẢI THÍCH SƠ ĐỒ') ||
                upper.includes('SƠ ĐỒ MERMAID') ||
                upper.includes('BIỂU ĐỒ MERMAID')) {
                return false;
            }
            return true;
        });

        return filteredLines.join('\n').trim();
    }

    // ── Print Queue ──────────────────────────────────────────────────────────
    async function processQueue() {
        if (printQueue.length === 0) { isPrinting = false; return; }
        isPrinting = true;
        const item = printQueue.shift();

        // Start marker (sequentially queued agent start)
        if (item.type === 'start') {
            highlightNode(item.node); // Sequential highlight transition
            printAgentStartInLog(item.node);
            isPrinting = false;
            processQueue();
            return;
        }

        // Completion marker
        if (item.type === 'completion') {
            isPrinting = false;
            return;
        }

        const nk = item.node;

        // Remove start placeholder if it exists
        const placeholder = document.getElementById(`start-placeholder-${nk}`);
        if (placeholder) {
            placeholder.remove();
        }

        // Agent output — colored header + typewriter body
        highlightNode(item.node);

        // Update metrics badge for this node in real-time sync with log printing!
        const badge = document.getElementById(`metrics-${item.node}`);
        if (badge) {
            const durVal = item.duration ? item.duration : 0;
            const durText = `${durVal.toFixed(3)}s`;
            const tk = item.tokens ? item.tokens.toLocaleString() : '0';
            const tps = item.toks_per_sec ? item.toks_per_sec.toFixed(1) : '0.0';
            const mdl = item.model ? item.model.split('/').pop() : '';
            badge.textContent = mdl ? `${mdl} · ${durText} · ${tps} tk/s · ${tk} tk` : `${durText} · ${tk} tk`;
            badge.title = item.model || '';
        }

        let titleColor = '#94a3b8';
        if      (nk === 'guardrail')    titleColor = 'var(--accent-guardrail)';
        else if (nk === 'researcher')   titleColor = 'var(--accent-researcher)';
        else if (nk === 'analyst')      titleColor = 'var(--accent-analyst)';
        else if (nk === 'risk_assessor') titleColor = 'var(--accent-risk)';
        else if (nk === 'recommender')  titleColor = 'var(--accent-recommender)';
        else if (nk === 'reporter')     titleColor = 'var(--accent-reporter)';

        const logHeader = document.createElement('div');
        logHeader.className = 'console-log';
        const agentName = agentMappings[nk]?.name ?? nk.toUpperCase();
        logHeader.innerHTML = `<span style="color:${titleColor};font-weight:bold;">[${agentName}]</span><span class="analysis-log-suffix"> nhật ký phân tích:</span>`;
        consoleOutput.appendChild(logHeader);

        // Add collapsible thinking block if thinking is available
        if (item.thinking) {
            const thinkingContainer = document.createElement('details');
            thinkingContainer.className = 'console-log thinking-details';
            thinkingContainer.style.cssText = 'border-radius: 0 8px 8px 0;';
            thinkingContainer.open = true; // default to open for clear intuition
            
            const summary = document.createElement('summary');
            summary.style.cssText = 'cursor: pointer; font-weight: 600; outline: none; margin-bottom: 4px; user-select: none; color: #a0aec0;';
            summary.innerHTML = '<i class="fa-solid fa-brain"></i> Quá trình suy nghĩ (Thinking Process)';
            thinkingContainer.appendChild(summary);
            
            const thinkingContent = document.createElement('div');
            thinkingContent.style.cssText = 'white-space: pre-line; line-height: 1.5; padding: 4px 0;';
            thinkingContent.textContent = sanitizeConsoleText(stripMarkdown(item.thinking));
            thinkingContainer.appendChild(thinkingContent);
            consoleOutput.appendChild(thinkingContainer);
        }

        const logBody = document.createElement('div');
        logBody.className  = 'console-log';
        logBody.style.cssText = `color:#b0bec8;padding-left:12px;border-left:2px solid ${titleColor};margin-bottom:12px;line-height:1.55;`;
        consoleOutput.appendChild(logBody);

        await typeText(logBody, stripMarkdown(item.content) || 'Không có thông tin ghi nhận.', 4);
        saveActiveSearchState('running');
        processQueue();
    }

    function printAgentStartInLog(nodeKey) {
        const mapping = agentMappings[nodeKey];
        if (!mapping) return;
        
        let titleColor = '#94a3b8';
        const nk = nodeKey;
        if      (nk === 'guardrail')    titleColor = 'var(--accent-guardrail)';
        else if (nk === 'researcher')   titleColor = 'var(--accent-researcher)';
        else if (nk === 'analyst')      titleColor = 'var(--accent-analyst)';
        else if (nk === 'risk_assessor') titleColor = 'var(--accent-risk)';
        else if (nk === 'recommender')  titleColor = 'var(--accent-recommender)';
        else if (nk === 'reporter')     titleColor = 'var(--accent-reporter)';

        // If placeholder already exists, don't duplicate
        if (document.getElementById(`start-placeholder-${nk}`)) return;

        const startLog = document.createElement('div');
        startLog.className = 'console-log agent-start-placeholder';
        startLog.id = `start-placeholder-${nk}`;
        const agentName = mapping.name ?? nk.toUpperCase();
        startLog.innerHTML = `<span style="color:${titleColor};font-weight:bold;">[${agentName}]</span><span style="color: #a0aec0; font-style: italic;"> đang phân tích yêu cầu... <i class="fa-solid fa-spinner fa-spin"></i></span>`;
        consoleOutput.appendChild(startLog);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
        
        statStatus.textContent = `${agentName} đang xử lý…`;
        statStatus.style.color = 'var(--fpt-orange)';
    }

    function queuePrint(node, content, duration, tokens, thinking, model = '', toksPerSec = 0) {
        printQueue.push({ node, content, duration, tokens, thinking, model, toks_per_sec: toksPerSec });
        if (!isPrinting) processQueue();
    }

    // ── Mermaid Diagram ──────────────────────────────────────────────────────
    async function renderMermaidDiagram(markdownOrCode) {
        if (!mermaidOutput) return;
        let code = (markdownOrCode || '').trim();
        
        // ── Comprehensive Mermaid Sanitizer ──────────────────────────────────
        // 1. Replace Unicode arrows used by LLMs with ASCII Mermaid arrows
        code = code.replace(/\u2192/g, '-->');   // → 
        code = code.replace(/\u2190/g, '<--');   // ←
        code = code.replace(/\u27F6/g, '-->');   // ⟶
        code = code.replace(/\u27F5/g, '<--');   // ⟵
        code = code.replace(/\u2194/g, '<-->');  // ↔
        code = code.replace(/\uFF0D\uFF1E/g, '-->');  // －＞ fullwidth
        
        // 2. Fix single-dash arrows in flowcharts
        if (code.includes('graph') || code.includes('flowchart') || code.includes('TD') || code.includes('LR')) {
            code = code.replace(/(?<!-)->(?!>)/g, '-->');
        }

        // 2.5. Remove duplicate shape definitions on nodes in connection links (causes syntax error in Mermaid)
        let definedNodes = new Set();
        let lines = code.split('\n');
        let processedLines = [];
        for (let line of lines) {
            let trimmed = line.trim();
            if (!trimmed || trimmed.startsWith('%%')) {
                processedLines.push(line);
                continue;
            }
            let isLink = /-->|---|==>|-.->/g.test(trimmed);
            let nodeRegex = /(\w+[-\w]*)(?:\["([^"]*)"\]|\[([^\]]*)\]|\("([^"]*)"\)|\(([^)]*)\)|\{"([^"]*)"\}|\{([^}]*)\})/g;
            if (isLink) {
                let newLine = line.replace(nodeRegex, (match, id, q1, u1, q2, u2, q3, u3) => {
                    let lbl = q1 || u1 || q2 || u2 || q3 || u3 || '';
                    if (definedNodes.has(id)) {
                        return id;
                    } else {
                        definedNodes.add(id);
                        return match;
                    }
                });
                processedLines.push(newLine);
            } else {
                let match;
                while ((match = nodeRegex.exec(trimmed)) !== null) {
                    definedNodes.add(match[1]);
                }
                processedLines.push(line);
            }
        }
        code = processedLines.join('\n');

        // 2.6. Sanitize all double-quoted labels to prevent nested parentheses/quotes from breaking parser
        code = code.replace(/"([^"\\]*(?:\\.[^"\\]*)*)"/g, (match, content) => {
            let clean = content;
            clean = clean.replace(/<br\s*\/?>/gi, '__BR_TAG__');
            clean = clean.replace(/\(/g, '（')
                         .replace(/\)/g, '）')
                         .replace(/\[/g, '［')
                         .replace(/\]/g, '］')
                         .replace(/\{/g, '｛')
                         .replace(/\}/g, '｝')
                         .replace(/</g, '＜')
                         .replace(/>/g, '＞')
                         .replace(/'/g, '’')
                         .replace(/"/g, '”');
            clean = clean.replace(/__BR_TAG__/g, '<br/>');
            return `"${clean}"`;
        });

        // 3. Sanitize parentheses & brackets inside node labels to prevent parse errors.
        //    Pattern: NodeID[Label containing (bad) chars] or NodeID(Label)
        code = code.replace(/(\w+)\[([^\]]*)\]/g, (match, id, label) => {
            let clean = label.trim();
            if (clean.startsWith('"') && clean.endsWith('"')) clean = clean.slice(1, -1);
            if (clean.startsWith("'") && clean.endsWith("'")) clean = clean.slice(1, -1);
            clean = clean.replace(/\(/g, '（').replace(/\)/g, '）').replace(/"/g, '”').replace(/'/g, '’');
            return `${id}["${clean}"]`;
        });
        code = code.replace(/(\w+)\(([^)]*)\)/g, (match, id, label) => {
            let clean = label.trim();
            if (clean.startsWith('"') && clean.endsWith('"')) clean = clean.slice(1, -1);
            if (clean.startsWith("'") && clean.endsWith("'")) clean = clean.slice(1, -1);
            clean = clean.replace(/\[/g, '［').replace(/\]/g, '］').replace(/"/g, '”').replace(/'/g, '’');
            return `${id}("${clean}")`;
        });


        // 4. Strip any raw HTML tags that could slip in
        code = code.replace(/<[^>]+>/g, '');

        // 5. Remove lines with only whitespace to avoid parser trips
        code = code.split('\n').map(l => l.trimEnd()).filter(l => l.length > 0).join('\n');

        let hasMermaidBlock = false;
        if (code.includes('```mermaid')) {
            const regex = /```mermaid\s*([\s\S]*?)\s*```/;
            const match = code.match(regex);
            code = (match && match[1]) ? match[1].trim() : '';
            hasMermaidBlock = true;
        }

        currentDiagramCode = code;

        // If it doesn't have a ```mermaid block, check if it's a raw diagram
        if (!hasMermaidBlock) {
            const trimmed = code.toLowerCase();
            const mermaidKeywords = ['graph', 'flowchart', 'sequencediagram', 'gantt', 'classdiagram', 'statediagram', 'erdiagram', 'journey', 'pie', 'gitgraph'];
            const isRawDiagram = mermaidKeywords.some(kw => trimmed.startsWith(kw));
            if (!isRawDiagram) {
                showUncreatedDiagramCard();
                return;
            }
        }

        // Extra check for known placeholders or missing report indicators
        if (!code || code.length < 10 || 
            code.includes('chưa được tạo') || 
            code.includes('not created') || 
            code.includes('no report generated') || 
            code.includes('not generated yet')) {
            showUncreatedDiagramCard();
            return;
        }

        const uniqueId = 'mermaid-' + Math.random().toString(36).substring(2, 9);
        try {
            // Restore toolbar and original styling for diagram rendering
            const toolbar = document.querySelector('.diagram-toolbar');
            if (toolbar) toolbar.style.display = 'flex';

            mermaidOutput.className = 'mermaid-diagram-output';
            mermaidOutput.style.border = '1px solid var(--panel-border)';
            mermaidOutput.style.borderRadius = '6px';
            mermaidOutput.style.background = '#ffffff';
            mermaidOutput.style.padding = '10px';
            mermaidOutput.style.boxShadow = 'none';
            mermaidOutput.style.maxWidth = 'none';
            mermaidOutput.style.margin = '0';
            mermaidOutput.style.minHeight = '250px';
            mermaidOutput.style.maxHeight = '450px';
            mermaidOutput.style.display = 'flex';

            mermaidOutput.innerHTML = '<p class="placeholder-text"><i class="fa-solid fa-spinner fa-spin"></i> Đang vẽ sơ đồ quy trình…</p>';
            
            // Clear any stale SVG elements
            mermaidOutput.querySelectorAll('svg').forEach(el => el.remove());
            
            // Set initial zoom level
            currentZoom = 100;
            if (zoomLevelEl) zoomLevelEl.textContent = '100%';

            const { svg } = await mermaid.render(uniqueId, code);
            mermaidOutput.innerHTML = svg;
            
            // Center the SVG diagram and ensure proper sizing
            const renderedSvg = document.getElementById(uniqueId);
            if (renderedSvg) {
                renderedSvg.style.transition = 'transform 0.15s ease-out';
                renderedSvg.style.maxWidth = 'none';
                renderedSvg.style.height = 'auto';
                renderedSvg.style.display = 'block';
                renderedSvg.style.margin = '0 auto';
                renderedSvg.style.width = '100%';

                // Extract native dimensions from viewBox for intelligent sizing
                const viewBoxAttr = renderedSvg.getAttribute('viewBox');
                if (viewBoxAttr) {
                    const parts = viewBoxAttr.split(/[\s,]+/);
                    if (parts.length === 4) {
                        const nativeW = parseFloat(parts[2]) || 0;
                        const nativeH = parseFloat(parts[3]) || 0;
                        const containerW = mermaidOutput.clientWidth - 20; // account for padding
                        // If SVG is narrower than container, use native width for crisp rendering
                        if (nativeW > 0 && nativeW < containerW) {
                            renderedSvg.style.width = nativeW + 'px';
                        }
                    }
                }
            }
            // Ensure the container centers content
            mermaidOutput.style.display = 'flex';
            mermaidOutput.style.flexDirection = 'column';
            mermaidOutput.style.alignItems = 'center';
            mermaidOutput.style.justifyContent = 'center';
            mermaidOutput.style.textAlign = 'center';
        } catch (err) {
            console.error('Mermaid error:', err);
            let displayErr = `Lỗi biên dịch sơ đồ: ${err.message}`;
            if (err.message.includes('No diagram type detected') || 
                err.message.includes('No diagram type') || 
                code.includes('Report not created') || 
                code.includes('Báo cáo chưa được tạo') || 
                code.includes('No report generated') ||
                code.includes('not generated yet')) {
                showUncreatedDiagramCard();
            } else {
                mermaidOutput.innerHTML = `<p class="placeholder-text" style="color:#ef4444;"><i class="fa-solid fa-circle-exclamation"></i> ${displayErr}</p>`;
            }
            // Cleanup
            mermaidOutput.querySelectorAll('svg').forEach(el => el.remove());
            const staleTemp = document.getElementById(uniqueId);
            if (staleTemp) staleTemp.remove();
        }
    }

    function startPollingForReport() {
        if (pollingInterval) clearInterval(pollingInterval);
        
        statStatus.textContent = 'Đang nhận kết quả…';
        statStatus.style.color = 'var(--fpt-orange)';
        
        if (consoleOutput) {
            const logDiv = document.createElement('div');
            logDiv.className = 'console-log';
            logDiv.style.cssText = 'color: var(--fpt-orange); font-style: italic; margin-top: 10px; padding: 10px; background: rgba(217, 119, 6, 0.08); border-left: 4px solid var(--fpt-orange); border-radius: 4px;';
            logDiv.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Kết nối tạm thời bị gián đoạn. Tiến trình phân tích của các Tác nhân vẫn đang tiếp tục chạy ngầm trên máy chủ, hệ thống đang đồng bộ để lấy báo cáo...';
            consoleOutput.appendChild(logDiv);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
        }

        pollCount = 0;
        pollingInterval = setInterval(() => {
            pollCount++;
            if (pollCount > MAX_POLLS) {
                clearInterval(pollingInterval);
                statStatus.textContent = 'Hết hạn kết nối';
                statStatus.style.color = '#ef4444';
                runBtn.disabled = false;
                runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
                if (stopBtn) stopBtn.style.display = 'none';
                return;
            }

            fetch(getApiPrefix() + '/api/report?session_id=' + sessionId + '&t=' + Date.now())
                .then(res => { if (!res.ok) throw new Error(); return res.json(); })
                .then(data => {
                    const isIrrelevantReport = data.report && (data.report.trim().startsWith('# Không áp dụng') || data.report.trim().startsWith('# IRRELEVANT'));
                    if (data.report && (isIrrelevantReport || (!data.report.includes('Báo cáo chưa được tạo') && data.report.trim().length > 100))) {
                        clearInterval(pollingInterval);
                        hasCompletedSuccessfully = true;
                        if (isIrrelevantReport) {
                            // Metrics remain visible with default values — no rejection card
                            statStatus.textContent = 'Bị Từ Chối';
                            statStatus.style.color = '#dc2626';
                        } else {
                            statStatus.textContent = 'Hoàn Thành ✅';
                            statStatus.style.color = '#16a069';
                        }
                        runBtn.disabled = false;
                        runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
                        if (stopBtn) stopBtn.style.display = 'none';
                        
                        displayReportData(data);
                        
                        document.querySelectorAll('.graph-node').forEach(n => {
                            if (!n.classList.contains('node-hidden')) {
                                n.classList.remove('active');
                                n.classList.add('completed');
                            }
                        });
                        document.querySelectorAll('.graph-edges line').forEach(l => {
                            if (!l.classList.contains('edge-hidden')) {
                                l.classList.add('active');
                            }
                        });
                        localStorage.removeItem('fpt_active_search');
                    }
                })
                .catch(e => {
                    console.warn('Polling status, retrying...', e);
                });
        }, 3000);
    }

    // ── Run Pipeline ─────────────────────────────────────────────────────────
    function handleSseMessage(data) {
        if (data.error) {
            clearInterval(timerInterval);
            statStatus.textContent = 'Thất Bại';
            statStatus.style.color = '#ef4444';
            runBtn.disabled  = false;
            runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
            if (stopBtn) stopBtn.style.display = 'none';

            let cleanErr = data.error.split('\n')[0];
            const logDiv = document.createElement('div');
            logDiv.className   = 'console-log';
            logDiv.style.color = '#ef4444';
            
            if (cleanErr.includes('429') && (cleanErr.includes('limit') || cleanErr.includes('ollama'))) {
                logDiv.innerHTML = `<span style="font-weight:bold;">[Lỗi Hệ Thống]</span> Bạn đã đạt giới hạn sử dụng hàng tuần của Ollama Cloud (Lỗi 429).<br><br>
                <strong>Cách khắc phục:</strong> Giới hạn sẽ được đặt lại vào thứ Hai hàng tuần. Bạn có thể thử lại sau hoặc sử dụng API Key từ nhà cung cấp khác.<br><br>
                <em>Lưu ý: Hệ thống đã tích hợp cơ chế dự phòng tự động (Fast Fallback) — khi mô hình chính gặp giới hạn, hệ thống sẽ tự chuyển sang mô hình dự phòng khả dụng.</em>`;
            } else {
                const safeErr = cleanErr.replace(/</g,'&lt;').replace(/>/g,'&gt;');
                logDiv.innerHTML = `<span style="font-weight:bold;">[Lỗi Hệ Thống]</span> Tiến trình gặp sự cố: <strong>${safeErr}</strong>. Vui lòng kiểm tra lại cấu hình hoặc API Key.`;
            }
            consoleOutput.appendChild(logDiv);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
            localStorage.removeItem('fpt_active_search');
            return;
        }

        if (data.socratic_pause) {
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            activeStateSnapshot = data.state_snapshot;
            
            const text = data.socratic_questions || "";
            const questionLines = text.split('\n')
                .map(l => l.trim())
                .filter(l => /^\d+\.\s+/.test(l));
            
            let q1 = questionLines[0] || "Câu hỏi Socratic 1: Làm thế nào để áp dụng cuốn sách này vào thực tế học tập?";
            let q2 = questionLines[1] || "Câu hỏi Socratic 2: Những rào cản nhận thức nào bạn cần vượt qua?";
            let q3 = questionLines[2] || "Câu hỏi Socratic 3: Bạn có đề xuất hành động cụ thể nào sau khi đọc?";
            
            socraticQuestionsContainer.innerHTML = `
                <div style="margin-bottom: 20px;">
                    <label style="display: block; color: #e2e8f0; font-weight: 600; font-size: 13.5px; margin-bottom: 8px; line-height: 1.4;">${q1}</label>
                    <textarea id="socratic-ans-1" required style="width: 100%; height: 75px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(240, 95, 36, 0.15); border-radius: 6px; color: #ffffff; padding: 10px; font-size: 13px; resize: none; outline: none; transition: border 0.2s;" placeholder="Nhập câu trả lời phản biện của bạn..."></textarea>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; color: #e2e8f0; font-weight: 600; font-size: 13.5px; margin-bottom: 8px; line-height: 1.4;">${q2}</label>
                    <textarea id="socratic-ans-2" required style="width: 100%; height: 75px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(240, 95, 36, 0.15); border-radius: 6px; color: #ffffff; padding: 10px; font-size: 13px; resize: none; outline: none; transition: border 0.2s;" placeholder="Nhập câu trả lời phản biện của bạn..."></textarea>
                </div>
                <div style="margin-bottom: 20px;">
                    <label style="display: block; color: #e2e8f0; font-weight: 600; font-size: 13.5px; margin-bottom: 8px; line-height: 1.4;">${q3}</label>
                    <textarea id="socratic-ans-3" required style="width: 100%; height: 75px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(240, 95, 36, 0.15); border-radius: 6px; color: #ffffff; padding: 10px; font-size: 13px; resize: none; outline: none; transition: border 0.2s;" placeholder="Nhập câu trả lời phản biện của bạn..."></textarea>
                </div>
            `;
            
            setTimeout(() => {
                [1,2,3].forEach(i => {
                    const el = document.getElementById(`socratic-ans-${i}`);
                    if (el) {
                        el.addEventListener('focus', () => el.style.borderColor = 'var(--fpt-orange)');
                        el.addEventListener('blur', () => el.style.borderColor = 'rgba(240, 95, 36, 0.15)');
                    }
                });
            }, 100);

            socraticModal.style.display = 'flex';
            
            statStatus.textContent = 'Chờ phản biện';
            statStatus.style.color = '#f05f24';
            
            activeAgentBadge.textContent = 'Chờ độc giả';
            activeAgentBadge.className = 'agent-badge active-risk_assessor';
            
            const logDiv = document.createElement('div');
            logDiv.className = 'console-log';
            logDiv.style.color = 'var(--fpt-orange)';
            logDiv.style.fontStyle = 'italic';
            logDiv.innerHTML = `<span style="font-weight:bold;">[Hệ Thống]</span> Đang tạm dừng để chờ độc giả trả lời 3 câu hỏi Socratic mở trên màn hình chính...`;
            consoleOutput.appendChild(logDiv);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
            return;
        }

        if (data.done) {
            hasCompletedSuccessfully = true;
            // Render report and update stats immediately in real-time!
            clearInterval(timerInterval);
            highlightPanel('complete');

            if (data.stats) {
                statTime.textContent   = formatTimeString(data.stats.time);
                statTokens.textContent = data.stats.tokens;

                if (data.stats.irrelevant) {
                    // Metrics remain visible with default values — no rejection card
                    statAgents.textContent = '1 / 6';
                    statStatus.textContent = 'Bị Từ Chối';
                    statStatus.style.color = '#dc2626';
                } else {
                    const agentCount = data.stats.agents || 6;
                    statAgents.textContent = `${agentCount} / ${agentCount === 3 ? 3 : 6}`;
                    statStatus.textContent = 'Hoàn Thành ✅';
                    statStatus.style.color = '#16a069';
                    if (downloadGroup) downloadGroup.style.display = 'flex';
                }

                // Update metrics badges for all agents in real-time
                if (data.stats.agent_tokens) {
                    const agentKeys = ['guardrail', 'researcher', 'analyst', 'risk_assessor', 'recommender', 'reporter'];
                    agentKeys.forEach(k => {
                        const badge = document.getElementById(`metrics-${k}`);
                        if (badge) {
                            const durVal = data.stats.agent_durations && data.stats.agent_durations[k] ? data.stats.agent_durations[k] : 0;
                            const durText = `${durVal.toFixed(3)}s`;
                            const tk = data.stats.agent_tokens[k] ? data.stats.agent_tokens[k].toLocaleString() : '0';
                            const tps = data.stats.agent_toks_per_sec && data.stats.agent_toks_per_sec[k] ? data.stats.agent_toks_per_sec[k].toFixed(1) : '0.0';
                            const mdl = data.stats.agent_models && data.stats.agent_models[k] ? data.stats.agent_models[k].split('/').pop() : '';
                            badge.textContent = mdl ? `${mdl} · ${durText} · ${tps} tk/s · ${tk} tk` : `${durText} · ${tk} tk`;
                            badge.title = (data.stats.agent_models && data.stats.agent_models[k]) || '';
                        }
                    });
                }
            }

            runBtn.disabled  = false;
            runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
            if (data.report) {
                displayReportData(data);
            } else {
                fetchReport();
            }

            // Mark all active graph nodes and edges as completed
            document.querySelectorAll('.graph-node').forEach(n => {
                if (!n.classList.contains('node-hidden')) {
                    n.classList.remove('active');
                    n.classList.add('completed');
                }
            });
            document.querySelectorAll('.graph-edges line').forEach(l => {
                if (!l.classList.contains('edge-hidden')) {
                    l.classList.add('active');
                }
            });

            // Push completion marker to printQueue to gracefully end typewriter logic in background
            printQueue.push({ 
                type: 'completion', 
                stats: data.stats, 
                report: data.report, 
                diagram: data.diagram, 
                explanation: data.explanation 
            });
            if (!isPrinting) processQueue();
            if (stopBtn) stopBtn.style.display = 'none';
            localStorage.removeItem('fpt_active_search');

            // UX Tab Redirection Sequence: Report -> Diagram -> Report
            if (data.stats && !data.stats.irrelevant) {
                setTimeout(() => {
                    const reportTabBtn = document.getElementById('tab-btn-report');
                    if (reportTabBtn) {
                        reportTabBtn.click();
                        console.log("UX Sequence Step 1: Navigated to Detailed Report tab.");
                    }
                    
                    setTimeout(() => {
                        const diagramTabBtn = document.getElementById('tab-btn-diagram');
                        if (diagramTabBtn) {
                            diagramTabBtn.click();
                            console.log("UX Sequence Step 2: Navigated to Process Diagram tab.");
                        }
                        
                        setTimeout(() => {
                            if (reportTabBtn) {
                                reportTabBtn.click();
                                console.log("UX Sequence Step 3: Navigated back to Detailed Report for final check.");
                            }
                        }, 2500);
                    }, 2500);
                }, 800);
            }
            return;
        }

        if (data.type === 'node_start') {
            // Update node visual highlight and badge immediately in real-time!
            highlightNode(data.node);
            
            // Immediately create the DOM containers for real-time streaming console logs!
            const nk = data.node;
            const mapping = agentMappings[nk];
            let titleColor = '#94a3b8';
            if      (nk === 'guardrail')    titleColor = 'var(--accent-guardrail)';
            else if (nk === 'researcher')   titleColor = 'var(--accent-researcher)';
            else if (nk === 'analyst')      titleColor = 'var(--accent-analyst)';
            else if (nk === 'risk_assessor') titleColor = 'var(--accent-risk)';
            else if (nk === 'recommender')  titleColor = 'var(--accent-recommender)';
            else if (nk === 'reporter')     titleColor = 'var(--accent-reporter)';

            // Add a beautiful transition notice in console Output
            let transitionMsg = '';
            if (nk === 'researcher')      transitionMsg = '<i class="fa-solid fa-arrow-right-long" style="margin-right: 6px;"></i> Đang chuyển tiếp yêu cầu đến Tác nhân Hồ Sơ...';
            else if (nk === 'analyst')    transitionMsg = '<i class="fa-solid fa-arrow-right-long" style="margin-right: 6px;"></i> Đang chuyển tiếp yêu cầu đến Tác nhân Gợi Ý Sách...';
            else if (nk === 'risk_assessor') transitionMsg = '<i class="fa-solid fa-arrow-right-long" style="margin-right: 6px;"></i> Đang chuyển tiếp yêu cầu đến Tác nhân Socrates...';
            else if (nk === 'recommender') transitionMsg = '<i class="fa-solid fa-arrow-right-long" style="margin-right: 6px;"></i> Đang chuyển tiếp yêu cầu đến Tác nhân Phản Biện...';
            else if (nk === 'reporter')    transitionMsg = '<i class="fa-solid fa-arrow-right-long" style="margin-right: 6px;"></i> Đang chuyển tiếp yêu cầu đến Tác nhân Biên Soạn...';

            if (transitionMsg) {
                const welcome = consoleOutput.querySelector('.console-welcome');
                if (welcome) consoleOutput.innerHTML = '';
                
                const transDiv = document.createElement('div');
                transDiv.className = 'console-log';
                transDiv.style.cssText = 'color: #94a3b8; font-style: italic; font-size: 11.5px; margin: 8px 0; border-top: 1px dashed rgba(255,255,255,0.05); padding-top: 8px;';
                transDiv.innerHTML = transitionMsg;
                consoleOutput.appendChild(transDiv);
            }

            // Clean welcome panel if it exists
            const welcome = consoleOutput.querySelector('.console-welcome');
            if (welcome) {
                consoleOutput.innerHTML = '';
            }

            const logHeader = document.createElement('div');
            logHeader.className = 'console-log';
            const agentName = mapping?.name ?? nk.toUpperCase();
            logHeader.innerHTML = `<span style="color:${titleColor};font-weight:bold;">[${agentName}]</span><span class="analysis-log-suffix"> nhật ký phân tích:</span>`;
            consoleOutput.appendChild(logHeader);

            // Collapsible thinking process container (visible/open by default)
            const thinkingContainer = document.createElement('details');
            thinkingContainer.className = 'console-log thinking-details';
            thinkingContainer.open = true;

            const summary = document.createElement('summary');
            summary.innerHTML = '<i class="fa-solid fa-brain"></i> Quá trình suy nghĩ (Thinking Process)';
            thinkingContainer.appendChild(summary);

            const thinkingContent = document.createElement('div');
            thinkingContent.style.cssText = 'white-space: pre-line; line-height: 1.5; padding: 4px 0;';
            thinkingContainer.appendChild(thinkingContent);
            consoleOutput.appendChild(thinkingContainer);

            // Log body container
            const logBody = document.createElement('div');
            logBody.className  = 'console-log';
            logBody.style.cssText = `color:#b0bec8;padding-left:12px;border-left:2px solid ${titleColor};margin-bottom:12px;line-height:1.55;`;
            consoleOutput.appendChild(logBody);

            consoleOutput.scrollTop = consoleOutput.scrollHeight;

            // Update active stream details
            activeStream = {
                node: nk,
                rawText: '',
                thinkingText: '',
                contentText: '',
                reportText: '',
                diagramText: '',
                explanationText: '',
                section: 'none',
                logHeaderEl: logHeader,
                thinkingDetailsEl: thinkingContainer,
                thinkingContentEl: thinkingContent,
                logBodyEl: logBody
            };

            saveActiveSearchState('running');
        }

        if (data.type === 'token') {
            // Append incoming LLM token in real-time
            if (data.node === activeStream.node) {
                activeStream.rawText += data.token;
                const rawText = activeStream.rawText;
                const rawTextUpper = rawText.toUpperCase();
                const tokenUpper = data.token.toUpperCase();
                
                // Track transitions between THINKING, CONSOLE MESSAGE, DETAILED REPORT, MERMAID DIAGRAM and DIAGRAM EXPLANATION sections (both English and Vietnamese)
                const hasThinkingMarker = rawTextUpper.includes('=== THINKING ===') || 
                                          rawTextUpper.includes('=== QUÁ TRÌNH TƯ DUY ===') || 
                                          rawTextUpper.includes('=== SUY NGHĨ ===') || 
                                          rawTextUpper.includes('=== TƯ DUY ===');
                if (hasThinkingMarker && activeStream.section === 'none') {
                    activeStream.section = 'thinking';
                    activeStream.thinkingDetailsEl.style.display = 'block';
                }
                
                const hasConsoleMarker = rawTextUpper.includes('=== CONSOLE MESSAGE ===') || 
                                         rawTextUpper.includes('=== THÔNG BÁO CONSOLE ===') || 
                                         rawTextUpper.includes('=== NHẬT KÝ CONSOLE ===') || 
                                         rawTextUpper.includes('=== TÓM TẮT CONSOLE ===') || 
                                         rawTextUpper.includes('=== NHẬT KÝ ===') || 
                                         rawTextUpper.includes('=== TÓM TẮT ===');
                if (hasConsoleMarker && activeStream.section !== 'content' && activeStream.section !== 'report' && activeStream.section !== 'diagram' && activeStream.section !== 'explanation') {
                    // Truncate thinkingText at the console marker so thinking block doesn't show console content
                    const consoleMarkersList = ['=== CONSOLE MESSAGE ===','=== THÔNG BÁO CONSOLE ===','=== NHẬT KÝ CONSOLE ===','=== TÓM TẮT CONSOLE ===','=== NHẬT KÝ ===','=== TÓM TẮT ==='];
                    for (const cm of consoleMarkersList) {
                        const cmIdx = rawTextUpper.indexOf(cm);
                        if (cmIdx !== -1 && activeStream.thinkingText) {
                            const truncated = rawText.substring(0, cmIdx);
                            // only keep the part after the thinking marker
                            const thinkIdx = ['=== THINKING ===','=== QUÁ TRÌNH TƯ DUY ===','=== SUY NGHĨ ===','=== TƯ DUY ==='].reduce((best, tk) => {
                                const fi = rawTextUpper.indexOf(tk); return (fi !== -1 && (best === -1 || fi < best)) ? fi + tk.length : best;
                            }, -1);
                            if (thinkIdx !== -1) {
                                activeStream.thinkingText = rawText.substring(thinkIdx, cmIdx);
                                if (activeStream.thinkingContentEl) activeStream.thinkingContentEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(activeStream.thinkingText)));
                            }
                            break;
                        }
                    }
                    activeStream.section = 'content';
                }

                const hasReportMarker = rawTextUpper.includes('=== DETAILED REPORT ===') || 
                                        rawTextUpper.includes('=== BÁO CÁO CHI TIẾT ===') || 
                                        rawTextUpper.includes('=== BÁO CÁO CỤ THỂ ===') || 
                                        rawTextUpper.includes('=== BÁO CÁO ===');
                if (hasReportMarker && activeStream.section !== 'report' && activeStream.section !== 'diagram' && activeStream.section !== 'explanation') {
                    // Truncate contentText at the report marker so console log doesn't show report content
                    const reportMarkersList = ['=== DETAILED REPORT ===','=== BÁO CÁO CHI TIẾT ===','=== BÁO CÁO CỤ THỂ ===','=== BÁO CÁO ==='];
                    for (const rm of reportMarkersList) {
                        const rmIdx = rawTextUpper.indexOf(rm);
                        if (rmIdx !== -1 && activeStream.contentText) {
                            const consoleMarkersList2 = ['=== CONSOLE MESSAGE ===','=== THÔNG BÁO CONSOLE ===','=== NHẬT KÝ CONSOLE ===','=== TÓM TẮT CONSOLE ===','=== NHẬT KÝ ===','=== TÓM TẮT ==='];
                            const cmStart = consoleMarkersList2.reduce((best, cm) => {
                                const fi = rawTextUpper.indexOf(cm); return (fi !== -1 && (best === -1 || fi < best)) ? fi + cm.length : best;
                            }, -1);
                            if (cmStart !== -1) {
                                activeStream.contentText = rawText.substring(cmStart, rmIdx);
                                if (activeStream.logBodyEl) activeStream.logBodyEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(activeStream.contentText)));
                            }
                            break;
                        }
                    }
                    activeStream.section = 'report';
                    // Programmatically switch to the Report tab when report starts streaming! (Disabled for post-run sequential redirect)
                    // const reportTabBtn = document.getElementById('tab-btn-report');
                    // if (reportTabBtn && !reportTabBtn.classList.contains('active')) {
                    //     reportTabBtn.click();
                    // }
                }

                if ((rawTextUpper.includes('=== MERMAID DIAGRAM ===') || rawTextUpper.includes('=== SƠ ĐỒ MERMAID ===') || rawTextUpper.includes('=== BIỂU ĐỒ MERMAID ===')) && activeStream.section !== 'diagram' && activeStream.section !== 'explanation') {
                    activeStream.section = 'diagram';
                    // Programmatically switch to the Diagram tab when diagram starts streaming! (Disabled for post-run sequential redirect)
                    // const diagramTabBtn = document.getElementById('tab-btn-diagram');
                    // if (diagramTabBtn && !diagramTabBtn.classList.contains('active')) {
                    //     diagramTabBtn.click();
                    // }
                }

                if ((rawTextUpper.includes('=== DIAGRAM EXPLANATION ===') || rawTextUpper.includes('=== GIẢI THÍCH CHI TIẾT SƠ ĐỒ ===') || rawTextUpper.includes('=== GIẢI THÍCH SƠ ĐỒ ===') || rawTextUpper.includes('=== GIẢI THÍCH ===')) && activeStream.section !== 'explanation') {
                    activeStream.section = 'explanation';
                }
                
                if (activeStream.section === 'thinking') {
                    if (activeStream.thinkingContentEl.textContent === '') {
                        let idx = -1;
                        let offset = 16;
                        const markers = [
                            { key: '=== THINKING ===', len: 16 },
                            { key: '=== QUÁ TRÌNH TƯ DUY ===', len: 24 },
                            { key: '=== SUY NGHĨ ===', len: 16 },
                            { key: '=== TƯ DUY ===', len: 14 }
                        ];
                        for (const m of markers) {
                            const found = rawTextUpper.indexOf(m.key);
                            if (found !== -1 && (idx === -1 || found < idx)) {
                                idx = found;
                                offset = m.len;
                            }
                        }
                        if (idx !== -1) {
                            const after = rawText.substring(idx + offset);
                            activeStream.thinkingText = after;
                            activeStream.thinkingContentEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(after)));
                            consoleOutput.scrollTop = consoleOutput.scrollHeight;
                            return;
                        }
                    }
                    activeStream.thinkingText += data.token;
                    activeStream.thinkingContentEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(activeStream.thinkingText)));
                } else if (activeStream.section === 'content') {
                    if (activeStream.logBodyEl.textContent === '') {
                        let idx = -1;
                        let offset = 23;
                        const markers = [
                            { key: '=== CONSOLE MESSAGE ===', len: 23 },
                            { key: '=== THÔNG BÁO CONSOLE ===', len: 25 },
                            { key: '=== NHẬT KÝ CONSOLE ===', len: 23 },
                            { key: '=== TÓM TẮT CONSOLE ===', len: 23 },
                            { key: '=== NHẬT KÝ ===', len: 15 },
                            { key: '=== TÓM TẮT ===', len: 15 }
                        ];
                        for (const m of markers) {
                            const found = rawTextUpper.indexOf(m.key);
                            if (found !== -1 && (idx === -1 || found < idx)) {
                                idx = found;
                                offset = m.len;
                            }
                        }
                        if (idx !== -1) {
                            const after = rawText.substring(idx + offset);
                            activeStream.contentText = after;
                            activeStream.logBodyEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(after)));
                            consoleOutput.scrollTop = consoleOutput.scrollHeight;
                            return;
                        }
                    }
                    activeStream.contentText += data.token;
                    activeStream.logBodyEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(activeStream.contentText)));
                } else if (activeStream.section === 'report') {
                    if (!activeStream.reportText) {
                        let idx = -1;
                        let offset = 23;
                        const markers = [
                            { key: '=== DETAILED REPORT ===', len: 23 },
                            { key: '=== BÁO CÁO CHI TIẾT ===', len: 24 },
                            { key: '=== BÁO CÁO CỤ THỂ ===', len: 22 },
                            { key: '=== BÁO CÁO ===', len: 15 }
                        ];
                        for (const m of markers) {
                            const found = rawTextUpper.indexOf(m.key);
                            if (found !== -1 && (idx === -1 || found < idx)) {
                                idx = found;
                                offset = m.len;
                            }
                        }
                        if (idx !== -1) {
                            const after = rawText.substring(idx + offset);
                            activeStream.reportText = after;
                        } else {
                            activeStream.reportText = '';
                        }
                    } else {
                        activeStream.reportText += data.token;
                    }
                    if (activeStream.reportText) {
                        const cleanedReportText = normalizeVietnameseText(cleanInternalFilenames(activeStream.reportText.replace(/={2,}/g, '').replace(/\*\*\*/g, '')));
                        currentMarkdown = cleanedReportText;
                        if (rawMarkdownText) rawMarkdownText.value = cleanedReportText;
                        throttledRenderMarkdownReport(cleanedReportText);
                    }
                } else if (activeStream.section === 'diagram') {
                    if (!activeStream.diagramText) {
                        const idx = Math.max(rawTextUpper.indexOf('=== MERMAID DIAGRAM ==='), rawTextUpper.indexOf('=== SƠ ĐỒ MERMAID ==='), rawTextUpper.indexOf('=== BIỂU ĐỒ MERMAID ==='));
                        if (idx !== -1) {
                            let offset = 23;
                            if (rawTextUpper.includes('=== SƠ ĐỒ MERMAID ===')) offset = 21;
                            else if (rawTextUpper.includes('=== BIỂU ĐỒ MERMAID ===')) offset = 23;
                            const after = rawText.substring(idx + offset);
                            activeStream.diagramText = after;
                        } else {
                            activeStream.diagramText = '';
                        }
                    } else {
                        activeStream.diagramText += data.token;
                    }
                    if (activeStream.diagramText) {
                        const cleanedDiagramText = activeStream.diagramText.replace(/={2,}/g, '').trim();
                        const outputContainer = document.getElementById('mermaid-render-output');
                        if (outputContainer && cleanedDiagramText) {
                            outputContainer.innerHTML = `<div style="padding:20px; font-family: 'Fira Code', monospace; font-size:11px; white-space:pre-wrap; text-align:left; color:#475569; width: 100%; height: 100%; box-sizing: border-box;"><div style="color:var(--fpt-blue); font-weight:700; margin-bottom:8px;"><i class="fa-solid fa-spinner fa-spin"></i> ĐANG VẼ SƠ ĐỒ QUY TRÌNH...</div><code style="display:block; background:#f8fafc; padding:12px; border-radius:6px; border:1px solid #e2e8f0; overflow-x:auto;">${cleanedDiagramText}</code></div>`;
                        }
                    }
                } else if (activeStream.section === 'explanation') {
                    if (!activeStream.explanationText) {
                        const idx = Math.max(
                            rawTextUpper.indexOf('=== DIAGRAM EXPLANATION ==='),
                            rawTextUpper.indexOf('=== GIẢI THÍCH CHI TIẾT SƠ ĐỒ ==='),
                            rawTextUpper.indexOf('=== GIẢI THÍCH SƠ ĐỒ ==='),
                            rawTextUpper.indexOf('=== GIẢI THÍCH ===')
                        );
                        if (idx !== -1) {
                            let offset = 27;
                            if (rawTextUpper.includes('=== GIẢI THÍCH CHI TIẾT SƠ ĐỒ ===')) offset = 33;
                            else if (rawTextUpper.includes('=== GIẢI THÍCH SƠ ĐỒ ===')) offset = 24;
                            else if (rawTextUpper.includes('=== GIẢI THÍCH ===')) offset = 18;
                            const after = rawText.substring(idx + offset);
                            activeStream.explanationText = after;
                        } else {
                            activeStream.explanationText = '';
                        }
                    } else {
                        activeStream.explanationText += data.token;
                    }
                    if (activeStream.explanationText) {
                        throttledRenderExplanation(activeStream.explanationText);
                    }
                }
                consoleOutput.scrollTop = consoleOutput.scrollHeight;
            }
        }

        if (data.type === 'node_end' && data.content) {
            // Update the node's visual completion status and metrics badge immediately in real-time!
            const nodeEl = document.getElementById(agentMappings[data.node]?.nodeId);
            if (nodeEl) {
                nodeEl.classList.add('completed');
                nodeEl.classList.remove('active');
            }
            const edgeId = (data.node === 'reporter' && !hasAnalystRun) ? 'edge-researcher-reporter' : agentMappings[data.node]?.edgeId;
            if (edgeId) {
                const edgeEl = document.getElementById(edgeId);
                if (edgeEl) {
                    edgeEl.classList.add('active');
                }
            }
            const badge = document.getElementById(`metrics-${data.node}`);
            if (badge) {
                const durVal = data.duration ? data.duration : 0;
                const durText = `${durVal.toFixed(3)}s`;
                const tk = data.tokens ? data.tokens.toLocaleString() : '0';
                const tps = data.toks_per_sec ? data.toks_per_sec.toFixed(1) : '0.0';
                const mdl = data.model ? data.model.split('/').pop() : '';
                badge.textContent = mdl ? `${mdl} · ${durText} · ${tps} tk/s · ${tk} tk` : `${durText} · ${tk} tk`;
                badge.title = data.model || '';
            }

            // Sync with final cleaned text from server
            if (data.node === activeStream.node) {
                if (activeStream.thinkingContentEl && data.thinking) {
                    activeStream.thinkingContentEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(data.thinking)));
                }
                if (activeStream.logBodyEl && data.content) {
                    activeStream.logBodyEl.textContent = sanitizeConsoleText(cleanInternalFilenames(stripMarkdown(data.content)));
                }
                activeStream.node = null;
            }

            saveActiveSearchState('running');
        }
    }

    // ── SSE Connection Helper (supports auto-reconnect with exponential backoff) ──
    function connectSse(url) {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        if (sseReconnectTimer) {
            clearTimeout(sseReconnectTimer);
            sseReconnectTimer = null;
        }
        sseCurrentUrl = url;
        eventSource = new EventSource(url);

        eventSource.onmessage = (event) => {
            sseErrorCount = 0;
            sseReconnectCount = 0; // successful message = reset reconnect counter
            if (!event.data) return;
            try {
                const data = JSON.parse(event.data);
                handleSseMessage(data);
            } catch (e) {
                console.error('SSE parse error:', e);
            }
        };

        eventSource.onerror = (err) => {
            // Case 1: Already completed — close cleanly, no action
            if (hasCompletedSuccessfully) {
                if (eventSource) { eventSource.close(); eventSource = null; }
                return;
            }

            // Case 2: Status already shows a final state — close cleanly
            const statusText = statStatus.textContent || '';
            if (statusText.includes('Hoàn Thành') || statusText.includes('Bị Từ Chối') ||
                statusText.includes('Đã tạm dừng') || statusText.includes('Thất Bại')) {
                if (eventSource) { eventSource.close(); eventSource = null; }
                return;
            }

            // Case 3: SSE dropped mid-run — STOP completely (no background polling)
            if (eventSource) { eventSource.close(); eventSource = null; }
            if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
            if (pollingInterval) { clearInterval(pollingInterval); pollingInterval = null; }

            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
            if (stopBtn) stopBtn.style.display = 'none';
            statStatus.textContent = 'Mất kết nối';
            statStatus.style.color = '#ef4444';
            localStorage.removeItem('fpt_active_search');
        };
    }

    // ── SSE via POST (secure: API keys in request body, not URL) ────────────────
    async function connectSsePost(url, body) {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        if (sseReconnectTimer) {
            clearTimeout(sseReconnectTimer);
            sseReconnectTimer = null;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'text/event-stream' },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const errText = await response.text();
                let errMsg = `Lỗi máy chủ: ${response.status}`;
                try {
                    const errJson = JSON.parse(errText);
                    if (errJson.error) errMsg = errJson.error;
                } catch (e) {}
                handleSseMessage({ error: errMsg });
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                if (buffer.trim().startsWith('{')) {
                    try {
                        const parsedJson = JSON.parse(buffer.trim());
                        if (parsedJson.error) {
                            handleSseMessage({ error: parsedJson.error });
                            return;
                        }
                    } catch (e) {}
                }
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const dataStr = line.slice(6).trim();
                        if (!dataStr) continue;
                        try {
                            const data = JSON.parse(dataStr);
                            handleSseMessage(data);
                        } catch (e) {
                            // Non-JSON data, ignore
                        }
                    }
                    // Skip SSE comments (": ping" etc.) and empty lines
                }
            }

            // Process any remaining buffer
            if (buffer.startsWith('data: ')) {
                const dataStr = buffer.slice(6).trim();
                if (dataStr) {
                    try {
                        const data = JSON.parse(dataStr);
                        handleSseMessage(data);
                    } catch (e) {}
                }
            }
        } catch (err) {
            if (hasCompletedSuccessfully) return;

            const statusText = statStatus.textContent || '';
            if (statusText.includes('Hoàn Thành') || statusText.includes('Bị Từ Chối') ||
                statusText.includes('Đã tạm dừng') || statusText.includes('Thất Bại')) {
                return;
            }

            if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
            if (pollingInterval) { clearInterval(pollingInterval); pollingInterval = null; }

            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
            if (stopBtn) stopBtn.style.display = 'none';
            statStatus.textContent = 'Mất kết nối';
            statStatus.style.color = '#ef4444';
            localStorage.removeItem('fpt_active_search');
        }
    }

    runBtn.addEventListener('click', () => {
        const topic = topicInput.value.trim();
        if (!topic) { alert('Vui lòng nhập câu hỏi hoặc chủ đề nghiên cứu trước khi kích hoạt!'); return; }

        resetUI();
        hasCompletedSuccessfully = false;
        sseErrorCount = 0;
        sseReconnectCount = 0;
        if (sseReconnectTimer) { clearTimeout(sseReconnectTimer); sseReconnectTimer = null; }
        if (pollingInterval) {
            clearInterval(pollingInterval);
            pollingInterval = null;
        }
        runBtn.disabled  = true;
        runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang chạy…';
        if (stopBtn) stopBtn.style.display = 'block';
        highlightPanel('start');

        runStartTime  = Date.now();
        saveActiveSearchState('running');
        let lastSaveTime = Date.now();
        timerInterval = setInterval(() => {
            const now = Date.now();
            statTime.textContent = `${((now - runStartTime) / 1000).toFixed(3)}s`;
            if (now - lastSaveTime >= 1000) {
                saveActiveSearchState('running');
                lastSaveTime = now;
            }
        }, 50);

        if (!isProfileValid()) {
            alert('Vui lòng điền đầy đủ các thông tin bắt buộc trong phần Chân Dung Độc Giả (Họ tên, Mã số sinh viên, Ngành học) ở cột bên trái trước khi kích hoạt!');
            if (profileModal) profileModal.style.display = 'flex';
            runBtn.disabled = false;
            runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
            if (stopBtn) stopBtn.style.display = 'none';
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            return;
        }

        // Use POST to avoid exposing API keys in URL query parameters
        const postUrl = getApiPrefix() + '/api/run';
        const body = { 
            topic: topic,
            user_profile: getUserProfileString(),
            session_id: sessionId
        };
        connectSsePost(postUrl, body);
    });


    function throttledRenderMarkdownReport(content) {
        pendingReportContent = content;
        if (renderTimeout) return;
        if (irrelevantDetected) return; // Don't schedule renders after irrelevant card is shown
        
        renderTimeout = setTimeout(() => {
            renderTimeout = null;
            if (pendingReportContent !== null) {
                renderMarkdownReport(pendingReportContent);
            }
        }, 300);
    }

    function throttledRenderExplanation(content) {
        pendingExpContent = content;
        if (expRenderTimeout) return;

        expRenderTimeout = setTimeout(() => {
            expRenderTimeout = null;
            if (pendingExpContent !== null) {
                const expContainer = document.getElementById('mermaid-explanation-container');
                const expContent = document.getElementById('mermaid-explanation-content');
                if (expContainer && expContent) {
                    const cleanedExplanation = cleanInternalFilenames(pendingExpContent.replace(/={2,}/g, ''));
                    expContent.innerHTML = marked.parse(cleanedExplanation);
                    expContainer.style.display = 'block';
                }
            }
        }, 300);
    }

    // ── Render Markdown and LaTeX (KaTeX) ──────────────────────────────────────
    function renderMarkdownReport(content) {
        if (!reportView) return;
        if (!content) {
            reportView.innerHTML = '';
            return;
        }

        // Normalize Vietnamese text: fix broken diacritics + remove CJK chars
        let normalizedContent = normalizeVietnameseText(content);
        let processed = normalizedContent;
        
        // Parse Guardrail JSON — if irrelevant, show rejection card immediately (matching diagram behavior)
        let cleanText = normalizedContent.trim();
        if (cleanText.startsWith('{') || cleanText.includes('"relevant"')) {
            try {
                let jsonStr = cleanText.replace(/```json/g, '').replace(/```/g, '').trim();
                const parsed = JSON.parse(jsonStr);
                if (parsed.relevant === false || parsed.relevant === 'false') {
                    // Irrelevant query → show rejection card (same style as diagram)
                    showIrrelevantReportCard();
                    return;
                }
                // Relevant query → just skip this JSON block, reporter will produce the real report
                return;
            } catch (e) {
                // Try to detect irrelevant via regex fallback
                const isIrrelevantMatch = cleanText.match(/"relevant"\s*:\s*(false|"false")/i);
                if (isIrrelevantMatch) {
                    showIrrelevantReportCard();
                    return;
                }
                // If we can't parse but it contains "relevant", likely guardrail output — skip
                return;
            }
        } else {
            processed = cleanReportContent(processed);
        }

        // Protect math blocks from marked.js escaping
        const displayMath = [];
        const inlineMath = [];

        // Display math: $$...$$ — must be on its own line(s)
        processed = processed.replace(/\$\$([\s\S]+?)\$\$/g, (match, math) => {
            const placeholder = `MATHBLOCKPLACEHOLDER${displayMath.length}`;
            displayMath.push(math.trim());
            return `\n\n${placeholder}\n\n`;
        });

        // Inline math: $...$ — single line, no newline inside
        processed = processed.replace(/\$([^\$\n]+?)\$/g, (match, math) => {
            const placeholder = `MATHINLINEPLACEHOLDER${inlineMath.length}`;
            inlineMath.push(math.trim());
            return placeholder;
        });

        let html = marked.parse(processed);

        // Replace display math placeholders (marked may wrap in <p> tags)
        displayMath.forEach((math, idx) => {
            try {
                const rendered = window.katex ? window.katex.renderToString(math, { displayMode: true, throwOnError: false }) : math;
                // Handle case where marked wraps placeholder in <p>...</p>
                const pWrapped = `<p>${`MATHBLOCKPLACEHOLDER${idx}`}</p>`;
                if (html.includes(pWrapped)) {
                    html = html.replace(pWrapped, `<div class="katex-display">${rendered}</div>`);
                } else {
                    html = html.replace(`MATHBLOCKPLACEHOLDER${idx}`, `<div class="katex-display">${rendered}</div>`);
                }
            } catch (e) {
                const fallback = `<span class="text-danger">${math.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span>`;
                const pWrapped = `<p>${`MATHBLOCKPLACEHOLDER${idx}`}</p>`;
                if (html.includes(pWrapped)) {
                    html = html.replace(pWrapped, `<div class="katex-display">${fallback}</div>`);
                } else {
                    html = html.replace(`MATHBLOCKPLACEHOLDER${idx}`, `<div class="katex-display">${fallback}</div>`);
                }
            }
        });

        // Replace inline math placeholders
        inlineMath.forEach((math, idx) => {
            try {
                const rendered = window.katex ? window.katex.renderToString(math, { displayMode: false, throwOnError: false }) : math;
                html = html.replace(`MATHINLINEPLACEHOLDER${idx}`, rendered);
            } catch (e) {
                html = html.replace(`MATHINLINEPLACEHOLDER${idx}`, `<span class="text-danger">${math.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span>`);
            }
        });

        reportView.innerHTML = html;
        
        // Open all external links in new tab + display raw URL so user can copy
        reportView.querySelectorAll('a[href]').forEach(link => {
            const href = link.getAttribute('href');
            if (href && (href.startsWith('http') || href.startsWith('//'))) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
                // Only add URL display if link text is not already the URL
                const linkText = link.textContent.trim();
                if (linkText !== href && !link.nextElementSibling?.classList.contains('raw-url-display')) {
                    const urlSpan = document.createElement('span');
                    urlSpan.className = 'raw-url-display';
                    urlSpan.textContent = ' → ' + href;
                    urlSpan.style.cssText = 'display:inline; font-size:0.78em; color:#6b7280; word-break:break-all; margin-left:4px; font-family:monospace; user-select:all;';
                    link.insertAdjacentElement('afterend', urlSpan);
                }
            }
        });

        // Wrap all tables in a scroll container to prevent overflow outside the report frame
        reportView.querySelectorAll('table').forEach(tbl => {
            if (!tbl.parentElement.classList.contains('table-scroll-wrapper')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-scroll-wrapper';
                tbl.parentNode.insertBefore(wrapper, tbl);
                wrapper.appendChild(tbl);
            }
        });
    }

    // ── Display Report & Diagram Data ──────────────────────────────────────────
    function displayReportData(data) {
        if (!data || !data.report) return;

        // Normalize: fix broken diacritics + remove CJK chars at the source
        let rawReport = normalizeVietnameseText(data.report);
        let diagramText = data.diagram ? normalizeVietnameseText(data.diagram) : '';
        let explanationText = data.explanation ? normalizeVietnameseText(data.explanation) : '';

        // Extract diagram if diagramText is empty and rawReport has a mermaid block
        if (!diagramText && rawReport.includes('```mermaid')) {
            const regex = /```mermaid\s*([\s\S]*?)\s*```/i;
            const match = rawReport.match(regex);
            if (match) {
                diagramText = match[1].trim();
            }
        }

        // Clean report content from any mermaid or leaked markers
        let reportText = cleanReportContent(rawReport);

        // Robust Fallback Parser if standard section markers are missing
        const rawReportUpper = rawReport.toUpperCase();
        const hasMarkers = rawReportUpper.includes('=== DETAILED REPORT ===') || 
                           rawReportUpper.includes('=== BÁO CÁO CHI TIẾT ===') ||
                           rawReportUpper.includes('=== BÁO CÁO CỤ THỂ ===') ||
                           rawReportUpper.includes('=== BÁO CÁO ===') ||
                           rawReportUpper.includes('=== CONSOLE MESSAGE ===') || 
                           rawReportUpper.includes('=== THÔNG BÁO CONSOLE ===') ||
                           rawReportUpper.includes('=== NHẬT KÝ CONSOLE ===') ||
                           rawReportUpper.includes('=== TÓM TẮT CONSOLE ===') ||
                           rawReportUpper.includes('=== NHẬT KÝ ===') ||
                           rawReportUpper.includes('=== TÓM TẮT ===') ||
                           rawReportUpper.includes('=== THINKING ===') ||
                           rawReportUpper.includes('=== SUY NGHĨ ===') ||
                           rawReportUpper.includes('=== QUÁ TRÌNH TƯ DUY ===') ||
                           rawReportUpper.includes('=== TƯ DUY ===');

        if (!hasMarkers) {
            if (rawReport.includes('```mermaid')) {
                const regex = /```mermaid\s*([\s\S]*?)\s*```/i;
                const match = rawReport.match(regex);
                if (match) {
                    const idx = rawReport.indexOf('```mermaid');
                    const beforeDiagram = rawReport.substring(0, idx).trim();
                    const endIdx = rawReport.indexOf('```', idx + 10);
                    let afterDiagram = '';
                    if (endIdx !== -1) {
                        afterDiagram = rawReport.substring(endIdx + 3).trim();
                    }
                    reportText = cleanReportContent(beforeDiagram);
                    explanationText = cleanReportContent(afterDiagram);
                }
            }
            
            if (reportText.trim().length === 0 && explanationText.trim().length > 0) {
                reportText = explanationText;
                explanationText = '';
            }

            // Sync Console Message with the first body paragraph (disabled to prevent overwriting friendly logs)
            /*
            const paragraphs = reportText.split('\n').map(p => p.trim()).filter(p => p.length > 0);
            let firstPara = paragraphs.length > 0 ? paragraphs[0] : '';
            if (firstPara.startsWith('#') && paragraphs.length > 1) {
                firstPara = paragraphs[1];
            }
            if (firstPara) {
                const cleanSummary = cleanInternalFilenames(stripMarkdown(firstPara));
                const consoleLogs = consoleOutput.querySelectorAll('.console-log');
                if (consoleLogs.length > 0) {
                    const lastLog = consoleLogs[consoleLogs.length - 1];
                    if (lastLog && !lastLog.querySelector('summary') && !lastLog.querySelector('span')) {
                        lastLog.textContent = cleanSummary;
                    }
                }
            }
            */
        }

        currentMarkdown = reportText;
        if (rawMarkdownText) rawMarkdownText.value = reportText;
        
        // Check if this is a genuine irrelevant/rejected report
        // Only match if the report starts with the rejection heading (guardrail rejection format)
        // This prevents false positives where a fully-analyzed report mentions "Không áp dụng" in context
        const reportFirstLine = reportText.trim().split('\n')[0].trim();
        const isIrrelevant = /^#\s*(Không áp dụng|IRRELEVANT)/i.test(reportFirstLine) ||
                             reportText.trim().startsWith('# Không áp dụng') ||
                             reportText.trim().startsWith('# IRRELEVANT');

        reportView.style.cssText = '';
        if (isIrrelevant) {
            showIrrelevantReportCard();
        } else if (reportText.includes('Báo cáo chưa được tạo') || reportText.includes('Report not created') || reportText.includes('not generated yet')) {
            showUncreatedReportCard();
        } else if (reportText.trim().length === 0 || reportText.trim() === explanationText.trim()) {
            showDiagramOnlyReportCard();
        } else {
            renderMarkdownReport(reportText);
        }

        
        try {
            if (isIrrelevant) {
                showIrrelevantDiagramCard();
            } else if (diagramText) {
                renderMermaidDiagram(diagramText);
            } else {
                renderMermaidDiagram(reportText);
            }
        } catch (mErr) {
            console.error('Mermaid render failure:', mErr);
        }

        // Render diagram explanation (skip for irrelevant queries — already hidden by showIrrelevantDiagramCard)
        const expContainer = document.getElementById('mermaid-explanation-container');
        const expContent = document.getElementById('mermaid-explanation-content');
        if (expContainer && expContent && explanationText && !isIrrelevant) {
            expContent.innerHTML = marked.parse(explanationText);
            expContainer.style.display = 'block';
        } else if (expContainer) {
            expContainer.style.display = 'none';
        }

        if (!isIrrelevant &&
            !reportText.includes('Request Rejected') &&
            !reportText.includes('not generated yet') &&
            !reportText.includes('Báo cáo chưa được tạo') &&
            !reportText.includes('Report not created')) {
            if (downloadGroup) downloadGroup.style.display = 'flex';
            // ── Persist session data so navigating away & back won't lose the report
            try {
                sessionStorage.setItem('bookmind_session_report', JSON.stringify({
                    report: reportText,
                    diagram: diagramText,
                    explanation: explanationText,
                    timestamp: Date.now()
                }));
            } catch (e) { /* storage full — ignore */ }
        } else {
            if (downloadGroup) downloadGroup.style.display = 'none';
        }
    }

    // ── Fetch & Render Final Report ───────────────────────────────────────────
    function fetchReport() {
        fetch(getApiPrefix() + '/api/report?session_id=' + sessionId + '&t=' + Date.now())
            .then(res => { if (!res.ok) throw new Error(`HTTP ${res.status}`); return res.json(); })
            .then(data => {
                if (data.report) {
                    displayReportData(data);
                }
            })
            .catch(err => {
                console.error('Fetch report error:', err);
                showUncreatedReportCard();
                showUncreatedDiagramCard();
            });
    }

    // ── Diagram Zoom & Toggle Event Listeners ─────────────────────────────────
    function applyZoom() {
        const svgEl = mermaidOutput.querySelector('svg');
        if (svgEl) {
            svgEl.style.transform = `scale(${currentZoom / 100})`;
            svgEl.style.transformOrigin = 'center top';
        }
        if (zoomLevelEl) {
            zoomLevelEl.textContent = `${currentZoom}%`;
        }
    }

    if (zoomInBtn) {
        zoomInBtn.addEventListener('click', () => {
            if (currentZoom < 250) {
                currentZoom += 15;
                applyZoom();
            }
        });
    }

    if (zoomOutBtn) {
        zoomOutBtn.addEventListener('click', () => {
            if (currentZoom > 40) {
                currentZoom -= 15;
                applyZoom();
            }
        });
    }

    if (zoomResetBtn) {
        zoomResetBtn.addEventListener('click', () => {
            currentZoom = 100;
            applyZoom();
        });
    }



    // ── Stop Button Click Handler ──────────────────────────────────────────
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            if (pollingInterval) {
                clearInterval(pollingInterval);
                pollingInterval = null;
            }

            // Gửi yêu cầu huỷ tiến trình ngầm trên backend
            fetch(getApiPrefix() + '/api/stop?session_id=' + sessionId, { method: 'POST' })
                .then(res => res.json())
                .then(data => console.log('Backend stop response:', data.message))
                .catch(err => console.error('Lỗi khi gửi yêu cầu dừng tới backend:', err));

            // Restore buttons
            runBtn.disabled  = false;
            runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
            stopBtn.style.display = 'none';
            
            statStatus.textContent = 'Đã dừng';
            statStatus.style.color = 'var(--text-muted)';
            
            const abortLog = document.createElement('div');
            abortLog.className = 'console-log';
            abortLog.style.color = 'var(--fpt-orange)';
            abortLog.innerHTML = `<span style="font-weight:bold;">[Hệ Thống]</span> Tiến trình đã dừng theo yêu cầu của người dùng.`;
            consoleOutput.appendChild(abortLog);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
            localStorage.removeItem('fpt_active_search');
        });
    }





    // Helper to format any time string or number to seconds with milliseconds precision
    function formatTimeString(timeStr) {
        if (!timeStr) return '0.000s';
        if (typeof timeStr === 'string' && timeStr.endsWith('ms')) {
            const val = parseFloat(timeStr);
            return `${(val / 1000).toFixed(3)}s`;
        }
        if (typeof timeStr === 'string' && timeStr.endsWith('s')) {
            const val = parseFloat(timeStr);
            return `${val.toFixed(3)}s`;
        }
        const val = parseFloat(timeStr);
        if (isNaN(val)) return timeStr;
        if (val > 100) return `${(val / 1000).toFixed(3)}s`;
        return `${val.toFixed(3)}s`;
    }

    // New Chat Action: resets everything to initial empty state
    function startNewChat() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
        if (timerInterval) {
            clearInterval(timerInterval);
            timerInterval = null;
        }
        if (renderTimeout) {
            clearTimeout(renderTimeout);
            renderTimeout = null;
        }
        if (expRenderTimeout) {
            clearTimeout(expRenderTimeout);
            expRenderTimeout = null;
        }
        pendingReportContent = null;
        pendingExpContent = null;
        irrelevantDetected = false; // Reset guard flag for new runs
        topicInput.value = '';
        statTime.textContent   = '0.000s';
        statTokens.textContent = '0';
        statAgents.textContent = '0 / 6';
        statStatus.textContent = 'Sẵn sàng';
        statStatus.style.color = 'var(--text-secondary)';

        if (downloadGroup) downloadGroup.style.display = 'none';

        document.querySelectorAll('.graph-node').forEach(n => {
            n.classList.remove('active');
            n.classList.remove('completed');
            n.classList.remove('node-hidden');
        });
        document.querySelectorAll('.graph-edges line').forEach(l => {
            l.classList.remove('active');
            l.classList.remove('edge-hidden');
        });
        const directEdge = document.getElementById('edge-researcher-reporter');
        if (directEdge) {
            directEdge.style.display = 'none';
        }
        const agentKeys = ['guardrail', 'researcher', 'analyst', 'risk_assessor', 'recommender', 'reporter'];
        agentKeys.forEach(k => {
            const badge = document.getElementById(`metrics-${k}`);
            if (badge) badge.textContent = '0.000s | 0 tk';
        });

        consoleOutput.innerHTML = `
            <div class="console-welcome">
                <p class="welcome-title"><i class="fa-solid fa-network-wired"></i> Hệ Thống Báo Cáo Chi Tiết Tri Thức Doanh Nghiệp — VNU BookMind</p>
                <p>Sáu tác nhân chuyên biệt phối hợp xử lý yêu cầu theo chuỗi, từ xác thực đầu vào đến biên soạn báo cáo học thuật hoàn chỉnh:</p>
                <div class="welcome-grid">
                    <div class="welcome-card">
                        <h4><i class="fa-solid fa-filter"></i> Lọc Ngữ Cảnh</h4>
                        <p>Xác thực tính liên quan của yêu cầu, phân loại loại truy vấn và định tuyến luồng xử lý phù hợp.</p>
                    </div>
                    <div class="welcome-card">
                        <h4><i class="fa-solid fa-magnifying-glass"></i> Nghiên Cứu</h4>
                        <p>Truy xuất tri thức từ kho dữ liệu VNU BookMind qua cơ chế Hybrid Search kết hợp Chroma &amp; BM25.</p>
                    </div>
                    <div class="welcome-card">
                        <h4><i class="fa-solid fa-chart-simple"></i> Phân Tích</h4>
                        <p>Xây dựng ma trận so sánh đa chiều, đánh giá các phương án kiến trúc và lợi thế cạnh tranh.</p>
                    </div>
                    <div class="welcome-card">
                        <h4><i class="fa-solid fa-triangle-exclamation"></i> Kiểm Soát Rủi Ro</h4>
                        <p>Nhận diện rủi ro kỹ thuật &amp; vận hành, đề xuất biện pháp kiểm soát theo chuẩn VNU BookMind Secure-First.</p>
                    </div>
                    <div class="welcome-card">
                        <h4><i class="fa-solid fa-lightbulb"></i> Đề Xuất Chiến Lược</h4>
                        <p>Thiết lập lộ trình triển khai đa giai đoạn và hệ thống KPI đo lường hiệu quả thực thi.</p>
                    </div>
                    <div class="welcome-card">
                        <h4><i class="fa-solid fa-file-lines"></i> Biên Soạn Báo Cáo</h4>
                        <p>Tổng hợp toàn bộ đầu ra, biên soạn báo cáo học thuật và trực quan hóa kiến trúc qua sơ đồ Mermaid.</p>
                    </div>
                </div>
            </div>
        `;
        activeAgentBadge.textContent = 'Chờ lệnh';
        activeAgentBadge.className   = 'agent-badge inactive';

        showUncreatedReportCard();
        showUncreatedDiagramCard();
        if (rawMarkdownText) rawMarkdownText.value = 'Báo cáo chưa được tạo';
        currentMarkdown = '';

        printQueue = [];
        isPrinting = false;


        hasAnalystRun = false;
        runBtn.disabled  = false;
        runBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Kích Hoạt Phân Tích';
        if (stopBtn) stopBtn.style.display = 'none';

        localStorage.removeItem('fpt_active_search');
        // Clear session persistence so new query starts fresh
        try { sessionStorage.removeItem('bookmind_session_report'); } catch(e){}
    }

    // New Chat "+" icon button
    const newChatBtn = document.getElementById('new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
    }

    function initializeOrSyncWithServer() {
        // ── Step 1: Try to restore a completed report from sessionStorage (same tab, navigated away) ──
        const savedReport = (() => { try { return sessionStorage.getItem('bookmind_session_report'); } catch(e){ return null; }})();
        if (savedReport) {
            try {
                const parsed = JSON.parse(savedReport);
                if (parsed && parsed.report && (Date.now() - (parsed.timestamp || 0)) < 60 * 60 * 1000) {
                    displayReportData({
                        report: parsed.report,
                        diagram: parsed.diagram || '',
                        explanation: parsed.explanation || ''
                    });
                    return;
                }
            } catch(e) { /* ignore */ }
        }

        // ── Step 2: Check if there is an in-progress run saved for THIS TAB ──
        const savedSearch = (() => { try { return localStorage.getItem('fpt_active_search'); } catch(e){ return null; }})();
        if (savedSearch) {
            try {
                const parsed = JSON.parse(savedSearch);
                // Only resume if saved within the last 30 minutes and it belongs to our session
                const isOurs = parsed.sessionId && parsed.sessionId === sessionId;
                const isFresh = (Date.now() - (parsed.timestamp || 0)) < 30 * 60 * 1000;
                if (isOurs && isFresh && parsed.status === 'running' && parsed.topic) {
                    // Restore UI state so user sees where they were
                    topicInput.value = parsed.topic;
                    if (parsed.logs) consoleOutput.innerHTML = parsed.logs;
                    if (parsed.stateSnapshot) activeStateSnapshot = parsed.stateSnapshot;
                    if (parsed.activeNode) {
                        try {
                            highlightNode(parsed.activeNode);
                        } catch(e) { console.error("Error highlighting node:", e); }
                    }

                    // Restore metrics badges
                    const s = parsed.stats || {};
                    if (s.time)   statTime.textContent = s.time;
                    if (s.tokens) statTokens.textContent = s.tokens;
                    if (s.agents) statAgents.textContent = s.agents;
                    statStatus.textContent = 'Đang khôi phục…';
                    statStatus.style.color = 'var(--fpt-orange)';

                    runBtn.disabled  = true;
                    runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang chạy…';
                    if (stopBtn) stopBtn.style.display = 'inline-flex';

                    // Show notification banner
                    const banner = document.createElement('div');
                    banner.className = 'console-log';
                    banner.style.cssText = 'color: #f0a030; font-style: italic; font-size: 12px; margin: 8px 0; border-top: 1px dashed rgba(255,200,0,0.15); padding-top: 8px;';
                    banner.innerHTML = '<i class="fa-solid fa-rotate-right" style="margin-right:6px;"></i> Trang đã được tải lại — đang kiểm tra tiến trình từ máy chủ…';
                    consoleOutput.appendChild(banner);
                    consoleOutput.scrollTop = consoleOutput.scrollHeight;

                    // Start polling to sync final result (uses existing startPollingForReport)
                    startPollingForReport();
                    return;
                }
            } catch(e) { /* ignore */ }
        }

        // ── Step 3: Nothing to restore — show blank cards ──
        localStorage.removeItem('fpt_active_search');
        showUncreatedReportCard();
        showUncreatedDiagramCard();
    }

    if (consoleOutput && hideAnalysisLogText) {
        consoleOutput.classList.add('hide-analysis-suffix');
    }

    // Configure marked.js for proper GFM rendering
    if (typeof marked !== 'undefined') {
        marked.setOptions({ gfm: true, breaks: false });
    }

    // Check server connection on load and every 15 seconds
    checkServerConnection();
    setInterval(checkServerConnection, 15000);

    // Socratic Form Submit Handler for Phase 2 Resume
    if (socraticForm) {
        socraticForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const ans1 = document.getElementById('socratic-ans-1').value.trim();
            const ans2 = document.getElementById('socratic-ans-2').value.trim();
            const ans3 = document.getElementById('socratic-ans-3').value.trim();
            
            if (!ans1 || !ans2 || !ans3) {
                alert("Vui lòng nhập câu trả lời cho cả 3 câu hỏi Socratic.");
                return;
            }
            
            const socraticAnswers = `Câu trả lời 1: ${ans1}\nCâu trả lời 2: ${ans2}\nCâu trả lời 3: ${ans3}`;
            socraticModal.style.display = 'none';
            
            // Resume timer
            const currentSec = parseFloat(statTime.textContent) || 0;
            let sec = currentSec;
            timerInterval = setInterval(() => {
                sec += 0.001;
                statTime.textContent = sec.toFixed(3) + 's';
            }, 1);

            // Print intermediate resume log in console Output
            const resumeLog = document.createElement('div');
            resumeLog.className = 'console-log';
            resumeLog.style.cssText = 'color: #94a3b8; font-style: italic; font-size: 11.5px; margin: 8px 0; border-top: 1px dashed rgba(255,255,255,0.05); padding-top: 8px;';
            resumeLog.innerHTML = '<i class="fa-solid fa-arrow-right-long" style="margin-right: 6px;"></i> Đang chuyển tiếp câu trả lời của độc giả sang Tác nhân Phản Biện...';
            consoleOutput.appendChild(resumeLog);
            consoleOutput.scrollTop = consoleOutput.scrollHeight;
            
            // Build Phase 2 body
            const body = {
                topic: activeStateSnapshot.topic,
                user_profile: activeStateSnapshot.user_profile,
                socratic_answers: socraticAnswers,
                analysis: activeStateSnapshot.analysis,
                risks: activeStateSnapshot.risks,
                research_data: activeStateSnapshot.research_data,
                retrieved_context: activeStateSnapshot.retrieved_context,
                citations: activeStateSnapshot.citations,
                session_id: sessionId
            };
            
            // Run Phase 2
            const postUrl = `${getApiPrefix()}/api/run`;
            connectSsePost(postUrl, body);
        });
    }

    initializeOrSyncWithServer();
    // VNU BookMind Socratic Pipeline Initialized
});

