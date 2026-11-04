from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "service": "Product Servic",
        "status": "Running"
    })

@app.route("/products")
def products():
    return jsonify([
        {"id": 1, "name": "Laptop", "price": 50000},
        {"id": 2, "name": "Mobile", "price": 20000},
        {"id": 3, "name": "Keyboard", "price": 1500}
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
