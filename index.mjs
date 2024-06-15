import express from 'express';
import bodyParser from 'body-parser';
import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
dotenv.config();

const app = express();
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

const azureMLApiKey = process.env.AZURE_ML_API_KEY;
const azureMLEndpoint = process.env.AZURE_ML_ENDPOINT;

// Correct path resolution for ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Function to use Azure ML Inference API
const generateTextWithAzureML = async (inputText) => {
  try {
    const response = await axios.post(
      azureMLEndpoint,
      { input_data: { input_string: [{ role: 'user', content: inputText }], parameters: { max_new_tokens: 256 } } },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${azureMLApiKey}`
        }
      }
    );
    console.log('Received response from Azure ML:', response.data);
    return response.data.output || 'No response generated';
  } catch (error) {
    console.error('Error using Azure ML Inference API:', error);
    throw new Error('Failed to generate text with Azure ML Inference API');
  }
};

// Serve static files from the public directory
app.use(express.static(path.join(__dirname, 'Public')));

app.post('/chat', async (req, res) => {
  const incomingMessage = req.body.message.trim().toLowerCase();
  let responseMessage = '';

  const words = incomingMessage.split(' ');
  if (words.includes('stock')) {
    responseMessage = 'Currently, fetching stock data is not available. Please ask other questions.';
  } else {
    try {
      responseMessage = await generateTextWithAzureML(incomingMessage);
    } catch (error) {
      responseMessage = 'Sorry, there was an error fetching the data. Please try again later.';
    }
  }

  res.json({ message: cleanResponse(responseMessage) });
});

function cleanResponse(response) {
  if (typeof response === 'string') {
    return response.replace(/"conversation_id":".*?"/g, '').replace(/^\{result:/, '').replace(/}$/, '').trim();
  }
  return response;
}

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
