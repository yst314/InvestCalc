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
    st.set_page_config(page_title="InvestCalc", layout="wide")

    with st.sidebar:
        st.header("Settings")
        language = st.selectbox(
            "Language",
            options=["English", "日本語"],
            index=1,
        )
        
    
    # 言語に応じてテキストを切り替え
    texts = {
        "English": {
            "investment_settings": "Investment Settings",
            "investment_period": "Investment Period [years]",
            "monthly_investment": "Investment per month",
            "historical_data": "Historical Data Selection",
            "select_years": "Select years to plot",
            "title": "S&P 500 Investment Simulator",
            "caption": "Compare historical S&P 500 investment returns with different starting periods",
            "benchmark": "Benchmark Options",
            "show_4p": "Show 4% annual interest rate",
            "label_4p": "Annual interest rate: 4%",
            "show_6p": "Show 6% annual interest rate",
            "label_6p": "Annual interest rate: 6%",
            "label_deposit": "Deposit",
            "show_deposit": "Show deposit",
            "plot_investment_growth": "Investment Growth Over Time",
        },
        "日本語": {
            "investment_settings": "投資設定",
            "investment_period": "投資期間 [年]",
            "monthly_investment": "月々の投資額",
            "historical_data": "過去データの選択",
            "select_years": "表示する年を選択",
            "title": "S&P 500 積立投資シミュレーター",
            "caption": "開始時期の違いによるS&P 500積立投資のリターン比較",
            "benchmark": "ベンチマーク設定",
            "show_4p": "年利4%を表示",
            "label_4p": "年利: 4%",
            "show_6p": "年利6%を表示",
            "label_6p": "年利: 6%",
            "label_deposit": "預金",
            "show_deposit": "預金を表示",
            "plot_investment_growth": "投資資産の推移",
        }
    }
    t = texts[language]
    st.title(t["title"])
    st.caption(t["caption"])
    df = load_data()
    st.header(t["investment_settings"])
    period = st.slider(t["investment_period"], 5, 40, value=20)
    period_m = period * 12
    x_years = [i/12 for i in range(period_m)]
    
    monthly_investment = st.number_input(t["monthly_investment"], value=10000)

    df_result = calculate_historical_investment(df, period, monthly_investment)
    interest_004 = calculate_investment(monthly_amount=monthly_investment, monthly_rate=(1.04)**(1/12)-1, months=period_m)
    interest_006 = calculate_investment(monthly_amount=monthly_investment, monthly_rate=(1.06)**(1/12)-1, months=period_m)
    deposit = calculate_investment(monthly_amount=monthly_investment, monthly_rate=0, months=period_m)
        
    fig = go.Figure()

    if 'show_4p' not in st.session_state:
        st.session_state.show_4p = True
    if 'show_6p' not in st.session_state:
        st.session_state.show_6p = False
    if 'show_deposit' not in st.session_state:
        st.session_state.show_deposit = True
    if st.session_state.show_4p:
        fig.add_trace(go.Scatter(
            x=x_years,
            y=interest_004,
            name=t["label_4p"],
            mode='lines',
            line=dict(dash='dash')
        ))
    if st.session_state.show_6p:
        fig.add_trace(go.Scatter(
            x=x_years,
            y=interest_006,
            name=t["label_6p"],
            mode='lines',
            line=dict(dash='dash')
        ))
    if st.session_state.show_deposit:
        fig.add_trace(go.Scatter(
            x=x_years,
            y=deposit,
            name=t["label_deposit"],
            mode='lines',
            line=dict(dash='dot')
        ))
    st.subheader(t["historical_data"])
    multi = st.multiselect(t["select_years"], range(1928, 2024-period+1), [1928, 1981])
    
    for year in multi:
        fig.add_trace(go.Scatter(
            x=x_years,
            y=df_result[df_result.keys()[year-1928]],
            name=f"{year}-1 - {year+period-1}-1",
            mode='lines'
        ))

    
    fig.update_layout(
        title=t["plot_investment_growth"],
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
    with st.expander(t["benchmark"]):
        st.session_state.show_4p = st.checkbox(t["show_4p"], True)
        st.session_state.show_6p = st.checkbox(t["show_6p"], False)
        st.session_state.show_deposit = st.checkbox(t["show_deposit"], True)