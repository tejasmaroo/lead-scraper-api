from flask import Flask, request, jsonify
from apollo_filter_generator import ApolloFilterGenerator
import logging
import os

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create an instance of the filter generator
filter_generator = ApolloFilterGenerator()

@app.route('/api/generate-link', methods=['POST'])
def generate_link():
    try:
        # Get the query from request data
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query parameter',
                'status': 'error'
            }), 400
            
        query = data['query']
        logger.info(f"Processing query: {query}")
        
        # Generate the Apollo.io URL
        apollo_url = filter_generator.generate_filter_url(query)
        
        # Return the URL as a JSON response
        return jsonify({
            'apollo_url': apollo_url,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>Apollo Filter Generator API</h1>
    <p>Use POST /api/generate-link with a JSON body containing 'query' to generate an Apollo.io search link.</p>
    <h2>Quick Test</h2>
    <form id="testForm" style="margin-bottom: 20px;">
        <input type="text" id="queryInput" placeholder="Enter your search query" style="width: 300px; padding: 8px;">
        <button type="submit" style="padding: 8px;">Generate Link</button>
    </form>
    <div id="result" style="padding: 10px; background-color: #f5f5f5; display: none;"></div>
    
    <script>
        document.getElementById('testForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('queryInput').value;
            if (!query) return;
            
            fetch('/api/generate-link', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: query })
            })
            .then(response => response.json())
            .then(data => {
                const resultDiv = document.getElementById('result');
                if (data.status === 'success') {
                    resultDiv.innerHTML = `
                        <p><strong>Generated Link:</strong></p>
                        <p><a href="${data.apollo_url}" target="_blank">${data.apollo_url}</a></p>
                    `;
                } else {
                    resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
                resultDiv.style.display = 'block';
            })
            .catch(error => {
                document.getElementById('result').innerHTML = `<p style="color: red;">Error: ${error}</p>`;
                document.getElementById('result').style.display = 'block';
            });
        });
    </script>
    """

if __name__ == '__main__':
    # Use the PORT environment variable provided by Render
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
