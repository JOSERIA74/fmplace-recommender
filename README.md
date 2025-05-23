
# FM Place Recommender API

This is a Python-based recommendation API for FM Place, deployed on Google Cloud Run. It receives a user's form responses and returns the top 3 FP&A tools based on a matrix scoring model and similarity calculation.

---

## 📦 Project Structure

```
.
├── main.py                             # Flask API endpoint for /recommend
├── requirements.txt                   # Python dependencies
├── Dockerfile                         # Container definition for Cloud Run
├── matriz_ponderada.csv               # Final scoring matrix (tools x questions)
└── Matriz Score y Vector Ponderacion.xlsx # Source: raw scores + weights + metadata
```

---

## 🧠 What It Does

This API:

1. Loads a precomputed matrix of scores (`matriz_ponderada.csv`)
2. Loads metadata and weighting factors from the Excel file
3. Accepts a JSON with user responses to 13 questions
4. Builds a binary vector (one-hot) for the 60 options
5. Applies weightings to generate a user embedding
6. Calculates cosine similarity between the user vector and each tool
7. Returns the top 3 tools with similarity scores

---

## 🔗 Endpoint

```
POST /recommend
Content-Type: application/json
```

### 🔸 Input Format

```json
{
  "responses": {
    "What is the size of your company?": "51-200 employees",
    "What is your annual budget?": "30K-60K USD/year",
    ...
  }
}
```

### 🔸 Response Format

```json
{
  "top_1": "Cube",
  "top_2": "Pigment",
  "top_3": "Acterys",
  "ranking": [
    { "tool": "Cube", "score": 0.938 },
    { "tool": "Pigment", "score": 0.911 },
    ...
  ]
}
```

---

## 🚀 Deployment

This app is containerized via `Dockerfile` and designed to be deployed to Google Cloud Run.

To build and deploy:

```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/fmplace-recommender
gcloud run deploy fmplace-recommender   --image gcr.io/YOUR_PROJECT_ID/fmplace-recommender   --platform managed   --region europe-west1   --allow-unauthenticated
```

---

## 🧩 Integrations

- **Fillout + Make**: Sends form responses to this API
- **GPT Assistant (OpenAI)**: Uses top 3 tools to generate a justification HTML
- **Make**: Sends final email with recommendations to the user

---

## 📌 Author

Built by Jose Ramon for FM Place (AI-driven FP&A Tool Selector).
