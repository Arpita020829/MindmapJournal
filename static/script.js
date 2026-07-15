/* ============================================================
   MindMate Journal — JavaScript Animations & Interactions
   ============================================================ */

'use strict';

/* ── Ambient Particle System ─────────────────────────────── */
(function initParticles() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let particles = [];
  let W, H;

  function resize() {
    W = canvas.width  = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  const COLORS = ['#C9C3DE', '#B9B1CD', '#B6A8CA', '#8E83A9', '#F4EAF1'];

  function createParticle() {
    return {
      x: Math.random() * W,
      y: Math.random() * H + H,
      r: Math.random() * 4 + 1.5,
      dx: (Math.random() - 0.5) * 0.4,
      dy: -(Math.random() * 0.6 + 0.2),
      alpha: Math.random() * 0.5 + 0.15,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      pulse: Math.random() * Math.PI * 2,
    };
  }

  for (let i = 0; i < 55; i++) {
    const p = createParticle();
    p.y = Math.random() * H; // Start spread across screen
    particles.push(p);
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach((p, i) => {
      p.pulse += 0.02;
      const r = p.r + Math.sin(p.pulse) * 0.6;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha * (0.7 + 0.3 * Math.sin(p.pulse));
      ctx.fill();
      ctx.globalAlpha = 1;

      p.x += p.dx;
      p.y += p.dy;

      // Drift effect
      p.dx += (Math.random() - 0.5) * 0.01;
      p.dx = Math.max(-0.8, Math.min(0.8, p.dx));

      if (p.y < -20 || p.x < -20 || p.x > W + 20) {
        particles[i] = createParticle();
      }
    });
    requestAnimationFrame(animate);
  }
  animate();
})();

/* ── Book Opening Animation ───────────────────────────────── */
(function initBookAnimation() {
  const openBtn   = document.getElementById('open-journal-btn');
  const closedView = document.getElementById('closed-diary-view');
  const openView  = document.getElementById('open-diary-view');
  const bookCover = document.getElementById('book-cover-panel');

  if (!openBtn || !closedView || !openView) return;

  openBtn.addEventListener('click', function () {
    // 1. Add opening class to trigger 3D rotation
    if (bookCover) {
      bookCover.style.transition = 'transform 1.3s cubic-bezier(0.645,0.045,0.355,1)';
      bookCover.style.transform  = 'rotateY(-160deg)';
    }

    // 2. Fade out closed view
    closedView.style.transition = 'opacity 0.6s ease 0.8s, transform 0.6s ease 0.8s';
    closedView.style.opacity    = '0';
    closedView.style.transform  = 'scale(0.96)';

    // 3. Show open view after animation
    setTimeout(() => {
      closedView.style.display = 'none';
      openView.style.display   = 'flex';
      openView.classList.add('visible');
    }, 1200);
  });
})();

/* ── Emotion Badge Class Assignment ───────────────────────── */
(function assignEmotionClasses() {
  document.querySelectorAll('.emotion-badge').forEach(badge => {
    const text = badge.textContent.trim().toLowerCase();
    if (text.includes('anxiety'))    badge.classList.add('anxiety');
    else if (text.includes('depression')) badge.classList.add('depression');
    else if (text.includes('stress'))     badge.classList.add('stress');
    else if (text.includes('normal'))     badge.classList.add('normal');
  });
})();

/* ── Confidence Bar Animation ─────────────────────────────── */
(function animateConfidenceBars() {
  document.querySelectorAll('.confidence-fill').forEach(bar => {
    const target = bar.dataset.width || '0';
    bar.style.width = '0%';
    setTimeout(() => {
      bar.style.width = target + '%';
    }, 300);
  });
})();

/* ── Journal Textarea Character Counter ───────────────────── */
(function initCharCounter() {
  const textarea = document.querySelector('textarea[name="journal"]');
  const counter  = document.getElementById('char-counter');
  if (!textarea || !counter) return;

  function update() {
    const len = textarea.value.length;
    counter.textContent = len + ' characters';
    counter.style.color = len > 400 ? '#8E83A9' : 'rgba(142,131,169,0.6)';
  }
  textarea.addEventListener('input', update);
  update();
})();

/* ── Active Nav Link Highlighter ──────────────────────────── */
(function highlightNav() {
  const path  = window.location.pathname;
  const links = document.querySelectorAll('.diary-nav-link');
  links.forEach(link => {
    const href = link.getAttribute('href');
    if (
      (href === '/'          && (path === '/' || path === ''))  ||
      (href !== '/'          && path.startsWith(href))
    ) {
      link.classList.add('active');
    }
  });
})();

/* ── History Card Stagger Entrance ────────────────────────── */
(function staggerCards() {
  const cards = document.querySelectorAll('.history-card, .stat-card, .entry-card');
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(28px)';
    setTimeout(() => {
      card.style.transition = 'opacity 0.55s ease, transform 0.55s cubic-bezier(0.34,1.56,0.64,1)';
      card.style.opacity    = '1';
      card.style.transform  = 'translateY(0)';
    }, 80 + i * 70);
  });
})();

/* ── Page Flip Transition for Internal Navigation ─────────── */
(function initPageFlip() {
  const navLinks = document.querySelectorAll('.diary-nav-link, .spread-btn, .dashboard-tab');
  navLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      const href = this.getAttribute('href');
      if (!href || href.startsWith('#') || href === window.location.pathname) return;

      e.preventDefault();
      const wrapper = document.querySelector('.inner-page-wrapper') ||
                      document.querySelector('.open-book-wrapper') ||
                      document.querySelector('.landing-scene');

      if (wrapper) {
        wrapper.style.transition  = 'opacity 0.45s ease, transform 0.45s cubic-bezier(0.645,0.045,0.355,1)';
        wrapper.style.opacity     = '0';
        wrapper.style.transform   = 'perspective(1200px) rotateY(20deg) translateX(60px)';
        setTimeout(() => { window.location.href = href; }, 440);
      } else {
        window.location.href = href;
      }
    });
  });
})();

/* ── Delete Confirmation ──────────────────────────────────── */
(function initDeleteConfirm() {
  document.querySelectorAll('.delete-btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
      if (!confirm('Remove this diary entry?')) {
        e.preventDefault();
      }
    });
  });
})();

/* ── Dashboard Chart Customization ───────────────────────── */
(function styleDashboardChart() {
  // Applied after Chart.js renders — see dashboard template inline script
  window.mindmateChartDefaults = {
    backgroundColor: ['#C9C3DE', '#B9B1CD', '#B6A8CA', '#8E83A9'],
    borderColor:     ['#8E83A9', '#7B6E98', '#A89CC0', '#6B6090'],
    borderWidth: 2,
    borderRadius: 8,
    hoverBackgroundColor: ['#B9B1CD', '#A8A0BC', '#A699BA', '#7E7499'],
  };
})();

/* ── Smooth scroll for anchor links ──────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
