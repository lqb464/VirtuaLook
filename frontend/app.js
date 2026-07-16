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
    home: 'Catalogue',
    admin: 'Jobs',
    badge: 'VTON demo',
    heroSub: 'Pick a garment → upload a photo → run inference (CatVTON / Replicate / mock).',
    garmentsTitle: 'Garment catalogue',
    catAll: 'All',
    catTops: 'Tops',
    catDresses: 'Dresses',
    catPants: 'Pants',
    tryOn: 'Try On',
    noGarments: 'No garments found.',
    loadError: 'Failed to load garments. Make sure the server is running.',
    footer: 'VirtuaLook · VTON inference demo',
    tryOnTitle: 'Virtual Try-On',
    backLink: 'Back to catalogue',
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
    adminTitle: 'Jobs & garments',
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
    home: 'Catalogue',
    admin: 'Jobs',
    badge: 'VTON demo',
    heroSub: 'Chọn trang phục → upload ảnh → chạy inference (CatVTON / Replicate / mock).',
    garmentsTitle: 'Catalogue trang phục',
    catAll: 'Tất cả',
    catTops: 'Áo',
    catDresses: 'Váy',
    catPants: 'Quần',
    tryOn: 'Thử Đồ',
    noGarments: 'Chưa có trang phục.',
    loadError: 'Không tải được catalogue. Kiểm tra server đang chạy.',
    footer: 'VirtuaLook · VTON inference demo',
    tryOnTitle: 'Thử Đồ Ảo',
    backLink: 'Quay lại catalogue',
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
    adminTitle: 'Jobs & trang phục',
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
    noGarmentsAdmin: 'Chưa có trang phục.',
    tryLink: 'Thử',
    deleteBtn: 'Xóa',
    jobsSection: 'Lịch Sử Thử Đồ',
    noJobs: 'Chưa có job nào.',
    viewResult: 'Xem kết quả →',
  },
};

let currentLang = localStorage.getItem('lang') || 'vi';

function applyLang(lang) {
  currentLang = lang;
  localStorage.setItem('lang', lang);
  const t = TRANSLATIONS[lang];

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (t[key] !== undefined) el.innerHTML = t[key];
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    if (t[key] !== undefined) el.placeholder = t[key];
  });

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('lang-btn-active', btn.dataset.lang === lang);
  });

  document.documentElement.lang = lang;
}

function initLang() {
  applyLang(currentLang);
}
