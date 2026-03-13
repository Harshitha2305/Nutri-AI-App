# =============================================================================
# ui_components.py
# All reusable rendering functions for NutriAI v3 UI.
# app.py imports these so the main file stays clean and readable.
# =============================================================================

import streamlit as st # type: ignore


# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT PRIMITIVES
# ─────────────────────────────────────────────────────────────────────────────

def section_header(title: str, subtitle: str = ""):
    """Renders a styled section heading with optional subtitle."""
    sub_html = f'<div style="font-size:0.78rem;color:var(--text-muted);margin-top:0.15rem">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="sec-head">{title}{sub_html}</div>', unsafe_allow_html=True)


def info_strip(text: str, kind: str = "blue"):
    """Renders a coloured info strip. kind: blue | green | amber | red | purple."""
    st.markdown(f'<div class="strip-{kind}">{text}</div>', unsafe_allow_html=True)


def empty_state(icon: str, title: str, subtitle: str):
    """Renders a centered empty-state placeholder."""
    st.markdown(f"""
    <div class="empty-state">
        <div class="es-icon">{icon}</div>
        <div class="es-title">{title}</div>
        <div class="es-sub">{subtitle}</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# METRIC CARDS
# ─────────────────────────────────────────────────────────────────────────────

def metric_card(icon: str, label: str, value, unit: str = "",
                sub: str = "", trend: str = "", trend_kind: str = "ok",
                color: str = "green"):
    """
    Renders a single dashboard metric card.

    Args:
        icon:       Emoji icon
        label:      Uppercase label text
        value:      Primary value to display prominently
        unit:       Small unit string after value
        sub:        Small grey subtitle
        trend:      Optional trend text (e.g. "+0.5 kg")
        trend_kind: "up" | "down" | "ok"
        color:      Card accent color class
    """
    trend_html = ""
    if trend:
        trend_html = f'<div class="mc-trend {trend_kind}">{trend}</div>'

    st.markdown(f"""
    <div class="mc-wrap {color}">
        <div class="mc-icon">{icon}</div>
        <div class="mc-label">{label}</div>
        <div>
            <span class="mc-value">{value}</span>
            <span class="mc-unit">{unit}</span>
        </div>
        {"<div class='mc-sub'>"+sub+"</div>" if sub else ""}
        {trend_html}
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MACRO PROGRESS BARS
# ─────────────────────────────────────────────────────────────────────────────

def macro_progress(icon: str, label: str, current: int, target: int, kind: str):
    """
    Renders a custom styled macro progress bar.
    kind: "protein" | "carbs" | "fat" | "fiber"
    """
    pct     = min(current / max(target, 1), 1.0)
    pct_int = int(pct * 100)
    width   = f"{pct_int}%"

    color_map = {
        "protein": "#7C3AED",
        "carbs":   "#2563EB",
        "fat":     "#D97706",
        "fiber":   "#059669",
    }
    color = color_map.get(kind, "#16A34A")

    st.markdown(f"""
    <div class="macro-block">
        <div class="mb-header">
            <span class="mb-label">{icon} {label}</span>
            <span class="mb-nums">{current}g / {target}g &nbsp;·&nbsp; {pct_int}%</span>
        </div>
        <div class="macro-track">
            <div class="macro-fill {kind}" style="width:{width};background:linear-gradient(90deg,{color},{color}aa)"></div>
        </div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MEAL CARDS
# ─────────────────────────────────────────────────────────────────────────────

def meal_card(meal: dict):
    """
    Renders a full meal card with header, macros, and score bar.
    Does NOT include the swap button — caller adds that separately.
    """
    score      = meal.get("score", 5)
    grade      = meal.get("score_grade", "C")
    score_tip  = meal.get("score_tip", "")
    score_pct  = f"{int(score / 10 * 100)}%"

    if score >= 8:
        score_color = "#16A34A"; score_bg = "#DCFCE7"
    elif score >= 6:
        score_color = "#D97706"; score_bg = "#FEF3C7"
    else:
        score_color = "#DC2626"; score_bg = "#FEE2E2"

    st.markdown(f"""
    <div class="meal-wrap">
        <div class="meal-header">
            <div class="meal-time-row">
                <span class="meal-type-badge">{meal.get('label','Meal')}</span>
                <span class="meal-time-text">⏰ {meal.get('time','')}</span>
            </div>
            <div class="meal-icon-row">
                <span class="meal-icon">{meal.get('icon','🍽️')}</span>
                <div>
                    <div class="meal-name">{meal['food_name']}</div>
                    <div class="meal-desc">{meal.get('description','')}</div>
                </div>
            </div>
        </div>
        <div class="meal-body">
            <div class="meal-macros">
                <span class="mmb cal">🔥 {meal['calories']} cal</span>
                <span class="mmb pro">💪 {meal['protein']}g protein</span>
                <span class="mmb crb">🌾 {meal['carbs']}g carbs</span>
                <span class="mmb fat">🥑 {meal['fat']}g fat</span>
                <span class="mmb fib">🌿 {meal.get('fiber',0)}g fibre</span>
            </div>
            <div class="score-row">
                <span class="score-label">Health Score</span>
                <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{score_pct};background:{score_color}"></div>
                </div>
                <span class="score-num" style="color:{score_color}">{score}/10 {grade}</span>
            </div>
            <div style="font-size:0.72rem;color:var(--text-muted);margin-top:0.3rem">{score_tip}</div>
        </div>
    </div>""", unsafe_allow_html=True)


def mini_meal_card(meal: dict):
    """Compact meal card used in the weekly planner grid."""
    score = meal.get("score", 5)
    score_color = "#16A34A" if score >= 8 else "#D97706" if score >= 6 else "#DC2626"

    st.markdown(f"""
    <div class="mini-meal">
        <div class="mm-icon">{meal.get('icon','🍽️')}</div>
        <div class="mm-type">{meal.get('label','')}</div>
        <div class="mm-name">{meal['food_name']}</div>
        <div class="mm-cal">🔥 {meal['calories']} cal</div>
        <div class="mm-score" style="color:{score_color}">⭐ {score}/10</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AI DECISION ENGINE VISUALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def render_pipeline(profile: dict = None, agent_status: list = None):
    """
    Renders the multi-agent pipeline visualization.
    Shows live status when profile is available.
    """
    is_live = profile is not None
    status_label = "LIVE — All Agents Active" if is_live else "READY — Awaiting Profile"

    # Build node data
    nodes = [
        {
            "icon":  "👤",
            "name":  "User Input",
            "sub":   "Age, weight, goals, diet, allergies",
            "tag":   "INPUT",
            "class": "input",
        },
        {
            "icon":  "🔬",
            "name":  "Nutrition Agent",
            "sub":   "BMI · BMR · TDEE · Macros",
            "tag":   "ANALYSIS",
            "class": "active",
        },
        {
            "icon":  "🍽️",
            "name":  "Meal Planning Agent",
            "sub":   "Daily · Weekly · Swap · Grocery",
            "tag":   "PLANNING",
            "class": "active",
        },
        {
            "icon":  "💡",
            "name":  "Health Insights Agent",
            "sub":   "Tips · Alerts · Projections",
            "tag":   "INSIGHTS",
            "class": "active",
        },
        {
            "icon":  "📸",
            "name":  "Food Image Agent",
            "sub":   "Claude Vision · Calorie scan",
            "tag":   "VISION",
            "class": "active",
        },
        {
            "icon":  "💬",
            "name":  "Chat Assistant Agent",
            "sub":   "Claude · Context-aware Q&A",
            "tag":   "LLM",
            "class": "active",
        },
        {
            "icon":  "✅",
            "name":  "Personalised Output",
            "sub":   "Dashboard · Plans · Coaching",
            "tag":   "OUTPUT",
            "class": "output",
        },
    ]

    # Build flow HTML — nodes + arrows
    flow_html = ""
    for i, node in enumerate(nodes):
        flow_html += f"""
        <div class="pipe-node {node['class']}">
            <div class="pipe-node-icon">{node['icon']}</div>
            <div class="pipe-node-name">{node['name']}</div>
            <div class="pipe-node-sub">{node['sub']}</div>
            <span class="pipe-node-tag">{node['tag']}</span>
        </div>"""
        if i < len(nodes) - 1:
            flow_html += '<div class="pipe-arrow">→</div>'

    # Data flow labels
    data_chips = [
        "User Profile", "BMI + TDEE", "Calorie Target",
        "Macro Goals", "Meal Plan", "Nutrition Score",
        "Health Tips", "Grocery List", "Chat Response",
    ]
    chips_html = "".join(
        f'<div class="pipe-data-chip">{c}</div>' for c in data_chips
    )

    # Live stats row (shown when profile exists)
    live_stats = ""
    if is_live and profile:
        live_stats = f"""
        <div style="display:flex;flex-wrap:wrap;gap:0.8rem;margin-top:1rem;padding:1rem;
                    background:var(--green-50);border-radius:var(--radius-sm);
                    border:1px solid var(--green-100)">
            <div style="font-size:0.75rem;font-weight:700;color:var(--green-700);width:100%;margin-bottom:0.3rem">
                🔴 Live Agent Outputs:
            </div>
            <div style="font-size:0.78rem;color:var(--text-mid)">
                <strong>BMI:</strong> {profile.get('bmi','–')} ({profile.get('bmi_category','–')})
            </div>
            <div style="font-size:0.78rem;color:var(--text-mid)">
                <strong>Target Cal:</strong> {profile.get('target_calories','–')} kcal
            </div>
            <div style="font-size:0.78rem;color:var(--text-mid)">
                <strong>Protein:</strong> {profile.get('protein_g','–')}g
            </div>
            <div style="font-size:0.78rem;color:var(--text-mid)">
                <strong>Carbs:</strong> {profile.get('carbs_g','–')}g
            </div>
            <div style="font-size:0.78rem;color:var(--text-mid)">
                <strong>Fat:</strong> {profile.get('fat_g','–')}g
            </div>
            <div style="font-size:0.78rem;color:var(--text-mid)">
                <strong>Water:</strong> {profile.get('water_litres','–')}L/day
            </div>
            <div style="font-size:0.78rem;color:var(--text-mid)">
                <strong>Goal:</strong> {profile.get('goal','–')}
            </div>
        </div>"""

    st.markdown(f"""
    <div class="pipeline-wrap">
        <div class="pipeline-header">
            <div>
                <div class="pipeline-title">🧠 AI Decision Engine</div>
            </div>
            <div class="pipeline-live">{status_label}</div>
        </div>
        <div class="pipeline-body">
            <div class="pipeline-flow">{flow_html}</div>
            <div class="pipe-data-row">{chips_html}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Agent detail cards (below the pipeline)
    st.markdown("<br>", unsafe_allow_html=True)
    section_header("🤖 Agent Responsibilities")

    agents = [
        ("🔬", "Nutrition Agent",       "BMI / BMR / TDEE / macronutrient targets / hydration goal / meal scoring formula",        agent_status[0] if agent_status else ""),
        ("🍽️", "Meal Planning Agent",   "Daily plans / 7-day weekly plans / meal swap (3 alternatives) / grocery list generation",  agent_status[1] if agent_status else ""),
        ("💡", "Health Insights Agent", "BMI insight / macro imbalance alerts / goal tips / food recommendations / risk alerts",     agent_status[2] if agent_status else ""),
        ("📸", "Food Image Agent",      "Accepts uploaded image → base64 encode → Claude Vision API → calorie + macro estimates",    agent_status[3] if agent_status else ""),
        ("💬", "Chat Assistant Agent",  "Full conversation history → Claude API with user profile + meal plan as system context",    agent_status[4] if agent_status else ""),
    ]

    cols = st.columns(5)
    for i, (icon, name, role, stat) in enumerate(agents):
        with cols[i]:
            calls = ""
            if stat:
                # Extract call count from status line like "calls: 2 | last: 14.2 ms"
                import re
                m = re.search(r'calls: (\d+).*?last: ([\d.]+)', stat)
                if m:
                    calls = f"calls: {m.group(1)} · {m.group(2)} ms"

            st.markdown(f"""
            <div class="agent-detail">
                <div class="ad-icon">{icon}</div>
                <div class="ad-name">{name}</div>
                <div class="ad-role">{role}</div>
                {"<div class='ad-stat'>"+calls+"</div>" if calls else ""}
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# GROCERY LIST
# ─────────────────────────────────────────────────────────────────────────────

def render_grocery_category(category: str, items: list):
    """Renders one grocery category card."""
    items_html = "".join(f'<span class="grocery-item">{item}</span>' for item in items)
    st.markdown(f"""
    <div class="grocery-cat">
        <div class="grocery-cat-header">{category}</div>
        <div>{items_html}</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HYDRATION TRACKER
# ─────────────────────────────────────────────────────────────────────────────

def render_hydration_ring(drunk_ml: int, goal_ml: int):
    """Big hydration progress display."""
    pct      = min(drunk_ml / max(goal_ml, 1), 1.0)
    pct_int  = int(pct * 100)
    width    = f"{pct_int}%"
    glasses  = int(drunk_ml / 250)
    total_gl = int(goal_ml / 250)

    glass_icons = ""
    for i in range(min(total_gl, 10)):
        cls = "filled" if i < glasses else "empty"
        glass_icons += f'<span class="glass-icon {cls}">🥤</span>'

    st.markdown(f"""
    <div class="hydration-ring-wrap">
        <div class="hydration-ring-val">{drunk_ml}<span class="hydration-ring-unit"> ml</span></div>
        <div class="hydration-ring-goal">of {goal_ml} ml daily goal · {pct_int}% complete</div>
        <div class="hydration-track">
            <div class="hydration-fill" style="width:{width}"></div>
        </div>
        <div class="glass-grid">{glass_icons}</div>
        <div style="font-size:0.78rem;color:var(--text-muted)">
            {glasses} of {total_gl} glasses (250 ml each)
        </div>
    </div>""", unsafe_allow_html=True)


def render_hydration_schedule(schedule: list):
    """Renders the recommended drinking schedule rows."""
    for time_lbl, tip in schedule:
        st.markdown(f"""
        <div class="schedule-row">
            <span class="sr-time">{time_lbl}</span>
            <span class="sr-tip">{tip}</span>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def render_sidebar_logo():
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">🥗</div>
        <div class="logo-name">SmartMeal</div>
        <div class="logo-tag">Multi-Agent System</div>
    </div>""", unsafe_allow_html=True)


def render_sidebar_stats(profile: dict):
    """Quick-glance stats shown in sidebar after profile is analysed."""
    bmi_color = {"Normal Weight":"#16A34A","Underweight":"#2563EB",
                 "Overweight":"#D97706","Obese":"#DC2626"}.get(profile.get("bmi_category",""),"#16A34A")
    stats = [
        ("BMI", f"{profile.get('bmi', 'N/A')} — {profile.get('bmi_category', '')}"),
        ("Calories", f"{profile.get('target_calories', profile.get('calories', 'N/A'))} kcal/day"),
        ("Protein",  f"{profile.get('protein_g', profile.get('protein', 'N/A'))}g · "
             f"Carbs {profile.get('carbs_g', profile.get('carbs', 'N/A'))}g"),
        ("Water", f"{profile.get('water_litres', profile.get('water', 'N/A'))} L/day"),
        ("Goal", profile.get("goal", "–")),
    ]
    for label, value in stats:
        st.markdown(f"""
        <div class="sb-stat">
            <span class="sb-label">{label}</span>
            <span class="sb-value">{value}</span>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TOP NAV BAR
# ─────────────────────────────────────────────────────────────────────────────

def render_topbar(ready: bool = False, profile: dict = None):
    """Renders the app-level topbar with badges."""
    agents = ["🔬 NutritionAgent","🍽️ MealPlanningAgent",
              "💡 InsightsAgent","📸 ImageAgent","💬 ChatAgent"]
    badges_html = ""
    for a in agents:
        cls = "active" if ready else ""
        badges_html += f'<span class="topbar-badge {cls}">{a}</span>'

    status_dot = "🟢" if ready else "⚪"
    status_txt = f"Profile analysed · {profile.get('goal','')} · {profile.get('diet_preference','')}" if ready else "Fill your profile in the sidebar to get started"

    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-left">
            <span class="topbar-icon">🥗</span>
            <div>
                <div class="topbar-title">SmartMeal</div>
                <div class="topbar-sub">{status_dot} {status_txt}</div>
            </div>
        </div>
        <div class="topbar-badges">{badges_html}</div>
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# INSIGHT CARD
# ─────────────────────────────────────────────────────────────────────────────

def insight_card(content: str, kind: str = ""):
    """kind: "" | amber | blue | purple | red | teal"""
    st.markdown(f'<div class="insight-card {kind}">{content}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# AUTH PAGE COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def render_landing_page():
    """Full-page landing hero with feature grid and CTA buttons."""
    st.markdown("""
    <div style="text-align:center;padding:2rem 1rem 1rem">
        <div style="font-size:4rem;margin-bottom:0.5rem">🥗</div>
        <h1 style="font-family:'Instrument Serif',serif;font-size:3rem;
                   color:var(--green-900);line-height:1.1;margin-bottom:0.5rem">
            SmartMeal <span style="color:var(--green-700);font-style:italic"></span>
        </h1>
        <p style="font-size:1rem;color:var(--text-muted);max-width:500px;
                  margin:0 auto 1.5rem;line-height:1.65">
            Your personalised AI nutrition system — multi-agent meal planning,
            calorie analysis, and conversational coaching, all in one place.
        </p>
    </div>""", unsafe_allow_html=True)

    badges = ["🔬 NutritionAgent","🍽️ MealPlanningAgent","💡 InsightsAgent","📸 ImageAgent","💬 ChatAgent"]
    badge_html = "".join(f'<span class="lh-badge">{b}</span>' for b in badges)
    st.markdown(f'<div class="lh-badges" style="justify-content:center;margin-bottom:1.5rem">{badge_html}</div>', unsafe_allow_html=True)

    feats = [
        ("🔬","Multi-Agent AI",  "5 specialised AI agents coordinate to deliver personalised nutrition intelligence."),
        ("🔐","Secure Profiles", "Data stored locally in SQLite with hashed passwords — never plaintext."),
        ("📅","Weekly Planning", "Auto-generate 7-day meal plans, grocery lists, and weekly nutrition summaries."),
        ("📸","Image Calories",  "Upload a photo of any meal — Claude Vision estimates the calories and macros."),
        ("💬","AI Coach",        "Ask anything nutrition-related. Claude knows your profile and today's meals."),
        ("📊","Smart Dashboard", "BMI, TDEE, macro targets, hydration tracker, and health projections."),
    ]
    cols = st.columns(3)
    for i, (em, name, desc) in enumerate(feats):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="meal-wrap" style="margin-bottom:0.8rem;text-align:center">
                <div class="meal-header" style="padding:1rem">
                    <div style="font-size:2rem">{em}</div>
                    <div class="meal-name" style="margin-top:0.3rem">{name}</div>
                </div>
                <div class="meal-body"><div style="font-size:0.8rem;color:var(--text-muted);line-height:1.5">{desc}</div></div>
            </div>""", unsafe_allow_html=True)


def render_auth_logo():
    st.markdown("""
    <div class="auth-logo">
        <div class="al-icon">🥗</div>
        <div class="al-name">SmartMeal</div>
        <div class="al-tag">Multi-Agent Nutrition System</div>
    </div>""", unsafe_allow_html=True)


def render_profile_setup_progress(step: int):
    steps = [
        ("1","Physical Stats","Height, weight, age, gender"),
        ("2","Goals & Diet",  "Fitness goal and food preferences"),
        ("3","Ready to Go",   "Your dashboard awaits"),
    ]
    for i, (num, title, sub) in enumerate(steps):
        s = i + 1
        cls = "done" if s < step else ("current" if s == step else "")
        st.markdown(f"""
        <div class="setup-step {cls}">
            <div class="setup-dot"></div>
            <div>
                <div style="font-weight:700">{title}</div>
                <div style="font-size:0.72rem;opacity:0.7;margin-top:0.1rem">{sub}</div>
            </div>
        </div>""", unsafe_allow_html=True)


def render_user_topbar(user: dict, profile: dict = None, ready: bool = False):
    initials = "".join(w[0].upper() for w in (user.get("name","U").split())[:2])
    agents   = ["🔬","🍽️","💡","📸","💬"]
    badge_cls = "active" if ready else ""
    badges   = "".join(f'<span class="topbar-badge {badge_cls}">{a}</span>' for a in agents)
    status   = f"Goal: {profile.get('fitness_goal','–')} · Diet: {profile.get('diet_preference','–')}" if (profile and ready) else "Set up your profile to start →"
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-left">
            <span class="topbar-icon">🥗</span>
            <div>
                <div class="topbar-title">SmartMeal</div>
                <div class="topbar-sub">{'🟢 ' if ready else '⚪ '}{status}</div>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:1rem">
            <div class="topbar-badges">{badges}</div>
            <div style="display:flex;align-items:center;gap:0.5rem">
                <div class="user-avatar">{initials}</div>
                <div style="font-size:0.82rem;font-weight:700;color:var(--text-dark)">{user.get('name','')}</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def render_meal_history(history: list):
    if not history:
        st.markdown('<div class="strip-blue">No meal plans generated yet.</div>', unsafe_allow_html=True)
        return
    for h in history:
        t    = h.get("plan", {}).get("daily_totals", {})
        cals = h.get("calories") or t.get("calories","–")
        st.markdown(f"""
        <div class="history-card">
            <div>
                <div class="hc-date">📅 {h.get('plan_date','–')}</div>
                <div class="hc-cals">🔥 {cals} kcal · 💪 {t.get('protein','–')}g · 🌾 {t.get('carbs','–')}g · 🥑 {t.get('fat','–')}g</div>
            </div>
            <div style="font-size:0.72rem;color:var(--green-700);font-weight:700">{h.get('plan_type','daily').title()}</div>
        </div>""", unsafe_allow_html=True)
