# =============================================================================
# ui_styles.py
# All custom CSS for NutriAI v3 — loaded once by app.py via inject_css()
#
# Design Language: "BioGreen" — clinical precision meets organic warmth
#   • Primary:  #0A3D1F  (deep forest)
#   • Accent:   #16A34A  (vibrant green)
#   • Highlight:#4ADE80  (lime glow)
#   • Warm:     #F59E0B  (amber)
#   • Surface:  #F0F7F3  (mint fog)
#   • Cards:    #FFFFFF  with layered shadows
# =============================================================================

import streamlit as st # type: ignore

CSS = """
<style>
/* ═══════════════════════════════════════════════════════════
   FONTS
═══════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Instrument+Serif:ital@0;1&display=swap');

/* ═══════════════════════════════════════════════════════════
   ROOT VARIABLES
═══════════════════════════════════════════════════════════ */
:root {
  --green-950: #052010;
  --green-900: #0A3D1F;
  --green-700: #15803D;
  --green-500: #22C55E;
  --green-300: #86EFAC;
  --green-100: #DCFCE7;
  --green-50:  #F0FDF4;
  --amber:     #F59E0B;
  --amber-bg:  #FFFBEB;
  --blue:      #3B82F6;
  --blue-bg:   #EFF6FF;
  --purple:    #8B5CF6;
  --purple-bg: #F5F3FF;
  --red:       #EF4444;
  --red-bg:    #FEF2F2;
  --teal:      #14B8A6;
  --teal-bg:   #F0FDFA;
  --surface:   #F2F8F4;
  --card:      #FFFFFF;
  --border:    #E2EDE8;
  --text-dark: #0C1F14;
  --text-mid:  #374151;
  --text-muted:#6B7280;
  --shadow-sm: 0 1px 3px rgba(10,61,31,0.06), 0 1px 2px rgba(10,61,31,0.04);
  --shadow-md: 0 4px 12px rgba(10,61,31,0.08), 0 2px 4px rgba(10,61,31,0.04);
  --shadow-lg: 0 12px 32px rgba(10,61,31,0.12), 0 4px 8px rgba(10,61,31,0.06);
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 20px;
}

/* ═══════════════════════════════════════════════════════════
   GLOBAL RESET
═══════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  background: #ffffff !important;
  color: #111111 !important;
}
[data-testid="stAppViewContainer"] {
  background-color: #ffffff !important;
}
h1,h2,h3,h4,h5 { font-family: 'Instrument Serif', serif !important; }

/* Hide default Streamlit menu/footer */
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 0.1rem !important;
padding-left:2rem !important;
padding-right :2rem !important;
padding-bottom: 2rem !important;
max-width: 1300px !important;}

/* Remove top blank space from Streamlit */
header[data-testid="stHeader"] {
    height: 0px !important;
}

[data-testid="stToolbar"] {
    display: none !important;
}
/* ═══════════════════════════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
  color : #111111 !important;
  margin-top :0.2rem !important;
  margin-bottom :0.6rem !important;
}
[data-testid="stAlert"] p {
  color : #111111 !important;
  font-weight :500;
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, var(--green-950) 0%, #0D3320 50%, var(--green-900) 100%) !important;
  border-right: 1px solid rgba(74,222,128,0.1);
}
[data-testid="stSidebar"] > div { padding-top: 1rem; }
[data-testid="stSidebar"] * { color: #D1FAE5 !important; }
[data-testid="stSidebar"] label {
  color: #6EE7B7 !important; font-size: 0.72rem !important;
  font-weight: 700 !important; letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput > div > div > input,
[data-testid="stSidebar"] .stTextInput > div > div > input {
  background: rgba(255,255,255,0.07) !important;
  border: 1px solid rgba(110,231,183,0.2) !important;
  color: #E8F5EE !important;
  border-radius: 8px !important;
  font-size: 0.88rem !important;
}
[data-testid="stSidebar"] .stSelectbox > div > div:focus-within,
[data-testid="stSidebar"] .stNumberInput > div > div > input:focus {
  border-color: rgba(74,222,128,0.5) !important;
  box-shadow: 0 0 0 2px rgba(74,222,128,0.15) !important;
}
[data-testid="stSidebar"] .stRadio > div { gap: 0.3rem; }

/* Sidebar nav logo area */
.sidebar-logo {
  text-align: center; padding: 0.8rem 0 1.2rem;
  border-bottom: 1px solid rgba(74,222,128,0.12);
  margin-bottom: 1rem;
}
.sidebar-logo .logo-icon { font-size: 2.4rem; line-height: 1; }
.sidebar-logo .logo-name {
  font-family: 'Instrument Serif', serif; font-size: 1.4rem;
  color: #E8F5EE !important; margin: 0.2rem 0 0;
}
.sidebar-logo .logo-tag {
  font-size: 0.68rem; color: #6EE7B7 !important;
  letter-spacing: 0.12em; text-transform: uppercase; font-weight: 600;
}

/* Sidebar nav section header */
.sb-section {
  font-size: 0.64rem; font-weight: 800; letter-spacing: 0.14em;
  text-transform: uppercase; color: rgba(110,231,183,0.55) !important;
  padding: 0.6rem 0 0.2rem; margin-top: 0.4rem;
}

/* Sidebar stat pills */
.sb-stat {
  display: flex; justify-content: space-between; align-items: center;
  background: rgba(74,222,128,0.08); border: 1px solid rgba(74,222,128,0.14);
  border-radius: 8px; padding: 0.45rem 0.75rem; margin-bottom: 0.35rem;
}
.sb-stat .sb-label { font-size: 0.73rem; color: #6EE7B7 !important; font-weight: 600; }
.sb-stat .sb-value { font-size: 0.85rem; color: #D1FAE5 !important; font-weight: 700; }

/* ═══════════════════════════════════════════════════════════
   TOP NAVBAR
═══════════════════════════════════════════════════════════ */
.topbar {
  display: flex; align-items: center; justify-content: space-between;
  background: var(--card); border-radius: 3px;
  padding: 1.6rem 2.5rem !important; margin-bottom: 1.4rem;
  box-shadow: var(--shadow-sm); border: 1px solid var(--border);
}
.topbar-left { display: flex; align-items: center; gap: 0.9rem; }
.topbar-icon { font-size: 2rem; }
.topbar-title {
  font-family: 'Instrument Serif', serif; font-size: 1.7rem;
  color: var(--green-900); line-height: 1; margin: 0;
}
.topbar-sub { font-size: 0.78rem; color: var(--text-muted); margin-top: 0.15rem; }
.topbar-badges { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.topbar-badge {
  background: var(--green-50); border: 1px solid var(--green-100);
  color: var(--green-700); border-radius: 20px;
  padding: 0.22rem 0.7rem; font-size: 0.71rem; font-weight: 700;
  letter-spacing: 0.02em;
}
.topbar-badge.active {
  background: var(--green-900); color: var(--green-300);
  border-color: var(--green-700);
  animation: pulse-badge 2s infinite;
}
@keyframes pulse-badge {
  0%,100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
  50%      { box-shadow: 0 0 0 4px rgba(34,197,94,0.15); }
}

/* ═══════════════════════════════════════════════════════════
   SECTION HEADERS
═══════════════════════════════════════════════════════════ */
.sec-head {
  display: flex; align-items: center; gap: 0.6rem;
  font-family: 'Instrument Serif', serif; font-size: 1.35rem;
  color: var(--green-900); margin: 1.6rem 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--green-100);
}
.sec-head::before {
  content: ''; width: 4px; height: 1.2rem;
  background: linear-gradient(180deg, var(--green-500), var(--green-700));
  border-radius: 4px; flex-shrink: 0;
}

/* ═══════════════════════════════════════════════════════════
   METRIC CARDS  
═══════════════════════════════════════════════════════════ */
.mc-wrap {
  background: var(--card); border-radius: var(--radius-md);
  padding: 1.3rem 1.5rem; box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
  position: relative; overflow: hidden;
}
.mc-wrap:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); }
.mc-wrap::after {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--accent-a), var(--accent-b));
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}
.mc-wrap.green  { --accent-a: #16A34A; --accent-b: #4ADE80; }
.mc-wrap.blue   { --accent-a: #2563EB; --accent-b: #60A5FA; }
.mc-wrap.amber  { --accent-a: #D97706; --accent-b: #FCD34D; }
.mc-wrap.purple { --accent-a: #7C3AED; --accent-b: #C4B5FD; }
.mc-wrap.teal   { --accent-a: #0D9488; --accent-b: #5EEAD4; }
.mc-wrap.red    { --accent-a: #DC2626; --accent-b: #FCA5A5; }
.mc-icon { font-size: 1.6rem; margin-bottom: 0.5rem; opacity: 0.85; }
.mc-label {
  font-size: 0.68rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: 0.09em; color: var(--text-muted); margin-bottom: 0.3rem;
}
.mc-value {
  font-family: 'Instrument Serif', serif; font-size: 2.1rem;
  font-weight: 400; color: var(--text-dark); line-height: 1;
}
.mc-unit { font-size: 0.82rem; color: var(--text-muted); margin-left: 3px; }
.mc-sub  { font-size: 0.74rem; color: var(--text-muted); margin-top: 0.3rem; line-height: 1.3; }
.mc-trend {
  display: inline-flex; align-items: center; gap: 0.2rem;
  font-size: 0.72rem; font-weight: 700; margin-top: 0.4rem;
  padding: 0.15rem 0.5rem; border-radius: 20px;
}
.mc-trend.up   { background: #DCFCE7; color: #15803D; }
.mc-trend.down { background: #FEE2E2; color: #B91C1C; }
.mc-trend.ok   { background: #D1FAE5; color: #065F46; }

/* ═══════════════════════════════════════════════════════════
   MACRO PROGRESS BARS (custom)
═══════════════════════════════════════════════════════════ */
.macro-block { margin-bottom: 1rem; }
.macro-block .mb-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0.4rem;
}
.macro-block .mb-label {
  font-size: 0.82rem; font-weight: 700; color: var(--text-mid);
  display: flex; align-items: center; gap: 0.35rem;
}
.macro-block .mb-nums { font-size: 0.78rem; color: var(--text-muted); font-weight: 600; }
.macro-track {
  height: 10px; background: #E5E7EB; border-radius: 10px; overflow: hidden;
}
.macro-fill {
  height: 100%; border-radius: 10px;
  transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}
.macro-fill.protein { background: linear-gradient(90deg, #7C3AED, #A78BFA); }
.macro-fill.carbs   { background: linear-gradient(90deg, #2563EB, #60A5FA); }
.macro-fill.fat     { background: linear-gradient(90deg, #D97706, #FCD34D); }
.macro-fill.fiber   { background: linear-gradient(90deg, #059669, #34D399); }

/* ═══════════════════════════════════════════════════════════
   MEAL CARDS
═══════════════════════════════════════════════════════════ */
.meal-wrap {
  background: var(--card); border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm); border: 1px solid var(--border);
  overflow: hidden; transition: transform 0.18s ease, box-shadow 0.18s ease;
  height: 100%;
}
.meal-wrap:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.meal-header {
  padding: 1rem 1.2rem 0.7rem;
  border-bottom: 1px solid var(--border);
}
.meal-time-row {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 0.5rem;
}
.meal-type-badge {
  font-size: 0.66rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--green-700);
  background: var(--green-50); border: 1px solid var(--green-100);
  padding: 0.15rem 0.55rem; border-radius: 20px;
}
.meal-time-text { font-size: 0.7rem; color: var(--text-muted); }
.meal-icon-row { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.35rem; }
.meal-icon { font-size: 2.2rem; }
.meal-name {
  font-family: 'Instrument Serif', serif; font-size: 1.05rem;
  color: var(--text-dark); line-height: 1.25;
}
.meal-desc { font-size: 0.77rem; color: var(--text-muted); line-height: 1.45; margin-top: 0.25rem; }
.meal-body { padding: 0.9rem 1.2rem; }
.meal-macros { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-bottom: 0.65rem; }
.mmb {
  font-size: 0.71rem; font-weight: 700; padding: 0.18rem 0.55rem;
  border-radius: 20px; white-space: nowrap;
}
.mmb.cal { background: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
.mmb.pro { background: #EDE9FE; color: #5B21B6; border: 1px solid #DDD6FE; }
.mmb.crb { background: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
.mmb.fat { background: #FCE7F3; color: #831843; border: 1px solid #FBCFE8; }
.mmb.fib { background: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }

/* Score bar inside meal card */
.score-row { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; }
.score-label { font-size: 0.72rem; font-weight: 700; color: var(--text-muted); }
.score-bar-track {
  flex: 1; height: 6px; background: #E5E7EB; border-radius: 6px; overflow: hidden;
}
.score-bar-fill {
  height: 100%; border-radius: 6px;
  transition: width 1s cubic-bezier(0.4,0,0.2,1);
}
.score-num {
  font-size: 0.78rem; font-weight: 800; min-width: 2.2rem;
  text-align: right;
}

/* ═══════════════════════════════════════════════════════════
   AI DECISION ENGINE / PIPELINE DIAGRAM
═══════════════════════════════════════════════════════════ */
.pipeline-wrap {
  background: var(--card); border-radius: var(--radius-lg);
  border: 1px solid var(--border); overflow: hidden;
  box-shadow: var(--shadow-md);
}
.pipeline-header {
  background: linear-gradient(135deg, var(--green-950), var(--green-900));
  padding: 1.2rem 1.8rem;
  display: flex; align-items: center; justify-content: space-between;
}
.pipeline-title {
  font-family: 'Instrument Serif', serif; font-size: 1.25rem;
  color: #E8F5EE; margin: 0;
}
.pipeline-subtitle { font-size: 0.75rem; color: #6EE7B7; margin-top: 0.15rem; }
.pipeline-live {
  display: flex; align-items: center; gap: 0.4rem;
  background: rgba(74,222,128,0.15); border: 1px solid rgba(74,222,128,0.3);
  border-radius: 20px; padding: 0.25rem 0.75rem;
  font-size: 0.72rem; font-weight: 700; color: #86EFAC;
}
.pipeline-live::before {
  content: ''; width: 7px; height: 7px; background: #4ADE80;
  border-radius: 50%; animation: blink 1.4s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.3} }

.pipeline-body { padding: 1.6rem 2rem; }
.pipeline-flow {
  display: flex; align-items: stretch; justify-content: center;
  gap: 0; flex-wrap: nowrap; overflow-x: auto; padding-bottom: 0.5rem;
}
.pipe-node {
  display: flex; flex-direction: column; align-items: center;
  min-width: 130px; max-width: 150px; flex: 1;
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--radius-md); padding: 1rem 0.8rem;
  position: relative; transition: all 0.2s;
  cursor: default;
}
.pipe-node:hover { border-color: var(--green-500); box-shadow: 0 0 0 3px rgba(34,197,94,0.1); transform: translateY(-2px); }
.pipe-node.input  { border-color: #60A5FA; background: #EFF6FF; }
.pipe-node.active { border-color: var(--green-500); background: var(--green-50); }
.pipe-node.output { border-color: #C084FC; background: #F5F3FF; }
.pipe-node-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
.pipe-node-name {
  font-size: 0.73rem; font-weight: 700; text-align: center;
  color: var(--text-dark); line-height: 1.3;
}
.pipe-node-sub {
  font-size: 0.63rem; color: var(--text-muted); text-align: center;
  margin-top: 0.25rem; line-height: 1.35;
}
.pipe-node-tag {
  font-size: 0.6rem; font-weight: 800; text-transform: uppercase;
  letter-spacing: 0.07em; padding: 0.12rem 0.45rem;
  border-radius: 20px; margin-top: 0.45rem;
}
.pipe-node.input  .pipe-node-tag { background: #DBEAFE; color: #1E40AF; }
.pipe-node.active .pipe-node-tag { background: var(--green-100); color: var(--green-700); }
.pipe-node.output .pipe-node-tag { background: #EDE9FE; color: #5B21B6; }
.pipe-arrow {
  display: flex; align-items: center; padding: 0 0.3rem;
  color: var(--green-500); font-size: 1.3rem; font-weight: 700;
  flex-shrink: 0; align-self: center;
}

/* Pipeline data flow labels */
.pipe-data-row {
  display: flex; justify-content: space-around; flex-wrap: wrap;
  gap: 0.5rem; margin-top: 1.2rem; padding-top: 1rem;
  border-top: 1px dashed var(--border);
}
.pipe-data-chip {
  display: flex; align-items: center; gap: 0.35rem;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 20px; padding: 0.3rem 0.75rem;
  font-size: 0.72rem; font-weight: 600; color: var(--text-mid);
}
.pipe-data-chip::before {
  content: '→'; color: var(--green-500); font-weight: 800; font-size: 0.8rem;
}

/* Agent detail cards below pipeline */
.agent-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.8rem; margin-top: 1.2rem; }
.agent-detail {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 0.9rem 0.8rem;
  text-align: center; transition: all 0.18s;
}
.agent-detail:hover { border-color: var(--green-500); background: var(--green-50); }
.agent-detail .ad-icon { font-size: 1.4rem; margin-bottom: 0.3rem; }
.agent-detail .ad-name { font-size: 0.72rem; font-weight: 700; color: var(--text-dark); }
.agent-detail .ad-role { font-size: 0.63rem; color: var(--text-muted); margin-top: 0.2rem; line-height: 1.35; }
.agent-detail .ad-stat {
  margin-top: 0.5rem; font-size: 0.65rem; font-weight: 700;
  background: var(--green-100); color: var(--green-700);
  padding: 0.15rem 0.45rem; border-radius: 20px; display: inline-block;
}

/* ═══════════════════════════════════════════════════════════
   GROCERY LIST CARDS
═══════════════════════════════════════════════════════════ */
.grocery-cat {
  background: var(--card); border-radius: var(--radius-md);
  border: 1px solid var(--border); padding: 1.1rem 1.3rem;
  margin-bottom: 0.8rem; box-shadow: var(--shadow-sm);
}
.grocery-cat-header {
  display: flex; align-items: center; gap: 0.5rem;
  font-family: 'Instrument Serif', serif; font-size: 1rem;
  color: var(--text-dark); margin-bottom: 0.7rem;
  padding-bottom: 0.5rem; border-bottom: 1px solid var(--border);
}
.grocery-item {
  display: inline-flex; align-items: center; gap: 0.3rem;
  background: var(--green-50); border: 1px solid var(--green-100);
  color: var(--green-700); border-radius: 20px;
  padding: 0.22rem 0.65rem; font-size: 0.75rem; font-weight: 600;
  margin: 0.18rem; cursor: default; transition: all 0.15s;
}
.grocery-item:hover { background: var(--green-100); border-color: var(--green-300); }
.grocery-item::before { content: '✓'; font-size: 0.65rem; opacity: 0.7; }

/* ═══════════════════════════════════════════════════════════
   HYDRATION TRACKER
═══════════════════════════════════════════════════════════ */
.hydration-ring-wrap {
  background: var(--card); border-radius: var(--radius-lg);
  border: 1px solid var(--border); padding: 2rem;
  text-align: center; box-shadow: var(--shadow-sm);
}
.hydration-ring-val {
  font-family: 'Instrument Serif', serif; font-size: 3.5rem;
  color: var(--teal); line-height: 1;
}
.hydration-ring-unit { font-size: 1rem; color: var(--text-muted); }
.hydration-ring-goal { font-size: 0.85rem; color: var(--text-muted); margin-top: 0.3rem; }
.hydration-track {
  height: 14px; background: #E0F2FE; border-radius: 14px;
  overflow: hidden; margin: 1rem 0;
}
.hydration-fill {
  height: 100%; border-radius: 14px;
  background: linear-gradient(90deg, #0EA5E9, #38BDF8, #7DD3FC);
  transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}
.glass-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin: 1rem 0; }
.glass-icon { font-size: 1.8rem; cursor: default; transition: transform 0.15s; }
.glass-icon.filled { opacity: 1; filter: none; transform: scale(1.05); }
.glass-icon.empty  { opacity: 0.25; filter: grayscale(1); }
.schedule-row {
  display: flex; align-items: center; gap: 0.8rem;
  background: var(--teal-bg); border: 1px solid #CCFBF1;
  border-radius: var(--radius-sm); padding: 0.6rem 1rem;
  margin-bottom: 0.45rem;
}
.schedule-row .sr-time { font-size: 0.78rem; font-weight: 700; color: #0F766E; min-width: 7rem; }
.schedule-row .sr-tip  { font-size: 0.78rem; color: var(--text-mid); }

/* ═══════════════════════════════════════════════════════════
   INSIGHT CARDS
═══════════════════════════════════════════════════════════ */
.insight-card {
  background: var(--card); border-radius: var(--radius-sm);
  padding: 1rem 1.2rem; margin-bottom: 0.65rem;
  border-left: 4px solid var(--green-500);
  box-shadow: var(--shadow-sm); font-size: 0.85rem;
  line-height: 1.65; color: var(--text-mid);
}
.insight-card.amber  { border-left-color: var(--amber); }
.insight-card.blue   { border-left-color: var(--blue); }
.insight-card.purple { border-left-color: var(--purple); }
.insight-card.red    { border-left-color: var(--red); }
.insight-card.teal   { border-left-color: var(--teal); }
.insight-card strong { color: var(--text-dark); }

/* Alert strips */
.strip-green  { background: var(--green-50);  border: 1px solid var(--green-100); color: #166534; border-radius: var(--radius-sm); padding: 0.65rem 1rem; margin-bottom: 0.5rem; font-size: 0.84rem; line-height: 1.5; }
.strip-amber  { background: var(--amber-bg);  border: 1px solid #FDE68A; color: #92400E; border-radius: var(--radius-sm); padding: 0.65rem 1rem; margin-bottom: 0.5rem; font-size: 0.84rem; }
.strip-red    { background: var(--red-bg);    border: 1px solid #FECACA; color: #991B1B; border-radius: var(--radius-sm); padding: 0.65rem 1rem; margin-bottom: 0.5rem; font-size: 0.84rem; }
.strip-blue   { background: var(--blue-bg);   border: 1px solid #BFDBFE; color: #1E40AF; border-radius: var(--radius-sm); padding: 0.65rem 1rem; margin-bottom: 0.5rem; font-size: 0.84rem; }
.strip-purple { background: var(--purple-bg); border: 1px solid #DDD6FE; color: #5B21B6; border-radius: var(--radius-sm); padding: 0.65rem 1rem; margin-bottom: 0.5rem; font-size: 0.84rem; }

/* ═══════════════════════════════════════════════════════════
   CHAT INTERFACE
═══════════════════════════════════════════════════════════ */
.chat-wrap {
  background: var(--card); border-radius: var(--radius-lg);
  border: 1px solid var(--border); overflow: hidden;
  box-shadow: var(--shadow-sm);
}
.chat-header {
  background: linear-gradient(135deg, var(--green-950), var(--green-900));
  padding: 1rem 1.5rem; display: flex; align-items: center; gap: 0.8rem;
}
.chat-header-icon { font-size: 1.6rem; }
.chat-header-title { font-family: 'Instrument Serif', serif; font-size: 1.1rem; color: #E8F5EE; }
.chat-header-status { font-size: 0.72rem; color: #6EE7B7; margin-top: 0.1rem; }
.chat-body { padding: 1.2rem; min-height: 200px; max-height: 440px; overflow-y: auto; }
.chat-msg-user {
  background: linear-gradient(135deg, var(--green-900), var(--green-700));
  color: #fff; border-radius: 16px 16px 4px 16px;
  padding: 0.75rem 1.1rem; margin: 0.5rem 0 0.5rem 3.5rem;
  font-size: 0.86rem; line-height: 1.55;
  box-shadow: 0 2px 8px rgba(10,61,31,0.2);
}
.chat-msg-ai {
  background: var(--surface); color: var(--text-dark);
  border-radius: 16px 16px 16px 4px; border: 1px solid var(--border);
  padding: 0.75rem 1.1rem; margin: 0.5rem 3.5rem 0.5rem 0;
  font-size: 0.86rem; line-height: 1.55;
  box-shadow: var(--shadow-sm);
}
.chat-msg-ai strong { color: var(--green-700); }
.chat-suggestion-row { display: flex; flex-wrap: wrap; gap: 0.4rem; padding: 0.5rem 0; }
.chat-sug {
  background: var(--green-50); border: 1px solid var(--green-100);
  color: var(--green-700); border-radius: 20px;
  padding: 0.35rem 0.85rem; font-size: 0.77rem; font-weight: 600;
  cursor: pointer; transition: all 0.15s;
}
.chat-sug:hover { background: var(--green-100); border-color: var(--green-300); }

/* ═══════════════════════════════════════════════════════════
   WEEKLY PLAN EXPANDABLE ROWS
═══════════════════════════════════════════════════════════ */
.day-row-header {
  display: flex; align-items: center; justify-content: space-between;
  background: linear-gradient(90deg, var(--green-50), var(--card));
  border: 1px solid var(--green-100); border-radius: var(--radius-sm);
  padding: 0.7rem 1.2rem; margin-bottom: 0.3rem;
}
.day-name { font-weight: 700; color: var(--green-900); font-size: 0.9rem; }
.day-cals { font-size: 0.8rem; color: var(--text-muted); font-weight: 600; }
.mini-meal {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 0.8rem;
  text-align: center;
}
.mini-meal .mm-icon { font-size: 1.5rem; }
.mini-meal .mm-type { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--green-700); }
.mini-meal .mm-name { font-size: 0.77rem; font-weight: 600; color: var(--text-dark); margin-top: 0.2rem; line-height: 1.3; }
.mini-meal .mm-cal  { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.2rem; }
.mini-meal .mm-score { font-size: 0.7rem; font-weight: 700; margin-top: 0.3rem; }

/* ═══════════════════════════════════════════════════════════
   FOOD CARD GRID (Indian diet showcase)
═══════════════════════════════════════════════════════════ */
.food-showcase {
  background: var(--card); border-radius: var(--radius-md);
  border: 1px solid var(--border); padding: 1rem;
  text-align: center; transition: all 0.18s;
  box-shadow: var(--shadow-sm);
}
.food-showcase:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--green-300); }
.food-showcase .fs-icon { font-size: 2rem; margin-bottom: 0.4rem; }
.food-showcase .fs-name { font-weight: 700; font-size: 0.85rem; color: var(--text-dark); }
.food-showcase .fs-cal  { font-size: 0.72rem; background: #FEF3C7; color: #92400E; padding: 0.12rem 0.45rem; border-radius: 20px; display: inline-block; margin-top: 0.3rem; }
.food-showcase .fs-pro  { font-size: 0.72rem; background: #EDE9FE; color: #5B21B6; padding: 0.12rem 0.45rem; border-radius: 20px; display: inline-block; margin-top: 0.2rem; }
.food-showcase .fs-note { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.4rem; line-height: 1.35; }

/* ═══════════════════════════════════════════════════════════
   EMPTY STATE
═══════════════════════════════════════════════════════════ */
.empty-state {
  text-align: center; padding: 3rem 2rem;
  background: var(--card); border-radius: var(--radius-lg);
  border: 2px dashed var(--border);
}
.empty-state .es-icon { font-size: 3.5rem; margin-bottom: 0.8rem; opacity: 0.6; }
.empty-state .es-title { font-family: 'Instrument Serif', serif; font-size: 1.4rem; color: var(--text-dark); margin-bottom: 0.5rem; }
.empty-state .es-sub   { font-size: 0.88rem; color: var(--text-muted); line-height: 1.55; max-width: 380px; margin: 0 auto; }

/* ═══════════════════════════════════════════════════════════
   STREAMLIT OVERRIDES
═══════════════════════════════════════════════════════════ */
/* Tab navigation */
.stTabs [data-baseweb="tab-list"] {
  gap: 4px; background: var(--card);
  border-radius: var(--radius-md); padding: 0.3rem;
  border: 1px solid var(--border); margin-bottom: 0.5rem;
}
.stTabs [data-baseweb="tab"] {
  background: transparent; border: none;
  border-radius: var(--radius-sm); padding: 0.45rem 0.9rem;
  font-weight: 600; color: var(--text-muted); font-size: 0.82rem;
  transition: all 0.15s;
}
.stTabs [data-baseweb="tab"]:hover { background: var(--green-50); color: var(--green-700); }
.stTabs [aria-selected="true"] {
  background: var(--green-900) !important;
  color: var(--green-300) !important;
  box-shadow: 0 1px 4px rgba(10,61,31,0.2);
}
/* Buttons */
div[data-testid="stButton"] > button {
  background: linear-gradient(135deg, var(--green-900), var(--green-700));
  color: #fff; border: none; border-radius: var(--radius-sm);
  font-weight: 700; padding: 0.5rem 1.4rem; font-size: 0.84rem;
  font-family: 'Plus Jakarta Sans', sans-serif;
  transition: opacity 0.18s, transform 0.18s;
  letter-spacing: 0.01em;
}
div[data-testid="stButton"] > button:hover {
  opacity: 0.88; transform: translateY(-1px);
}
div[data-testid="stButton"] > button:active { transform: translateY(0); }
/* Progress bars */
.stProgress > div > div > div > div { border-radius: 10px !important; }
/* Expander */
.streamlit-expanderHeader {
  background: var(--surface) !important; border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border) !important; font-weight: 600 !important;
}
/* Metrics */
[data-testid="stMetricValue"] { font-family: 'Instrument Serif', serif !important; color: var(--text-dark) !important; }
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted) !important; }

/* Info/success/error boxes */
.stAlert { border-radius: var(--radius-sm) !important; }

/* Download button */
div[data-testid="stDownloadButton"] > button {
  background: linear-gradient(135deg, #1D4ED8, #3B82F6);
}

/* Divider */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ═══════════════════════════════════════════════════════════
   AUTH PAGES (landing, login, register)
═══════════════════════════════════════════════════════════ */
.auth-shell {
  min-height: 100vh; display: flex; align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--green-950) 0%, #0D3320 55%, #0F5C30 100%);
}
.auth-card {
  background: var(--card); border-radius: 24px;
  padding: 2.8rem 2.4rem; width: 100%; max-width: 420px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.35);
}
.auth-logo { text-align: center; margin-bottom: 1.8rem; }
.auth-logo .al-icon { font-size: 3rem; }
.auth-logo .al-name {
  font-family: 'Instrument Serif', serif; font-size: 2rem;
  color: var(--green-900); margin: 0.3rem 0 0.1rem;
}
.auth-logo .al-tag {
  font-size: 0.72rem; color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;
}
.auth-tab-row {
  display: flex; gap: 0.5rem; margin-bottom: 1.6rem;
}
.auth-tab {
  flex: 1; padding: 0.55rem; border-radius: 10px;
  font-weight: 700; font-size: 0.85rem; text-align: center;
  cursor: pointer; border: 2px solid var(--border);
  color: var(--text-muted); background: var(--surface);
  transition: all 0.15s;
}
.auth-tab.active {
  background: var(--green-900); color: var(--green-300);
  border-color: var(--green-700);
}
.auth-divider {
  text-align: center; color: var(--text-muted);
  font-size: 0.75rem; margin: 1rem 0;
  position: relative;
}
.auth-divider::before, .auth-divider::after {
  content: ''; position: absolute; top: 50%;
  width: 42%; height: 1px; background: var(--border);
}
.auth-divider::before { left: 0; }
.auth-divider::after  { right: 0; }
/* Fix login/register text */
.stTextInput label,
.stTextInput div,
.stTextInput input,
.stMarkdown,
.stForm label {
  color: #111111 !important;
}

/* Fix input fields */
.stTextInput input {
  background: #ffffff !important;
  color: #111111 !important;
  border: 1px solid #d1d5db !important;
}
/* Ensure auth card is white */
.auth-card {
  background: linear-gradient(135deg, #166534, #16A34A) !important;
  border-radius: 24px;
  padding: 2.8rem 2.4rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.35);
  color: white !important;
}
.auth-card * {
  color: #ECFDF5 !important;
}
/* Auth buttons */
.stButton > button {
  background-color: #065F46 !important;
  color: white !important;
  border-radius: 10px !important;
  border: none !important;
}

.stButton > button:hover {
  background-color: #064E3B !important;
  color: white !important;
}
/* Landing page hero */
.landing-hero {
  background: linear-gradient(135deg, var(--green-950), #0D3320, #0A5530);
  min-height: 100vh; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 2rem; text-align: center;
}
.lh-icon  { font-size: 5rem; margin-bottom: 0.8rem; }
.lh-title {
  font-family: 'Instrument Serif', serif; font-size: 3.5rem;
  color: #fff; line-height: 1.05; margin-bottom: 0.6rem;
}
.lh-title span { color: var(--green-300); font-style: italic; }
.lh-sub   {
  font-size: 1.05rem; color: rgba(255,255,255,0.72);
  max-width: 520px; line-height: 1.6; margin-bottom: 2rem;
}
.lh-badges { display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; margin-bottom: 2.5rem; }
.lh-badge {
  background: rgba(74,222,128,0.12); border: 1px solid rgba(74,222,128,0.25);
  color: var(--green-300); padding: 0.3rem 0.85rem;
  border-radius: 20px; font-size: 0.78rem; font-weight: 600;
}
.lh-features {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
  max-width: 720px; margin: 0 auto 2.5rem;
}
.lh-feat {
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  border-radius: 14px; padding: 1.2rem; text-align: left;
}
.lh-feat .lf-icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
.lh-feat .lf-name { font-size: 0.88rem; font-weight: 700; color: #E8F5EE; margin-bottom: 0.2rem; }
.lh-feat .lf-desc { font-size: 0.75rem; color: rgba(255,255,255,0.55); line-height: 1.45; }

/* Profile setup stepper */
.setup-step {
  display: flex; align-items: center; gap: 0.7rem;
  padding: 0.6rem 0.9rem; border-radius: 10px;
  font-size: 0.82rem; font-weight: 600; color: var(--text-muted);
  border: 1px solid var(--border); margin-bottom: 0.4rem;
}
.setup-step.done    { border-color: var(--green-300); color: var(--green-700); background: var(--green-50); }
.setup-step.current { border-color: var(--green-500); color: var(--green-900); background: var(--green-50); box-shadow: 0 0 0 3px rgba(34,197,94,0.15); }
.setup-dot { width:10px; height:10px; border-radius:50%; background:var(--border); }
.setup-step.done    .setup-dot { background: var(--green-500); }
.setup-step.current .setup-dot { background: var(--green-500); animation: blink 1.2s infinite; }

/* User avatar in topbar */
.user-avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg, var(--green-700), var(--green-500));
  display: inline-flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 800; font-size: 0.85rem;
  flex-shrink: 0;
}

/* History cards */
.history-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-sm); padding: 0.9rem 1.1rem;
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 0.5rem; box-shadow: var(--shadow-sm);
  transition: box-shadow 0.15s;
}
.history-card:hover { box-shadow: var(--shadow-md); }
.hc-date { font-size: 0.78rem; font-weight: 700; color: var(--green-700); }
.hc-cals { font-size: 0.82rem; color: var(--text-muted); }

/* Account settings card */
.account-card {
  background: var(--card); border: 1px solid var(--border);
  border-radius: var(--radius-md); padding: 1.6rem 1.8rem;
  box-shadow: var(--shadow-sm); margin-bottom: 1.2rem;
}
.account-card h3 {
  font-family: 'Instrument Serif', serif; font-size: 1.1rem;
  color: var(--text-dark); margin: 0 0 1rem;
  padding-bottom: 0.6rem; border-bottom: 1px solid var(--border);
}
/* Force auth card green */
.auth-card {
  background: linear-gradient(135deg, #166534, #16A34A) !important;
  color: white !important;
}

/* Fix all text inside auth card */
.auth-card * {
  color: #ECFDF5 !important;
}

/* Override Streamlit button */
button {
  background-color: #065F46 !important;
  color: white !important;
  border-radius: 10px !important;
  border: none !important;
}

/* Prevent white hover */
button:hover {
  background-color: #064E3B !important;
  color: white !important;
}

/* Prevent focus white flash */
button:focus {
  background-color: #065F46 !important;
  color: white !important;
}
/* Add spacing below Streamlit header */
.block-container {
    padding-top: 3rem !important;
}
/* ===== Fix expander header hover ===== */

/* normal state */
[data-testid="stExpander"] summary {
    background-color: #111827 !important;   /* dark background */
    color: white !important;
}

/* hover state */
[data-testid="stExpander"] summary:hover {
    background-color: #111827 !important;   /* keep same color */
    color: white !important;
}

/* active / open state */
[data-testid="stExpander"][open] summary {
    background-color: #111827 !important;
}

/* remove white flash on click */
[data-testid="stExpander"] summary:focus {
    background-color: #111827 !important;
    outline: none !important;
}
/* Hide Streamlit top navbar */
header[data-testid="stHeader"] {
    display: none;
}

/* Hide toolbar */
[data-testid="stToolbar"] {
    display: none;
}

/* Remove top spacing */
.block-container {
    padding-top: 1rem;
}
</style>
"""

def inject_css():
    """Call once at top of app.py to inject all custom styles."""
    st.markdown(CSS, unsafe_allow_html=True)
