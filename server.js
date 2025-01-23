// Import required modules
const http = require('http');
const axios = require('axios');
const { URL } = require('url');
const fs = require('fs'); // To handle file operations
const path = require('path');

// Define headers for the external APIs
const IMAGE_GENERATOR_HEADERS = {
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

const SPOTIFY_HEADERS = {
  'accept': '*/*',
  'accept-language': 'en-US,en;q=0.9,de;q=0.8',
  'priority': 'u=1, i',
  'referer': 'https://spotifydownloader.online/',
  'sec-ch-ua': '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
};

// Define external API URLs
const IMAGE_GENERATOR_API_URL = 'https://www.blackbox.ai/api/image-generator';
const SPOTIFY_API_URL = 'https://spotifydownloader.online/api/track';

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

        // Send the request to the external API
        const data = { query: payload.query };
        const apiResponse = await axios.post(IMAGE_GENERATOR_API_URL, data, { headers: IMAGE_GENERATOR_HEADERS });

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
  } else if (req.method === 'POST' && req.url === '/download-mp3') {
    let body = '';

    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', async () => {
      try {
        const payload = JSON.parse(body);

        // Validate the payload
        if (!payload.url) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: "Missing 'url' in request body" }));
          return;
        }

        // Prepare parameters for the Spotify API
        const params = { q: payload.url };

        // Send request to Spotify API
        const apiResponse = await axios.get(SPOTIFY_API_URL, { params, headers: SPOTIFY_HEADERS });

        const data = apiResponse.data;

        if (data.status) {
          const title = data.data.title;
          const downloadUrl = data.data.url;

          // Download the MP3 file
          const mp3Response = await axios.get(downloadUrl, { responseType: 'arraybuffer' });

          // Save the file temporarily
          const filePath = path.join(__dirname, `${title}.mp3`);
          fs.writeFileSync(filePath, mp3Response.data);

          // Send the file as a response
          res.writeHead(200, {
            'Content-Type': 'audio/mpeg',
            'Content-Disposition': `attachment; filename="${title}.mp3"`
          });

          fs.createReadStream(filePath).pipe(res).on('finish', () => {
            // Clean up the file after sending
            fs.unlinkSync(filePath);
          });
        } else {
          res.writeHead(500, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Failed to download the MP3 file' }));
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
