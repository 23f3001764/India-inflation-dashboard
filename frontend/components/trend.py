import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render(data: list, compact: bool = False):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    if not compact:
        st.markdown("### Monthly CPI index trend")
        st.markdown("CPI index values for Rural, Urban and Combined series (Base 2012=100)")

        view = st.radio("Show", ["Index values", "YoY inflation (%)"],
                        horizontal=True)
    else:
        view = "Index values"

    fig = go.Figure()

    if view == "Index values":
        fig.add_trace(go.Scatter(x=df['date'], y=df['combined_index'],
                                 name='Combined', line=dict(color='#185FA5', width=2)))
        fig.add_trace(go.Scatter(x=df['date'], y=df['rural_index'],
                                 name='Rural', line=dict(color='#0F6E56', width=1.5, dash='dash')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['urban_index'],
                                 name='Urban', line=dict(color='#993C1D', width=1.5, dash='dot')))
        y_title = "CPI Index (2012=100)"
    else:
        fig.add_trace(go.Scatter(x=df['date'], y=df['combined_inflation'],
                                 name='Combined', line=dict(color='#185FA5', width=2)))
        fig.add_trace(go.Scatter(x=df['date'], y=df['rural_inflation'],
                                 name='Rural', line=dict(color='#0F6E56', width=1.5, dash='dash')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['urban_inflation'],
                                 name='Urban', line=dict(color='#993C1D', width=1.5, dash='dot')))
        # RBI tolerance band
        fig.add_hrect(y0=2, y1=6, fillcolor='rgba(24,95,165,0.08)',
                      line_width=0, annotation_text="RBI target band (2–6%)",
                      annotation_position="top left")
        y_title = "YoY Inflation (%)"

    fig.update_layout(
        height=320 if compact else 420,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title=y_title,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    if not compact:
        st.markdown("**Key observations:**")
        latest = df.dropna(subset=['combined_inflation']).iloc[-1]
        st.markdown(
            f"- Latest combined inflation: **{latest['combined_inflation']}%** ({latest['date'].strftime('%b %Y')})\n"
            f"- CPI index was **{df['combined_index'].iloc[0]:.1f}** in {df['date'].iloc[0].strftime('%b %Y')} "
            f"and is now **{df['combined_index'].iloc[-1]:.1f}** — a **{(df['combined_index'].iloc[-1]/df['combined_index'].iloc[0]-1)*100:.1f}%** rise"
        )
