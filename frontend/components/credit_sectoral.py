import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


def render(sectoral: list, shares: list, compact: bool = False):

    if not compact:
        st.markdown("### Sectoral Credit Deployment — Latest Year")
        tab1, tab2 = st.tabs(["📊 Sector Shares", "📈 Sector Trends"])

        with tab1:
            _render_shares(shares)
        with tab2:
            _render_trends(sectoral)
    else:
        _render_shares(shares)


def _render_shares(shares: list):
    df = pd.DataFrame(shares).sort_values('share', ascending=True)
    colors = px.colors.sequential.Blues[2:]
    colors = (colors * (len(df) // len(colors) + 1))[:len(df)]

    fig = go.Figure(go.Bar(
        x=df['share'],
        y=df['sector'],
        orientation='h',
        marker_color=colors,
        text=[f"{v:.1f}%" for v in df['share']],
        textposition='outside',
        hovertemplate='%{y}: %{x:.2f}%<extra></extra>'
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=0, r=50, t=10, b=0),
        xaxis_title="Share of Total Credit (%)",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def _render_trends(sectoral: list):
    # Show top 5 sectors (excluding total)
    top_sectors = ['Agriculture', 'Industry', 'Services', 'Personal Loans', 'NBFCs']
    colors = ['#185FA5', '#0F6E56', '#993C1D', '#6B3FA0', '#B87333']

    fig = go.Figure()
    for item, color in zip(
        [s for s in sectoral if s['sector'] in top_sectors], colors
    ):
        fig.add_trace(go.Scatter(
            x=item['years'], y=item['values'],
            name=item['sector'],
            line=dict(color=color, width=2),
            mode='lines+markers'
        ))

    fig.update_layout(
        height=380,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title="₹ Lakh Crore",
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
