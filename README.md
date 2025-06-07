The long term goal of this project is to develop a flight search engine that shows the price to every other city in the world from any given city. I've decided to use FastAPI, since I'm most comfortable with python.

**Current Features** 
Real-time flight search between any two airports using IATA codes (if in production environment rather than test)
Live pricing in USD currency
Smart routing - correctly handles connecting flights and shows final destinations
RESTful API with automatic interactive documentation
User-friendly interface with clickable homepage and examples

**Prerequisites**
Python 3.7+
Amadeus API credentials (free tier available)

**Installation**
Clone the repository:
    git clone https://github.com/DBKGabriel/FlightSearchEngine.git
    cd FlightSearchEngine

**Install dependencies:**
    pip install fastapi uvicorn httpx python-dotenv

**Get Amadeus API credentials:**
Sign up at Amadeus for Developers
Create a new app in your dashboard
Copy your Client ID and Client Secret


**Configure environment**
# Create .env file in the root directory
AMADEUS_CLIENT_ID=your_client_id_here
AMADEUS_CLIENT_SECRET=your_client_secret_here

**Run the application:**
bashpython -m app.main

**Access the API:**
Homepage: http://localhost:8000 (with clickable interface)
Interactive Docs: http://localhost:8000/docs
Health Check: http://localhost:8000/health


**API Usage**
# Search Flights
# Just replace LAX and JFK with your origin and destination
GET /search/flights?origin=LAX&destination=JFK&departure_date=2025-06-15

Parameters:
    origin (required): 3-letter IATA airport code (case insensitive)
    destination (required): 3-letter IATA airport code (case insensitive)
    departure_date (optional): Date in YYYY-MM-DD format (defaults to tomorrow)



********************************************************************************************************************
**Progress Report**

I've done very minimal work with FastAPI and HTML so I'll be using this readme to also document my progress.

**06 June 2025**
Signed up for an account at https://developers.amadeus.com
Created a .env file that holds my API key and secret
Wrote main.py and amadeus.py. These scripts are just to get my feet under me, flight search wise.
    - main.py is the ... well, main/central script. It initializes http://localhost:8000 and http://localhost:8000/docs from which I can test the flight searches.
    - amadeus.py connects to the API and gives you every flight from a specified origin to a specified destination on a specified date (yyyy-mm-dd). **NOTE**: this is only test data. I don't think it's up-to-date.

I spent a while trying to figure out why the amadeus script was getting the origin correct, but not the destination. Then I realized that if there were any stops, it was only reporting the first leg. I think I have that fixed now (at least for up to 1 stop flights).

This of course isn't the long-term goal. Long-term, I want to specify an origin and see flights from that airport to every other city in the world. But this basic 1-to-1 search engine is a starting point for me.