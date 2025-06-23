import re
import json

with open("pattern_rules.json", "r", encoding="utf-8") as f:
    RULES = json.load(f)["patterns"]

def detect_pattern(history):
    seq = "".join(history[-10:])  # Lấy 10 phiên gần nhất
    for key, rule in RULES.items():
        patterns = rule["rule"].split("|")
        for p in patterns:
            if re.search(p, seq):
                return rule
    return None
