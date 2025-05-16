# Apollo Filter Generator API

This API takes natural language queries and returns Apollo.io search links.

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_herecurl -X POST https://your-render-app-url.onrender.com/api/generate-link \
  -H "Content-Type: application/json" \
  -d '{"query": "Marketing managers in medium-sized tech companies"}'
```

3. Run the server:
```
python app.py
```

## API Usage

### Generate Apollo Search Link

**Endpoint:** `POST /api/generate-link`

**Request Body:**
```json
{
  "query": "Your search query here, e.g. 'Find importers in the USA with company size of 10-50 employees'"
}
```

**Example Response:**
```json
{
  "apollo_url": "https://app.apollo.io/#/people?page=1&sortAscending=false&sortByField=recommendations_score&contactEmailStatusV2[]=verified&personTitles[]=importer&organizationNumEmployeesRanges[]=11,20&organizationNumEmployeesRanges[]=21,50&personLocations[]=USA",
  "status": "success"
}
```

## Error Handling

If an error occurs, the API will return a JSON response with an error message and a 400 or 500 status code.
