import os
from fastapi import FastAPI, HTTPException
from .amadeus import AmadeusClient
from fastapi.responses import HTMLResponse

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Create the FastAPI app
app = FastAPI(
    title="Simple Flight Search Engine", 
    version="1.0.0",
    description="A simple flight search API using data from Amadeus to return flights between any 2 origin and destination airports either tomorrow (default) or on a specified date."
)

# Create Amadeus client
amadeus = AmadeusClient()

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple Flight Search Engine</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .button {
                display: inline-block;
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 5px;
                margin: 10px;
                font-weight: bold;
            }
            .button:hover {
                background-color: #2980b9;
            }
            .example {
                background-color: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            code {
                background-color: #34495e;
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1> Flight Search Engine API</h1>
            <p><strong>Version:</strong> 1.0.0</p>
            <p>Welcome to the Flight Search Engine! This API provides real-time flight data using the Amadeus Travel API.</p>
            
            <h2> Quick Start</h2>
            <div>
                <a href="/docs" class="button"> View API Documentation</a>
                <a href="/health" class="button"> Health Check</a>
            </div>

            <h2> Try a Flight Search</h2>
            <div class="example">
                <p><strong>Example:</strong> Search flights from Los Angeles to New York</p>
                <a href="/search/flights?origin=LAX&destination=JFK&departure_date=2025-06-15" class="button">
                    Search LAX to JFK
                </a>
            </div>

            <h2> API Endpoints</h2>
            <ul>
                <li><code>GET /search/flights</code> - Search for flights</li>
                <li><code>GET /docs</code> - Interactive API documentation</li>
                <li><code>GET /health</code> - API health status</li>
            </ul>
            
            <h2> Usage</h2>
            <p>To search flights, use: <code>/search/flights?origin=LAX&destination=JFK&departure_date=2025-06-15</code></p>
            <p>Replace LAX/JFK with any 3-letter airport codes, and adjust the date as needed.</p>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "flight-search-api"}

@app.get("/search/flights")
async def search_flights(origin: str, destination: str, departure_date: str = None):
    """
    Search for flights between two airports
    
    - **origin**: 3-letter IATA airport code (e.g., LAX, JFK, LHR)
    - **destination**: 3-letter IATA airport code
    - **departure_date**: Date in YYYY-MM-DD format (optional, defaults to tomorrow)
    """
    
    try:
        results = await amadeus.search_flights(origin, destination, departure_date)
        
        if "error" in results:
            raise HTTPException(status_code=400, detail=results["error"])
        
        return {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date,
            "flights": results["flights"],
            "total_results": results["total_results"],
            "data_source": "Amadeus API"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)