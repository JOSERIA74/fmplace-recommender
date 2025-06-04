import pandas as pd
import json

def main():
    # 1) Read the master Excel file
    xls = pd.ExcelFile("config_recomendador.xlsx")
    df_tools     = xls.parse("Tools", dtype=str)
    df_questions = xls.parse("Questions", dtype=str)
    df_scores    = xls.parse("Scores", dtype=str)
    df_weights   = xls.parse("Weights", dtype={'question_code':str, 'weight':float})
    df_justs     = xls.parse("Justifications", dtype=str)
    df_adj       = xls.parse("Adjustments", dtype={
        'question_code': str,
        'option_index':  int,
        'tool_key':      str,
        'adjustment':    float
    })

    # 2) Map question_label to question_code
    label_to_code = df_questions.set_index("question_label")["question_code"].to_dict()

    # 3) Build scores JSON
    scores = {}
    for _, r in df_scores.iterrows():
        oi = str(int(r["option_index"]))
        ql = r["question_label"]
        qc = label_to_code.get(ql)
        if qc is None:
            raise ValueError(f"Question label not found: {ql}")
        tool_scores = {tk: float(r[tk]) for tk in df_tools["tool_key"]}
        scores[oi] = {
            "question_code": qc,
            "option_label":  r["option_label"],
            "scores":        tool_scores
        }
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2, ensure_ascii=False)

    # 4) Build weights JSON (question_code -> weight_factor)
    weights = df_weights.set_index("question_code")["weight"].to_dict()
    with open("weights.json", "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2, ensure_ascii=False)

    # 5) Build justifications JSON
    justifications = {}
    for _, r in df_justs.iterrows():
        tk = r["tool_key"]
        qc = r["question_code"]
        oi = str(int(r["option_index"]))
        justifications.setdefault(tk, {}).setdefault(qc, {
            "question_justification": r["question_justification"],
            "options": {}
        })["options"][oi] = r["option_justification"]
    with open("justifications.json", "w", encoding="utf-8") as f:
        json.dump(justifications, f, indent=2, ensure_ascii=False)

    # 6) Build adjustments JSON (tool_key -> question_code -> option_index -> adjustment)
    adjustments = {}
    for _, r in df_adj.iterrows():
        tk  = r["tool_key"]
        qc  = r["question_code"]
        oi  = str(int(r["option_index"]))
        val = float(r["adjustment"])
        adjustments.setdefault(tk, {}).setdefault(qc, {})[oi] = val
    with open("adjustments.json", "w", encoding="utf-8") as f:
        json.dump(adjustments, f, indent=2, ensure_ascii=False)

    # 7) Build metadata JSON (tools, questions, options)
    meta_tools = {}
    for _, row in df_tools.iterrows():
        key = row["tool_key"]
        meta_tools[key] = {
            "name": row["tool_name"],
            "url":  row.get("tool_url", "")
        }
    meta_questions = df_questions.set_index("question_code")["question_label"].to_dict()

    # Options labels metadata
    meta_options = {}
    for _, r in df_scores.iterrows():
        qc = label_to_code[r["question_label"]]
        oi = str(int(r["option_index"]))
        meta_options.setdefault(qc, {})[oi] = r["option_label"]

    metadata = {
        "tools":     meta_tools,
        "questions": meta_questions,
        "options":   meta_options
    }
    with open("metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print("✅ JSON files generated: scores.json, weights.json, justifications.json, adjustments.json, metadata.json")

if __name__ == "__main__":
    main()
