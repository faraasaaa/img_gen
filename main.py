from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    # Get the JSON data from the request
    data = request.get_json()
    
    # Check if 'query' is in the data
    if 'query' not in data:
        return jsonify({'error': 'No query provided'}), 400
    
    query = data['query']
    
    headers = {
        'accept': '*/*',
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

    # Prepare the data for the request
    request_data = f'{{"query":"{query}"}}'

    # Make the request to the image generation API
    response = requests.post('https://www.blackbox.ai/api/image-generator', headers=headers, data=request_data)

    # Check if the response is successful
    if response.status_code == 200:
        response_json = response.json()
        return jsonify(response_json), 200
    else:
        return jsonify({'error': 'Failed to generate image'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
