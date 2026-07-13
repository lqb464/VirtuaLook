// ── Shared API helpers ────────────────────────────────────────────────────────

const BASE = '';

async function api(path) {
  const res = await fetch(BASE + path);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiPost(path, data) {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiPatch(path, data) {
  const res = await fetch(BASE + path, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiForm(path, formData) {
  const res = await fetch(BASE + path, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

async function apiDelete(path) {
  const res = await fetch(BASE + path, { method: 'DELETE' });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

// ── i18n ──────────────────────────────────────────────────────────────────────

const TRANSLATIONS = {
  en: {
    // nav
    home: 'Home',
    features: 'Features',
    guide: 'Guide',
    pricing: 'Pricing',
    about: 'About',
    admin: 'Admin',
    // index
    badge: 'Powered by IDM-VTON AI',
    heroTitle: 'Try On Any Outfit<br class="hidden md:block"/> Instantly with AI',
    heroSub: 'Upload your photo, pick a garment, and see how it looks on you — no fitting room needed.',
    browseBtn: 'Browse Garments',
    howTitle: 'How It Works',
    step1Title: 'Choose a Garment',
    step1Sub: 'Browse our collection and pick the outfit you want to try.',
    step2Title: 'Upload Your Photo',
    step2Sub: 'Upload a full-body photo of yourself standing straight.',
    step3Title: 'See the Result',
    step3Sub: 'Our AI generates a realistic try-on image in seconds.',
    garmentsTitle: 'Garments',
    catAll: 'All',
    catTops: 'Tops',
    catDresses: 'Dresses',
    catPants: 'Pants',
    tryOn: 'Try On',
    noGarments: 'No garments found.',
    loadError: 'Failed to load garments. Make sure the server is running.',
    footer: 'AI Virtual Try-On Technology Demo — © 2026 VirtuaLook',
    // tryon
    tryOnTitle: 'Virtual Try-On',
    backLink: 'Back to garments',
    selectedGarment: 'Selected Garment',
    yourPhoto: 'Your Photo',
    photoHint: 'Stand straight, full body visible. Wear fitted clothes for best results.',
    uploadPhoto: 'Upload a new photo',
    noPhotos: 'No photos yet. Upload one above.',
    resultTitle: 'Result',
    selectHint: 'Select a photo to get started',
    selectHint2: 'Upload your photo and click "Start Try-On"',
    startBtn: 'Start Try-On',
    processingTitle: 'AI is processing your try-on…',
    processingHint: 'This may take 30–60 seconds',
    cpuWarning: 'CPU mode: AI is computing, may take 5–15 minutes. Do not close the page.',
    download: 'Download',
    tryAgain: 'Try Again',
    failedTitle: 'Processing failed',
    setDefault: 'Set default',
    delete: 'Delete',
    // admin
    adminTitle: 'Admin Dashboard',
    statGarments: 'Garments',
    statJobs: 'Total Try-Ons',
    statDone: 'Successful',
    statRate: 'Success Rate',
    garmentsSection: 'Garments',
    addGarment: '+ Add Garment',
    newGarment: 'New Garment',
    namePlaceholder: 'Name',
    imageUrlPlaceholder: 'Image URL',
    descPlaceholder: 'Description (optional)',
    save: 'Save',
    cancel: 'Cancel',
    noGarmentsAdmin: 'No garments yet.',
    tryLink: 'Try',
    deleteBtn: 'Delete',
    jobsSection: 'Try-On Jobs',
    noJobs: 'No try-on jobs yet.',
    viewResult: 'View result →',
  },
  vi: {
    // nav
    home: 'Trang chủ',
    features: 'Tính năng',
    guide: 'Hướng dẫn',
    pricing: 'Bảng giá',
    about: 'Về dự án',
    admin: 'Quản trị',
    // index
    badge: 'Ứng dụng AI IDM-VTON',
    heroTitle: 'Thử Đồ Ngay Lập Tức<br class="hidden md:block"/> Bằng Trí Tuệ Nhân Tạo',
    heroSub: 'Tải ảnh của bạn, chọn trang phục và xem bạn mặc như thế nào — không cần phòng thử đồ.',
    browseBtn: 'Xem Trang Phục',
    howTitle: 'Cách Hoạt Động',
    step1Title: 'Chọn Trang Phục',
    step1Sub: 'Duyệt bộ sưu tập và chọn bộ đồ bạn muốn thử.',
    step2Title: 'Tải Ảnh Của Bạn',
    step2Sub: 'Tải ảnh toàn thân, đứng thẳng, để có kết quả tốt nhất.',
    step3Title: 'Xem Kết Quả',
    step3Sub: 'AI tạo ra hình ảnh thử đồ thực tế trong vài giây.',
    garmentsTitle: 'Trang Phục',
    catAll: 'Tất cả',
    catTops: 'Áo',
    catDresses: 'Váy',
    catPants: 'Quần',
    tryOn: 'Thử Đồ',
    noGarments: 'Không tìm thấy trang phục nào.',
    loadError: 'Không thể tải trang phục. Hãy đảm bảo server đang chạy.',
    footer: 'Demo Công Nghệ Thử Đồ AI — © 2026 VirtuaLook',
    // tryon
    tryOnTitle: 'Thử Đồ Ảo',
    backLink: 'Quay lại danh sách',
    selectedGarment: 'Trang Phục Đã Chọn',
    yourPhoto: 'Ảnh Của Bạn',
    photoHint: 'Đứng thẳng, hiện toàn thân. Mặc quần áo vừa vặn để có kết quả tốt nhất.',
    uploadPhoto: 'Tải ảnh mới lên',
    noPhotos: 'Chưa có ảnh nào. Hãy tải ảnh lên trên.',
    resultTitle: 'Kết Quả',
    selectHint: 'Chọn ảnh để bắt đầu',
    selectHint2: 'Tải ảnh và nhấn "Bắt Đầu Thử Đồ"',
    startBtn: 'Bắt Đầu Thử Đồ',
    processingTitle: 'AI đang xử lý ảnh thử đồ của bạn…',
    processingHint: 'Quá trình này có thể mất 30–60 giây',
    cpuWarning: 'CPU mode: AI đang tính toán, có thể mất 5–15 phút. Đừng đóng trang.',
    download: 'Tải Xuống',
    tryAgain: 'Thử Lại',
    failedTitle: 'Xử lý thất bại',
    setDefault: 'Đặt mặc định',
    delete: 'Xóa',
    // admin
    adminTitle: 'Bảng Điều Khiển Admin',
    statGarments: 'Trang Phục',
    statJobs: 'Tổng Lượt Thử',
    statDone: 'Thành Công',
    statRate: 'Tỷ Lệ Thành Công',
    garmentsSection: 'Trang Phục',
    addGarment: '+ Thêm Trang Phục',
    newGarment: 'Trang Phục Mới',
    namePlaceholder: 'Tên',
    imageUrlPlaceholder: 'URL Hình Ảnh',
    descPlaceholder: 'Mô tả (tùy chọn)',
    save: 'Lưu',
    cancel: 'Hủy',
    noGarmentsAdmin: 'Chưa có trang phục nào.',
    tryLink: 'Thử',
    deleteBtn: 'Xóa',
    jobsSection: 'Lịch Sử Thử Đồ',
    noJobs: 'Chưa có lượt thử đồ nào.',
    viewResult: 'Xem kết quả →',
  },
};

let currentLang = localStorage.getItem('lang') || 'vi';

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);
  const t = TRANSLATIONS[lang];

  // Update all data-i18n elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (t[key] !== undefined) el.innerHTML = t[key];
  });

  // Update placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (t[key] !== undefined) el.placeholder = t[key];
  });

  // Toggle lang button states
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('lang-btn-active', btn.dataset.lang === lang);
  });

  // Update html lang attribute
  document.documentElement.lang = lang;
}

function initLang() {
  applyLang(currentLang);
}
