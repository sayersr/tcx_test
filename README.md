# tcx_test

# TCX File Parser and Heart Rate Visualizer

## Description
The TCX File Parser and Heart Rate Visualizer is a web-based application that allows users to upload and analyze Training Center XML (TCX) files. It provides interactive visualizations of GPS routes and heart rate data from workout activities.

## Features
- Upload and parse multiple TCX files
- Display GPS routes on an interactive Leaflet map
- Visualize heart rate data over time using Plotly
- Color-coded heart rate indicators
- Interactive linking between map and heart rate plot
- Responsive design for various screen sizes

## How to Use
1. Open the HTML file in a web browser
2. Click on the file input button to select one or more TCX files
3. Wait for the files to be processed (this may take a moment depending on file size and quantity)
4. Explore the visualizations:
   - The map shows the GPS route with color-coded markers indicating heart rate
   - The plot displays heart rate over time for each activity

## Technologies Used
- HTML/CSS/JavaScript for the frontend
- PyScript for running Python in the browser
- Pandas for data processing
- XML parsing with Python's ElementTree
- Leaflet.js for interactive mapping
- Plotly.js for interactive plotting

## Requirements
- A modern web browser with JavaScript enabled
- Internet connection (for loading external libraries)

## Known Limitations
- Large TCX files or multiple files may take some time to process
- The application runs entirely in the browser, so performance may vary depending on the user's device

---

This project demonstrates the capabilities of modern web technologies in creating interactive data visualization tools for fitness data analysis. Enjoy exploring your TCX data!