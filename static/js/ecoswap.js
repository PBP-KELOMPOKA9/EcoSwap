(function () {
  'use strict';

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]*)'));
    return match ? decodeURIComponent(match[2]) : null;
  }

  /* ---------- Navbar: menu profil & menu mobile ---------- */
  const profile = document.querySelector('[data-profile]');
  if (profile) {
    const toggle = profile.querySelector('[data-profile-toggle]');
    toggle.addEventListener('click', function (e) {
      e.stopPropagation();
      const open = profile.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('click', function (e) {
      if (!profile.contains(e.target)) {
        profile.classList.remove('is-open');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  const navbar = document.querySelector('[data-navbar]');
  const burger = document.querySelector('[data-burger]');
  if (navbar && burger) {
    burger.addEventListener('click', function () {
      const open = navbar.classList.toggle('is-menu-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- Toast otomatis hilang ---------- */
  document.querySelectorAll('[data-toast]').forEach(function (toast) {
    const close = function () { toast.remove(); };
    toast.querySelector('button').addEventListener('click', close);
    setTimeout(close, 4500);
  });

  /* ---------- Wishlist (tombol hati) ---------- */
  const badge = document.querySelector('[data-wishlist-count]');

  document.addEventListener('submit', function (e) {
    const form = e.target.closest('[data-wishlist-form]');
    if (!form) return;
    e.preventDefault();

    const button = form.querySelector('.heart');
    button.disabled = true;

    fetch(form.action, {
      method: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: new FormData(form),
    })
      .then(function (res) {
        return res.json().then(function (data) { return { status: res.status, data: data }; });
      })
      .then(function (result) {
        if (result.status === 401) {
          window.location.href = result.data.login_url;
          return;
        }
        const on = result.data.tersimpan;
        button.classList.toggle('is-on', on);
        button.setAttribute('aria-pressed', on ? 'true' : 'false');
        button.setAttribute('aria-label', on ? 'Hapus dari wishlist' : 'Simpan ke wishlist');

        if (badge) {
          badge.textContent = result.data.jumlah;
          badge.hidden = result.data.jumlah === 0;
        }

        // Di halaman Wishlist, kartu langsung hilang saat hati dimatikan.
        const card = form.closest('[data-wishlist-card]');
        if (card && !on) {
          card.remove();
          const sisa = document.querySelectorAll('[data-wishlist-card]').length;
          const counter = document.querySelector('[data-wishlist-total]');
          if (counter) counter.textContent = sisa + ' barang tersimpan';
          if (sisa === 0) {
            const grid = document.querySelector('[data-wishlist-grid]');
            const empty = document.querySelector('[data-wishlist-empty]');
            if (grid) grid.remove();
            if (empty) empty.hidden = false;
            if (counter) counter.textContent = 'Belum ada barang tersimpan';
          }
        }
      })
      .catch(function () {
        form.submit();
      })
      .finally(function () {
        button.disabled = false;
      });
  });

  /* ---------- Modal konfirmasi hapus ---------- */
  const modal = document.querySelector('[data-modal-hapus]');
  if (modal) {
    const form = modal.querySelector('form');
    const nama = modal.querySelector('[data-modal-nama]');
    let lastTrigger = null;

    document.querySelectorAll('[data-hapus-url]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        lastTrigger = btn;
        form.action = btn.dataset.hapusUrl;
        if (nama) nama.textContent = btn.dataset.hapusNama || 'barang ini';
        modal.classList.add('is-open');
        modal.querySelector('[data-modal-batal]').focus();
      });
    });

    const tutup = function () {
      modal.classList.remove('is-open');
      if (lastTrigger) lastTrigger.focus();
    };
    modal.querySelector('[data-modal-batal]').addEventListener('click', tutup);
    modal.addEventListener('click', function (e) { if (e.target === modal) tutup(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.classList.contains('is-open')) tutup();
    });
  }

  /* ---------- Galeri detail barang ---------- */
  const galleryMain = document.querySelector('[data-gallery-main]');
  if (galleryMain) {
    document.querySelectorAll('[data-gallery-thumb]').forEach(function (thumb) {
      thumb.addEventListener('click', function () {
        galleryMain.src = thumb.dataset.src;
        document.querySelectorAll('[data-gallery-thumb]').forEach(function (t) {
          t.classList.remove('is-active');
          t.setAttribute('aria-pressed', 'false');
        });
        thumb.classList.add('is-active');
        thumb.setAttribute('aria-pressed', 'true');
      });
    });
  }

  /* ---------- Checkbox "Semua" di filter kategori ---------- */
  const semua = document.querySelector('[data-check-semua]');
  if (semua) {
    const kategori = document.querySelectorAll('[data-check-kategori]');
    semua.addEventListener('change', function () {
      if (semua.checked) kategori.forEach(function (c) { c.checked = false; });
      else if (!Array.from(kategori).some(function (c) { return c.checked; })) semua.checked = true;
    });
    kategori.forEach(function (c) {
      c.addEventListener('change', function () {
        semua.checked = !Array.from(kategori).some(function (k) { return k.checked; });
      });
    });
  }

  /* ---------- Ubah status (versi pemilik) ---------- */
  document.querySelectorAll('[data-auto-submit]').forEach(function (select) {
    select.addEventListener('change', function () { select.form.submit(); });
  });

  /* ---------- Form tambah/edit barang ---------- */
  const barangForm = document.querySelector('[data-barang-form]');
  if (barangForm) {
    const MAKS = 5;
    const fileInput = barangForm.querySelector('input[type="file"]');
    const dropzone = barangForm.querySelector('[data-dropzone]');
    const thumbs = barangForm.querySelector('[data-thumbs]');
    let fileBaru = [];

    const jumlahFotoLama = function () {
      return barangForm.querySelectorAll('[data-foto-lama]:not(.is-removed)').length;
    };

    const syncInput = function () {
      const dt = new DataTransfer();
      fileBaru.forEach(function (f) { dt.items.add(f); });
      fileInput.files = dt.files;
    };

    const tandaiUtama = function () {
      barangForm.querySelectorAll('.thumb__tag').forEach(function (tag) { tag.remove(); });
      const pertama = thumbs.querySelector('.thumb:not(.is-removed)');
      if (pertama) {
        const tag = document.createElement('span');
        tag.className = 'thumb__tag';
        tag.textContent = 'Utama';
        pertama.appendChild(tag);
      }
    };

    const tombolHapus = function (label) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'thumb__x';
      btn.setAttribute('aria-label', label);
      btn.innerHTML = '<span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></span>';
      return btn;
    };

    const renderBaru = function () {
      thumbs.querySelectorAll('[data-foto-baru]').forEach(function (el) { el.remove(); });
      fileBaru.forEach(function (file, i) {
        const wrap = document.createElement('div');
        wrap.className = 'thumb';
        wrap.dataset.fotoBaru = '';
        const img = document.createElement('img');
        img.alt = 'Pratinjau ' + file.name;
        img.src = URL.createObjectURL(file);
        wrap.appendChild(img);
        const btn = tombolHapus('Hapus ' + file.name);
        btn.addEventListener('click', function () {
          fileBaru.splice(i, 1);
          syncInput();
          renderBaru();
        });
        wrap.appendChild(btn);
        thumbs.appendChild(wrap);
      });
      tandaiUtama();
    };

    const tambahFile = function (files) {
      Array.from(files).forEach(function (file) {
        if (!/^image\/(jpeg|png)$/.test(file.type)) return;
        if (jumlahFotoLama() + fileBaru.length >= MAKS) return;
        fileBaru.push(file);
      });
      syncInput();
      renderBaru();
    };

    barangForm.querySelector('[data-pilih-foto]').addEventListener('click', function () { fileInput.click(); });
    fileInput.addEventListener('change', function () {
      const dipilih = Array.from(fileInput.files);
      // Input file selalu direset oleh browser, jadi gabungkan dengan pilihan sebelumnya.
      fileInput.value = '';
      tambahFile(dipilih);
    });

    ['dragenter', 'dragover'].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) { e.preventDefault(); dropzone.classList.add('is-drag'); });
    });
    ['dragleave', 'drop'].forEach(function (evt) {
      dropzone.addEventListener(evt, function (e) { e.preventDefault(); dropzone.classList.remove('is-drag'); });
    });
    dropzone.addEventListener('drop', function (e) { tambahFile(e.dataTransfer.files); });

    // Foto lama (halaman edit): tombol X mencentang checkbox hapus_foto.
    barangForm.querySelectorAll('[data-foto-lama]').forEach(function (wrap) {
      const check = wrap.querySelector('input[type="checkbox"]');
      wrap.querySelector('.thumb__x').addEventListener('click', function () {
        check.checked = true;
        wrap.classList.add('is-removed');
        tandaiUtama();
      });
    });

    // Harga hanya muncul untuk tipe Jual.
    const hargaField = barangForm.querySelector('[data-harga-field]');
    const hargaInput = hargaField.querySelector('input');
    const syncTipe = function () {
      const terpilih = barangForm.querySelector('input[name="tipe"]:checked');
      const jual = terpilih && terpilih.value === 'jual';
      hargaField.hidden = !jual;
      hargaInput.disabled = !jual;
    };
    barangForm.querySelectorAll('input[name="tipe"]').forEach(function (r) { r.addEventListener('change', syncTipe); });
    syncTipe();

    // Format harga 75000 -> 75.000 saat diketik.
    hargaInput.addEventListener('input', function () {
      const angka = hargaInput.value.replace(/\D/g, '').replace(/^0+(?=\d)/, '');
      hargaInput.value = angka.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    });

    // Penghitung karakter deskripsi.
    const desc = barangForm.querySelector('textarea');
    const counter = barangForm.querySelector('[data-counter]');
    const hitung = function () { counter.textContent = desc.value.length + '/500'; };
    desc.addEventListener('input', hitung);
    hitung();

    // Loading state tombol simpan.
    barangForm.addEventListener('submit', function () {
      const btn = barangForm.querySelector('[data-submit]');
      btn.classList.add('is-loading');
      btn.disabled = true;
      btn.textContent = 'Menyimpan...';
    });
  }
})();
