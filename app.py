import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Read from environment (EC2/GitHub Actions/Docker)
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")


@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error_message = None

    if request.method == "POST":
        city = (request.form.get("city") or "").strip()

        if not city:
            error_message = "Please enter a city name."
        elif not OPENWEATHER_API_KEY:
            error_message = "Server error: API key is not configured."
        else:
            try:
                url = "https://api.openweathermap.org/data/2.5/weather"
                params = {
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                }
                response = requests.get(url, params=params, timeout=5)
                data = response.json()

                if response.status_code != 200:
                    error_message = data.get("message", "Could not fetch weather.")
                else:
                    weather_data = {
                        "city": data.get("name"),
                        "country": data.get("sys", {}).get("country"),
                        "temperature": data.get("main", {}).get("temp"),
                        "feels_like": data.get("main", {}).get("feels_like"),
                        "humidity": data.get("main", {}).get("humidity"),
                        "description": (data.get("weather") or [{}])[0].get("description", "").title(),
                    }

            except requests.RequestException:
                error_message = "Network error while contacting weather service."

    return render_template("index.html", weather=weather_data, error=error_message)


if __name__ == "__main__":
    # Local/dev run only. In EC2 production, use gunicorn or Docker.
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
