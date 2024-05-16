from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api', methods=['POST'])
def hello_world():
  # Check if request method is POST
  if request.method == 'POST':
    return "Hello World"
  else:
    return "This endpoint only accepts POST requests", 405  # Method Not Allowed

if __name__ == '__main__':
  app.run(debug=True)