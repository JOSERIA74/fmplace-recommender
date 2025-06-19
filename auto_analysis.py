import json
import math
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt

def load_configs():
    with open("scores.json", encoding="utf-8") as f:
        scores = json.load(f)
    with open("weights.json", encoding="utf-8") as f:
        weights = json.load(f)
    with open("adjustments.json", encoding="utf-8") as f:
        adjustments = json.load(f)
    return scores, weights, adjustments

def build_matrix(scores, weights, adjustments):
    # herramientas
    tools = list(next(iter(scores.values()))["scores"].keys())
    # preguntas en orden
    questions = sorted({row["question_code"] for row in scores.values()})
    X = []
    for tk in tools:
        row_vals = []
        for qc in questions:
            cell_vals = []
            for oi_str, entry in scores.items():
                if entry["question_code"] != qc:
                    continue
                sc = entry["scores"].get(tk, 0.0) or 0.0
                w  = weights.get(qc, 0.0) or 0.0
                adj = adjustments.get(tk, {}).get(qc, {}).get(oi_str, 0.0) or 0.0
                cell_vals.append(sc * w + adj)
            row_vals.append(np.mean(cell_vals) if cell_vals else 0.0)
        X.append(row_vals)
    return np.array(X), tools, questions

def optimize_weights(scores, weights, adjustments):
    # placeholder: tu lógica real aquí
    print(f"Margen promedio con pesos actuales: {np.random.rand():.4f}")
    for i in range(5):
        print(f"Iteración {i+1}: margen = {np.random.rand():.4f}")
    # ej.: no cambiamos realmente
    return weights.copy()

def plot_pca_and_normalize(X, tools):
    # PCA
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    # DataFrame original
    df_pca = pd.DataFrame(X_pca, index=tools, columns=["PC1", "PC2"])
    print("\n📊 PCA Coordinates (first 2 components):")
    print(df_pca.to_string())

    # Guarda JSON
    df_pca.to_json("pca_coordinates.json", orient="index")
    print("\n✅ Saved PCA coords to pca_coordinates.json")

    # Normalización 0–1 con MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0,1))
    df_norm = pd.DataFrame(
        scaler.fit_transform(df_pca),
        index=df_pca.index,
        columns=["PC1_norm", "PC2_norm"]
    )
    df_final = df_pca.join(df_norm)
    df_final.to_csv("pca_coordinates_normalized.csv", index=True)
    print("\n✅ Saved normalized PCA coords to pca_coordinates_normalized.csv")
    print(df_final.head().to_string())

    # Plot original PCA
    plt.figure(figsize=(6,6))
    plt.scatter(X_pca[:,0], X_pca[:,1])
    for i, t in enumerate(tools):
        plt.text(X_pca[i,0], X_pca[i,1], t, fontsize=9)
    plt.title("PCA of Tools (raw PC1 vs PC2)")
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.tight_layout()
    plt.savefig("pca_plot.png")
    plt.close()

    return X_pca

def plot_clusters(X_pca, tools, k=3):
    km = KMeans(n_clusters=k, random_state=0).fit(X_pca)
    labels = km.labels_
    plt.figure(figsize=(6,6))
    for i, t in enumerate(tools):
        plt.text(X_pca[i,0], X_pca[i,1], t, color=f"C{labels[i]}")
    plt.title(f"KMeans Clusters (k={k})")
    plt.tight_layout()
    plt.savefig("clusters_plot.png")
    plt.close()

def main():
    # 1) Carga config
    scores, weights, adjustments = load_configs()

    # 2) Construye matriz
    X, tools, questions = build_matrix(scores, weights, adjustments)

    # 3) Optimiza pesos (si aplica)
    _ = optimize_weights(scores, weights, adjustments)

    # 4) PCA + normalización + CSV + gráfico
    X_pca = plot_pca_and_normalize(X, tools)

    # 5) Clusters
    plot_clusters(X_pca, tools, k=3)

    print("\n✅ Análisis completado. Archivos generados:")
    print(" - pca_coordinates.json")
    print(" - pca_coordinates_normalized.csv")
    print(" - pca_plot.png")
    print(" - clusters_plot.png")

if __name__ == "__main__":
    main()
