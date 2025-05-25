from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import json

app = Flask(__name__)

# 1) Carga del Excel al iniciar
excel_path = "matriz.xlsx"

# 1.1) Matriz de scores con índice "Index"
df_scores = pd.read_excel(
    excel_path,
    sheet_name="Matriz Score",
    index_col="Index"
)

# 1.2) Vector de ponderación: columna "Pond Factor"
df_weights = (
    pd.read_excel(
        excel_path,
        sheet_name="Vector Ponderacion",
        usecols=["Index", "Pond Factor"]
    )
    .set_index("Index")["Pond Factor"]
)

# 1.3) Nombres de herramientas (columnas a partir de la 3ª)
tool_names = df_scores.columns[2:].tolist()

def compute_recommend(responses_idx):
    n = df_scores.shape[0]  # Número de preguntas
    # a) Vector binario
    user_vec = np.zeros(n, dtype=float)
    for r in responses_idx:
        idx = int(r)
        if idx in df_weights.index:
            user_vec[idx] = 1
        else:
            print(f"⚠️ Índice {idx} no válido")

    # b) Aplica ponderación
    weighted = user_vec * df_weights.values

    # c) Matriz de puntuaciones de herramientas
    score_matrix = df_scores[tool_names].values  # (n×m)

    # d) Multiplicación para obtener score por herramienta
    tool_scores = score_matrix.T.dot(weighted)   # (m,)

    # e) Ranking
    ranked = sorted(
        zip(tool_names, tool_scores),
        key=lambda x: x[1],
        reverse=True
    )

    return {
        "ranking": [{"tool": t, "score": float(s)} for t, s in ranked],
        "top_1": ranked[0][0],
        "top_2": ranked[1][0],
        "top_3": ranked[2][0]
    }

@app.route("/")
def home():
    return "API de recomendación FP&A funcionando"

@app.route("/recommend", methods=["POST"])
def recommend_route():
    # 1) Intentar JSON puro
    if request.is_json:
        data = request.get_json(force=True)
        responses = data.get("responses", [])
    else:
        # 2) Leer form-urlencoded o form-data
        raw = request.form.get("responses") or request.values.get("responses", "")
        try:
            # Si viene como JSON string "[1,2,3]"
            responses = json.loads(raw)
        except Exception:
            # Sino asumimos CSV "1,2,3"
            responses = [s.strip() for s in raw.split(",") if s.strip()]

    # Convertir todo a cadenas
    responses_str = [str(x) for x in responses]
    try:
        result = compute_recommend(responses_str)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Replit escucha en el puerto 3000 por defecto
    app.run(host="0.0.0.0", port=3000)
