from flask import Flask, request, jsonify, send_file
from fetch_weather_data import fetch_weather_data
import os

# Initialize Flask app
app = Flask(__name__)

@app.route("/fetch_weather", methods=["POST"])
def fetch_weather():
    try:
        # Validate and parse parameters
        history = int(request.form.get("history", "1"))
        if history < 1:
            raise ValueError("History must be a positive integer.")
        temp_unit = request.form.get("temp_unit", "C")
        save_csv = request.form.get("save_csv") == "true"
        save_excel = request.form.get("save_excel") == "true"

        # Fetch weather data
        weather_data, summary = fetch_weather_data(requested_hours=history)

        # Optionally save data
        if save_csv:
            print("CSV saving enabled")
        if save_excel:
            print("Excel saving enabled")

        # Return JSON response
        return jsonify({"success": True, "summary": summary, "data": weather_data})
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/download", methods=["POST"])
def download_data():
    format_type = request.form.get("format")
    file_paths = {
        "csv": "data/csv/weather_data.csv",
        "excel": "data/excel/weather_data.xlsx",
        "json": "data/raw/latest_raw.json"
    }

    file_path = file_paths.get(format_type)
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        error_message = f"File not found or invalid format: {format_type}"
        print(error_message)
        return jsonify({
            "success": False,
            "error": error_message,
            "available_formats": list(file_paths.keys())
        }), 404

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5001)
