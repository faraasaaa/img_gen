from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Define headers used for the external API
HEADERS = {
    'accept': '/',
    'accept-language': 'en-US,en;q=0.9,de;q=0.8',
    'content-type': 'text/plain;charset=UTF-8',
    'origin': 'https://www.blackbox.ai',
    'priority': 'u=1, i',
    'referer': 'https://www.blackbox.ai/agent/create/new',
    'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
}

# Define the external API URL
EXTERNAL_API_URL = 'https://www.blackbox.ai/api/image-generator'

@app.route('/generate-image', methods=['POST'])
def generate_image():
    try:
        # Get the JSON payload from the request
        payload = request.json

        # Validate the payload
        if not payload or 'query' not in payload:
            return jsonify({"error": "Missing 'query' in request body"}), 400

        # Prepare the data for the external API
        data = {"query": payload['query']}

        # Send the request to the external API
        response = requests.post(EXTERNAL_API_URL, headers=HEADERS, json=data)

        # Check the response status
        if response.status_code != 200:
            return jsonify({"error": "Failed to generate image", "details": response.text}), response.status_code

        # Parse the response
        response_json = response.json()
        markdown = response_json.get("markdown", "")

        # Extract the image URL from the markdown
        if markdown.startswith("![](") and markdown.endswith(")"):
            image_url = markdown[4:-1]
            return jsonify({"image_url": image_url})
        else:
            return jsonify({"error": "Invalid response format from external API"}), 500

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
