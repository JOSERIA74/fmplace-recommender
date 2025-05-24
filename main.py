
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Load the Excel file with multiple sheets
excel_path = "Matriz Score-Vector Ponderacion-Respuestas Index.xlsx"
df_scores = pd.read_excel(excel_path, sheet_name="Matriz Score")
df_weights = pd.read_excel(excel_path, sheet_name="Vector Ponderacion", index_col=0)
df_mapping = pd.read_excel(excel_path, sheet_name="Respuestas Index")

# Create the mapping dictionary from response_id to row index
mapping_dict = dict(zip(df_mapping["Respuesta ID"], df_mapping["Index"]))

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    if "responses" not in data:
        return jsonify({"error": "Missing 'responses' in request"}), 400

    try:
        user_response_ids = data["responses"]
        user_vector = np.zeros(len(df_scores), dtype=int)
        for response_id in user_response_ids:
            idx = mapping_dict.get(response_id)
            if idx is not None:
                user_vector[idx] = 1

        # Apply weights
        weights = df_weights["Peso"].values
        weighted_vector = user_vector * weights

        # Compute scores
        score_matrix = df_scores.iloc[:, 3:].values
        tool_scores = score_matrix.T @ weighted_vector
        tools = df_scores.columns[3:]
        ranking = sorted(zip(tools, tool_scores), key=lambda x: x[1], reverse=True)

        response = {
            "ranking": [{"tool": tool, "score": float(score)} for tool, score in ranking],
            "top_1": ranking[0][0],
            "top_2": ranking[1][0],
            "top_3": ranking[2][0],
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "FM Place Recommender API is live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
