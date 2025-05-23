
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# === Load data once at startup ===

EXCEL_PATH = "Matriz Score-Vector Ponderacion-Respuestas Index.xlsx"

df_score = pd.read_excel(EXCEL_PATH, sheet_name="Matriz Score", index_col=0)
df_weights = pd.read_excel(EXCEL_PATH, sheet_name="Vector Ponderacion", header=None).iloc[:, 0]
df_mapping = pd.read_excel(EXCEL_PATH, sheet_name="Mapping Respuestas")

tools = df_score.columns.tolist()
num_options = len(df_score)

# === Build mapping: (question, option) -> index in score matrix ===

mapping_dict = {
    (row["Pregunta (ENG)"], row["Opción de Respuesta (ENG)"]): row["Index"]
    for _, row in df_mapping.iterrows()
}

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    if "responses" not in data:
        return jsonify({"error": "Missing 'responses' in request"}), 400

    responses = data["responses"]
    vector = np.zeros(num_options)

    for question, answer in responses.items():
        key = (question, answer)
        if key not in mapping_dict:
            return jsonify({"error": f"No mapping found for: {question} → {answer}"}), 400
        idx = mapping_dict[key]
        vector[idx] = 1.0

    # Apply weights
    weighted_vector = vector * df_weights.values

    # Compute similarity score (dot product)
    scores = df_score.T.dot(weighted_vector)

    ranking = scores.sort_values(ascending=False).reset_index()
    ranking.columns = ["tool", "score"]

    return jsonify({
        "top_1": ranking.iloc[0]["tool"],
        "top_2": ranking.iloc[1]["tool"],
        "top_3": ranking.iloc[2]["tool"],
        "ranking": ranking.to_dict(orient="records")
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
