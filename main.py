
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# === Load data on startup ===
matriz = pd.read_csv("matriz_ponderada.csv")
etiquetas = pd.read_excel("Matriz Score y Vector Ponderacion.xlsx", sheet_name="Matriz Score")
ponderacion = pd.read_excel("Matriz Score y Vector Ponderacion.xlsx", sheet_name="Vector Ponderacion")["Pond Factor"].values

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    user_responses = data.get("responses", {})

    # Crear vector binario de 60 posiciones
    vector_usuario = []
    for pregunta, opcion in zip(etiquetas["Pregunta (ENG)"], etiquetas["Opción de Respuesta (ENG)"]):
        r = user_responses.get(pregunta, "")
        vector_usuario.append(1.0 if isinstance(r, str) and opcion.strip() in r else 0.0)

    vector_usuario = np.array(vector_usuario)
    embedding_usuario = vector_usuario * ponderacion

    tools = matriz.columns.tolist()
    tool_vectors = matriz.to_numpy().T
    similitudes = cosine_similarity([embedding_usuario], tool_vectors)[0]
    ranking = sorted(zip(tools, similitudes), key=lambda x: x[1], reverse=True)

    return jsonify({
        "top_1": ranking[0][0],
        "top_2": ranking[1][0],
        "top_3": ranking[2][0],
        "ranking": [{ "tool": t, "score": float(s) } for t, s in ranking]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
