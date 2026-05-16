import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def render(data: list, compact: bool = False):
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])

    if not compact:
        st.markdown("### Monthly Bank Credit & Deposits Trend")
        view = st.radio("Show", ["Outstanding (₹ Lakh Cr)", "YoY Growth (%)"], horizontal=True)
    else:
        view = "Outstanding (₹ Lakh Cr)"

    fig = go.Figure()

    if view == "Outstanding (₹ Lakh Cr)":
        fig.add_trace(go.Scatter(x=df['date'], y=df['bank_credit'],
                                 name='Bank Credit', line=dict(color='#185FA5', width=2)))
        fig.add_trace(go.Scatter(x=df['date'], y=df['deposits'],
                                 name='Deposits', line=dict(color='#0F6E56', width=2)))
        y_title = "₹ Lakh Crore"
    else:
        fig.add_trace(go.Scatter(
            x=df['date'], y=df['credit_growth_yoy'],
            name='Credit Growth YoY', line=dict(color='#185FA5', width=2),
            fill='tozeroy', fillcolor='rgba(24,95,165,0.1)'
        ))
        fig.add_hline(y=0, line_color='rgba(0,0,0,0.2)', line_width=1)
        y_title = "YoY Growth (%)"

    fig.update_layout(
        height=300 if compact else 420,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis_title=y_title,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

    if not compact:
        latest = df.dropna(subset=['credit_growth_yoy']).iloc[-1]
        st.markdown(
            f"- Latest bank credit: **₹{latest['bank_credit']:.1f} Lakh Crore** ({latest['date'].strftime('%b %Y')})\n"
            f"- YoY credit growth: **{latest['credit_growth_yoy']}%**\n"
            f"- Credit-Deposit ratio: **{round(latest['bank_credit']/latest['deposits']*100, 1)}%**"
        )
