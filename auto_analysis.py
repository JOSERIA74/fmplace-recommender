import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# --- 1. Carga de datos JSON ---
with open("scores.json", encoding="utf-8") as f:
    scores = json.load(f)
with open("weights.json", encoding="utf-8") as f:
    weights = json.load(f)
with open("adjustments.json", encoding="utf-8") as f:
    adjustments = json.load(f)
with open("metadata.json", encoding="utf-8") as f:
    metadata = json.load(f)

questions = metadata["questions"]
tool_keys = list(metadata["tools"].keys())

# --- 2. Construir DataFrame de raw scores: herramientas × opción ---
rows = []
for oi, entry in scores.items():
    qc = entry["question_code"]
    for tk, raw in entry["scores"].items():
        rows.append({
            "option_index": oi,
            "question_code": qc,
            "tool_key": tk,
            "raw_score": float(raw)
        })
df_raw_long = pd.DataFrame(rows)

# Matriz: filas=tool_key, columnas=option_index
df_raw = df_raw_long.pivot_table(index="tool_key", columns="option_index", values="raw_score", fill_value=0.0)

# --- 3. PCA ---
pca = PCA(n_components=2)
components = pca.fit_transform(df_raw)
df_pca = pd.DataFrame(components, columns=["PC1", "PC2"], index=df_raw.index)

plt.figure(figsize=(8, 6))
for tk in df_pca.index:
    x, y = df_pca.loc[tk]
    plt.scatter(x, y, s=100)
    plt.text(x + 0.02, y + 0.02, tk.capitalize(), fontsize=9)
plt.title("PCA de vectores de raw scores")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.grid(True)
plt.savefig("pca_plot.png")
plt.clf()

# --- 4. Clustering KMeans sobre PCA ---
kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(components)
df_pca["Cluster"] = labels

plt.figure(figsize=(8, 6))
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
for cluster_id in sorted(df_pca["Cluster"].unique()):
    subset = df_pca[df_pca["Cluster"] == cluster_id]
    plt.scatter(subset["PC1"], subset["PC2"], c=colors[cluster_id], label=f"Cluster {cluster_id}", s=100)
    for tk in subset.index:
        x, y = subset.loc[tk, ["PC1", "PC2"]]
        plt.text(x + 0.02, y + 0.02, tk.capitalize(), fontsize=9)
plt.title("Clustering KMeans (k=3) sobre PCA")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.legend()
plt.grid(True)
plt.savefig("clusters_plot.png")
plt.clf()

# --- 5. Simulación de margen medio ---
options_by_question = {
    qc: list(group["option_index"].astype(int).values)
    for qc, group in df_raw_long.groupby("question_code")
}
def compute_ranking(responses, weights_override=None):
    total = {tk: 0.0 for tk in tool_keys}
    for qc, oi in responses.items():
        entry = scores.get(str(oi), {})
        w = weights_override.get(qc, weights.get(qc, 0.0)) if weights_override else weights.get(qc, 0.0)
        for tk, raw in entry.get("scores", {}).items():
            total[tk] += float(raw) * float(w)
    return total

def average_margin(weights_override=None, n_samples=1000):
    margins = []
    for _ in range(n_samples):
        simulated = {qc: np.random.choice(opts) for qc, opts in options_by_question.items()}
        scores_dict = compute_ranking(simulated, weights_override)
        sorted_scores = sorted(scores_dict.values(), reverse=True)
        if len(sorted_scores) >= 2:
            margins.append(sorted_scores[0] - sorted_scores[1])
    return np.mean(margins)

base_margin = average_margin(n_samples=2000)
print(f"Margen promedio con pesos actuales: {base_margin:.4f}")

# --- 6. Búsqueda heurística de optimización de pesos ---
current_weights = weights.copy()
for iteration in range(5):
    for qc in options_by_question.keys():
        orig_w = current_weights[qc]
        # probar -10%
        w_down = orig_w * 0.90
        margin_down = average_margin({**current_weights, qc: w_down}, n_samples=500)
        # probar +10%
        w_up = orig_w * 1.10
        margin_up = average_margin({**current_weights, qc: w_up}, n_samples=500)
        # comparar y asignar mejor
        best_w = orig_w
        best_m = average_margin(current_weights, n_samples=500)
        if margin_down > best_m and margin_down > margin_up:
            best_w = w_down
        elif margin_up > best_m:
            best_w = w_up
        current_weights[qc] = best_w
    print(f"Iteración {iteration+1}: margen = {average_margin(current_weights, n_samples=1000):.4f}")

# --- 7. Tablas de salida ---
df_metrics = []
for qc, grp in df_raw_long.groupby("question_code"):
    diffs = grp.groupby("option_index")["raw_score"].agg(["max", "min"])
    diffs["spread"] = diffs["max"] - diffs["min"]
    df_metrics.append({
        "question_code": qc,
        "label": questions.get(qc, qc),
        "variance_raw": grp["raw_score"].var(),
        "avg_spread": diffs["spread"].mean(),
        "max_spread": diffs["spread"].max(),
        "current_weight": weights.get(qc, 0.0)
    })
df_metrics = pd.DataFrame(df_metrics).sort_values("avg_spread", ascending=False)
print("\n--- Discriminación por Pregunta ---")
print(df_metrics.to_string(index=False))

# Ajustes vs contribución
adj_rows = []
for tk, tool_dict in adjustments.items():
    for qc, opts in tool_dict.items():
        for oi, bonus in opts.items():
            raw = df_raw_long[(df_raw_long["tool_key"]==tk) &
                              (df_raw_long["question_code"]==qc) &
                              (df_raw_long["option_index"]==oi)]["raw_score"].iloc[0]
            w = weights.get(qc, 0.0)
            weighted_raw = raw * w
            adj_rows.append({
                "tool_key": tk,
                "question_code": qc,
                "option_index": oi,
                "raw_score": raw,
                "weight": w,
                "weighted_raw": weighted_raw,
                "adjustment": bonus,
                "ratio": bonus / weighted_raw if weighted_raw else np.nan
            })
df_adj = pd.DataFrame(adj_rows)
df_adj_sorted = df_adj.sort_values("ratio", ascending=False).head(20)
print("\n--- Ajustes vs Contribución Pesada (top 20) ---")
print(df_adj_sorted.to_string(index=False))

# Comparativa pesos original vs optimizado
df_new = pd.DataFrame.from_dict(current_weights, orient="index", columns=["optimizado"])
df_orig = pd.DataFrame.from_dict(weights, orient="index", columns=["original"])
df_compare = df_orig.join(df_new)
df_compare["delta_pct"] = (df_compare["optimizado"] - df_compare["original"]) / df_compare["original"] * 100
print("\n--- Comparativa de Pesos (Original vs Optimizado) ---")
print(df_compare.to_string())

outliers = df_compare[np.abs(df_compare["delta_pct"]) > 10]
print("\n--- Preguntas con cambio de peso >10% ---")
print(outliers.to_string())

# --- 8. Gráfico final de comparación de pesos ---
plt.figure(figsize=(10, 5))
df_compare[["original", "optimizado"]].plot(kind="barh")
plt.title("Pesos Originales vs Optimizado")
plt.xlabel("Valor de peso")
plt.tight_layout()
plt.savefig("weights_comparison.png")
plt.clf()

print("\n✅ Análisis completado. Archivos generados:")
print(" - pca_plot.png")
print(" - clusters_plot.png")
print(" - weights_comparison.png")
