# FM Place Recommender

**FP\&A Tool Recommendation API & Configuration**

This repository contains all the configuration and code needed to generate personalized FP\&A tool recommendations based on user responses.

---

## 📁 Repository Structure

```
├── config_recomendador.xlsx   # Master Excel with all tools, questions, scores, weights, justifications
├── excel_to_json.py           # Script to convert Excel sheets into JSON configs
├── generate-json.yml          # (Optional) GitHub Actions workflow to auto–regenerate JSON on push
├── metadata.json              # Generated: question labels + tool names & URLs
├── scores.json                # Generated: per‑option scores for each tool
├── weights.json               # Generated: per‑question weight factors
├── justifications.json        # Generated: text justifications for each tool & option
├── main.py                    # Flask API exposing `/recommend` endpoint
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## ⚙️ Setup & Usage

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Edit your Excel**

   * Open `config_recomendador.xlsx` in the **Tools**, **Questions**, **Scores**, **Weights**, and **Justifications** sheets.
   * To add a new FP\&A tool, append rows in **Tools** (include `tool_key`, `tool_name`, `tool_url`).
   * To change questions or options, update the **Questions** and **Scores** sheets.

3. **Generate JSON configs**

   ```bash
   python excel_to_json.py
   ```

   This produces:

   * `metadata.json` (tools + question labels + URLs)
   * `scores.json`  (option‑level scoring matrix)
   * `weights.json` (per‑question weights)
   * `justifications.json` (text justifications)

4. **Run the API**

   ```bash
   python main.py
   ```

   The Flask app will listen on port `3000`:

   * **GET /** → health check
   * **POST /recommend** → accepts JSON `{ "responses": { "q1_size": 2, … } }` and returns top 3 tool keys, names, and URLs.

5. **Integrate with Make (Integromat)**

   * Call `/recommend` with user responses.
   * Fetch `metadata.json` & `justifications.json` via HTTP modules.
   * Send data to your OpenAI Assistant to generate personalized HTML.
   * Send email with the generated content and CTA buttons using the dynamic `tool_url` fields.

---

## 🔄 Continuous Integration (Optional)

A GitHub Actions workflow (`generate-json.yml`) can be configured to auto–run `excel_to_json.py` and commit the updated JSON files whenever you push changes to `config_recomendador.xlsx`.

---

## 📝 Contributing

* **Excel edits**: update the master file.
* **Code tweaks**: propose changes to `main.py` or `excel_to_json.py`.
* **Issues & PRs**: welcome for bugs, enhancements, or documentation improvements.

---

© 2025 FM Place. All rights reserved.
