from shiny import App, ui, render, reactive
import xml.etree.ElementTree as ET
from io import BytesIO
import traceback
import json
import folium
from folium import plugins
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

app_ui = ui.page_fluid(
    ui.h2("TCX File Parser and Visualizer"),
    ui.input_file("tcx_file", "Upload TCX file", accept=".tcx"),
    ui.output_text("file_info"),
    ui.output_text("activity_info"),
    ui.output_ui("map"),
    ui.output_plot("data_plot"),
    ui.output_text("debug_info")
)
a
def server(input, output, session):
    
    file_data = reactive.Value(None)
    trackpoints_data = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.tcx_file)
    def process_file():
        file = input.tcx_file()
        if file:
            try:
                content = file[0]["datapath"].read() if hasattr(file[0]["datapath"], 'read') else open(file[0]["datapath"], "rb").read()
                parsed_data = ET.parse(BytesIO(content))
                file_data.set(parsed_data)
                process_trackpoints(parsed_data)
            except Exception as e:
                file_data.set(str(e))
                trackpoints_data.set(None)

    def process_trackpoints(data):
        # [The process_trackpoints function remains unchanged]
        pass

    @render.text
    def file_info():
        # [The file_info function remains unchanged]
        pass

    @render.text
    @reactive.event(file_data)
    def activity_info():
        # [The activity_info function remains unchanged]
        pass

    @render.ui
    @reactive.event(trackpoints_data)
    def map():
        df = trackpoints_data()
        if df is None or isinstance(df, str):
            return ui.p("No data available for map.")
        
        m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=12)
        
        points = df[['lat', 'lon']].dropna().values.tolist()
        
        # Determine the midpoint of the route
        midpoint = len(points) // 2
        
        # Create outbound route (first half)
        outbound = points[:midpoint]
        folium.PolyLine(outbound, color="blue", weight=3, opacity=0.8).add_to(m)
        
        # Create return route (second half)
        return_route = points[midpoint:]
        folium.PolyLine(return_route, color="red", weight=3, opacity=0.8).add_to(m)
        
        # Add arrows to show direction
        plugins.PolyLineTextPath(
            folium.PolyLine(outbound),
            '>',
            repeat=True,
            offset=8,
            attributes={'fill': '#0000FF', 'font-weight': 'bold'}
        ).add_to(m)
        
        plugins.PolyLineTextPath(
            folium.PolyLine(return_route),
            '>',
            repeat=True,
            offset=8,
            attributes={'fill': '#FF0000', 'font-weight': 'bold'}
        ).add_to(m)
        
        # Add markers for start/end and midpoint
        folium.Marker(points[0], popup="Start/End", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker(points[midpoint], popup="Midpoint", icon=folium.Icon(color='orange')).add_to(m)
        
        return ui.HTML(m._repr_html_())

    @render.plot
    @reactive.event(trackpoints_data)
    def data_plot():
        # [The data_plot function remains unchanged]
        pass

    @render.text
    @reactive.event(input.tcx_file)
    def debug_info():
        # [The debug_info function remains unchanged]
        pass

# Don't create the App instance here

# Add this line at the end of the file
from shiny.express import app
