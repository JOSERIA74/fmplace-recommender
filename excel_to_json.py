import pandas as pd
import json

# 1) Read the master Excel file
xls = pd.ExcelFile("config_recomendador.xlsx")
df_tools     = xls.parse("Tools", dtype=str)
df_questions = xls.parse("Questions", dtype=str).set_index("question_label")
df_scores    = xls.parse("Scores")
df_weights   = xls.parse("Weights", dtype={'question_code':str, 'weight':float}).set_index("question_code")
df_justs     = xls.parse("Justifications", dtype=str)

# 2) Map question_label to question_code
label_to_code = df_questions["question_code"].to_dict()

# 3) Build scores JSON
scores = {}
for _, r in df_scores.iterrows():
    oi = str(int(r["option_index"]))
    ql = r["question_label"]
    qc = label_to_code.get(ql)
    if qc is None:
        raise ValueError(f"Question label not found: {ql}")
    scores[oi] = {
        "question_code": qc,
        "option_label": r["option_label"],
        **{tk: float(r[tk]) for tk in df_tools["tool_key"]}
    }

# 4) Build weights JSON
weights = df_weights["weight"].to_dict()

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

# 6) Build metadata JSON (with URLs)
#    Extract both tool_name and tool_url
meta_tools = {}
for _, row in df_tools.iterrows():
    key = row["tool_key"]
    meta_tools[key] = {
        "name": row["tool_name"],
        "url":  row.get("tool_url", "")
    }

meta_questions = xls.parse("Questions", dtype=str).set_index("question_code")["question_label"].to_dict()

metadata = {
    "tools":     meta_tools,
    "questions": meta_questions
}

# 7) Save JSON files
with open("scores.json", "w", encoding="utf-8") as f:
    json.dump(scores, f, indent=2, ensure_ascii=False)
with open("weights.json", "w", encoding="utf-8") as f:
    json.dump(weights, f, indent=2, ensure_ascii=False)
with open("justifications.json", "w", encoding="utf-8") as f:
    json.dump(justifications, f, indent=2, ensure_ascii=False)
with open("metadata.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print("✅ JSON files generated.")
