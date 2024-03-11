from flask import Flask, request, jsonify
import socket
import math
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/health")
def health_check():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return (
        jsonify(
            {
                "message": "Service is healthy.",
                "service": "Calculate Risk Percentages",
                "ip_address": local_ip,
            }
        ),
        200,
    )


@app.route("/percentage", methods=["POST"])
def calculate_risk_percentage():
    data = request.get_json()

    # Base risk percentages for each suspect case
    # Change Test cases percentages if base risk is changed.
    # Test cases Percentages are hardcoded.
    base_risk = {
        1: 10,  # After Hour Login
        2: 20,  # Potential Account Sharing
        3: 50,  # Terminated Employee Login
        4: 15,  # Failed Attempt to Enter Building / Potential Tailgating
        5: 50,  # Impossible Traveler
        6: 50,  # Potential Data Exfiltration
    }

    # Initialize variables to hold the records
    categories = ["building_access", "proxy_log", "pc_access"]
    suspects = []

    for category in categories:
        records = data.get(category, [])
        if not all("suspect" in record for record in records):
            return (
                jsonify(
                    {"message": f"Missing 'suspect' key in records of '{category}'."}
                ),
                400,
            )

        suspects.extend(record["suspect"] for record in records)

    # Check if there is at least one log in one of the categories
    if not suspects:
        return jsonify({"message": "No logs found in the request."}), 400  # Bad request
    
    # Count occurrences of each suspect case
    suspect_counts = {key: suspects.count(key) for key in base_risk.keys()}

    total_risk = 0
    for suspect, count in suspect_counts.items():
        risk_percentage = base_risk[suspect]
        for i in range(count):
            total_risk += risk_percentage
            risk_percentage /= 2  # Apply frequency scaling

    # Round total_risk to the nearest full percentage, rounding up
    total_risk = math.ceil(total_risk)

    # Normalize total risk score to a maximum of 100%
    total_risk = min(total_risk, 100)

    return (
        jsonify(
            {
                "message": "Risk calculation complete.",
                "total_risk_percentage": total_risk,
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

