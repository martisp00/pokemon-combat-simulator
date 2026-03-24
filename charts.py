import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def stats_comparison_df(p1, p2):
    def to_stats(p):
        return {s["stat"]["name"]: s["base_stat"] for s in p.get("stats", [])}

    s1 = to_stats(p1)
    s2 = to_stats(p2)

    stats_order = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]

    df = pd.DataFrame({
        "stat":      stats_order,
        p1["name"]: [s1.get(k, 0) for k in stats_order],
        p2["name"]: [s2.get(k, 0) for k in stats_order],
    })

    # ✅ REQUIRED: melt() para grouped bar chart
    df_melt = df.melt(id_vars="stat", var_name="Pokemon", value_name="Value")
    return df, df_melt


def make_stats_bar_chart(df_melt):
    fig = px.bar(
        df_melt, x="stat", y="Value", color="Pokemon",
        barmode="group",
        title="Base Stats Comparison",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_layout(xaxis_title="Stat", yaxis_title="Base Value")
    return fig


def make_radar_chart(p1, p2):
    """BONUS: radar/spider chart for stat comparison."""
    def to_stats(p):
        return {s["stat"]["name"]: s["base_stat"] for s in p.get("stats", [])}

    s1 = to_stats(p1)
    s2 = to_stats(p2)

    categories = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]

    fig = go.Figure()
    for p, stats in [(p1, s1), (p2, s2)]:
        values = [stats.get(c, 0) for c in categories]
        values += values[:1]  # cerrar el polígono
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=p["name"].title(),
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 255])),
        title="Stats Radar Chart",
        showlegend=True,
    )
    return fig


def make_hp_line_chart(hp_over_time_df):
    fig = px.line(
        hp_over_time_df, x="Turn", y="HP", color="Pokemon",
        markers=True, title="HP over Time",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    fig.update_layout(xaxis_title="Turn", yaxis_title="HP Remaining")
    return fig