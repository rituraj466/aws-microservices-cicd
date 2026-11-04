from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "service": "Order Service",
        "status": "Running"
    })

@app.route("/orders")
def orders():
    return jsonify([
        {"id": 101, "product": "Laptop"},
        {"id": 102, "product": "Mobile"}
    ])

app.run(host="0.0.0.0", port=5000)
