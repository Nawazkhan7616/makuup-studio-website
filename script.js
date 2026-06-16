/* =============================================
   MakuUP Studio — JavaScript
   ============================================= */

(function () {
    'use strict';

    /* -----------------------------------------------
       1. NAVBAR — scroll effect + mobile hamburger
    ----------------------------------------------- */
    const navbar    = document.getElementById('navbar');
    const hamburger = document.getElementById('hamburger');
    const navLinks  = document.getElementById('nav-links');

    function onScroll() {
        if (window.scrollY > 60) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        toggleBackToTop();
        animateStats();
    }

    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('load', () => { animateStats(); });

    hamburger.addEventListener('click', () => {
        const isOpen = navLinks.classList.toggle('open');
        hamburger.classList.toggle('active', isOpen);
        hamburger.setAttribute('aria-expanded', isOpen);
        document.body.style.overflow = isOpen ? 'hidden' : '';
    });

    navLinks.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('open');
            hamburger.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        });
    });

    /* -----------------------------------------------
       2. BACK TO TOP BUTTON
    ----------------------------------------------- */
    const backToTop = document.getElementById('back-to-top');

    function toggleBackToTop() {
        backToTop.classList.toggle('visible', window.scrollY > 500);
    }

    backToTop.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    /* -----------------------------------------------
       3. ANIMATED STATS (count up on scroll into view)
    ----------------------------------------------- */
    const statNums    = document.querySelectorAll('.stat-num');
    let statsAnimated = false;

    function animateStats() {
        if (statsAnimated) return;
        const statsSection = document.getElementById('stats');
        if (!statsSection) return;
        const rect = statsSection.getBoundingClientRect();
        if (rect.top < window.innerHeight - 60) {
            statsAnimated = true;
            statNums.forEach(el => {
                const target   = parseInt(el.dataset.target, 10);
                const duration = 1600;
                const start    = performance.now();
                function step(now) {
                    const elapsed  = now - start;
                    const progress = Math.min(elapsed / duration, 1);
                    const ease     = 1 - Math.pow(1 - progress, 4);
                    el.textContent = Math.round(ease * target).toLocaleString();
                    if (progress < 1) requestAnimationFrame(step);
                }
                requestAnimationFrame(step);
            });
        }
    }

    // ✅ Call after all variables (backToTop, statNums, statsAnimated) are declared
    onScroll();

    /* -----------------------------------------------
       4. PORTFOLIO FILTER TABS
    ----------------------------------------------- */
    const tabBtns        = document.querySelectorAll('.tab-btn');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            portfolioItems.forEach(item => item.classList.remove('port-large', 'port-tall'));
            portfolioItems.forEach(item => {
                const cat = item.dataset.category;
                if (filter === 'all' || cat === filter) {
                    item.classList.remove('hidden');
                    item.style.animation = 'none';
                    requestAnimationFrame(() => {
                        item.style.animation = 'fadeSlideUp 0.5s ease forwards';
                    });
                } else {
                    item.classList.add('hidden');
                }
            });
            if (filter === 'all') {
                const items = [...portfolioItems];
                items[0].classList.add('port-large');
                if (items[5]) items[5].classList.add('port-tall');
            }
        });
    });

    /* -----------------------------------------------
       5. TESTIMONIALS SLIDER
    ----------------------------------------------- */
    const track         = document.getElementById('testimonials-track');
    const dotsContainer = document.getElementById('slider-dots');
    const prevBtn       = document.getElementById('prev-btn');
    const nextBtn       = document.getElementById('next-btn');

    let currentSlide = 0;
    let visibleCount = getVisibleCount();
    let autoPlayTimer;

    function getVisibleCount() {
        if (window.innerWidth < 768)  return 1;
        if (window.innerWidth < 1024) return 2;
        return 3;
    }

    function getCards() {
        return track ? Array.from(track.querySelectorAll('.testimonial-card')) : [];
    }

    function totalSlides() {
        return Math.max(0, getCards().length - visibleCount + 1);
    }

    function buildDots() {
        if (!dotsContainer) return;
        dotsContainer.innerHTML = '';
        const n = totalSlides();
        for (let i = 0; i < n; i++) {
            const dot = document.createElement('button');
            dot.className = 'slider-dot' + (i === 0 ? ' active' : '');
            dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
            dot.addEventListener('click', () => goTo(i));
            dotsContainer.appendChild(dot);
        }
    }

    function updateDots() {
        if (!dotsContainer) return;
        dotsContainer.querySelectorAll('.slider-dot').forEach((d, i) => {
            d.classList.toggle('active', i === currentSlide);
        });
    }

    function goTo(index) {
        const cards = getCards();
        const n     = totalSlides();
        currentSlide = Math.max(0, Math.min(index, n - 1));
        const cardWidth = cards[0] ? cards[0].offsetWidth + 24 : 0;
        if (track) track.style.transform = `translateX(-${currentSlide * cardWidth}px)`;
        updateDots();
        restartAutoplay();
    }

    function startAutoplay() {
        autoPlayTimer = setInterval(() => {
            const n = totalSlides();
            goTo(currentSlide >= n - 1 ? 0 : currentSlide + 1);
        }, 5000);
    }

    function restartAutoplay() {
        clearInterval(autoPlayTimer);
        startAutoplay();
    }

    function initSlider() {
        const cards = getCards();
        if (prevBtn && nextBtn && cards.length) {
            buildDots();
            startAutoplay();
        }
    }

    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            const n = totalSlides();
            goTo(currentSlide <= 0 ? n - 1 : currentSlide - 1);
        });
        nextBtn.addEventListener('click', () => {
            const n = totalSlides();
            goTo(currentSlide >= n - 1 ? 0 : currentSlide + 1);
        });
        window.addEventListener('resize', () => {
            visibleCount = getVisibleCount();
            buildDots();
            goTo(0);
        });
        if (track) {
            let touchStartX = 0;
            track.addEventListener('touchstart', e => { touchStartX = e.changedTouches[0].clientX; }, { passive: true });
            track.addEventListener('touchend', e => {
                const diff = touchStartX - e.changedTouches[0].clientX;
                if (Math.abs(diff) > 50) {
                    const n = totalSlides();
                    if (diff > 0) goTo(currentSlide >= n - 1 ? 0 : currentSlide + 1);
                    else          goTo(currentSlide <= 0 ? n - 1 : currentSlide - 1);
                }
            }, { passive: true });
        }
    }

    initSlider();

    /* -----------------------------------------------
       6. BOOKING FORM — Django Backend API
    ----------------------------------------------- */

    // 🔧 LOCAL DEV — change to Railway URL before deploying
    const API_BASE = 'https://makuup-backend.up.railway.app';
    // const API_BASE = 'http://127.0.0.1:8000';

    const bookingForm = document.getElementById('booking-form');
    const formSuccess = document.getElementById('form-success');
    const submitBtn   = document.getElementById('submit-btn');

    if (bookingForm) {
        bookingForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name    = document.getElementById('name').value.trim();
            const email   = document.getElementById('email').value.trim();
            const phone   = document.getElementById('phone').value.trim();
            const service = document.getElementById('service').value;
            const date    = document.getElementById('date').value;
            const message = document.getElementById('message').value.trim();

            // Client-side validation
            if (!name || !email || !service || !date) {
                bookingForm.style.animation = 'none';
                requestAnimationFrame(() => {
                    bookingForm.style.animation = 'shake 0.5s ease';
                });
                return;
            }

            submitBtn.textContent = 'Sending…';
            submitBtn.disabled    = true;

            try {
                const response = await fetch(`${API_BASE}/api/bookings/create/`, {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify({ name, email, phone, service, date, message }),
                });

                const result = await response.json();

                if (response.ok && result.success) {
                    // ✅ Booking saved
                    bookingForm.reset();
                    formSuccess.hidden = false;
                    formSuccess.style.animation = 'fadeSlideUp 0.4s ease forwards';
                    setTimeout(() => { formSuccess.hidden = true; }, 6000);

                } else if (response.status === 409) {
                    // ⚠️ Date is fully booked
                    alert(result.message || 'This date is fully booked. Please choose another date.');

                } else {
                    // ❌ Validation or server error — show the actual message
                    const msg = result.error || 'Something went wrong. Please try again.';
                    alert(msg);
                }

            } catch (err) {
                console.error('Booking error:', err);
                alert('Unable to reach the server. Please check your connection and try again.');
            } finally {
                submitBtn.textContent = 'Request Booking';
                submitBtn.disabled    = false;
            }
        });
    }

    /* -----------------------------------------------
       7. SCROLL REVEAL ANIMATIONS
    ----------------------------------------------- */
    const revealEls = document.querySelectorAll(
        '.service-card, .portfolio-item, .testimonial-card, .stat-item, .feature-item, .about-img-frame, .about-text-side, .cta-text, .booking-form'
    );

    revealEls.forEach((el, i) => {
        el.classList.add('reveal');
        if (i % 4 === 1) el.classList.add('reveal-delay-1');
        if (i % 4 === 2) el.classList.add('reveal-delay-2');
        if (i % 4 === 3) el.classList.add('reveal-delay-3');
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    revealEls.forEach(el => observer.observe(el));

    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.min = new Date().toISOString().split('T')[0];
    }

    /* -----------------------------------------------
       8. DYNAMIC TESTIMONIALS from API
       Graceful fallback: static HTML shows if API unavailable
    ----------------------------------------------- */
    async function loadTestimonialsFromAPI() {
        try {
            const res = await fetch(`${API_BASE}/api/testimonials/`, {
                signal: AbortSignal.timeout ? AbortSignal.timeout(5000) : undefined,
            });
            if (!res.ok) return;

            const data         = await res.json();
            const testimonials = data.testimonials || [];
            if (!testimonials.length) return;

            const sliderTrack = document.getElementById('testimonials-track');
            if (!sliderTrack) return;

            sliderTrack.innerHTML = testimonials.map(t => `
              <div class="testimonial-card">
                <div class="testi-stars">${'★'.repeat(t.rating)}${'☆'.repeat(5 - t.rating)}</div>
                <p class="testi-quote">"${escapeHtml(t.quote)}"</p>
                <div class="testi-author">
                  <div class="testi-avatar" style="background:${t.avatar_bg}">${escapeHtml(t.initial)}</div>
                  <div>
                    <strong>${escapeHtml(t.name)}</strong>
                    <span>${escapeHtml(t.location || '')}${t.service ? ' · ' + escapeHtml(t.service) : ''}</span>
                  </div>
                </div>
              </div>
            `).join('');

            currentSlide = 0;
            buildDots();
            clearInterval(autoPlayTimer);
            startAutoplay();

        } catch (_) {
            // Silent fail — static testimonials remain visible
        }
    }

    function escapeHtml(str) {
        const el = document.createElement('div');
        el.textContent = str || '';
        return el.innerHTML;
    }

    loadTestimonialsFromAPI();

    /* -----------------------------------------------
       9. REVIEW SUBMISSION FORM — Star rating + submit
    ----------------------------------------------- */
    const reviewForm      = document.getElementById('review-form');
    const reviewSubmitBtn = document.getElementById('review-submit-btn');
    const reviewSuccessEl = document.getElementById('review-success-msg');
    const reviewErrorEl   = document.getElementById('review-error-msg');
    const reviewRatingIn  = document.getElementById('review-rating');
    const reviewStars     = document.querySelectorAll('.review-star');

    let selectedRating = 5;

    // ── Star interactivity ──
    reviewStars.forEach(star => {
        star.addEventListener('click', () => {
            selectedRating = parseInt(star.dataset.val, 10);
            if (reviewRatingIn) reviewRatingIn.value = selectedRating;
            reviewStars.forEach((s, i) => s.classList.toggle('active', i < selectedRating));
        });
        star.addEventListener('mouseenter', () => {
            const hv = parseInt(star.dataset.val, 10);
            reviewStars.forEach((s, i) => s.classList.toggle('active', i < hv));
        });
        star.addEventListener('mouseleave', () => {
            reviewStars.forEach((s, i) => s.classList.toggle('active', i < selectedRating));
        });
    });

    // ── Form submit ──
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name     = (document.getElementById('review-name')     || {}).value?.trim() || '';
            const location = (document.getElementById('review-location') || {}).value?.trim() || '';
            const service  = (document.getElementById('review-service')  || {}).value || '';
            const quote    = (document.getElementById('review-quote')    || {}).value?.trim() || '';
            const rating   = parseInt(reviewRatingIn ? reviewRatingIn.value : 5, 10);

            // Client-side validation
            if (!name || !quote || quote.length < 20) {
                if (reviewErrorEl) {
                    reviewErrorEl.textContent = !name
                        ? 'Please enter your full name.'
                        : 'Your review must be at least 20 characters.';
                    reviewErrorEl.style.display = 'block';
                }
                return;
            }
            if (reviewErrorEl) reviewErrorEl.style.display = 'none';

            reviewSubmitBtn.textContent = 'Submitting…';
            reviewSubmitBtn.disabled    = true;

            try {
                const res  = await fetch(`${API_BASE}/api/testimonials/submit/`, {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify({ name, location, service, quote, rating }),
                });
                const data = await res.json();

                if (res.ok && data.success) {
                    reviewForm.reset();
                    selectedRating = 5;
                    reviewStars.forEach((s, i) => s.classList.toggle('active', i < 5));
                    if (reviewRatingIn) reviewRatingIn.value = 5;
                    if (reviewSuccessEl) {
                        reviewSuccessEl.style.display = 'block';
                        setTimeout(() => { reviewSuccessEl.style.display = 'none'; }, 7000);
                    }
                } else {
                    if (reviewErrorEl) {
                        reviewErrorEl.textContent = data.error || 'Something went wrong. Please try again.';
                        reviewErrorEl.style.display = 'block';
                    }
                }
            } catch (_) {
                if (reviewErrorEl) {
                    reviewErrorEl.textContent = 'Could not connect to server. Please try again.';
                    reviewErrorEl.style.display = 'block';
                }
            } finally {
                reviewSubmitBtn.textContent = 'Submit My Review';
                reviewSubmitBtn.disabled    = false;
            }
        });
    }

})(); // END IIFE
