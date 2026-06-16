"""
Glow Guide AI — Analysis Engine
Scores skin, hair, and nail health from quiz answers and generates recommendations.
"""

# ─────────────────────────────────────────────
# SKIN ANALYSIS
# ─────────────────────────────────────────────

SKIN_INGREDIENTS = {
    'oily': [
        {'name': 'Niacinamide', 'benefit': 'Controls sebum, minimises pores', 'usage': 'Apply 2-3 drops after toner, morning & night', 'conflicts': 'Avoid mixing with Vitamin C at the same time'},
        {'name': 'Salicylic Acid', 'benefit': 'Unclogs pores, fights acne', 'usage': '2-3x per week in cleanser or toner', 'conflicts': 'Do not layer with Retinol on the same night'},
        {'name': 'Hyaluronic Acid', 'benefit': 'Lightweight hydration without greasiness', 'usage': 'Apply on damp skin, morning & night', 'conflicts': 'None'},
    ],
    'dry': [
        {'name': 'Hyaluronic Acid', 'benefit': 'Deep hydration, plumps skin', 'usage': 'Apply on damp skin morning & night', 'conflicts': 'None'},
        {'name': 'Ceramides', 'benefit': 'Repairs skin barrier, locks moisture', 'usage': 'Use in moisturiser, both AM & PM', 'conflicts': 'None'},
        {'name': 'Squalane', 'benefit': 'Ultra-nourishing, non-comedogenic oil', 'usage': '2-3 drops as last PM step', 'conflicts': 'None'},
    ],
    'combination': [
        {'name': 'Niacinamide', 'benefit': 'Balances T-zone oil, hydrates dry areas', 'usage': 'Apply all over, morning & night', 'conflicts': 'Avoid same-time use with Vitamin C'},
        {'name': 'Hyaluronic Acid', 'benefit': 'Lightweight hydration for all zones', 'usage': 'Apply on damp skin', 'conflicts': 'None'},
        {'name': 'AHA (Glycolic Acid)', 'benefit': 'Exfoliates, brightens, refines texture', 'usage': '2x per week, PM only', 'conflicts': 'Do not use with Retinol same night'},
    ],
    'sensitive': [
        {'name': 'Centella Asiatica', 'benefit': 'Calms redness, repairs barrier', 'usage': 'Use in serum or moisturiser AM & PM', 'conflicts': 'None'},
        {'name': 'Ceramides', 'benefit': 'Strengthens skin barrier', 'usage': 'Use in moisturiser both AM & PM', 'conflicts': 'None'},
        {'name': 'Aloe Vera', 'benefit': 'Soothes irritation and redness', 'usage': 'Apply gel directly or in products AM & PM', 'conflicts': 'None'},
    ],
    'normal': [
        {'name': 'Vitamin C', 'benefit': 'Brightens skin, fights pigmentation', 'usage': 'Apply in morning after cleansing', 'conflicts': 'Do not layer with Niacinamide simultaneously'},
        {'name': 'Retinol', 'benefit': 'Anti-ageing, smooths skin texture', 'usage': 'PM only, 2-3x per week', 'conflicts': 'Do not mix with AHAs/BHAs same night'},
        {'name': 'Hyaluronic Acid', 'benefit': 'Maintains hydration balance', 'usage': 'Apply on damp skin AM & PM', 'conflicts': 'None'},
    ],
}

ROUTINES = {
    'oily': {
        'morning': [
            {'step': 1, 'product': 'Foaming / Gel Cleanser', 'notes': 'Use a salicylic acid cleanser for oily skin'},
            {'step': 2, 'product': 'Niacinamide Serum', 'notes': '2-3 drops, let absorb for 60 seconds'},
            {'step': 3, 'product': 'Oil-Free Gel Moisturiser', 'notes': 'Lightweight, non-comedogenic formula'},
            {'step': 4, 'product': 'SPF 50 Sunscreen', 'notes': 'Matte-finish sunscreen works best for oily skin'},
        ],
        'night': [
            {'step': 1, 'product': 'Micellar Water / Oil Cleanser', 'notes': 'Double cleanse to remove makeup & SPF'},
            {'step': 2, 'product': 'BHA Toner (Salicylic Acid)', 'notes': '2-3x per week only'},
            {'step': 3, 'product': 'Niacinamide Serum', 'notes': 'Helps control overnight sebum production'},
            {'step': 4, 'product': 'Lightweight Night Moisturiser', 'notes': 'Gel-cream texture recommended'},
        ],
    },
    'dry': {
        'morning': [
            {'step': 1, 'product': 'Cream / Milk Cleanser', 'notes': 'Gentle, non-stripping formula'},
            {'step': 2, 'product': 'Hydrating Toner', 'notes': 'Prep skin before serum'},
            {'step': 3, 'product': 'Hyaluronic Acid Serum', 'notes': 'Apply on slightly damp skin'},
            {'step': 4, 'product': 'Rich Moisturiser with Ceramides', 'notes': 'Lock in hydration'},
            {'step': 5, 'product': 'SPF 50 Sunscreen', 'notes': 'Dewy finish sunscreen recommended'},
        ],
        'night': [
            {'step': 1, 'product': 'Balm / Cream Cleanser', 'notes': 'Never use foaming cleansers'},
            {'step': 2, 'product': 'Hyaluronic Acid Serum', 'notes': 'Double-dose hydration at night'},
            {'step': 3, 'product': 'Peptide or Ceramide Serum', 'notes': 'Barrier repair overnight'},
            {'step': 4, 'product': 'Rich Night Cream with Shea Butter', 'notes': 'Seal everything in'},
        ],
    },
    'combination': {
        'morning': [
            {'step': 1, 'product': 'Balanced pH Gel Cleanser', 'notes': 'Not too stripping, not too rich'},
            {'step': 2, 'product': 'Niacinamide Serum', 'notes': 'Balances T-zone while hydrating dry areas'},
            {'step': 3, 'product': 'Light Lotion Moisturiser', 'notes': 'Medium-weight formula'},
            {'step': 4, 'product': 'SPF 50+ Sunscreen', 'notes': 'Apply generously'},
        ],
        'night': [
            {'step': 1, 'product': 'Double Cleanse', 'notes': 'Oil cleanser → gel cleanser'},
            {'step': 2, 'product': 'AHA Toner (2x weekly)', 'notes': 'Glycolic acid for texture refinement'},
            {'step': 3, 'product': 'Hyaluronic Acid Serum', 'notes': 'Hydrate dry cheeks'},
            {'step': 4, 'product': 'Gel-Cream Moisturiser', 'notes': 'Lighter on T-zone, more on cheeks'},
        ],
    },
    'sensitive': {
        'morning': [
            {'step': 1, 'product': 'Fragrance-Free Gentle Cleanser', 'notes': 'pH balanced, no active acids'},
            {'step': 2, 'product': 'Centella Asiatica Serum', 'notes': 'Calming and barrier-strengthening'},
            {'step': 3, 'product': 'Ceramide-Rich Moisturiser', 'notes': 'Fragrance-free essential'},
            {'step': 4, 'product': 'Mineral SPF 50', 'notes': 'Zinc oxide-based is gentler for sensitive skin'},
        ],
        'night': [
            {'step': 1, 'product': 'Micellar Water + Gentle Cleanser', 'notes': 'Minimal rubbing, be gentle'},
            {'step': 2, 'product': 'Aloe Vera Gel', 'notes': 'Soothe any redness'},
            {'step': 3, 'product': 'Barrier Repair Serum', 'notes': 'Ceramides + Peptides'},
            {'step': 4, 'product': 'Rich Fragrance-Free Night Cream', 'notes': 'Repair skin overnight'},
        ],
    },
    'normal': {
        'morning': [
            {'step': 1, 'product': 'Gentle Gel Cleanser', 'notes': 'Keep it simple'},
            {'step': 2, 'product': 'Vitamin C Serum', 'notes': 'Brightening and antioxidant protection'},
            {'step': 3, 'product': 'Light Moisturiser', 'notes': 'SPF-boosting formula a bonus'},
            {'step': 4, 'product': 'SPF 50 Sunscreen', 'notes': 'Non-negotiable daily step'},
        ],
        'night': [
            {'step': 1, 'product': 'Micellar + Gentle Cleanser', 'notes': 'Remove SPF properly'},
            {'step': 2, 'product': 'Retinol Serum (2-3x weekly)', 'notes': 'Anti-ageing, refines texture'},
            {'step': 3, 'product': 'Hyaluronic Acid', 'notes': 'Hydration support'},
            {'step': 4, 'product': 'Balanced Night Cream', 'notes': 'Not too heavy'},
        ],
    },
}


def analyze_skin(answers: dict) -> dict:
    """
    Analyze skin quiz answers and return a scored skin report.
    answers keys: age, climate, skin_type, acne, dryness, sensitivity,
                  pigmentation, wrinkles, redness, open_pores,
                  water_intake, sleep_hours, stress_level, uses_sunscreen
    All values are strings from the quiz options.
    """
    # Determine skin type
    skin_type = answers.get('skin_type', 'normal').lower()
    if skin_type not in SKIN_INGREDIENTS:
        skin_type = 'normal'

    # Score components (each 0–100)
    score_parts = []

    # Hydration
    water = answers.get('water_intake', '6-8 glasses')
    if '8+' in water or '8-10' in water:
        hydration = 85
    elif '6' in water or '6-8' in water:
        hydration = 65
    elif '4' in water:
        hydration = 45
    else:
        hydration = 30
    score_parts.append(hydration)

    # Sleep
    sleep = answers.get('sleep_hours', '7-8')
    if '8+' in sleep or '7-8' in sleep:
        sleep_score = 90
    elif '6-7' in sleep:
        sleep_score = 70
    elif '5-6' in sleep:
        sleep_score = 50
    else:
        sleep_score = 30
    score_parts.append(sleep_score)

    # Sunscreen
    sunscreen = answers.get('uses_sunscreen', 'no').lower()
    sunscreen_score = 90 if sunscreen in ['yes', 'daily', 'always'] else 40
    score_parts.append(sunscreen_score)

    # Stress
    stress = answers.get('stress_level', 'moderate').lower()
    if 'low' in stress:
        stress_score = 85
    elif 'moderate' in stress:
        stress_score = 60
    else:
        stress_score = 35
    score_parts.append(stress_score)

    # Acne penalty
    acne = answers.get('acne', 'none').lower()
    if 'severe' in acne:
        acne_risk = 'High'
        score_parts.append(30)
    elif 'moderate' in acne:
        acne_risk = 'Medium'
        score_parts.append(55)
    elif 'mild' in acne or 'occasional' in acne:
        acne_risk = 'Low'
        score_parts.append(75)
    else:
        acne_risk = 'Very Low'
        score_parts.append(90)

    # Sensitivity
    sensitivity = answers.get('sensitivity', 'none').lower()
    if 'high' in sensitivity or 'very' in sensitivity:
        sensitivity_score = 30
    elif 'moderate' in sensitivity or 'mild' in sensitivity:
        sensitivity_score = 60
    else:
        sensitivity_score = 90

    health_score = min(100, int(sum(score_parts) / len(score_parts)))

    return {
        'skin_type': skin_type.capitalize(),
        'health_score': health_score,
        'hydration_score': hydration,
        'acne_risk': acne_risk,
        'sensitivity_score': sensitivity_score,
        'morning_routine': ROUTINES.get(skin_type, ROUTINES['normal'])['morning'],
        'night_routine': ROUTINES.get(skin_type, ROUTINES['normal'])['night'],
        'ingredients': SKIN_INGREDIENTS.get(skin_type, SKIN_INGREDIENTS['normal']),
    }


# ─────────────────────────────────────────────
# HAIR ANALYSIS
# ─────────────────────────────────────────────

HAIR_INGREDIENTS = {
    'oily': [
        {'name': 'Tea Tree Oil', 'benefit': 'Controls scalp oil, anti-fungal', 'how_to_use': 'Add 5 drops to shampoo or dilute in carrier oil'},
        {'name': 'Rosemary Oil', 'benefit': 'Stimulates hair growth, balances scalp', 'how_to_use': 'Dilute 5 drops in 1 tbsp jojoba oil, massage scalp'},
        {'name': 'Biotin', 'benefit': 'Strengthens hair shaft, reduces breakage', 'how_to_use': 'Take as supplement or use biotin-enriched shampoo'},
    ],
    'dry': [
        {'name': 'Argan Oil', 'benefit': 'Deep nourishment, tames frizz', 'how_to_use': '2-3 drops on damp hair or overnight mask'},
        {'name': 'Coconut Oil', 'benefit': 'Penetrates hair shaft, prevents protein loss', 'how_to_use': 'Pre-shampoo treatment 1-2 hours before wash'},
        {'name': 'Keratin', 'benefit': 'Smooths hair, repairs damage', 'how_to_use': 'Use keratin-enriched conditioner or treatment'},
    ],
    'normal': [
        {'name': 'Rosemary Oil', 'benefit': 'Promotes growth, improves circulation', 'how_to_use': 'Scalp massage 2x weekly with carrier oil'},
        {'name': 'Biotin', 'benefit': 'Maintains hair strength', 'how_to_use': 'Daily supplement or biotin-enriched products'},
        {'name': 'Castor Oil', 'benefit': 'Thickens hair, boosts growth', 'how_to_use': 'Apply to scalp and tips weekly overnight'},
    ],
}


def analyze_hair(answers: dict) -> dict:
    """
    Analyze hair quiz answers.
    answers keys: hair_type, scalp_type, hair_fall, dandruff, frizz,
                  heat_styling, wash_frequency, diet_quality, stress_level
    """
    scalp = answers.get('scalp_type', 'normal').lower()
    hair_type = answers.get('hair_type', 'straight').lower()

    score_parts = []

    # Hair fall
    fall = answers.get('hair_fall', 'minimal').lower()
    if 'severe' in fall or 'lots' in fall:
        score_parts.append(30)
    elif 'moderate' in fall:
        score_parts.append(55)
    else:
        score_parts.append(85)

    # Dandruff
    dandruff = answers.get('dandruff', 'none').lower()
    if 'severe' in dandruff:
        score_parts.append(30)
    elif 'mild' in dandruff or 'occasional' in dandruff:
        score_parts.append(60)
    else:
        score_parts.append(90)

    # Heat styling
    heat = answers.get('heat_styling', 'rarely').lower()
    if 'daily' in heat:
        score_parts.append(35)
    elif 'often' in heat or 'frequently' in heat:
        score_parts.append(50)
    elif 'sometimes' in heat or 'occasional' in heat:
        score_parts.append(70)
    else:
        score_parts.append(90)

    # Diet
    diet = answers.get('diet_quality', 'average').lower()
    if 'good' in diet or 'excellent' in diet:
        score_parts.append(85)
    elif 'average' in diet:
        score_parts.append(60)
    else:
        score_parts.append(35)

    # Stress
    stress = answers.get('stress_level', 'moderate').lower()
    if 'low' in stress:
        score_parts.append(85)
    elif 'moderate' in stress:
        score_parts.append(60)
    else:
        score_parts.append(35)

    health_score = min(100, int(sum(score_parts) / len(score_parts)))

    ingredients = HAIR_INGREDIENTS.get(scalp, HAIR_INGREDIENTS['normal'])

    weekly_routine = [
        {'day': 'Monday', 'action': 'Scalp Oil Massage', 'notes': 'Rosemary + Jojoba oil, 15 min'},
        {'day': 'Tuesday', 'action': 'Rest Day', 'notes': 'No heat styling today'},
        {'day': 'Wednesday', 'action': 'Shampoo + Condition', 'notes': 'Scalp-focused wash'},
        {'day': 'Thursday', 'action': 'Hair Mask', 'notes': 'Deep conditioning treatment 30 min'},
        {'day': 'Friday', 'action': 'Shampoo + Light Condition', 'notes': 'Mid-week refresh'},
        {'day': 'Saturday', 'action': 'Scalp Scrub (2x monthly)', 'notes': 'Remove buildup gently'},
        {'day': 'Sunday', 'action': 'Pre-oil Treatment', 'notes': 'Overnight mask for extra nourishment'},
    ]

    growth_recommendations = [
        'Massage scalp for 4 minutes daily to improve blood circulation',
        'Trim ends every 6-8 weeks to prevent split ends traveling up',
        'Sleep on a silk or satin pillowcase to reduce friction',
        'Take biotin and iron supplements after consulting a doctor',
        'Avoid tight hairstyles that pull on the scalp',
        'Rinse hair with cold water after conditioning to seal cuticles',
    ]

    return {
        'hair_health_score': health_score,
        'scalp_health': scalp.capitalize(),
        'hair_type': hair_type.capitalize(),
        'growth_recommendations': growth_recommendations,
        'weekly_routine': weekly_routine,
        'ingredients': ingredients,
    }


# ─────────────────────────────────────────────
# NAIL ANALYSIS
# ─────────────────────────────────────────────

def analyze_nail(answers: dict) -> dict:
    """
    Analyze nail quiz answers.
    answers keys: weak_nails, brittle_nails, discoloration, growth_issues, nail_biting
    """
    score_parts = [100]  # start at perfect

    if answers.get('weak_nails', 'no').lower() in ['yes', 'severe', 'moderate']:
        score_parts.append(50)
    if answers.get('brittle_nails', 'no').lower() in ['yes', 'severe']:
        score_parts.append(40)
    if answers.get('discoloration', 'no').lower() in ['yes', 'some']:
        score_parts.append(55)
    if answers.get('growth_issues', 'no').lower() in ['yes', 'slow']:
        score_parts.append(50)
    if answers.get('nail_biting', 'no').lower() in ['yes', 'sometimes']:
        score_parts.append(45)

    nail_score = min(100, int(sum(score_parts) / len(score_parts)))

    growth_routine = [
        'Apply cuticle oil (jojoba or almond) every night before bed',
        'Keep nails trimmed to avoid breakage and tears',
        'Wear gloves when doing dishes or cleaning with chemicals',
        'File nails in one direction only to prevent splitting',
        'Take biotin supplements for nail strength (consult doctor)',
        'Eat protein-rich foods — eggs, lentils, nuts, fish',
    ]

    hydration_tips = [
        'Apply hand cream 5-6x daily, especially after washing hands',
        'Use cuticle oil before sleeping — massage in for 1 minute',
        'Avoid hand sanitiser directly on nail areas when possible',
        'Drink minimum 8 glasses of water daily for nail hydration',
    ]

    color_recs = [
        'Dusty Rose — universally flattering for all skin tones',
        'Terracotta / Rust — stunning on medium to deep skin tones',
        'Nude Beige — elegant and professional for daily wear',
        'Deep Burgundy — rich, luxurious look for events',
        'Soft Lavender — trendy and feminine for everyday',
        'Classic Red — timeless and bold for all occasions',
    ]

    return {
        'nail_health_score': nail_score,
        'growth_routine': growth_routine,
        'hydration_tips': hydration_tips,
        'color_recommendations': color_recs,
    }
