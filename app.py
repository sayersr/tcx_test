import io
import base64
import xml.etree.ElementTree as ET
import json
import folium
from folium import plugins
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd

def parse_tcx(content):
    root = ET.fromstring(content)
    ns = {'tc': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    
    trackpoints = []
    for trkpt in root.findall('.//tc:Trackpoint', ns):
        time = trkpt.find('tc:Time', ns).text
        lat = trkpt.find('tc:Position/tc:LatitudeDegrees', ns)
        lon = trkpt.find('tc:Position/tc:LongitudeDegrees', ns)
        
        if lat is not None and lon is not None:
            trackpoints.append({
                'time': datetime.fromisoformat(time),
                'lat': float(lat.text),
                'lon': float(lon.text)
            })
    
    return pd.DataFrame(trackpoints)

def create_map(df):
    m = folium.Map(location=[df['lat'].mean(), df['lon'].mean()], zoom_start=12)
    
    points = df[['lat', 'lon']].values.tolist()
    midpoint = len(points) // 2
    
    outbound = points[:midpoint]
    return_route = points[midpoint:]
    
    folium.PolyLine(outbound, color="blue", weight=3, opacity=0.8).add_to(m)
    folium.PolyLine(return_route, color="red", weight=3, opacity=0.8).add_to(m)
    
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
    
    folium.Marker(points[0], popup="Start/End", icon=folium.Icon(color='green')).add_to(m)
    folium.Marker(points[midpoint], popup="Midpoint", icon=folium.Icon(color='orange')).add_to(m)
    
    return m

def create_plot(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df['time'], df['lat'], label='Latitude')
    ax.plot(df['time'], df['lon'], label='Longitude')
    ax.set_xlabel('Time')
    ax.set_ylabel('Degrees')
    ax.set_title('Latitude and Longitude over Time')
    ax.legend()
    
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    return f'data:image/png;base64,{img_str}'

def process_tcx(file_content):
    try:
        df = parse_tcx(file_content)
        map_html = create_map(df)._repr_html_()
        plot_img = create_plot(df)
        
        return {
            'status': 'success',
            'map_html': map_html,
            'plot_img': plot_img,
            'file_info': f"Processed {len(df)} trackpoints",
            'activity_info': f"Activity from {df['time'].min()} to {df['time'].max()}"
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

# This function will be called from JavaScript
def handle_file_upload(file_content):
    result = process_tcx(file_content)
    return json.dumps(result)
