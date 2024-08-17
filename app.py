from shiny import App, ui, render, reactive
import xml.etree.ElementTree as ET
from io import BytesIO
import traceback
import json
import folium
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
        try:
            root = data.getroot()
            ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
            
            trackpoints = root.findall('.//tcx:Trackpoint', ns)
            parsed_data = []
            
            for tp in trackpoints:
                time = tp.find('tcx:Time', ns)
                position = tp.find('tcx:Position', ns)
                heart_rate = tp.find('.//tcx:HeartRateBpm/tcx:Value', ns)
                elevation = tp.find('tcx:AltitudeMeters', ns)
                
                if time is not None and position is not None:
                    lat = position.find('tcx:LatitudeDegrees', ns)
                    lon = position.find('tcx:LongitudeDegrees', ns)
                    
                    parsed_data.append({
                        'time': datetime.fromisoformat(time.text),
                        'lat': float(lat.text) if lat is not None else None,
                        'lon': float(lon.text) if lon is not None else None,
                        'heart_rate': int(heart_rate.text) if heart_rate is not None else None,
                        'elevation': float(elevation.text) if elevation is not None else None
                    })
            
            df = pd.DataFrame(parsed_data)
            trackpoints_data.set(df)
        except Exception as e:
            trackpoints_data.set(f"Error processing trackpoints: {str(e)}")

    @render.text
    def file_info():
        if file_data() is None:
            return "No file uploaded yet."
        elif isinstance(file_data(), str):
            return f"Error parsing file: {file_data()}"
        return "File successfully parsed."

    @render.text
    @reactive.event(file_data)
    def activity_info():
        data = file_data()
        if data is None or isinstance(data, str):
            return ""
        
        try:
            root = data.getroot()
            ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
            
            activity = root.find('.//tcx:Activity', ns)
            if activity is None:
                return "No activity found in the TCX file."
            
            sport = activity.get('Sport')
            id_elem = activity.find('tcx:Id', ns)
            activity_id = id_elem.text if id_elem is not None else "Unknown"
            
            return (f"Sport: {sport}\n"
                    f"Activity ID: {activity_id}")
        except Exception as e:
            return f"Error processing activity info: {str(e)}"

    @render.ui
    @reactive.event(trackpoints_data)
    def map():
        df = trackpoints_data()
        if df is None or isinstance(df, str):
            return ui.p("No data available for map.")
        
        m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=12)
        
        points = df[['lat', 'lon']].dropna().values.tolist()
        folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(m)
        
        folium.Marker(points[0], popup="Start").add_to(m)
        folium.Marker(points[-1], popup="End").add_to(m)
        
        return ui.HTML(m._repr_html_())

    @render.plot
    @reactive.event(trackpoints_data)
    def data_plot():
        df = trackpoints_data()
        if df is None or isinstance(df, str):
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
        
        ax1.plot(df['time'], df['heart_rate'], color='red')
        ax1.set_ylabel('Heart Rate (bpm)')
        ax1.set_title('Heart Rate and Elevation over Time')
        
        ax2.plot(df['time'], df['elevation'], color='blue')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Elevation (m)')
        
        plt.tight_layout()
        return fig

    @render.text
    @reactive.event(input.tcx_file)
    def debug_info():
        file = input.tcx_file()
        if not file:
            return "No file uploaded yet."
        
        try:
            file_info = json.dumps(file[0], indent=2)
            return f"File info:\n{file_info}"
        except Exception as e:
            return f"Error reading file: {str(e)}\n{traceback.format_exc()}"

from shiny.express import app

app(app_ui, server)