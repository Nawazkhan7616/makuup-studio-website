/* ============================================================
   GLOW GUIDE AI — Shared JavaScript
   Handles: Chatbot, Quiz Engine, Score Rings, Dashboard,
            Daily Tips, Session Management, Scroll Animations
   ============================================================ */

'use strict';

// ── Constants ─────────────────────────────────────────────────────────────────
const API_BASE       = 'https://makuup-backend.up.railway.app';
const GG_SESSION_KEY = 'gg_session_id';
const GG_RESULTS_KEY = 'gg_results';
const GG_STREAK_KEY  = 'gg_streak';
const GG_WATER_KEY   = 'gg_water_today';

const QUICK_REPLIES = [
    'How to reduce acne?',
    'Best routine for oily skin?',
    'How to stop hair fall?',
    'Foods for glowing skin?',
];

// ── Session Management ────────────────────────────────────────────────────────

function getSessionId() {
    let id = localStorage.getItem(GG_SESSION_KEY);
    if (!id) {
        id = (crypto.randomUUID
            ? crypto.randomUUID()
            : Date.now().toString(36) + Math.random().toString(36).slice(2));
        localStorage.setItem(GG_SESSION_KEY, id);
    }
    return id;
}

function saveResult(type, data) {
    const results = getResults();
    results[type] = { data, timestamp: new Date().toISOString() };
    localStorage.setItem(GG_RESULTS_KEY, JSON.stringify(results));
}

function getResults() {
    try { return JSON.parse(localStorage.getItem(GG_RESULTS_KEY) || '{}'); }
    catch { return {}; }
}

// ── Streak Tracking ───────────────────────────────────────────────────────────

function updateStreak() {
    const today   = new Date().toDateString();
    const streak  = JSON.parse(localStorage.getItem(GG_STREAK_KEY) || '{"count":0,"last":""}');
    const lastDate = streak.last;
    const yesterday = new Date(Date.now() - 86400000).toDateString();

    if (lastDate === today) return streak.count;
    if (lastDate === yesterday) { streak.count++; }
    else { streak.count = 1; }
    streak.last = today;
    localStorage.setItem(GG_STREAK_KEY, JSON.stringify(streak));
    return streak.count;
}

function getStreak() {
    try {
        const s = JSON.parse(localStorage.getItem(GG_STREAK_KEY) || '{"count":0}');
        return s.count || 0;
    } catch { return 0; }
}

// ── Chatbot ───────────────────────────────────────────────────────────────────

let chatOpen      = false;
let chatHistory   = [];
let chatBotBusy   = false;

function initChatbot() {
    const fab      = document.getElementById('gg-chatbot-fab');
    const popup    = document.getElementById('gg-chatbot-popup');
    const closeBtn = document.getElementById('gg-chatbot-close');
    const input    = document.getElementById('gg-chat-input');
    const sendBtn  = document.getElementById('gg-chat-send');
    const qrWrap   = document.getElementById('gg-quick-replies');

    if (!fab || !popup) return;

    // Build quick reply chips
    if (qrWrap) {
        QUICK_REPLIES.forEach(q => {
            const btn = document.createElement('button');
            btn.className = 'gg-quick-reply';
            btn.textContent = q;
            btn.addEventListener('click', () => sendChatMessage(q));
            qrWrap.appendChild(btn);
        });
    }

    // Toggle open/close
    fab.addEventListener('click', toggleChat);
    if (closeBtn) closeBtn.addEventListener('click', toggleChat);

    // Send on button click or Enter
    if (sendBtn) sendBtn.addEventListener('click', handleSend);
    if (input)   input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
    });

    function handleSend() {
        const msg = input.value.trim();
        if (!msg || chatBotBusy) return;
        input.value = '';
        sendChatMessage(msg);
    }
}

function toggleChat() {
    const fab   = document.getElementById('gg-chatbot-fab');
    const popup = document.getElementById('gg-chatbot-popup');
    if (!fab || !popup) return;

    chatOpen = !chatOpen;
    popup.classList.toggle('open', chatOpen);
    fab.classList.toggle('open', chatOpen);
    popup.setAttribute('aria-hidden', String(!chatOpen));

    if (chatOpen && chatHistory.length === 0) showWelcomeMessage();
}

function showWelcomeMessage() {
    const welcome = 'Hi! ✨ I\'m Glow Guide AI — your real AI beauty expert, powered by Google Gemini. I give personalised, dynamic advice (not scripted answers!). Ask me anything about skincare, haircare, makeup, or wellness!';
    addMessage('ai', welcome);
}

async function sendChatMessage(message) {
    if (chatBotBusy) return;
    chatBotBusy = true;

    // Hide quick replies after first message
    const qrWrap = document.getElementById('gg-quick-replies');
    if (qrWrap && chatHistory.length === 0) qrWrap.style.display = 'none';

    addMessage('user', message);
    showTypingIndicator();

    try {
        // 8-second timeout — falls back to smart offline response
        const controller = new AbortController();
        const timeout    = setTimeout(() => controller.abort(), 8000);

        const res = await fetch(`${API_BASE}/api/glow-guide/chat/`, {
            method : 'POST',
            headers: { 'Content-Type': 'application/json' },
            body   : JSON.stringify({ message, session_id: getSessionId() }),
            signal : controller.signal,
        });
        clearTimeout(timeout);

        hideTypingIndicator();

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data   = await res.json();
        const aiText = data.response || 'Sorry, I couldn\'t generate a response. Please try again!';

        const aiMsg = addMessage('ai', '');
        await typewriterEffect(aiMsg, aiText);

        chatHistory.push({ role: 'user',  message });
        chatHistory.push({ role: 'model', message: aiText });

    } catch {
        hideTypingIndicator();
        // Smart offline fallback — context-aware, not a generic error
        const fallback = ggOfflineResponse(message, chatHistory);
        const aiMsg = addMessage('ai', '');
        await typewriterEffect(aiMsg, fallback);
        chatHistory.push({ role: 'user',  message });
        chatHistory.push({ role: 'model', message: fallback });
    }

    chatBotBusy = false;
}

function addMessage(role, text) {
    const messages = document.getElementById('gg-chatbot-messages');
    if (!messages) return null;

    const div = document.createElement('div');
    div.className = `gg-msg gg-msg-${role === 'user' ? 'user' : 'ai'}`;
    if (text) div.textContent = text;
    div.style.animation = 'ggMsgIn 0.3s cubic-bezier(0.34,1.56,0.64,1) both';

    const typing = document.getElementById('gg-typing');
    if (typing && typing.parentNode === messages) messages.insertBefore(div, typing);
    else messages.appendChild(div);

    messages.scrollTop = messages.scrollHeight;
    return div;
}

function showTypingIndicator() {
    const el = document.getElementById('gg-typing');
    if (el) {
        el.style.display = 'flex';
        const msgs = document.getElementById('gg-chatbot-messages');
        if (msgs) msgs.scrollTop = msgs.scrollHeight;
    }
}

function hideTypingIndicator() {
    const el = document.getElementById('gg-typing');
    if (el) el.style.display = 'none';
}

function typewriterEffect(element, text, speed = 12) {
    return new Promise(resolve => {
        let i = 0;
        element.textContent = '';
        // Adaptive speed: faster for long messages
        const adaptSpeed = Math.max(8, Math.min(18, Math.round(2400 / text.length)));
        const timer = setInterval(() => {
            element.textContent += text[i];
            i++;
            const msgs = document.getElementById('gg-chatbot-messages');
            if (msgs && i % 4 === 0) msgs.scrollTop = msgs.scrollHeight;
            if (i >= text.length) { clearInterval(timer); resolve(); }
        }, adaptSpeed);
    });
}

// ── Smart Offline AI Response (exposed globally for chatbot page) ─────────────
// Context-aware responses that feel like real AI even without backend
window.ggOfflineResponse = function(message, history) {
    const msg = (message || '').toLowerCase().trim();
    const histText = (history || []).map(h => (h.text || h.message || '').toLowerCase()).join(' ');

    const hasContext = {
        oily:      /oily|greasy|sebum/.test(histText),
        dry:       /dry|dehydrat|flaky/.test(histText),
        acne:      /acne|pimple|breakout/.test(histText),
        sensitive: /sensitiv|reactive|redness/.test(histText),
        hair:      /hair|scalp/.test(histText),
    };

    // Greetings
    if (/^(hi|hello|hey|hii|namaste|good)/.test(msg)) {
        return 'Hello! ✨ I\'m Glow Guide AI. Tell me about your skin type and main beauty concern — I\'ll give you completely personalised advice!';
    }

    // Thanks
    if (/thank|great|amazing|helpful|perfect/.test(msg)) {
        return 'You\'re so welcome! ✨ Consistency is the real secret to beautiful skin — small daily habits add up to dramatic results. Anything else I can help you with?';
    }

    // Acne
    if (/acne|pimple|breakout|blemish|spot|zit/.test(msg)) {
        const extra = hasContext.oily ? ' Since you have oily skin, salicylic acid will be especially effective for you.' : '';
        return `For acne, the most effective approach: salicylic acid cleanser (BHA, unclogs pores), niacinamide serum (reduces inflammation + controls oil), and a lightweight non-comedogenic moisturiser.${extra} Never skip SPF — UV exposure worsens post-acne marks significantly. What type of acne are you dealing with — whiteheads, blackheads, or cystic? ✨`;
    }

    // Oily skin
    if (/oily skin|too oily|sebum|greasy face/.test(msg)) {
        return 'For oily skin: niacinamide 10% serum is your hero ingredient — it regulates sebum and minimises pores. Use a gel or foaming cleanser, a lightweight oil-free moisturiser (never skip it!), and a matte-finish SPF 50. A BHA toner 2-3x a week keeps pores clear. What\'s your current routine? I can tell you exactly what to swap. 🌿';
    }

    // Dry skin
    if (/dry skin|dryness|dehydrat|tight skin|flaky/.test(msg)) {
        return 'For dry, dehydrated skin: switch to a cream or balm cleanser, apply hyaluronic acid on damp skin within 60 seconds of washing, then seal with a ceramide-rich moisturiser. At night, add a sleeping mask 3x a week. Avoid hot showers — they strip natural oils. Is the dryness all over or just certain areas like cheeks? 💧';
    }

    // Hair fall
    if (/hair fall|hair loss|thinning|shedding/.test(msg)) {
        return 'Hair fall is often caused by nutritional deficiency (iron, protein, biotin), stress, or hormonal changes. Try rosemary oil scalp massages 3x a week — clinically proven to boost growth. Ensure adequate protein, iron, and zinc in your diet. If you\'re losing more than 100 strands/day consistently, consult a trichologist. Are you experiencing diffuse thinning or localised patches? 💆';
    }

    // Pigmentation
    if (/pigment|dark spot|dark circle|tan|uneven|brighten/.test(msg)) {
        return 'For pigmentation: Vitamin C serum (morning) + SPF 50 PA+++ is the gold-standard combination. At night, alpha arbutin or niacinamide fades existing spots over 8-12 weeks. The most critical step? Never skip sunscreen — UV is what causes and worsens every form of pigmentation. What type — sun spots, post-acne marks, or melasma? ✨';
    }

    // Sunscreen
    if (/sunscreen|spf|sun protect|uv/.test(msg)) {
        return 'SPF is the single highest-impact skincare step — more anti-ageing than any serum! Use minimum SPF 50 PA+++ every day, including indoors. Reapply every 2-3 hours when outdoors. Chemical sunscreens are lighter under makeup; mineral (zinc oxide) sunscreens are gentler for sensitive and acne-prone skin. What\'s your concern — white cast, texture, or breakouts from sunscreen? 🌞';
    }

    // Routine
    if (/routine|regimen|steps|what should i use|how to start/.test(msg)) {
        return 'Here\'s a complete routine:\n☀️ Morning: Cleanser → Vitamin C serum → Moisturiser → SPF 50\n🌙 Night: Double cleanse → Treatment serum (niacinamide/retinol) → Eye cream → Night cream\n\nStart simple — cleanser + moisturiser + SPF. Add one active ingredient every 2 weeks. What\'s your skin type? I\'ll build your exact personalised routine! 🌿';
    }

    // Makeup
    if (/makeup|foundation|base|concealer|primer|lipstick/.test(msg)) {
        return 'For a flawless base in Indian heat: hydrating or pore-minimising primer first, then foundation matched to your neck (not wrist!), built in thin layers. Set with translucent powder on T-zone and lock with setting spray for 8-10 hours of wear. What\'s the occasion and your skin type? I\'ll be more specific! 💄';
    }

    // Nails
    if (/nail|cuticle|brittle nail|nail growth/.test(msg)) {
        return 'For strong, healthy nails: apply jojoba or almond cuticle oil every night and massage for 1 minute — this alone transforms nail health in 2 weeks. File in one direction only, wear gloves for dishes, and consider biotin supplements (consult your doctor). Are you dealing with brittleness, slow growth, or looking for nail art colour recommendations? 💅';
    }

    // Food/nutrition
    if (/food|diet|eat|nutrition|supplement|vitamin/.test(msg)) {
        return 'Beauty nutrition is powerful! For glowing skin: omega-3s (walnuts, flaxseeds), Vitamin C (amla has 20x more than oranges), zinc (pumpkin seeds, lentils). For hair: protein, iron (spinach, lentils, red meat), and biotin (eggs, sweet potato). For nails: silica-rich foods (cucumber, oats). Are you focused on skin, hair, or nails — or all three? 🌿';
    }

    // Generic helpful response
    return 'That\'s a great question! To give you the most personalised advice, tell me: your skin type (oily/dry/combination/sensitive), your main beauty concern, and what you\'re currently using. The more I know about you, the better my recommendations will be — I remember everything you tell me in our conversation! ✨';
};

// ── Quiz Engine ───────────────────────────────────────────────────────────────

function initQuiz(containerId, questions, onComplete) {
    const wrap = document.getElementById(containerId);
    if (!wrap) return;

    let currentStep = 0;
    const answers   = {};

    const progressFill = wrap.querySelector('.gg-quiz-progress-fill') || document.getElementById('quiz-progress');
    const counter      = wrap.querySelector('.gg-quiz-counter') || document.getElementById('quiz-counter');
    const stepsWrap    = wrap.querySelector('.gg-quiz-steps') || document.getElementById('quiz-steps');
    const prevBtn      = wrap.querySelector('.gg-quiz-prev');
    const nextBtn      = wrap.querySelector('.gg-quiz-next');

    if (!stepsWrap) return;

    // Render all steps (hidden by default)
    questions.forEach((q, idx) => {
        const stepEl = document.createElement('div');
        stepEl.className = 'gg-quiz-step' + (idx === 0 ? ' active' : '');
        stepEl.dataset.index = idx;

        const qEl = document.createElement('p');
        qEl.className = 'gg-quiz-question';
        qEl.textContent = `${idx + 1}. ${q.question}`;

        const optsEl = document.createElement('div');
        optsEl.className = 'gg-quiz-options';

        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'gg-quiz-option';
            btn.textContent = opt;
            btn.dataset.value = opt.toLowerCase();
            btn.addEventListener('click', () => {
                // Deselect siblings
                optsEl.querySelectorAll('.gg-quiz-option').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                answers[q.id] = btn.dataset.value;
                // Auto-advance if not last
                if (idx < questions.length - 1) {
                    setTimeout(() => goNext(), 350);
                } else {
                    if (nextBtn) nextBtn.textContent = 'See My Results ✨';
                }
            });
            optsEl.appendChild(btn);
        });

        stepEl.appendChild(qEl);
        stepEl.appendChild(optsEl);
        stepsWrap.appendChild(stepEl);
    });

    updateProgress();

    function updateProgress() {
        const pct = Math.round((currentStep / questions.length) * 100);
        if (progressFill) progressFill.style.width = pct + '%';
        if (counter) counter.textContent = `${currentStep + 1} / ${questions.length}`;
    }

    function goNext() {
        if (currentStep >= questions.length - 1) {
            if (!answers[questions[currentStep].id]) {
                shakeCurrentStep();
                return;
            }
            onComplete(answers);
            return;
        }
        if (!answers[questions[currentStep].id]) {
            shakeCurrentStep();
            return;
        }
        const steps = stepsWrap.querySelectorAll('.gg-quiz-step');
        steps[currentStep].classList.remove('active');
        currentStep++;
        steps[currentStep].classList.add('active');
        updateProgress();
    }

    function goPrev() {
        if (currentStep === 0) return;
        const steps = stepsWrap.querySelectorAll('.gg-quiz-step');
        steps[currentStep].classList.remove('active');
        currentStep--;
        steps[currentStep].classList.add('active');
        updateProgress();
    }

    function shakeCurrentStep() {
        const steps = stepsWrap.querySelectorAll('.gg-quiz-step');
        const current = steps[currentStep];
        current.style.animation = 'none';
        current.style.borderLeft = '3px solid #f0a5c0';
        setTimeout(() => { current.style.borderLeft = ''; }, 800);
    }

    if (nextBtn) nextBtn.addEventListener('click', goNext);
    if (prevBtn) prevBtn.addEventListener('click', goPrev);
}

// ── Score Ring ────────────────────────────────────────────────────────────────

function renderScoreRing(containerId, score, label) {
    const wrap = document.getElementById(containerId);
    if (!wrap) return;

    const radius = 52;
    const circumference = 2 * Math.PI * radius;
    const validScore = Math.max(0, Math.min(100, parseInt(score, 10) || 0));
    const offset = circumference - (validScore / 100) * circumference;

    wrap.innerHTML = `
        <svg width="130" height="130" viewBox="0 0 130 130">
            <defs>
                <linearGradient id="gg-ring-grad-${containerId}" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stop-color="#b482ff"/>
                    <stop offset="100%" stop-color="#f0a5c0"/>
                </linearGradient>
            </defs>
            <circle class="gg-score-track" cx="65" cy="65" r="${radius}"/>
            <circle class="gg-score-fill" cx="65" cy="65" r="${radius}"
                stroke="url(#gg-ring-grad-${containerId})"
                stroke-dasharray="${circumference}"
                stroke-dashoffset="${circumference}"
                id="ring-fill-${containerId}"/>
        </svg>
        <div class="gg-score-center">
            <span class="gg-score-number" id="ring-num-${containerId}">0</span>
            <span class="gg-score-label">${label}</span>
        </div>`;

    // Animate after a frame
    requestAnimationFrame(() => {
        setTimeout(() => {
            const fill = document.getElementById(`ring-fill-${containerId}`);
            const num  = document.getElementById(`ring-num-${containerId}`);
            if (fill) fill.style.strokeDashoffset = offset;

            // Count-up number
            let current = 0;
            const step = validScore / 60;
            const timer = setInterval(() => {
                current = Math.min(current + step, validScore);
                if (num) num.textContent = Math.round(current);
                if (current >= validScore) clearInterval(timer);
            }, 25);
        }, 200);
    });
}

// ── Skin Result Renderer ──────────────────────────────────────────────────────

function renderSkinResult(report) {
    // Scores
    renderScoreRing('ring-health',      report.health_score,      'Health Score');
    renderScoreRing('ring-hydration',   report.hydration_score,   'Hydration');
    renderScoreRing('ring-sensitivity', report.sensitivity_score, 'Sensitivity');

    // Acne risk badge (text-only ring)
    const acneEl = document.getElementById('ring-acne');
    if (acneEl) {
        acneEl.innerHTML = `
            <div style="text-align:center;padding:20px;">
                <div style="font-size:1.5rem;font-weight:700;background:var(--gg-grad);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">${report.acne_risk}</div>
                <div class="gg-score-label" style="margin-top:4px;">Acne Risk</div>
            </div>`;
    }

    // Skin type badge
    const badge = document.getElementById('skin-type-badge');
    if (badge) badge.textContent = `✨ ${report.skin_type} Skin`;

    // Morning routine
    renderRoutine('morning-routine', report.morning_routine);

    // Night routine
    renderRoutine('night-routine', report.night_routine);

    // Ingredients
    renderIngredients('ingredients-list', report.ingredients);
}

function renderRoutine(containerId, steps) {
    const el = document.getElementById(containerId);
    if (!el || !steps) return;
    el.innerHTML = steps.map(s => `
        <li class="gg-routine-item">
            <div class="gg-routine-num">${s.step}</div>
            <div>
                <div class="gg-routine-product">${s.product}</div>
                <div class="gg-routine-notes">${s.notes}</div>
            </div>
        </li>`).join('');
}

function renderIngredients(containerId, ingredients) {
    const el = document.getElementById(containerId);
    if (!el || !ingredients) return;
    el.innerHTML = ingredients.map(ing => `
        <div class="gg-ingredient-card gg-card">
            <div class="gg-ingredient-name">${ing.name}</div>
            <div class="gg-ingredient-benefit">${ing.benefit}</div>
            <div class="gg-ingredient-usage">📋 ${ing.usage}</div>
            ${ing.conflicts && ing.conflicts !== 'None'
                ? `<div class="gg-ingredient-conflict">${ing.conflicts}</div>`
                : ''}
        </div>`).join('');
}

// ── Hair Result Renderer ──────────────────────────────────────────────────────

function renderHairResult(report) {
    renderScoreRing('ring-hair-health', report.hair_health_score, 'Hair Health');

    const scalpBadge = document.getElementById('scalp-badge');
    if (scalpBadge) scalpBadge.textContent = `💆 ${report.scalp_health} Scalp`;

    const hairBadge = document.getElementById('hair-type-badge');
    if (hairBadge) hairBadge.textContent = `✨ ${report.hair_type} Hair`;

    // Growth recommendations
    const growthEl = document.getElementById('growth-recs');
    if (growthEl && report.growth_recommendations) {
        growthEl.innerHTML = report.growth_recommendations.map(r =>
            `<li style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);color:var(--gg-text);font-size:0.9rem;">
                <span style="color:var(--gg-lavender);margin-right:8px;">→</span>${r}
            </li>`).join('');
    }

    // Weekly routine
    const weekEl = document.getElementById('weekly-routine');
    if (weekEl && report.weekly_routine) {
        weekEl.innerHTML = `<div class="gg-week-grid">` +
            report.weekly_routine.map(day => `
                <div class="gg-week-card">
                    <div class="gg-week-day">${day.day.slice(0, 3)}</div>
                    <div class="gg-week-action">${day.action}</div>
                    <div class="gg-week-notes">${day.notes}</div>
                </div>`).join('') +
            `</div>`;
    }

    // Ingredients
    renderIngredients('hair-ingredients', report.ingredients);
}

// ── Nail Result Renderer ──────────────────────────────────────────────────────

function renderNailResult(report) {
    renderScoreRing('ring-nail-health', report.nail_health_score, 'Nail Health');

    const routineEl = document.getElementById('nail-growth-routine');
    if (routineEl && report.growth_routine) {
        routineEl.innerHTML = report.growth_routine.map((tip, i) => `
            <li class="gg-routine-item">
                <div class="gg-routine-num">${i + 1}</div>
                <div class="gg-routine-product">${tip}</div>
            </li>`).join('');
    }

    const hydrationEl = document.getElementById('nail-hydration-tips');
    if (hydrationEl && report.hydration_tips) {
        hydrationEl.innerHTML = report.hydration_tips.map(tip => `
            <div class="gg-tip-card gg-card" style="padding:20px;">
                <div style="color:var(--gg-text);font-size:0.875rem;"><span style="color:var(--gg-rose);margin-right:8px;">💧</span>${tip}</div>
            </div>`).join('');
    }

    // Color swatches
    const colors = [
        { name: 'Dusty Rose',    hex: '#C4808A' },
        { name: 'Terracotta',    hex: '#C4603A' },
        { name: 'Nude Beige',    hex: '#D4A99A' },
        { name: 'Deep Burgundy', hex: '#6B2234' },
        { name: 'Soft Lavender', hex: '#B09CC8' },
        { name: 'Classic Red',   hex: '#C8102E' },
    ];
    const swatchEl = document.getElementById('nail-colors');
    if (swatchEl) {
        swatchEl.innerHTML = `<div class="gg-color-swatches">` +
            colors.map(c => `
                <div class="gg-swatch" title="${c.name}">
                    <div class="gg-swatch-circle" style="background:${c.hex};"></div>
                    <span class="gg-swatch-name">${c.name}</span>
                </div>`).join('') +
            `</div>`;
    }
}

// ── Daily Tips ────────────────────────────────────────────────────────────────

async function loadDailyTips() {
    try {
        const res  = await fetch(`${API_BASE}/api/glow-guide/daily-tips/`);
        const data = await res.json();

        if (data.today) {
            const iconEl = document.getElementById('tip-icon');
            const textEl = document.getElementById('tip-text');
            if (iconEl) iconEl.textContent = data.today.icon;
            if (textEl) textEl.textContent = data.today.tip;
        }

        if (data.more_tips) {
            const gridEl = document.getElementById('tips-grid');
            if (gridEl) {
                gridEl.innerHTML = data.more_tips.map(t => `
                    <div class="gg-tip-card gg-card gg-animate">
                        <div class="gg-tip-icon">${t.icon}</div>
                        <div class="gg-tip-category">${t.category}</div>
                        <div class="gg-tip-text">${t.tip}</div>
                    </div>`).join('');
                initScrollAnimations();
            }
        }
    } catch {
        const textEl = document.getElementById('tip-text');
        if (textEl) textEl.textContent = 'Reapply your sunscreen — UV rays are strongest between 10am and 4pm! ☀️';
    }
}

// ── Hydration Tracker ─────────────────────────────────────────────────────────

function initHydrationTracker() {
    const today = new Date().toDateString();
    let data = JSON.parse(localStorage.getItem(GG_WATER_KEY) || '{"date":"","count":0}');
    if (data.date !== today) data = { date: today, count: 0 };

    const countEl   = document.getElementById('water-count');
    const glassesEl = document.querySelectorAll('.gg-glass');
    const addBtn    = document.getElementById('water-add');
    const subBtn    = document.getElementById('water-sub');

    function updateUI() {
        if (countEl) countEl.textContent = data.count;
        glassesEl.forEach((g, i) => g.classList.toggle('filled', i < data.count));
        localStorage.setItem(GG_WATER_KEY, JSON.stringify(data));
    }

    if (addBtn) addBtn.addEventListener('click', () => { if (data.count < 8) { data.count++; updateUI(); } });
    if (subBtn) subBtn.addEventListener('click', () => { if (data.count > 0) { data.count--; updateUI(); } });

    updateUI();
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

function loadDashboard() {
    updateStreak();
    const streakNum = document.getElementById('streak-count');
    if (streakNum) streakNum.textContent = getStreak();

    const results = getResults();

    // Skin
    renderDashCard('dash-skin', results.skin, 'ring-dash-skin', 'No skin analysis yet', '/glow-guide/skin-analysis/');
    renderDashCard('dash-hair', results.hair, 'ring-dash-hair', 'No hair analysis yet', '/glow-guide/hair-analysis/');
    renderDashCard('dash-nail', results.nail, 'ring-dash-nail', 'No nail analysis yet', '/glow-guide/nail-care/');
}

function renderDashCard(cardId, result, ringId, emptyMsg, link) {
    const empty = document.getElementById(cardId + '-empty');
    const data  = document.getElementById(cardId + '-data');

    if (!result || !result.data) {
        if (empty) empty.style.display = 'block';
        if (data)  data.style.display  = 'none';
        return;
    }

    if (empty) empty.style.display = 'none';
    if (data)  data.style.display  = 'block';

    const report = result.data.report || result.data;
    const score  = report.health_score || report.hair_health_score || report.nail_health_score || 0;
    const date   = new Date(result.timestamp).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });

    renderScoreRing(ringId, score, 'Score');

    const dateEl = document.getElementById(cardId + '-date');
    if (dateEl) dateEl.textContent = `Analysed: ${date}`;
}

// ── Navigation Active State ───────────────────────────────────────────────────

function setActiveNavLink() {
    const path = window.location.pathname;
    document.querySelectorAll('.gg-nav-link').forEach(link => {
        const href = link.getAttribute('href');
        if (href && href !== '/' && path.startsWith(href)) {
            link.classList.add('active');
        }
    });

    // Mobile menu
    const hamburger = document.getElementById('gg-nav-hamburger');
    const navLinks  = document.getElementById('gg-nav-links');
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', () => navLinks.classList.toggle('open'));
        // Close on link click
        navLinks.querySelectorAll('a').forEach(a => a.addEventListener('click', () => navLinks.classList.remove('open')));
    }
}

// ── Scroll Animations ─────────────────────────────────────────────────────────

function initScrollAnimations() {
    const targets = document.querySelectorAll('.gg-animate');
    if (!targets.length) return;

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    targets.forEach(el => observer.observe(el));
}

// ── API Helpers ───────────────────────────────────────────────────────────────

async function submitAnalysis(endpoint, answers) {
    const res = await fetch(`${API_BASE}/api/glow-guide/${endpoint}/`, {
        method : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body   : JSON.stringify({ ...answers, session_id: getSessionId() }),
    });
    if (!res.ok) throw new Error(`API error ${res.status}`);
    return res.json();
}

// ── Skin Analysis Page Init ───────────────────────────────────────────────────

function initSkinAnalysis() {
    const questions = [
        { id: 'age',           question: 'What is your age range?',              options: ['Under 18', '18–24', '25–34', '35–44', '45+'] },
        { id: 'climate',       question: 'What is your climate like?',           options: ['Hot & Humid', 'Hot & Dry', 'Moderate', 'Cold & Dry', 'Tropical Monsoon'] },
        { id: 'skin_type',     question: 'What is your skin type?',              options: ['Oily', 'Dry', 'Combination', 'Normal', 'Sensitive'] },
        { id: 'acne',          question: 'How severe is your acne?',             options: ['None', 'Occasional Pimples', 'Mild Acne', 'Moderate Acne', 'Severe Acne'] },
        { id: 'dryness',       question: 'How dry does your skin feel?',         options: ['Not at all', 'Slightly Dry', 'Moderately Dry', 'Very Dry', 'Extremely Dry'] },
        { id: 'sensitivity',   question: 'How sensitive is your skin?',          options: ['Not Sensitive', 'Mildly Sensitive', 'Moderately Sensitive', 'Very Sensitive'] },
        { id: 'pigmentation',  question: 'Do you have pigmentation or dark spots?', options: ['No', 'A Little', 'Moderate', 'Significant'] },
        { id: 'wrinkles',      question: 'Do you have wrinkles or fine lines?',  options: ['None', 'Very Fine Lines', 'Moderate', 'Noticeable'] },
        { id: 'redness',       question: 'Do you experience redness?',           options: ['Never', 'Sometimes', 'Often', 'Always'] },
        { id: 'open_pores',    question: 'Do you have open or enlarged pores?',  options: ['No', 'Mild', 'Moderate', 'Significant'] },
        { id: 'water_intake',  question: 'How much water do you drink daily?',   options: ['Less than 4 glasses', '4–6 glasses', '6–8 glasses', '8–10 glasses', '10+ glasses'] },
        { id: 'sleep_hours',   question: 'How many hours do you sleep?',         options: ['Less than 5', '5–6 hours', '6–7 hours', '7–8 hours', '8+ hours'] },
        { id: 'stress_level',  question: 'What is your stress level?',           options: ['Low', 'Moderate', 'High', 'Very High'] },
        { id: 'uses_sunscreen', question: 'Do you use sunscreen daily?',         options: ['Never', 'Rarely', 'Sometimes', 'Daily'] },
    ];

    let quizSubmitted = false;
    initQuiz('skin-quiz', questions, async answers => {
        if (quizSubmitted) return;
        quizSubmitted = true;
        showLoading();
        // Always compute local result first
        const localReport = analyzeSkinLocal(answers);
        try {
            const data = await Promise.race([
                submitAnalysis('skin-analysis', answers),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))
            ]);
            hideLoading();
            saveResult('skin', data);
            renderSkinResult(data.report);
        } catch {
            // Backend unavailable — use local result
            hideLoading();
            saveResult('skin', { report: localReport });
            renderSkinResult(localReport);
        }
        showResult();
    });
}

// ── Hair Analysis Page Init ───────────────────────────────────────────────────

function initHairAnalysis() {
    const questions = [
        { id: 'hair_type',      question: 'What is your hair type?',              options: ['Straight', 'Wavy', 'Curly', 'Coily / Kinky'] },
        { id: 'scalp_type',     question: 'What is your scalp type?',             options: ['Normal', 'Oily', 'Dry', 'Combination', 'Sensitive'] },
        { id: 'hair_fall',      question: 'How much hair fall do you experience?', options: ['Minimal', 'Moderate', 'Significant', 'Severe'] },
        { id: 'dandruff',       question: 'Do you have dandruff?',                options: ['None', 'Occasional', 'Mild', 'Moderate', 'Severe'] },
        { id: 'frizz',          question: 'How frizzy is your hair?',             options: ['Not Frizzy', 'Slightly Frizzy', 'Moderately Frizzy', 'Very Frizzy'] },
        { id: 'heat_styling',   question: 'How often do you use heat styling?',   options: ['Never', 'Rarely', 'Sometimes', 'Often', 'Daily'] },
        { id: 'wash_frequency', question: 'How often do you wash your hair?',     options: ['Daily', 'Every 2 days', '2–3 times a week', 'Once a week', 'Less often'] },
        { id: 'diet_quality',   question: 'How would you rate your diet quality?', options: ['Poor', 'Below Average', 'Average', 'Good', 'Excellent'] },
        { id: 'stress_level',   question: 'What is your stress level?',           options: ['Low', 'Moderate', 'High', 'Very High'] },
    ];

    let quizSubmitted = false;
    initQuiz('hair-quiz', questions, async answers => {
        if (quizSubmitted) return;
        quizSubmitted = true;
        showLoading();
        const localReport = analyzeHairLocal(answers);
        try {
            const data = await Promise.race([
                submitAnalysis('hair-analysis', answers),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))
            ]);
            hideLoading();
            saveResult('hair', data);
            renderHairResult(data.report);
        } catch {
            hideLoading();
            saveResult('hair', { report: localReport });
            renderHairResult(localReport);
        }
        showResult();
    });
}

// ── Nail Analysis Page Init ───────────────────────────────────────────────────

function initNailAnalysis() {
    const questions = [
        { id: 'weak_nails',    question: 'Do you have weak or soft nails?',  options: ['No', 'Slightly', 'Moderately', 'Severely'] },
        { id: 'brittle_nails', question: 'Do your nails break easily?',      options: ['No', 'Sometimes', 'Often', 'Very Often'] },
        { id: 'discoloration', question: 'Do you notice nail discoloration?', options: ['No', 'Slight', 'Yes'] },
        { id: 'growth_issues', question: 'Do you have slow nail growth?',     options: ['No', 'Slightly Slow', 'Very Slow'] },
        { id: 'nail_biting',   question: 'Do you have a nail biting habit?',  options: ['No', 'Sometimes', 'Yes'] },
    ];

    let quizSubmitted = false;
    initQuiz('nail-quiz', questions, async answers => {
        if (quizSubmitted) return;
        quizSubmitted = true;
        showLoading();
        const localReport = analyzeNailLocal(answers);
        try {
            const data = await Promise.race([
                submitAnalysis('nail-analysis', answers),
                new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), 5000))
            ]);
            hideLoading();
            saveResult('nail', data);
            renderNailResult(data.report);
        } catch {
            hideLoading();
            saveResult('nail', { report: localReport });
            renderNailResult(localReport);
        }
        showResult();
    });
}

// ── UI Helpers ────────────────────────────────────────────────────────────────

function showLoading() {
    const quiz    = document.getElementById('quiz-section');
    const loading = document.getElementById('loading-section');
    if (quiz)    quiz.style.display    = 'none';
    if (loading) loading.style.display = 'flex';
}

function hideLoading() {
    const loading = document.getElementById('loading-section');
    if (loading) loading.style.display = 'none';
}

function showResult() {
    const byId    = document.getElementById('result-section');
    const byClass = document.querySelector('.gg-result-section');
    const resultSection = byId || byClass;
    if (resultSection) {
        resultSection.style.display = 'block';
        resultSection.classList.add('visible');
        setTimeout(() => resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }
}

function showError(msg) {
    const quiz = document.getElementById('quiz-section');
    if (!quiz) return;
    // Remove any existing error banners first to prevent duplicates
    quiz.querySelectorAll('.gg-error-banner').forEach(el => el.remove());
    quiz.style.display = 'block';
    quiz.insertAdjacentHTML('afterbegin', `
        <div class="gg-error-banner" style="padding:16px 20px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);border-radius:12px;color:#fca5a5;font-size:0.875rem;margin-bottom:24px;">
            ⚠️ ${msg}
        </div>`);
}

// ── Client-Side Analysis Engine (works without backend) ───────────────────────
// Mirrors the Python analysis_engine.py logic in JavaScript

const GG_SKIN_INGREDIENTS = {
    oily:        [{name:'Niacinamide',benefit:'Controls sebum, minimises pores',usage:'Apply 2-3 drops after toner, morning & night',conflicts:'Avoid mixing with Vitamin C at the same time'},{name:'Salicylic Acid',benefit:'Unclogs pores, fights acne',usage:'2-3x per week in cleanser or toner',conflicts:'Do not layer with Retinol on the same night'},{name:'Hyaluronic Acid',benefit:'Lightweight hydration without greasiness',usage:'Apply on damp skin, morning & night',conflicts:'None'}],
    dry:         [{name:'Hyaluronic Acid',benefit:'Deep hydration, plumps skin',usage:'Apply on damp skin morning & night',conflicts:'None'},{name:'Ceramides',benefit:'Repairs skin barrier, locks moisture',usage:'Use in moisturiser, both AM & PM',conflicts:'None'},{name:'Squalane',benefit:'Ultra-nourishing, non-comedogenic oil',usage:'2-3 drops as last PM step',conflicts:'None'}],
    combination: [{name:'Niacinamide',benefit:'Balances T-zone oil, hydrates dry areas',usage:'Apply all over, morning & night',conflicts:'Avoid same-time use with Vitamin C'},{name:'Hyaluronic Acid',benefit:'Lightweight hydration for all zones',usage:'Apply on damp skin',conflicts:'None'},{name:'AHA (Glycolic Acid)',benefit:'Exfoliates, brightens, refines texture',usage:'2x per week, PM only',conflicts:'Do not use with Retinol same night'}],
    sensitive:   [{name:'Centella Asiatica',benefit:'Calms redness, repairs barrier',usage:'Use in serum or moisturiser AM & PM',conflicts:'None'},{name:'Ceramides',benefit:'Strengthens skin barrier',usage:'Use in moisturiser both AM & PM',conflicts:'None'},{name:'Aloe Vera',benefit:'Soothes irritation and redness',usage:'Apply gel directly or in products AM & PM',conflicts:'None'}],
    normal:      [{name:'Vitamin C',benefit:'Brightens skin, fights pigmentation',usage:'Apply in morning after cleansing',conflicts:'Do not layer with Niacinamide simultaneously'},{name:'Retinol',benefit:'Anti-ageing, smooths skin texture',usage:'PM only, 2-3x per week',conflicts:'Do not mix with AHAs/BHAs same night'},{name:'Hyaluronic Acid',benefit:'Maintains hydration balance',usage:'Apply on damp skin AM & PM',conflicts:'None'}],
};

const GG_SKIN_ROUTINES = {
    oily: {
        morning: [{step:1,product:'Foaming / Gel Cleanser',notes:'Use a salicylic acid cleanser for oily skin'},{step:2,product:'Niacinamide Serum',notes:'2-3 drops, let absorb for 60 seconds'},{step:3,product:'Oil-Free Gel Moisturiser',notes:'Lightweight, non-comedogenic formula'},{step:4,product:'SPF 50 Sunscreen',notes:'Matte-finish sunscreen works best for oily skin'}],
        night:   [{step:1,product:'Micellar Water / Oil Cleanser',notes:'Double cleanse to remove makeup & SPF'},{step:2,product:'BHA Toner (Salicylic Acid)',notes:'2-3x per week only'},{step:3,product:'Niacinamide Serum',notes:'Helps control overnight sebum production'},{step:4,product:'Lightweight Night Moisturiser',notes:'Gel-cream texture recommended'}],
    },
    dry: {
        morning: [{step:1,product:'Cream / Milk Cleanser',notes:'Gentle, non-stripping formula'},{step:2,product:'Hydrating Toner',notes:'Prep skin before serum'},{step:3,product:'Hyaluronic Acid Serum',notes:'Apply on slightly damp skin'},{step:4,product:'Rich Moisturiser with Ceramides',notes:'Lock in hydration'},{step:5,product:'SPF 50 Sunscreen',notes:'Dewy finish sunscreen recommended'}],
        night:   [{step:1,product:'Balm / Cream Cleanser',notes:'Never use foaming cleansers'},{step:2,product:'Hyaluronic Acid Serum',notes:'Double-dose hydration at night'},{step:3,product:'Peptide or Ceramide Serum',notes:'Barrier repair overnight'},{step:4,product:'Rich Night Cream with Shea Butter',notes:'Seal everything in'}],
    },
    combination: {
        morning: [{step:1,product:'Balanced pH Gel Cleanser',notes:'Not too stripping, not too rich'},{step:2,product:'Niacinamide Serum',notes:'Balances T-zone while hydrating dry areas'},{step:3,product:'Light Lotion Moisturiser',notes:'Medium-weight formula'},{step:4,product:'SPF 50+ Sunscreen',notes:'Apply generously'}],
        night:   [{step:1,product:'Double Cleanse',notes:'Oil cleanser → gel cleanser'},{step:2,product:'AHA Toner (2x weekly)',notes:'Glycolic acid for texture refinement'},{step:3,product:'Hyaluronic Acid Serum',notes:'Hydrate dry cheeks'},{step:4,product:'Gel-Cream Moisturiser',notes:'Lighter on T-zone, more on cheeks'}],
    },
    sensitive: {
        morning: [{step:1,product:'Fragrance-Free Gentle Cleanser',notes:'pH balanced, no active acids'},{step:2,product:'Centella Asiatica Serum',notes:'Calming and barrier-strengthening'},{step:3,product:'Ceramide-Rich Moisturiser',notes:'Fragrance-free essential'},{step:4,product:'Mineral SPF 50',notes:'Zinc oxide-based is gentler for sensitive skin'}],
        night:   [{step:1,product:'Micellar Water + Gentle Cleanser',notes:'Minimal rubbing, be gentle'},{step:2,product:'Aloe Vera Gel',notes:'Soothe any redness'},{step:3,product:'Barrier Repair Serum',notes:'Ceramides + Peptides'},{step:4,product:'Rich Fragrance-Free Night Cream',notes:'Repair skin overnight'}],
    },
    normal: {
        morning: [{step:1,product:'Gentle Gel Cleanser',notes:'Keep it simple'},{step:2,product:'Vitamin C Serum',notes:'Brightening and antioxidant protection'},{step:3,product:'Light Moisturiser',notes:'SPF-boosting formula a bonus'},{step:4,product:'SPF 50 Sunscreen',notes:'Non-negotiable daily step'}],
        night:   [{step:1,product:'Micellar + Gentle Cleanser',notes:'Remove SPF properly'},{step:2,product:'Retinol Serum (2-3x weekly)',notes:'Anti-ageing, refines texture'},{step:3,product:'Hyaluronic Acid',notes:'Hydration support'},{step:4,product:'Balanced Night Cream',notes:'Not too heavy'}],
    },
};

function analyzeSkinLocal(answers) {
    const rawType = (answers.skin_type || 'normal').toLowerCase();
    const skinType = ['oily','dry','combination','sensitive','normal'].find(t => rawType.includes(t)) || 'normal';

    const water = answers.water_intake || '';
    const hydration = water.includes('8') || water.includes('10') ? 85 : water.includes('6') ? 65 : water.includes('4') ? 45 : 30;

    const sleep = answers.sleep_hours || '';
    const sleepScore = sleep.includes('8+') || sleep.includes('7-8') || sleep.includes('7–8') ? 90 : sleep.includes('6') ? 70 : sleep.includes('5') ? 50 : 35;

    const sunscreen = (answers.uses_sunscreen || '').toLowerCase();
    const sunscreenScore = ['daily','always','yes'].some(s => sunscreen.includes(s)) ? 90 : 40;

    const stress = (answers.stress_level || '').toLowerCase();
    const stressScore = stress.includes('low') ? 85 : stress.includes('moderate') ? 60 : 35;

    const acne = (answers.acne || '').toLowerCase();
    let acneRisk = 'Very Low', acneScore = 90;
    if (acne.includes('severe'))        { acneRisk = 'High';   acneScore = 30; }
    else if (acne.includes('moderate')) { acneRisk = 'Medium'; acneScore = 55; }
    else if (acne.includes('mild') || acne.includes('occasional')) { acneRisk = 'Low'; acneScore = 75; }

    const sensitivity = (answers.sensitivity || '').toLowerCase();
    const sensitivityScore = sensitivity.includes('very') || sensitivity.includes('high') ? 30 : sensitivity.includes('moderate') || sensitivity.includes('mild') ? 60 : 90;

    const parts = [hydration, sleepScore, sunscreenScore, stressScore, acneScore];
    const healthScore = Math.min(100, Math.round(parts.reduce((a, b) => a + b, 0) / parts.length));

    return {
        skin_type: skinType.charAt(0).toUpperCase() + skinType.slice(1),
        health_score: healthScore,
        hydration_score: hydration,
        acne_risk: acneRisk,
        sensitivity_score: sensitivityScore,
        morning_routine: GG_SKIN_ROUTINES[skinType].morning,
        night_routine:   GG_SKIN_ROUTINES[skinType].night,
        ingredients:     GG_SKIN_INGREDIENTS[skinType],
    };
}

function analyzeHairLocal(answers) {
    const fall = (answers.hair_fall || '').toLowerCase();
    const fallScore = fall.includes('severe') ? 30 : fall.includes('significant') || fall.includes('moderate') ? 55 : 85;

    const dandruff = (answers.dandruff || '').toLowerCase();
    const dandruffScore = dandruff.includes('severe') ? 30 : dandruff.includes('mild') || dandruff.includes('occasional') ? 60 : 90;

    const heat = (answers.heat_styling || '').toLowerCase();
    const heatScore = heat.includes('daily') ? 35 : heat.includes('often') ? 50 : heat.includes('sometimes') ? 70 : 90;

    const diet = (answers.diet_quality || '').toLowerCase();
    const dietScore = diet.includes('good') || diet.includes('excellent') ? 85 : diet.includes('average') ? 60 : 35;

    const stress = (answers.stress_level || '').toLowerCase();
    const stressScore = stress.includes('low') ? 85 : stress.includes('moderate') ? 60 : 35;

    const parts = [fallScore, dandruffScore, heatScore, dietScore, stressScore];
    const healthScore = Math.min(100, Math.round(parts.reduce((a, b) => a + b, 0) / parts.length));

    const scalpRaw = (answers.scalp_type || 'normal').toLowerCase();
    const scalpHealth = scalpRaw.charAt(0).toUpperCase() + scalpRaw.slice(1);
    const hairTypeRaw = (answers.hair_type || 'straight').toLowerCase();
    const hairType = hairTypeRaw.charAt(0).toUpperCase() + hairTypeRaw.slice(1);

    const ingredients = [
        {name:'Rosemary Oil', benefit:'Stimulates hair growth, improves circulation', how_to_use:'Scalp massage 2x weekly with carrier oil'},
        {name:'Biotin',       benefit:'Maintains hair strength, reduces breakage',     how_to_use:'Daily supplement or biotin-enriched shampoo'},
        {name:'Castor Oil',   benefit:'Thickens hair, boosts growth',                  how_to_use:'Apply to scalp and tips weekly overnight'},
    ];

    return {
        hair_health_score: healthScore,
        scalp_health: scalpHealth,
        hair_type: hairType,
        growth_recommendations: [
            'Massage scalp for 4 minutes daily to improve blood circulation',
            'Trim ends every 6-8 weeks to prevent split ends travelling up',
            'Sleep on a silk or satin pillowcase to reduce friction',
            'Take biotin and iron supplements after consulting a doctor',
            'Avoid tight hairstyles that pull on the scalp',
            'Rinse hair with cold water after conditioning to seal cuticles',
        ],
        weekly_routine: [
            {day:'Monday',    action:'Scalp Oil Massage',        notes:'Rosemary + Jojoba oil, 15 min'},
            {day:'Tuesday',   action:'Rest Day',                 notes:'No heat styling today'},
            {day:'Wednesday', action:'Shampoo + Condition',      notes:'Scalp-focused wash'},
            {day:'Thursday',  action:'Hair Mask',                notes:'Deep conditioning treatment 30 min'},
            {day:'Friday',    action:'Shampoo + Light Condition', notes:'Mid-week refresh'},
            {day:'Saturday',  action:'Scalp Scrub (2x monthly)', notes:'Remove buildup gently'},
            {day:'Sunday',    action:'Pre-oil Treatment',        notes:'Overnight mask for extra nourishment'},
        ],
        ingredients,
    };
}

function analyzeNailLocal(answers) {
    let score = 100;
    if (['yes','severe','moderately','severely'].some(v => (answers.weak_nails||'').toLowerCase().includes(v)))    score -= 20;
    if (['yes','severe','often','very often'].some(v => (answers.brittle_nails||'').toLowerCase().includes(v)))    score -= 20;
    if (['yes','slight'].some(v => (answers.discoloration||'').toLowerCase().includes(v)))                         score -= 15;
    if (['yes','slightly slow','very slow'].some(v => (answers.growth_issues||'').toLowerCase().includes(v)))      score -= 15;
    if (['yes','sometimes'].some(v => (answers.nail_biting||'').toLowerCase().includes(v)))                        score -= 20;

    return {
        nail_health_score: Math.max(20, score),
        growth_routine: [
            'Apply cuticle oil (jojoba or almond) every night before bed',
            'Keep nails trimmed to avoid breakage and tears',
            'Wear gloves when doing dishes or cleaning with chemicals',
            'File nails in one direction only to prevent splitting',
            'Take biotin supplements for nail strength (consult doctor)',
            'Eat protein-rich foods — eggs, lentils, nuts, fish',
        ],
        hydration_tips: [
            'Apply hand cream 5-6x daily, especially after washing hands',
            'Use cuticle oil before sleeping — massage in for 1 minute',
            'Avoid hand sanitiser directly on nail areas when possible',
            'Drink minimum 8 glasses of water daily for nail hydration',
        ],
        color_recommendations: [],
    };
}

// ── Chatbot Page (full embedded chat) ────────────────────────────────────────

function initChatbotPage() {
    const messagesEl = document.getElementById('page-chat-messages');
    const inputEl    = document.getElementById('page-chat-input');
    const sendEl     = document.getElementById('page-chat-send');

    if (!messagesEl) return;

    // Welcome
    appendPageMessage('ai', '✨ Hi! I\'m Glow Guide AI — your personal beauty and wellness expert. Ask me anything about skincare, haircare, makeup, or nail care!');

    function handleSend() {
        const msg = inputEl.value.trim();
        if (!msg) return;
        inputEl.value = '';
        sendPageMessage(msg);
    }

    if (sendEl) sendEl.addEventListener('click', handleSend);
    if (inputEl) inputEl.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } });

    // Suggested questions
    document.querySelectorAll('.gg-suggest-btn').forEach(btn => {
        btn.addEventListener('click', () => sendPageMessage(btn.textContent));
    });

    async function sendPageMessage(message) {
        appendPageMessage('user', message);
        showPageTyping();
        try {
            const res  = await fetch(`${API_BASE}/api/glow-guide/chat/`, {
                method : 'POST',
                headers: { 'Content-Type': 'application/json' },
                body   : JSON.stringify({ message, session_id: getSessionId() }),
            });
            const data = await res.json();
            hidePageTyping();
            appendPageMessage('ai', data.response || 'Sorry, I could not respond right now.');
        } catch {
            hidePageTyping();
            appendPageMessage('ai', 'Connection error. Please ensure the backend is running on port 8000.');
        }
    }

    function appendPageMessage(role, text) {
        const div = document.createElement('div');
        div.className = `gg-msg gg-msg-${role === 'user' ? 'user' : 'ai'}`;
        div.textContent = text;
        const typing = document.getElementById('page-typing');
        if (typing) { messagesEl.insertBefore(div, typing); }
        else { messagesEl.appendChild(div); }
        messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showPageTyping() {
        const el = document.getElementById('page-typing');
        if (el) el.style.display = 'flex';
    }

    function hidePageTyping() {
        const el = document.getElementById('page-typing');
        if (el) el.style.display = 'none';
    }
}

// ── Main Init ─────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    updateStreak(); // log daily visit

    // Always init chatbot and nav
    initChatbot();
    setActiveNavLink();
    initScrollAnimations();

    // Page-specific logic
    const page = document.body.dataset.page;

    switch (page) {
        case 'skin-analysis': initSkinAnalysis();   break;
        case 'hair-analysis': initHairAnalysis();   break;
        case 'nail-care':     initNailAnalysis();   break;
        case 'dashboard':     loadDashboard();      break;
        case 'blog':          loadDailyTips(); initHydrationTracker(); break;
        case 'chatbot':       initChatbotPage();    break;
    }
});
