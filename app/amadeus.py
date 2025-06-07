import httpx
import os
from datetime import datetime, timedelta

class AmadeusClient:
    def __init__(self):
        self.client_id = os.getenv("AMADEUS_CLIENT_ID")
        self.client_secret = os.getenv("AMADEUS_CLIENT_SECRET")
        self.base_url = "https://test.api.amadeus.com"  # Test environment
        self.access_token = None
    
    async def get_access_token(self):
        """Get access token from Amadeus"""
        url = f"{self.base_url}/v1/security/oauth2/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                return True
            else:
                return False
    
    async def search_flights(self, origin: str, destination: str, departure_date: str = None):
        """Search for flights using Amadeus API"""
                
        # Get access token if we don't have one
        if not self.access_token:
            if not await self.get_access_token():
                return {"error": "Could not authenticate with Amadeus API"}
        
        # Use tomorrow as default date
        if not departure_date:
            tomorrow = datetime.now() + timedelta(days=1)
            departure_date = tomorrow.strftime("%Y-%m-%d")
        
        # Search for flights
        url = f"{self.base_url}/v2/shopping/flight-offers"
        
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": 1,
            "currencyCode": "USD"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return self.parse_flight_response(response.json())
            else:
                return {"error": f"Flight search failed: {response.status_code}"}
    
    def parse_flight_response(self, data):
        """Convert Amadeus response to our simple format"""
        flights = []
        
        if "data" not in data:
            return {"flights": [], "total_results": 0}
        
        for offer in data["data"][:10]:  # Limit to 10 results
            try:
                # Get the first itinerary
                itinerary = offer["itineraries"][0]
                segments = itinerary["segments"]
                
                # Get first and last segments for origin and final destination
                first_segment = segments[0]
                last_segment = segments[-1]
                
                flight = {
                    "flight_number": first_segment["carrierCode"] + first_segment["number"],
                    "airline": first_segment["carrierCode"],
                    "origin": first_segment["departure"]["iataCode"],
                    "destination": last_segment["arrival"]["iataCode"],
                    "departure_time": first_segment["departure"]["at"],
                    "arrival_time": last_segment["arrival"]["at"],
                    "duration": itinerary["duration"],
                    "price": float(offer["price"]["total"]),
                    "currency": offer["price"]["currency"],
                    "stops": len(segments) - 1
                }
                flights.append(flight)
                
            except KeyError:
                # Skip flights with missing data
                continue
        
        return {
            "flights": flights,
            "total_results": len(flights)
        }