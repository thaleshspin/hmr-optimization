import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def generate_pig_iron_balance_chart(balance):
    # Pig Iron Balance Data
    states = {state.time: state.value for state in balance}
    max_restrictive = {state.time: balance.max_restrictive for state in balance}
    spill_ev = {spill.time: balance.pig_iron_constants.torpedo_car_volume
                for spill in balance.spill_events}

    saldo_de_gusa = [(time, value) for time, value in states.items()]

    # Create DataFrame for Pig Iron Balance data
    df_saldo_gusa = pd.DataFrame({"Tempo": [item[0] for item in saldo_de_gusa],
                                  "Saldo de Gusa": [item[1] for item in saldo_de_gusa]})

    # Generate line plot for Pig Iron Balance
    fig_saldo_gusa = go.Figure()
    fig_saldo_gusa.add_trace(
        go.Scatter(
            x=df_saldo_gusa["Tempo"],
            y=df_saldo_gusa["Saldo de Gusa"],
            mode="lines",
            name="Saldo de Gusa",
            line=dict(color="blue", width=2),
        )
    )

    # Configure Pig Iron Balance layout
    fig_saldo_gusa.update_layout(
        xaxis_title="Time",
        yaxis_title="Pig Iron Balance",
        showlegend=False,
        height=400,
        width=800,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    # Add bar chart to Pig Iron Balance
    altura_parametrizavel = 250
    instantes_basculamento = [datetime(2023, 1, 1, 0, 35)]

    for instante in instantes_basculamento:
        fig_saldo_gusa.add_trace(
            go.Bar(
                x=[instante],
                y=[altura_parametrizavel],
                name="Basculamento",
                hovertemplate="Hour: %{x}<br>Value: 250",
                marker=dict(color="darkred"),
                width=timedelta(minutes=5).total_seconds() * 1000,
            )
        )

    # Add tooltip to Pig Iron Balance chart
    fig_saldo_gusa.update_traces(
        hovertemplate="Hour: %{x}<br>Value: %{y}"
    )

    # Set the x-axis range for the chart
    fig_saldo_gusa.update_xaxes(
        range=[
            min(df_saldo_gusa["Tempo"]).strftime("%Y-%m-%d %H:%M:%S"),
            max(df_saldo_gusa["Tempo"]).strftime("%Y-%m-%d %H:%M:%S")
        ]
    )

    # Display the chart
    fig_saldo_gusa.show()
