
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import json

app = Flask(__name__)

# Cargar matriz de puntuación y vector de ponderación
df_excel = pd.read_excel("Matriz Score-Vector Ponderacion-Respuestas Index.xlsx", sheet_name=None)

matriz_df = df_excel["Matriz Score"]
ponderacion_df = df_excel["Vector Ponderacion"]

# Cargar el mapeo válido de preguntas y respuestas
with open("mapping_respuestas.json") as f:
    valid_mappings = json.load(f)

# Preprocesar matriz
matriz_df = matriz_df.fillna(0)
tools = matriz_df.columns[3:]
matriz_puntajes = matriz_df[tools].to_numpy()
ponderacion_vector = ponderacion_df["Ponderación"].to_numpy()

# Crear diccionario índice para rápido acceso
index_mapping = dict(((row["Pregunta (ENG)"], row["Opción de Respuesta (ENG)"]), idx) for idx, row in matriz_df.iterrows())

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    if "respuestas" not in data:
        return jsonify({"error": "Missing 'respuestas' in request"}), 400

    respuestas = data["respuestas"]
    user_vector = np.zeros(matriz_puntajes.shape[0])

    for pregunta, opcion in respuestas.items():
        if pregunta not in valid_mappings or opcion not in valid_mappings[pregunta]:
            return jsonify({"error": f"No mapping found for: {pregunta} → {opcion}"}), 400
        key = (pregunta, opcion)
        idx = index_mapping.get(key)
        if idx is not None:
            user_vector[idx] = 1

    ponderado_vector = user_vector * ponderacion_vector
    scores = np.dot(ponderado_vector, matriz_puntajes)

    ranking = sorted(zip(scores, tools), reverse=True)
    resultado = {
        "ranking": [{"tool": tool, "score": float(score)} for score, tool in ranking],
        "top_1": ranking[0][1],
        "top_2": ranking[1][1],
        "top_3": ranking[2][1]
    }
    return jsonify(resultado)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
