import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_data():
    return pd.read_csv("gspc.csv")

@st.cache_data
def calculate_historical_investment(df, period, monthly_investment):
    period_m = period * 12
    df_result = pd.DataFrame()
    
    for start in range(0, df.shape[0] - period_m, 12):
        series = pd.Series(0., index=range(period_m))
        for i in range(0, period_m):
            if i == 0:
                series[i] = monthly_investment * df.iloc[i+start, df.columns.get_loc('interest_rate')]
            else:
                assets = series[i-1]
                series[i] = (assets + monthly_investment) * df.iloc[i+start, df.columns.get_loc('interest_rate')]
        df_result[f'{df.index[start]}'] = series
    
    return df_result

@st.cache_data
def calculate_investment(monthly_amount, monthly_rate, months):
    total = []
    current_amount = 0

    for _ in range(months):
        current_amount = (monthly_amount+current_amount) * (1 + monthly_rate)
        total.append(round(current_amount))

    return total

if __name__ == '__main__':
    df = load_data()
    st.header("Investment Settings")
    period = st.slider("Investment Period [years]", 5, 40, value=20)
    period_m = period * 12
    monthly_investment = st.number_input("Investment per month", value=10000)

    df_result = calculate_historical_investment(df, period, monthly_investment)
    interest_004 = calculate_investment(monthly_amount=monthly_investment, monthly_rate=(1.04)**(1/12)-1, months=period_m)
    interest_006 = calculate_investment(monthly_amount=monthly_investment, monthly_rate=(1.06)**(1/12)-1, months=period_m)
    deposit = calculate_investment(monthly_amount=monthly_investment, monthly_rate=0, months=period_m)
    st.header("Historical Data Selection")
    multi = st.multiselect("Select years to plot", range(1928, 2024-period+1), [1928])
    
    fig = go.Figure()
    st.header("Comparison View")

    x_years = [i/12 for i in range(period_m)]
    for year in multi:
        fig.add_trace(go.Scatter(
            x=x_years,
            y=df_result[df_result.keys()[year-1928]],
            name=f"{year}-1 - {year+period-1}-1",
            mode='lines'
        ))

    st.subheader("Benchmark Options")
    if st.checkbox("Show 4% interest rate", True):
        fig.add_trace(go.Scatter(
            x=x_years,
            y=interest_004,
            name="Interest rate: 4%",
            mode='lines',
            line=dict(dash='dash')
        ))

    if st.checkbox("Show 6% interest rate", False):
        fig.add_trace(go.Scatter(
            x=x_years,
            y=interest_006,
            name="Interest rate: 6%",
            mode='lines',
            line=dict(dash='dash')
        ))

    if st.checkbox("Show deposit", True):
        fig.add_trace(go.Scatter(
            x=x_years,
            y=deposit,
            name="Deposit",
            mode='lines',
            line=dict(dash='dot')
        ))
    
    fig.update_layout(
        title="Investment Growth Over Time",
        xaxis_title="Years",
        yaxis_title="Assets",
        yaxis=dict(
            rangemode='tozero',
            range=[0, None]
        ),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)