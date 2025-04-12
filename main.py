from flask import Flask, request, jsonify, render_template

import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True, port=5001)
