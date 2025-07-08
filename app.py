# import requests

# # Replace with your actual API key
# API_KEY = "MY-API-KEY"
# pickupLat = 29.326478098712588
# pickupLng = 48.02102339372158
# dropoffLat = 29.10293868418849
# dropoffLng = 47.76902450223553
# # API URL with coordinates
# url = f"https://api.tomtom.com/routing/1/calculateRoute/{pickupLat},{pickupLng}:{dropoffLat},{dropoffLng}/json?key={API_KEY}"

# try:
#     # Send GET request
#     response = requests.get(url)
#     response.raise_for_status()  # Raise error if request failed

#     # Parse JSON response
#     data = response.json()

#     # Extract length in meters
#     length_in_meters = data['routes'][0]['summary']['lengthInMeters']
#     time_in_seconds = data['routes'][0]['summary']['travelTimeInSeconds']
#     print(f"DISTANCE: {length_in_meters/1000} km")
#     print(f"TIME: {time_in_seconds/60} minutes")

# except requests.exceptions.HTTPError as http_err:
#     print(f"HTTP error: {http_err}")
# except Exception as err:
#     print(f"Error: {err}")


from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Use env variable or directly paste your TomTom API key here
API_KEY = os.getenv("TOMTOM_API_KEY")

def get_fare(distance, template):
    fare = 0
    if template == "verdi":
        if distance <= 15000:
            fare = 1.5
        elif distance > 15000 and distance <= 20000:
            fare = 2
        elif distance > 20000 and distance <= 25000:
            fare = 2.5 
        elif distance > 25000 and distance <= 45000:
            fare = 4
        elif distance > 45000 and distance <= 60000:
            fare = 6
        elif distance > 60000:
            fare = 6 + (0.25 * (distance - 60))
        
        return fare
    else:
        return 'Invalid template'


@app.route("/api/distance", methods=["GET"])
def get_distance():
    try:
        # Parse query params
        pickup_lat = request.args.get("pickup_lat", type=float)
        pickup_lng = request.args.get("pickup_lng", type=float)
        dropoff_lat = request.args.get("dropoff_lat", type=float)
        dropoff_lng = request.args.get("dropoff_lng", type=float)
        template = request.args.get("dropoff_lng", type=str)

        # Validate input
        if None in [pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]:
            return jsonify({"error": "Missing or invalid coordinates"}), 400

        # Build TomTom URL
        url = (
            f"https://api.tomtom.com/routing/1/calculateRoute/"
            f"{pickup_lat},{pickup_lng}:{dropoff_lat},{dropoff_lng}/json"
        )

        params = {"key": API_KEY}

        # Make request to TomTom API
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Parse response
        data = response.json()
        summary = data["routes"][0]["summary"]
        distance = summary["lengthInMeters"]
        time = summary["travelTimeInSeconds"]

        final_fare = get_fare(distance, template)

        return jsonify({"distance_meters": distance, "time_seconds": time, "Fare": final_fare})

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False)
