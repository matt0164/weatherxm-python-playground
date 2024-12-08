from flask import Flask, render_template, request, jsonify, send_file
from fetch_weather_data import fetch_weather_data
from settings import configure_settings

# Initialize Flask app
app = Flask(__name__)

# Configure the app if needed
# configure_settings()

@app.route("/fetch_weather", methods=["POST"])
def fetch_weather():
    try:
        # Get data from the form
        history = int(request.form.get("history", "1"))
        temp_unit = request.form.get("temp_unit", "C")
        save_csv = request.form.get("save_csv") == "true"
        save_excel = request.form.get("save_excel") == "true"

        # Fetch weather data and get the summary
        weather_data, summary = fetch_weather_data(requested_hours=history)

        # Handle CSV/Excel saving logic here if needed
        if save_csv:
            print("Save CSV enabled")
        if save_excel:
            print("Save Excel enabled")

        # Pass the summary and weather data to the template
        return render_template("index.html", summary=summary, weather_data=weather_data)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route("/download", methods=["POST"])
def download_data():
    format_type = request.form.get("format")
    file_paths = {
        "csv": "path/to/your/csv/file.csv",
        "excel": "path/to/your/excel/file.xlsx",
        "json": "path/to/your/json/file.json"
    }

    if format_type in file_paths and os.path.exists(file_paths[format_type]):
        return send_file(file_paths[format_type], as_attachment=True)
    else:
        return jsonify({"success": False, "error": "Invalid format requested or file not found."})

# Add this block to start the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=5001)
