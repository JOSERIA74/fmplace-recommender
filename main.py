from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Carga el archivo Excel con las tres hojas necesarias
excel_path = "matriz.xlsx"
df_scores = pd.read_excel(excel_path, sheet_name="Matriz Score")
df_weights = pd.read_excel(excel_path, sheet_name="Vector Ponderacion", index_col=0)
df_mapping = pd.read_excel(excel_path, sheet_name="Respuestas Index")

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    if "responses" not in data:
        return jsonify({"error": "Missing 'responses' in request"}), 400

    try:
        response_indices = data["responses"]  # Ejemplo: [1, 8, 13, ...]
        num_rows = len(df_scores)

        # Vector binario del usuario
        user_vector = np.zeros(num_rows, dtype=int)
        for idx in response_indices:
            if 0 <= idx < num_rows:
                user_vector[idx] = 1

        # Aplicar ponderaciones
        weights = df_weights["Peso"].values
        weighted_vector = user_vector * weights

        # Calcular scores para cada herramienta
        score_matrix = df_scores.iloc[:, 3:].values  # columnas con herramientas
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