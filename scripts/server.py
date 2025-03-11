from flask import Flask, request, jsonify
from main import main  # Replace with the actual script where main() is defined
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        main(url)  # Main function

        text_file = "output/out.txt"
        cover_file = "../media/cover.jpg"

        if not os.path.exists(text_file) or not os.path.exists(cover_file):
            return jsonify({'error': 'Files were not created'}), 500

        return jsonify({
            'success': True,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
