


import json
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from model.pig_iron_balance import Converter

def generate_gantt_chart(converters: list[Converter]):
    # Gantt Chart Data
    data_gantt = []
    converter_labels = ["CV 1", "CV 2"]
    for i, converter in enumerate(sorted(converters, key=lambda cv: cv.time)):
        data_gantt.append(
            {"Converter": converter_labels[int(converter.cv == 'cv_2')], "Start": converter.time,
             "Finish": converter.end, "HMR": converter.hmr})

    # Convert data to DataFrame
    df_gantt = pd.DataFrame(data_gantt)

    # Generate Gantt Chart
    fig_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Converter", color="HMR",
                            labels={"Converter": "Converter"}, title="Gantt Chart",
                            color_continuous_scale="Viridis")

    # Configure Gantt Chart layout
    fig_gantt.update_layout(
        xaxis_title="Time",
        yaxis_title="Equipment",
        showlegend=False,
        height=300,  # Increase the height by multiplying with 2
        width=1200,  # Increase the width
        margin=dict(l=50, r=50, t=50, b=50),
        coloraxis=dict(
            cmin=0.8,  # Minimum value for the color axis
            cmax=1  # Maximum value for the color axis
        ),
        coloraxis_colorbar=dict(x=1.05, y=0.68, len=1.8, thickness=20, title="HMR"),  # Adjust the color bar position
    )

    # Set the x-axis range for the chart
    fig_gantt.update_xaxes(
        range=[
            min(df_gantt["Start"]).strftime("%Y-%m-%d %H:%M:%S"),
            max(df_gantt["Finish"]).strftime("%Y-%m-%d %H:%M:%S")
        ]
    )

    # Display the chart
    fig_gantt.show()
