from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from main import main

app = Flask(__name__)
CORS(app)

@app.route('/process', methods=['POST'])
def process():
    url = request.get_json()['url']

    if not url:
        return jsonify({
            'error': 'No URL provided',
            'success': False
        }), 400

    try:
        return jsonify(main(url))

    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    app.run()