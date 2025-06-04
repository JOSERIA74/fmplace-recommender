from flask import Flask, request, jsonify
import json
import math

app = Flask(__name__)

# Load configuration JSONs
with open("scores.json", encoding="utf-8") as f:
    scores = json.load(f)
with open("weights.json", encoding="utf-8") as f:
    weights = json.load(f)
with open("justifications.json", encoding="utf-8") as f:
    justifications = json.load(f)
with open("adjustments.json", encoding="utf-8") as f:
    adjustments = json.load(f)
with open("metadata.json", encoding="utf-8") as f:
    metadata = json.load(f)

# List of all tool keys
tools_list = list(metadata["tools"].keys())


@app.route("/")
def health():
    return "OK"


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True)
    responses = data.get("responses", {})

    # 1) Base score: weighted sum (score * weight_factor)
    tool_scores = {tk: 0.0 for tk in tools_list}
    for qc, oi in responses.items():
        oi_str = str(oi)
        row = scores.get(oi_str)
        if not row or row.get("question_code") != qc:
            continue
        weight = weights.get(qc, 1.0)
        if weight is None:
            weight = 0.0
        for tk, sc in row.get("scores", {}).items():
            # Ensure sc is numeric
            try:
                sc_val = float(sc)
            except (TypeError, ValueError):
                sc_val = 0.0
            tool_scores[tk] += sc_val * weight

    # 2) Apply per-tool adjustments (treat NaN as 0)
    for tk, tool_adj in adjustments.items():
        for qc, opts in tool_adj.items():
            oi_str = str(responses.get(qc))
            raw_bonus = opts.get(oi_str, 0)
            # Convert possible NaN to 0
            try:
                bonus = float(raw_bonus)
                if math.isnan(bonus):
                    bonus = 0.0
            except (TypeError, ValueError):
                bonus = 0.0
            tool_scores[tk] += bonus

    # 3) Build full ranking
    ranked = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
    ranking = [{"tool": tk, "score": score} for tk, score in ranked]

    result = {
        "ranking": ranking,
        "top_1": ranking[0]["tool"] if len(ranking) > 0 else None,
        "top_2": ranking[1]["tool"] if len(ranking) > 1 else None,
        "top_3": ranking[2]["tool"] if len(ranking) > 2 else None
    }
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
