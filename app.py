import streamlit as st
from api import get_pokemon, get_damaging_moves_for_pokemon, get_all_pokemon_names
from battle import simulate_battle
from charts import stats_comparison_df, make_stats_bar_chart, make_radar_chart, make_hp_line_chart

st.set_page_config(page_title="Pokémon Combat Simulator", layout="wide", page_icon="⚔️")

# ── GLOBAL STYLES ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stat-label  { font-size: 0.78rem; color: #888; margin-bottom: 2px; }
    .stat-value  { font-size: 0.85rem; font-weight: 700; color: #eee; }
    .stat-row    { margin-bottom: 6px; }
    .type-badge  {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 4px;
        color: white;
        background: #555;
    }
    .move-card {
        background: #1e1e2e;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 6px;
    }
    .move-stat { font-size: 0.82rem; color: #aaa; }
    .move-val  { font-weight: 700; color: #fff; }
    .winner-banner {
        text-align: center;
        font-size: 2rem;
        font-weight: 800;
        padding: 18px;
        border-radius: 12px;
        background: linear-gradient(135deg, #f6d365, #fda085);
        color: #1a1a2e;
        margin-bottom: 16px;
    }
    /* tighten up the expander padding so the grid feels compact */
    [data-testid="stExpander"] details summary {
        font-size: 0.95rem;
    }
    /* make grid buttons small */
    .poke-grid button {
        padding: 2px 4px !important;
        font-size: 0.65rem !important;
    }
</style>
""", unsafe_allow_html=True)

TYPE_COLORS = {
    "fire": "#F08030", "water": "#6890F0", "grass": "#78C850",
    "electric": "#F8D030", "psychic": "#F85888", "ice": "#98D8D8",
    "dragon": "#7038F8", "dark": "#705848", "fairy": "#EE99AC",
    "normal": "#A8A878", "fighting": "#C03028", "flying": "#A890F0",
    "poison": "#A040A0", "ground": "#E0C068", "rock": "#B8A038",
    "bug": "#A8B820", "ghost": "#705898", "steel": "#B8B8D0",
}

STAT_COLORS = {
    "hp":              "#4CAF50",
    "attack":          "#F44336",
    "defense":         "#2196F3",
    "special-attack":  "#9C27B0",
    "special-defense": "#00BCD4",
    "speed":           "#FF9800",
}

STAT_LABELS = {
    "hp": "HP", "attack": "ATK", "defense": "DEF",
    "special-attack": "Sp.ATK", "special-defense": "Sp.DEF", "speed": "SPD",
}

MAX_STAT   = 255
SPRITE_URL = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{}.png"
GRID_COLS  = 6


def type_badge(type_name):
    color = TYPE_COLORS.get(type_name.lower(), "#555")
    return f'<span class="type-badge" style="background:{color}">{type_name.capitalize()}</span>'


def render_stat_bar(label, value, max_val=MAX_STAT, color="#4CAF50"):
    pct = min(value / max_val, 1.0)
    st.markdown(f"""
    <div class="stat-row">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;">
            <span class="stat-label">{label}</span>
            <span class="stat-value">{value}</span>
        </div>
        <div style="background:#333; border-radius:999px; height:8px; overflow:hidden;">
            <div style="width:{pct*100:.1f}%; background:{color}; height:100%; border-radius:999px;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_pokemon_stats(p):
    if not p:
        return
    stats = {s["stat"]["name"]: s["base_stat"] for s in p.get("stats", [])}
    for key in ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]:
        render_stat_bar(STAT_LABELS[key], stats.get(key, 0), color=STAT_COLORS[key])


def pokemon_selector(slot_key, default, all_names):
    """
    Visual Pokémon selector:
    - Shows current selection (sprite + name + types)
    - Expander with search + image grid to change it
    """
    sel_key = f"sel_{slot_key}"

    if sel_key not in st.session_state:
        st.session_state[sel_key] = default

    name = st.session_state[sel_key]
    idx  = (all_names.index(name) + 1) if name in all_names else 1

    # ── current selection card ────────────────────────────────────────────────
    p = get_pokemon(name)
    with st.container(border=True):
        c_img, c_info = st.columns([1, 3])
        with c_img:
            st.image(SPRITE_URL.format(idx), width=100)
        with c_info:
            if p:
                types  = [t["type"]["name"] for t in p.get("types", [])]
                badges = "".join(type_badge(t) for t in types)
                st.markdown(
                    f"<div style='font-size:1.3rem;font-weight:800;padding-top:10px'>"
                    f"{name.title()}</div>{badges}",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"**{name.title()}**")

        # ── expander = "dropdown" ─────────────────────────────────────────────
        with st.expander("🔍 Change Pokémon", expanded=False):
            query = st.text_input(
                "Search",
                key=f"q_{slot_key}",
                placeholder="Type a name to filter…",
                label_visibility="collapsed",
            )

            filtered = (
                [n for n in all_names if query.lower() in n.lower()]
                if query
                else all_names
            )[:24]

            for row_start in range(0, len(filtered), GRID_COLS):
                row = filtered[row_start : row_start + GRID_COLS]
                cols = st.columns(GRID_COLS)
                for j, pname in enumerate(row):
                    pidx = (all_names.index(pname) + 1)
                    with cols[j]:
                        st.image(SPRITE_URL.format(pidx), width=64)
                        if st.button(
                            pname.title(),
                            key=f"pick_{slot_key}_{pname}",
                            use_container_width=True,
                        ):
                            st.session_state[sel_key] = pname
                            st.rerun()

    return p


# ── APP ────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #e94560;
    border-radius: 16px;
    padding: 28px 36px 20px 36px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(233,69,96,0.15);
">
    <div style="font-size: 0.75rem; letter-spacing: 0.35em; color: #e94560; font-weight: 700; text-transform: uppercase; margin-bottom: 8px;">
        ⚔️ &nbsp; Python Group Project &nbsp; ⚔️
    </div>
    <div style="font-size: 2.6rem; font-weight: 900; color: #ffffff; letter-spacing: 0.05em; line-height: 1.1; margin-bottom: 12px;">
        Pokémon Combat Simulator
    </div>
    <div style="
        display: inline-block;
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 999px;
        padding: 6px 20px;
        font-size: 0.82rem;
        color: #aac4e0;
        letter-spacing: 0.04em;
    ">
        Andrea Sabatés &nbsp;·&nbsp; César Gonzalez &nbsp;·&nbsp; Tina Jannasch &nbsp;·&nbsp; Ricardo Velásquez &nbsp;·&nbsp; Martí Solà
    </div>
</div>
""", unsafe_allow_html=True)

pokemon_names = get_all_pokemon_names(limit=151)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("##### Pokémon 1")
    p1 = pokemon_selector("p1", "pikachu", pokemon_names)

with col2:
    st.markdown("##### Pokémon 2")
    p2 = pokemon_selector("p2", "bulbasaur", pokemon_names)

# ── STAT BARS ─────────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns(2, gap="large")

with col1:
    render_pokemon_stats(p1)

with col2:
    render_pokemon_stats(p2)

# ── STAT COMPARISON ───────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Stat Comparison")

if p1 and p2:
    stats_df, stats_melt = stats_comparison_df(p1, p2)
    tab_bar, tab_radar = st.tabs(["Bar Chart", "Radar Chart"])
    with tab_bar:
        st.plotly_chart(make_stats_bar_chart(stats_melt), use_container_width=True)
    with tab_radar:
        st.plotly_chart(make_radar_chart(p1, p2), use_container_width=True)
else:
    st.info("Select 2 valid Pokémon to see stat comparison.")

# ── MOVE SELECTION ────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("🌀 Move Selection")

col1_m, col2_m = st.columns(2, gap="large")

with col1_m:
    p1_selected = None
    if p1:
        with st.spinner("Loading moves…"):
            p1_moves = get_damaging_moves_for_pokemon(p1["name"])
        if p1_moves:
            p1_move_name = st.selectbox("Pokémon 1 move", [m["name"] for m in p1_moves])
            p1_selected  = next(m for m in p1_moves if m["name"] == p1_move_name)
            move_color = TYPE_COLORS.get(p1_selected["type"], "#555")
            st.markdown(f"""
            <div class="move-card">
                <span class="type-badge" style="background:{move_color}">{p1_selected['type'].capitalize()}</span>
                <span class="move-stat" style="margin-left:8px;">
                    Power <span class="move-val">{p1_selected['power']}</span>
                    &nbsp;·&nbsp; PP <span class="move-val">{p1_selected.get('pp','?')}</span>
                </span>
            </div>""", unsafe_allow_html=True)
        else:
            st.warning("No damaging moves found.")

with col2_m:
    p2_selected = None
    if p2:
        with st.spinner("Loading moves…"):
            p2_moves = get_damaging_moves_for_pokemon(p2["name"])
        if p2_moves:
            p2_move_name = st.selectbox("Pokémon 2 move", [m["name"] for m in p2_moves])
            p2_selected  = next(m for m in p2_moves if m["name"] == p2_move_name)
            move_color = TYPE_COLORS.get(p2_selected["type"], "#555")
            st.markdown(f"""
            <div class="move-card">
                <span class="type-badge" style="background:{move_color}">{p2_selected['type'].capitalize()}</span>
                <span class="move-stat" style="margin-left:8px;">
                    Power <span class="move-val">{p2_selected['power']}</span>
                    &nbsp;·&nbsp; PP <span class="move-val">{p2_selected.get('pp','?')}</span>
                </span>
            </div>""", unsafe_allow_html=True)
        else:
            st.warning("No damaging moves found.")

# ── BATTLE ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("⚔️ Battle")

col_btn1, col_btn2, _ = st.columns([1, 1, 4])
start = col_btn1.button("▶ Start Battle", type="primary", use_container_width=True)
col_btn2.button("🔄 Rematch", on_click=lambda: None, use_container_width=True)

if start:
    if not (p1 and p2 and p1_selected and p2_selected):
        st.error("Need 2 valid Pokémon and 1 damaging move each.")
    else:
        winner, battle_log_df, hp_over_time_df = simulate_battle(
            p1, p2, p1_selected, p2_selected
        )

        st.markdown(f'<div class="winner-banner">🏆 {winner.title()} wins!</div>', unsafe_allow_html=True)

        st.write("### HP over Time")
        st.plotly_chart(make_hp_line_chart(hp_over_time_df), use_container_width=True)

        with st.expander("📋 Battle Log", expanded=False):
            st.dataframe(battle_log_df, use_container_width=True)
