import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render(data: list, compact: bool = False):
    df = pd.DataFrame(data).dropna(subset=['inflation'])
    df = df.sort_values('inflation', ascending=True)

    if not compact:
        st.markdown("### Category-wise inflation — latest month")

    colors = ['#E24B4A' if v > 0 else '#0F6E56' for v in df['inflation']]

    fig = go.Figure(go.Bar(
        x=df['inflation'],
        y=df['category'],
        orientation='h',
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in df['inflation']],
        textposition='outside',
        hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
    ))

    fig.add_vline(x=0, line_color='rgba(0,0,0,0.2)', line_width=1)

    fig.update_layout(
        height=280 if compact else 420,
        margin=dict(l=0, r=60, t=10, b=0),
        xaxis_title="YoY Inflation (%)",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    if not compact:
        worst = df.loc[df['inflation'].idxmax()]
        best = df.loc[df['inflation'].idxmin()]
        st.markdown(
            f"- Highest inflation category: **{worst['category']}** at **{worst['inflation']:+.2f}%**\n"
            f"- Lowest inflation category: **{best['category']}** at **{best['inflation']:+.2f}%**\n"
            f"- Negative values mean prices fell year-on-year (deflation in that category)"
        )
