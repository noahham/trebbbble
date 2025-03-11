from flask import Flask, request, jsonify, send_from_directory
from main import main

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')

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

@app.route('/output/<filename>')
def serve_file(filename):
    if filename == "cover.jpg":
        return send_from_directory("../media", filename)
    else:
        return None

if __name__ == '__main__':
    app.run(debug=True)
