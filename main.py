import http.server
import socketserver
import json
import requests

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

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/generate-image':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                # Parse the incoming JSON payload
                payload = json.loads(post_data)

                # Validate the payload
                if 'query' not in payload:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Missing 'query' in request body"}).encode('utf-8'))
                    return

                # Prepare the data for the external API
                data = {"query": payload['query']}

                # Send the request to the external API
                response = requests.post(EXTERNAL_API_URL, headers=HEADERS, json=data)

                # Check the response status
                if response.status_code != 200:
                    self.send_response(response.status_code)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to generate image", "details": response.text}).encode('utf-8'))
                    return

                # Parse the response
                response_json = response.json()
                markdown = response_json.get("markdown", "")

                # Extract the image URL from the markdown
                if markdown.startswith("![](") and markdown.endswith(")"):
                    image_url = markdown[4:-1]
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"image_url": image_url}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Invalid response format from external API"}).encode('utf-8'))

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "An error occurred", "details": str(e)}).encode('utf-8'))

if __name__ == '__main__':
    PORT = 8000
    with socketserver.TCPServer(('', PORT), CustomHandler) as httpd:
        print(f"Server running on port {PORT}")
        httpd.serve_forever()
