import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render(data: list, compact: bool = False):
    df = pd.DataFrame(data)
    month_order = ['Jan','Feb','Mar','Apr','May','Jun',
                   'Jul','Aug','Sep','Oct','Nov','Dec']
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)

    pivot = df.pivot(index='year', columns='month', values='inflation')
    pivot = pivot[month_order]

    if not compact:
        st.markdown("### Seasonal inflation heatmap — combined YoY (%)")
        st.markdown("Darker = higher inflation. Reveals seasonal and structural patterns.")

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=list(pivot.columns),
        y=[str(y) for y in pivot.index],
        colorscale='Blues',
        colorbar=dict(title='Inflation %', thickness=12),
        hovertemplate='%{y} %{x}: %{z:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        height=280 if compact else 400,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="Month",
        yaxis_title="Year",
        yaxis=dict(autorange='reversed')
    )

    st.plotly_chart(fig, use_container_width=True)

    if not compact:
        st.markdown("**Pattern insights:**")
        st.markdown(
            "- July–September months tend to show higher inflation due to monsoon supply disruptions.\n"
            "- 2022 row stands out — post-COVID supply chain and energy price shock.\n"
            "- 2014 top row shows the inherited high-inflation regime from 2013."
        )
