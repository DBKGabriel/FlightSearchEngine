import httpx
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

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

        # Convert airport codes to uppercase to make the code play nice with Amadeus API
        origin = origin.upper()
        destination = destination.upper()

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
        """Convert Amadeus response to format with connection details"""
        flights = []
        
        if "data" not in data:
            return {"flights": [], "total_results": 0}
        
        for offer in data["data"][:10]:  # Limit to 10 results
            try:
                # Get the first itinerary
                if not offer.get("itineraries") or not offer["itineraries"]:
                    continue
                itinerary = offer["itineraries"][0]
                if not itinerary.get("segments"):
                    continue
                segments = itinerary["segments"]
                
                # Get first and last segments for origin and final destination
                first_segment = segments[0]
                last_segment = segments[-1]
                
                # Parse all segments to get connection details
                flight_segments = []
                connections = []
                
                for i, segment in enumerate(segments):
                    # Create segment details
                    segment_info = {
                        "segment_number": i + 1,
                        "flight_number": segment["carrierCode"] + segment["number"],
                        "airline": segment["carrierCode"],
                        "aircraft": segment.get("aircraft", {}).get("code", "Unknown"),
                        "origin": {
                            "airport_code": segment["departure"]["iataCode"],
                            "departure_time": segment["departure"]["at"],
                            "terminal": segment["departure"].get("terminal")
                        },
                        "destination": {
                            "airport_code": segment["arrival"]["iataCode"],
                            "arrival_time": segment["arrival"]["at"],
                            "terminal": segment["arrival"].get("terminal")
                        },
                        "duration": segment["duration"]
                    }
                    flight_segments.append(segment_info)
                    
                    # If there's a next segment, calculate layover time
                    if i < len(segments) - 1:
                        next_segment = segments[i + 1]
                        
                        # Parse datetime strings to calculate layover
                        arrival_time = datetime.fromisoformat(segment["arrival"]["at"].replace('Z', '+00:00'))
                        next_departure = datetime.fromisoformat(next_segment["departure"]["at"].replace('Z', '+00:00'))
                        layover_duration = next_departure - arrival_time
                        
                        connection_info = {
                            "airport_code": segment["arrival"]["iataCode"],
                            "arrival_time": segment["arrival"]["at"],
                            "departure_time": next_segment["departure"]["at"],
                            "layover_duration": str(layover_duration),
                            "layover_hours": round(layover_duration.total_seconds() / 3600, 2),
                            "arrival_terminal": segment["arrival"].get("terminal"),
                            "departure_terminal": next_segment["departure"].get("terminal")
                        }
                        connections.append(connection_info)
                
                # Calculate total travel time
                total_departure = datetime.fromisoformat(first_segment["departure"]["at"].replace('Z', '+00:00'))
                total_arrival = datetime.fromisoformat(last_segment["arrival"]["at"].replace('Z', '+00:00'))
                total_travel_time = total_arrival - total_departure
                
                flight = {
                    "flight_number": first_segment["carrierCode"] + first_segment["number"],
                    "flight_id": offer.get("id", ""),
                    "airline": first_segment["carrierCode"],
                    "origin": first_segment["departure"]["iataCode"],
                    "destination": last_segment["arrival"]["iataCode"],
                    "departure_time": first_segment["departure"]["at"],
                    "arrival_time": last_segment["arrival"]["at"],
                    "total_duration": itinerary["duration"],
                    "price": float(offer["price"]["total"]),
                    "currency": offer["price"]["currency"],
                    "stops": len(segments) - 1,
                    "segments": flight_segments,
                    "connections": connections,
                }
                flights.append(flight)
                
            except (KeyError, ValueError) as e:
                # Skip flights with missing or invalid data
                logger.warning(f"Error parsing flight offer: {e}")
                continue
        
        return {
            "flights": flights,
            "total_results": len(flights),
            }
    
