
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np

app = Flask(__name__)

# Cargar datos
excel = pd.read_excel("Matriz Score-Vector Ponderacion-Respuestas Index.xlsx", sheet_name=None)
matriz = excel["Matriz Score"]
ponderacion = excel["Vector Ponderacion"]

# Construir matriz de puntuaciones
tools = matriz.columns[3:]
matriz_puntajes = matriz[tools].fillna(0).to_numpy()
ponderacion_vector = ponderacion["Ponderación"].to_numpy()

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    respuestas = data.get("vector", [])

    # Inicializar vector binario de longitud igual al número de filas de la matriz
    vector_usuario = np.zeros(matriz_puntajes.shape[0])

    try:
        for idx in respuestas:
            index = int(idx)
            if 0 <= index < len(vector_usuario):
                vector_usuario[index] = 1
    except Exception as e:
        return jsonify({"error": f"Invalid input vector: {e}"}), 400

    # Aplicar ponderación
    ponderado = vector_usuario * ponderacion_vector

    # Calcular score por herramienta
    scores = np.dot(ponderado, matriz_puntajes)
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
