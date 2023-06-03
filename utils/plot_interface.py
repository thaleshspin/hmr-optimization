import os
import plotly.colors as pc
from model.pig_iron_balance import Converter

import colorlover as cl


colorscale = cl.scales['9']['seq']['Blues']

from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px

from model.pig_iron_balance import PigIronBalance

from PIL import Image
import plotly.io as pio
import plotly.graph_objects as go


def plot_interface(ct_name, pig_iron_balance, debug=True):
    gantt = generate_gantt_chart(pig_iron_balance.initial_conditions.time, pig_iron_balance.converters)
    balance = generate_pig_iron_balance_chart(pig_iron_balance, [spill.time for spill in pig_iron_balance.spill_events])

    pio.write_image(gantt, f"test_cases/images/gantt_{ct_name}.png", format='png', width=800, height=200, scale=3)
    pio.write_image(balance, f"test_cases/images/balance_{ct_name}.png", format='png', width=800, height=400, scale=3)

    save_plot(ct_name, debug)


def save_plot(ct_name, debug):
    # Load the PNG files
    image2 = Image.open(f"test_cases/images/balance_{ct_name}.png")
    image1 = Image.open(f"test_cases/images/gantt_{ct_name}.png")

    # Get the dimensions of the images
    width = max(image1.width, image2.width)
    height = image1.height + image2.height

    # Create a new blank image with the combined dimensions
    combined_image = Image.new("RGBA", (width, height))

    # Paste the first image at the top
    combined_image.paste(image1, (0, 0))

    # Paste the second image below the first image
    combined_image.paste(image2, (0, image1.height))
    if debug:
        combined_image.show()

    # Set the desired DPI value
    dpi = 120

    # Calculate the size of the saved image based on DPI
    width_in_pixels = int(combined_image.width * dpi / 72)
    height_in_pixels = int(combined_image.height * dpi / 72)

    # Create a new image with the desired DPI and size
    new_image = combined_image.resize((width_in_pixels, height_in_pixels))

    # Save the new image with high resolution
    new_image.save(f"test_cases/images/interface_{ct_name}.png", dpi=(dpi, dpi))
    os.remove(f"test_cases/images/balance_{ct_name}.png")
    os.remove(f"test_cases/images/gantt_{ct_name}.png")


def generate_gantt_chart(initial_time, converters: list[Converter]):
    # Gantt Chart Data
    data_gantt = []
    converter_labels = ["CV 1", "CV 2"]
    for i, converter in enumerate(sorted(converters, key=lambda cv: cv.time)):
        data_gantt.append(
            {"Converter": converter_labels[int(converter.cv == 'cv_2')], "Start": converter.time,
             "Finish": converter.end, "HMR": converter.hmr})

    # Convert data to DataFrame
    df_gantt = pd.DataFrame(data_gantt)

    # Define a discrete color scale with the desired number of colors
    num_colors = 4
    colorscale = pc.sequential.Bluered[:num_colors]

    # Generate Gantt Chart
    fig_gantt = px.timeline(df_gantt, x_start="Start", x_end="Finish", y="Converter",
                            labels={"Converter": "Converter"}, title="Gantt",
                            color="HMR",  # Definir cores com base no valor do HMR
                            color_continuous_scale=colorscale,  # Definir a escala de cores discreta
                            )
    # Configure Gantt Chart layout
    fig_gantt.update_layout(
        xaxis_title="Tempo",
        yaxis_title="Equipmento",
        showlegend=False,
        height=200,  # Increase the height by multiplying with 2
        width=800,  # Increase the width
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(
            showgrid=True,  # Exibe as linhas de grade verticais
            gridcolor='white',  # Define a cor das linhas de grade
            gridwidth=1,  # Define a largura das linhas de grade
        )
    )
    for i, converter in enumerate(sorted(converters, key=lambda cv: cv.time)):
        fig_gantt.add_annotation(
            x=converter.time + (converter.end - converter.time) / 2,
            y=converter_labels[int(converter.cv == 'cv_2')],
            text=f'{converter.hmr}',
            showarrow=False,
            font=dict(size=14, color="white" if converter.hmr < 0.96 else 'black'),
        )
    fig_gantt.update_layout(
        {
            "coloraxis_cmin": 0.8,
            "coloraxis_cmax": 1.0,
        }
    )


    fig_gantt.update_coloraxes(
        colorbar={
            'len': 0.51,  # Specify the length/width of the color bar
            'thickness': 20,
            'y': 1,
            'x': 0.76,
            'nticks': 10
        }
    )

    fig_gantt.update_coloraxes(colorbar={'orientation': 'h', 'thickness': 20, 'y': 1, "x": 0.76, "nticks": 20})

    # Set the x-axis range for the chart
    fig_gantt.update_xaxes(
        range=[
            initial_time.strftime("%Y-%m-%d %H:%M:%S"),
            max(df_gantt["Finish"]).strftime("%Y-%m-%d %H:%M:%S")
        ]
    )

    # fig_gantt.show()
    return fig_gantt


def generate_pig_iron_balance_chart(pig_iron_balance: PigIronBalance, highlighted_datetimes: list[datetime]):
    # Pig Iron Balance Data
    saldo_de_gusa = [(state.time, round(state.value)) for state in pig_iron_balance.pig_iron_balance]
    saldo_de_gusa_map = {state.time: state.value for state in pig_iron_balance.pig_iron_balance}
    # Create DataFrame for Pig Iron Balance data
    df_saldo_gusa = pd.DataFrame({"Tempo": [item[0] for item in saldo_de_gusa],
                                  "Saldo de Gusa": [item[1] for item in saldo_de_gusa]})

    # Generate line plot for Pig Iron Balance
    fig_saldo_gusa = go.Figure()

    # Add line plot for Pig Iron Balance
    fig_saldo_gusa.add_trace(
        go.Scatter(
            x=df_saldo_gusa["Tempo"],
            y=df_saldo_gusa["Saldo de Gusa"],
            mode="lines",
            name="Saldo de Gusa",
            line=dict(color="darkblue", width=2),
        )
    )

    for spill in pig_iron_balance.spill_events:
        x_vals = [spill.time, spill.time + timedelta(seconds=1)]
        y_vals = [saldo_de_gusa_map[x_vals[0]], saldo_de_gusa_map[x_vals[1]]]

        fig_saldo_gusa.add_trace(
            go.Scatter(
                x=x_vals,
                y=y_vals,
                mode="lines",
                name="Highlighted",
                line=dict(color="red", width=5),
                hoverinfo="none"
            )
        )

    # Add labels to the points of the blue line
    fig_saldo_gusa.add_trace(
        go.Scatter(
            x=df_saldo_gusa["Tempo"][1:],
            y=df_saldo_gusa["Saldo de Gusa"][1:],
            mode="markers+text",
            text=df_saldo_gusa["Saldo de Gusa"][1:],
            textposition=[["top right", "bottom left"][i % 2] for i in range(len(df_saldo_gusa[1:]))],
            marker=dict(color="#687a9e", size=4),
            showlegend=False,
        )
    )

    # Configure Pig Iron Balance layout
    fig_saldo_gusa.update_layout(
        xaxis_title="Tempo",
        yaxis_title="Ferro-Gusa (t)",
        title='Saldo de Gusa',
        showlegend=False,
        height=400,
        width=800,
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(
            showgrid=True,  # Exibe as linhas de grade verticais
            gridcolor='white',  # Define a cor das linhas de grade
            gridwidth=1  # Define a largura das linhas de grade
        )
    )

    # Add bar chart to Pig Iron Balance
    altura_parametrizavel = pig_iron_balance.pig_iron_constants.torpedo_car_volume
    instantes_basculamento = [spill.time for spill in pig_iron_balance.spill_events]

    for instante in instantes_basculamento:
        fig_saldo_gusa.add_trace(
            go.Bar(
                x=[instante],
                y=[altura_parametrizavel],
                name="Basculamento",
                text=[instante.strftime("%H:%M")],
                textposition="outside",
                hovertemplate="Hour: %{x}<br>Value: 250",
                marker=dict(color="red"),
                width=timedelta(minutes=15).total_seconds() * 1000,
            )
        )

    # Add horizontal line at y=2000
    fig_saldo_gusa.add_shape(
        type="line",
        x0=df_saldo_gusa["Tempo"].min(),
        x1=df_saldo_gusa["Tempo"].max(),
        y0=pig_iron_balance.max_restrictive,
        y1=pig_iron_balance.max_restrictive,
        line=dict(color="red", width=2),
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

    # Set the y-axis range for the chart
    fig_saldo_gusa.update_yaxes(
        range=[0, pig_iron_balance.max_restrictive + 100]
    )

    # Display the chart
    # fig_saldo_gusa.show()
    return fig_saldo_gusa
