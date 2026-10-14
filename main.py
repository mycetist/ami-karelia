from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI with HTMX</title>
        <script src="https://unpkg.com/htmx.org@1.6.1/dist/htmx.min.js"></script>
        <link rel="stylesheet" href="https://unpkg.com/maplibre-gl@5/dist/maplibre-gl.css">
        <script src="https://unpkg.com/maplibre-gl@5/dist/maplibre-gl.js"></script>
        <style>
            #map { height: 500px; width: 100%; }
        </style>
    </head>
    <body>
        <h1>Welcome to FastAPI with HTMX</h1>
        <div id="map"></div>
        <div id="content"></div>
        <button hx-get="/fetch-data" hx-target="#content">Fetch Data</button>
    </body>
    <script>
        const map = new maplibregl.Map({
            container: 'map',
            style: 'https://tiles.openfreemap.org/styles/liberty',
            center: [8.68, 50.11],
            zoom: 13
        });
        map.on('click', (e) => new maplibregl.Marker().setLngLat(e.lngLat).addTo(map));
    </script>
    </html>
    """

@app.get("/fetch-data", response_class=HTMLResponse)
async def fetch_data():
    return "<p>Here is some dynamic data fetched with HTMX!</p>"