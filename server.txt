// Import required modules
const http = require('http');
const { URL } = require('url');
const axios = require('axios');

// Define headers used for the external API
const HEADERS = {
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
};

// Define the external API URL
const EXTERNAL_API_URL = 'https://www.blackbox.ai/api/image-generator';

// Create the server
const server = http.createServer(async (req, res) => {
  if (req.method === 'POST' && req.url === '/generate-image') {
    let body = '';

    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', async () => {
      try {
        const payload = JSON.parse(body);

        // Validate the payload
        if (!payload.query) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: "Missing 'query' in request body" }));
          return;
        }

        // Prepare the data for the external API
        const data = { query: payload.query };

        // Send the request to the external API
        const apiResponse = await axios.post(EXTERNAL_API_URL, data, { headers: HEADERS });

        // Parse the response
        const markdown = apiResponse.data.markdown || '';

        // Extract the image URL from the markdown
        if (markdown.startsWith('![](') && markdown.endsWith(')')) {
          const imageUrl = markdown.slice(4, -1);
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ image_url: imageUrl }));
        } else {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Invalid response format from external API' }));
        }
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'An error occurred', details: err.message }));
      }
    });
  } else {
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Endpoint not found' }));
  }
});

// Start the server
const PORT = 8000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
