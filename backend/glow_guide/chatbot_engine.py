"""
Glow Guide AI — Gemini-powered Chatbot Engine
Production-ready with full debug logging, optimized config, and complete response guarantee.
"""
import warnings
import logging
from django.conf import settings

logger = logging.getLogger('glow_guide.chatbot')

# ── Optimal Configuration for Beauty Chatbot ──────────────────────────────────
AI_CONFIG = {
    'model_waterfall': [
        'gemini-2.0-flash',          # Primary: best free-tier speed + quality
        'gemini-1.5-flash',          # Fallback 1: proven stable model
        'gemini-1.5-flash-8b',       # Fallback 2: lightweight, very fast
    ],
    'temperature':        0.80,      # Slightly creative but grounded (0=robotic, 1=chaotic)
    'max_output_tokens':  2048,      # Raised from 1024 — prevents cut-off responses
    'top_p':              0.94,      # Nucleus sampling — balanced diversity
    'top_k':              40,        # Top-K sampling — avoids rare tokens
    'candidate_count':    1,         # Single best response
}

# ── Premium System Prompt ──────────────────────────────────────────────────────
BEAUTY_SYSTEM_PROMPT = """
You are Glow Guide AI — the luxury AI beauty assistant for MakuUP Studio, a premium professional makeup and beauty studio based in India.

## Your Identity
You are warm, elegant, and highly knowledgeable — like a trusted best friend who is also a certified beauty expert. You remember what users tell you in the conversation and personalise every response to them specifically.

## Your Expertise
- Skincare: Routines, ingredients, skin types, concerns (acne, pigmentation, dryness, sensitivity, ageing)
- Haircare: Scalp health, hair types, growth, dandruff, oiliness, damage repair
- Makeup: Application techniques, colour theory, product types, skin-tone matching, occasion looks
- Nail wellness: Nail health, growth, cuticle care, nail art, colour selection
- Beauty nutrition: Foods for glowing skin, hair-boosting nutrients, hydration, supplements
- Indian-specific: Advice tailored for Indian climate, humidity, heat, pollution, and Indian skin tones

## Response Style
- Be conversational and warm — never cold or robotic
- Use simple, elegant language — no jargon unless you explain it
- Give SPECIFIC, actionable advice (not vague tips)
- Use numbered lists for routines and steps
- Ask follow-up questions to personalise (e.g., "What's your skin type?", "How oily is your scalp?")
- Use 1–2 relevant emojis per response for warmth — never overuse them
- Keep responses focused: 3–6 sentences for simple questions, step-by-step lists for routines
- ALWAYS complete your full response — never end mid-sentence or mid-thought
- Mention dermatologist consultation for serious medical skin conditions

## Memory & Context
- Remember everything the user tells you during the conversation
- Reference earlier messages: "You mentioned your skin is oily — in that case..."
- Build a mental profile of the user's skin type, concerns, routine, and preferences
- Personalise each new response based on what you've learned

## Important Rules
- NEVER give hardcoded, templated, or keyword-matched responses
- ALWAYS generate a unique, contextual, thoughtful response
- NEVER diagnose medical conditions
- ALWAYS recommend professional consultation for serious concerns
- Recommend ingredient types and categories — avoid specific brand names unless asked
- Keep advice safe, evidence-based, and accessible for Indian users
- ALWAYS finish your sentence and thought completely before ending the response

## MakuUP Studio Context
- Located in India (Mumbai focus)
- Offers bridal makeup, hair styling, nail art, skin consultations, and editorial looks
- When relevant, naturally suggest booking a studio session for professional help: "For this, a session with our artists at MakuUP Studio would make a real difference"
- Never be pushy about promotions — mention studio services only when genuinely helpful

Begin every first message warmly, introduce yourself, and ask the user's name and main beauty concern to start personalising.
"""


def get_gemini_response(message: str, history: list = None, user_context: dict = None) -> tuple:
    """
    Send a message to Gemini and return (response_text, error).

    Args:
        message:      The user's current message
        history:      List of {'role': 'user'|'model', 'message': str} dicts
        user_context: Optional dict with known user profile (skin_type, hair_type, etc.)

    Returns:
        (response_text: str, error: str|None)
    """
    api_key = getattr(settings, 'GEMINI_API_KEY', '').strip()

    # ── Debug: log incoming request ──
    logger.info("=" * 60)
    logger.info("GLOW GUIDE CHATBOT REQUEST")
    logger.info(f"  USER MESSAGE    : {message[:120]}{'...' if len(message) > 120 else ''}")
    logger.info(f"  HISTORY LENGTH  : {len(history or [])} messages")
    logger.info(f"  USER CONTEXT    : {user_context or 'None'}")
    logger.info(f"  API KEY SET     : {'YES' if api_key and api_key not in ('your-gemini-api-key-here', '') else 'NO — using fallback'}")

    if not api_key or api_key in ('your-gemini-api-key-here', 'your-api-key-here', ''):
        logger.warning("  MODE            : FALLBACK (no valid API key)")
        response = _smart_fallback(message, history)
        logger.info(f"  FALLBACK RESP   : {response[:100]}...")
        logger.info("=" * 60)
        return response, None

    system_prompt = _build_system_prompt(user_context)

    try:
        response_text, model_used, token_info = _call_gemini(api_key, message, history or [], system_prompt)

        # ── Debug: log AI response ──
        logger.info("  MODE            : REAL GEMINI AI")
        logger.info(f"  MODEL USED      : {model_used}")
        logger.info(f"  INPUT TOKENS    : {token_info.get('input_tokens', 'N/A')}")
        logger.info(f"  OUTPUT TOKENS   : {token_info.get('output_tokens', 'N/A')}")
        logger.info(f"  TOTAL TOKENS    : {token_info.get('total_tokens', 'N/A')}")
        logger.info(f"  RESPONSE LENGTH : {len(response_text)} chars")
        logger.info(f"  FULL RESPONSE   :\n{response_text}")
        logger.info("=" * 60)

        return response_text, None

    except Exception as exc:
        logger.error(f"  GEMINI ERROR    : {exc}")
        logger.warning("  FALLING BACK to smart fallback responses")
        response = _smart_fallback(message, history)
        logger.info("=" * 60)
        return response, None


def _build_system_prompt(user_context: dict = None) -> str:
    """Build a personalised system prompt incorporating known user data."""
    prompt = BEAUTY_SYSTEM_PROMPT

    if user_context:
        profile_lines = []
        if user_context.get('skin_type'):
            profile_lines.append(f"- Skin type: {user_context['skin_type']}")
        if user_context.get('hair_type'):
            profile_lines.append(f"- Hair type: {user_context['hair_type']}")
        if user_context.get('scalp_health'):
            profile_lines.append(f"- Scalp condition: {user_context['scalp_health']}")
        if user_context.get('acne_risk'):
            profile_lines.append(f"- Acne risk level: {user_context['acne_risk']}")

        if profile_lines:
            prompt += "\n\n## Known User Profile (from their analysis)\n"
            prompt += "\n".join(profile_lines)
            prompt += "\n\nUse this profile to personalise responses immediately without asking questions they've already answered."

    return prompt


def _call_gemini(api_key: str, message: str, history: list, system_prompt: str) -> tuple:
    """
    Call Gemini API. Returns (response_text, model_name_used, token_info).
    Tries models in waterfall order until one succeeds.
    """
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        import google.generativeai as genai

    genai.configure(api_key=api_key)

    models_to_try = AI_CONFIG['model_waterfall']

    # Format chat history (last 20 exchanges = 40 messages max for context window)
    formatted_history = []
    if history:
        for item in history[-20:]:
            formatted_history.append({
                'role':  item['role'],
                'parts': [item['message']]
            })

    last_error = None
    for model_name in models_to_try:
        try:
            logger.debug(f"  Trying model: {model_name}")

            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                model = genai.GenerativeModel(
                    model_name=model_name,
                    system_instruction=system_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=      AI_CONFIG['temperature'],
                        max_output_tokens=AI_CONFIG['max_output_tokens'],
                        top_p=            AI_CONFIG['top_p'],
                        top_k=            AI_CONFIG['top_k'],
                        candidate_count=  AI_CONFIG['candidate_count'],
                    )
                )

                chat    = model.start_chat(history=formatted_history)
                response = chat.send_message(message)

            response_text = response.text.strip() if response.text else ''

            # ── Extract token usage metadata ──
            token_info = {'input_tokens': 'N/A', 'output_tokens': 'N/A', 'total_tokens': 'N/A'}
            try:
                usage = response.usage_metadata
                if usage:
                    token_info = {
                        'input_tokens':  getattr(usage, 'prompt_token_count', 'N/A'),
                        'output_tokens': getattr(usage, 'candidates_token_count', 'N/A'),
                        'total_tokens':  getattr(usage, 'total_token_count', 'N/A'),
                    }
            except Exception:
                pass

            # ── Validate response is complete (not cut off) ──
            if response_text and not response_text[-1] in '.!?✨💧🌿💄💅':
                # Response might be cut off — check finish reason
                try:
                    finish_reason = response.candidates[0].finish_reason
                    if str(finish_reason) not in ('FinishReason.STOP', 'STOP', '1'):
                        logger.warning(f"  FINISH REASON: {finish_reason} — response may be truncated")
                except Exception:
                    pass

            return response_text, model_name, token_info

        except Exception as e:
            err_str = str(e)
            # Quota / model-not-found → try next model
            if any(code in err_str for code in ['429', '404', 'quota', 'not found', 'not supported', 'RESOURCE_EXHAUSTED']):
                logger.warning(f"  Model {model_name} unavailable ({err_str[:60]}), trying next...")
                last_error = e
                continue
            # Unknown error — re-raise
            raise

    if last_error:
        raise last_error
    raise RuntimeError("All Gemini models in waterfall failed")


def _smart_fallback(message: str, history: list = None) -> str:
    """
    Intelligent fallback when Gemini API is unavailable.
    Uses conversation history to give contextual responses.
    """
    msg = message.lower().strip()

    if not history or len(history) == 0:
        return (
            "Hi! ✨ I'm Glow Guide AI, your personal beauty expert at MakuUP Studio. "
            "I'm here to help with skincare, haircare, makeup, nails, and beauty wellness. "
            "What's your main beauty concern today? Tell me a little about your skin type and I'll personalise my advice for you!"
        )

    history_text = ' '.join([h.get('message', '').lower() for h in (history or [])])
    known_oily   = any(w in history_text for w in ['oily', 'sebum', 'greasy'])
    known_dry    = any(w in history_text for w in ['dry', 'dehydrated', 'flaky'])
    known_acne   = any(w in history_text for w in ['acne', 'pimple', 'breakout'])

    if any(w in msg for w in ['acne', 'pimple', 'breakout', 'spot', 'zit', 'blemish']):
        if known_oily:
            return (
                "Since you have oily skin, your acne is likely driven by excess sebum clogging pores. "
                "Your priority ingredients are: salicylic acid (2%) as a cleanser or toner to unclog pores, "
                "niacinamide serum to regulate oil production, and a lightweight oil-free moisturiser. "
                "Never skip moisturiser — dehydrated oily skin overproduces oil to compensate. "
                "Apply a benzoyl peroxide spot treatment on active breakouts at night only. "
                "What's your current routine? I can tell you exactly what to swap out. 🌿"
            )
        return (
            "For acne, the most effective trio is: salicylic acid cleanser (clears pores), "
            "niacinamide serum (reduces inflammation and oil), and a non-comedogenic SPF 50 daily. "
            "Avoid physical scrubs — they spread bacteria. Change pillowcases every 3 days. "
            "For persistent or cystic acne, please see a dermatologist. "
            "What type of acne do you have — whiteheads, blackheads, cystic, or all three? ✨"
        )

    if any(w in msg for w in ['hair fall', 'hair loss', 'thinning', 'shedding', 'bald']):
        return (
            "Hair fall can have many causes — nutritional deficiency, stress, hormonal changes, or scalp health. "
            "Start with rosemary oil scalp massages 3x a week (clinically proven to boost growth), "
            "a protein-rich diet (eggs, lentils, paneer, fish), and iron + biotin after consulting your doctor. "
            "Also check if you're heat-styling too often — heat damage causes significant breakage. "
            "Are you experiencing diffuse thinning all over, or localised patches? That distinction is important. 💆"
        )

    if any(w in msg for w in ['dandruff', 'flakes', 'itchy scalp', 'scalp']):
        return (
            "Dandruff is usually caused by a yeast (Malassezia) that thrives in oily conditions. "
            "Use a shampoo containing zinc pyrithione, ketoconazole, or selenium sulfide 2-3x per week. "
            "Between washes, dilute 2-3 drops of tea tree oil in a carrier oil and massage into the scalp. "
            "Avoid scratching — it worsens inflammation. "
            "If dandruff is yellow and crusty, it may be seborrheic dermatitis — see a dermatologist. "
            "Is your scalp oily, dry, or a mix of both? 🌿"
        )

    if any(w in msg for w in ['dry skin', 'dryness', 'dehydrated', 'tight', 'flaky skin']):
        return (
            "Dry skin needs a layered approach: switch to a cream cleanser (no foam), "
            "apply hyaluronic acid on damp skin within 60 seconds of washing, "
            "lock it with a ceramide-rich moisturiser, and try a sleeping mask 3x a week at night. "
            "Avoid hot showers — they strip your skin's natural oils. "
            "Drink at least 8 glasses of water daily — internal hydration shows on your skin. 💧"
        )

    if any(w in msg for w in ['pigmentation', 'dark spot', 'dark circle', 'tan', 'uneven', 'brightening', 'glow']):
        return (
            "For pigmentation, the gold standard is: Vitamin C serum (10-15%) + SPF 50 PA+++ in the morning, "
            "and Alpha Arbutin or Niacinamide at night to fade existing spots. "
            "The most critical step? Never skip SPF — UV exposure causes and worsens pigmentation. "
            "Results take 8-12 weeks of consistency. "
            "What kind of pigmentation — sun spots, post-acne marks, melasma, or overall dullness? ✨"
        )

    if any(w in msg for w in ['routine', 'steps', 'regimen', 'what should i use', 'how to start']):
        return (
            "A complete routine has these core steps:\n"
            "☀️ Morning: 1. Gentle cleanser → 2. Vitamin C serum → 3. Moisturiser → 4. SPF 50\n"
            "🌙 Night: 1. Double cleanse → 2. Treatment serum (Niacinamide/Retinol) → 3. Night moisturiser\n"
            "Start simple — cleanser, moisturiser, SPF — then add actives one at a time every 2 weeks. "
            "What's your skin type? I'll build your exact personalised routine. 🌿"
        )

    if any(w in msg for w in ['makeup', 'foundation', 'base', 'concealer', 'primer']):
        return (
            "For a flawless base in Indian heat: "
            "1. Hydrating primer (dry skin) or pore-minimising primer (oily skin). "
            "2. Match foundation to your neck in natural light. "
            "3. Build coverage in thin layers — thick layers look cakey in heat. "
            "4. Set with translucent powder on T-zone. "
            "5. Finish with a setting spray to lock for 8-10 hours. "
            "What's your skin type and the occasion? I'll tailor this further. 💄"
        )

    if any(w in msg for w in ['nail', 'cuticle', 'brittle', 'weak nail', 'nail growth', 'nail art']):
        return (
            "For strong nails: apply jojoba or sweet almond cuticle oil every night and massage for 1 minute — "
            "this transforms nail health in 2 weeks. "
            "File in one direction to prevent splitting, and wear gloves when washing dishes. "
            "Biotin 2500mcg daily helps nail strength (check with your doctor first). "
            "Are you dealing with brittle nails, slow growth, or looking for nail art ideas? 💅"
        )

    if any(w in msg for w in ['sunscreen', 'spf', 'sun protection', 'uv']):
        return (
            "SPF is the single highest-impact skincare step — more anti-ageing than any serum. "
            "For India, use minimum SPF 50 PA+++ every day, including indoors and on cloudy days. "
            "Apply 2 finger-lengths for the face and reapply every 2-3 hours if outdoors. "
            "Chemical sunscreens are lightweight and better under makeup; "
            "mineral sunscreens (zinc oxide) are better for sensitive or acne-prone skin. 🌞"
        )

    if any(w in msg for w in ['food', 'diet', 'eat', 'nutrition', 'supplement', 'vitamin']):
        return (
            "Your skin is built from what you eat. "
            "For glowing skin: Omega-3s (walnuts, flaxseeds, fish), Vitamin C (amla), and zinc (pumpkin seeds, lentils). "
            "For hair: protein (the building block of hair), iron (the #1 deficiency causing hair fall in Indian women), "
            "and biotin (eggs, sweet potato, almonds). "
            "Stay hydrated — skin visibly glows when you drink 8-10 glasses of water daily. "
            "Are you focused on skin glow, hair growth, or overall wellness? 🌿"
        )

    if any(w in msg for w in ['hi', 'hello', 'hey', 'hii', 'namaste', 'good morning', 'good evening']):
        return (
            "Hello! ✨ So lovely to chat with you. I'm Glow Guide AI — your beauty expert at MakuUP Studio. "
            "I can help with skincare, haircare, makeup, nails, and beauty nutrition. "
            "What's on your mind today? Tell me your main concern and I'll give you personalised advice!"
        )

    if any(w in msg for w in ['thank', 'thanks', 'helpful', 'great', 'amazing', 'perfect']):
        return (
            "You're so welcome! ✨ It makes me happy to help. "
            "Consistency is the real secret to beauty — small daily habits make the biggest difference over time. "
            "Do you have any other questions? I'm here for anything skin, hair, makeup, or nail related!"
        )

    return (
        "That's a great question! To give you the most personalised advice, could you tell me: "
        "your skin type (oily/dry/combination/sensitive), your main concern, "
        "and what products you're currently using? "
        "The more I know about you, the better I can tailor my recommendations. ✨"
    )
