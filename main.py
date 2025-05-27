from flask import Flask, request, jsonify
import json

app = Flask(__name__)

# Load configuration from generated JSON files
d = lambda f: json.load(open(f, 'r', encoding='utf-8'))
scores = d("scores.json")
weights = d("weights.json")
justifications = d("justifications.json")
metadata = d("metadata.json")


def compute_recommend(responses):
    """
    Compute weighted scores per tool based on user responses.
    responses: dict mapping question_code -> option_index (int)
    returns: list of top 3 tool_keys
    """
    # Initialize accumulators
    tool_scores = {tk: 0.0 for tk in metadata["tools"].keys()}

    for qc, oi in responses.items():
        oi_str = str(oi)
        weight = weights.get(qc, 1.0)
        row = scores.get(oi_str)
        # Validate question_code
        if not row or row.get("question_code") != qc:
            continue
        # Add weighted score for each tool
        for tk in tool_scores:
            val = row.get(tk)
            if val is not None:
                tool_scores[tk] += float(val) * weight

    # Sort by descending score and return top 3 keys
    ranked = sorted(tool_scores.items(), key=lambda x: x[1], reverse=True)
    return [tk for tk, _ in ranked[:3]]


@app.route("/recommend", methods=["POST"])
def recommend_route():
    payload = request.get_json(force=True)
    responses = payload.get("responses", {})

    top3 = compute_recommend(responses)
    output = {}
    for idx, tk in enumerate(top3, start=1):
        output[f"top_{idx}"] = tk
        tool_info = metadata["tools"].get(tk, {})
        output[f"top_{idx}_name"] = tool_info.get("name")
        output[f"top_{idx}_url"] = tool_info.get("url")

    return jsonify(output)


@app.route("/")
def home():
    return "FP&A Recommendation API is running."


if __name__ == "__main__":
    # Replit listens on port 3000 by default
    app.run(host="0.0.0.0", port=3000)
