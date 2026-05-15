import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render(data: list, compact: bool = False):
    df = pd.DataFrame(data)

    if not compact:
        st.markdown("### Average annual CPI inflation (%)")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['year'], y=df['avg_combined'],
                         name='Combined', marker_color='#185FA5'))
    fig.add_trace(go.Bar(x=df['year'], y=df['avg_rural'],
                         name='Rural', marker_color='#0F6E56'))
    fig.add_trace(go.Bar(x=df['year'], y=df['avg_urban'],
                         name='Urban', marker_color='#993C1D'))

    fig.add_hline(y=4, line_dash='dash', line_color='rgba(0,0,0,0.3)',
                  annotation_text="RBI midpoint 4%", annotation_position="top right")

    fig.update_layout(
        barmode='group',
        height=300 if compact else 400,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title="Avg inflation (%)",
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    if not compact:
        peak = df.loc[df['avg_combined'].idxmax()]
        low = df.loc[df['avg_combined'].idxmin()]
        st.markdown(
            f"- Highest average inflation: **{peak['avg_combined']}%** in **{int(peak['year'])}**\n"
            f"- Lowest average inflation: **{low['avg_combined']}%** in **{int(low['year'])}**\n"
            f"- COVID years (2020–22) saw a resurgence after the low of {int(low['year'])}"
        )
