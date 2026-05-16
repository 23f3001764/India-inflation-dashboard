import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render(growth: list, compact: bool = False):
    # Filter to top sectors for clarity
    top = ['Agriculture', 'Industry', 'Services', 'Personal Loans', 'NBFCs']
    colors = ['#185FA5', '#0F6E56', '#993C1D', '#6B3FA0', '#B87333']

    if not compact:
        st.markdown("### YoY Sectoral Credit Growth (%)")
        selected = st.multiselect(
            "Select sectors",
            options=[s['sector'] for s in growth if s['sector'] != 'Total Non-Food Credit'],
            default=top
        )
        items = [s for s in growth if s['sector'] in selected]
    else:
        items = [s for s in growth if s['sector'] in top]

    fig = go.Figure()
    for item, color in zip(items, colors * 3):
        years = item['years'][1:]   # skip first (no growth for first year)
        vals  = item['growth'][1:]
        fig.add_trace(go.Bar(
            name=item['sector'],
            x=years,
            y=vals,
            marker_color=color,
        ))

    fig.add_hline(y=0, line_color='rgba(0,0,0,0.2)', line_width=1)
    fig.update_layout(
        barmode='group',
        height=300 if compact else 400,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title="YoY Growth (%)",
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    if not compact:
        # Insight table
        rows = []
        for item in items:
            if item['growth'][-1] is not None:
                rows.append({
                    'Sector': item['sector'],
                    f"Growth {item['years'][-1]} (%)": item['growth'][-1],
                    f"Growth {item['years'][-2]} (%)": item['growth'][-2] if len(item['growth']) > 1 else None,
                })
        if rows:
            st.dataframe(pd.DataFrame(rows).set_index('Sector'), use_container_width=True)
