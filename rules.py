
import yaml
from pathlib import Path

RULES_PATH = Path(__file__).with_name("tr_flow.yaml")

def load_rules():
    with open(RULES_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def evaluate_condition(cond_expr, context):
    """Very small sandboxed eval for simple boolean expressions."""
    try:
        return eval(cond_expr, {}, context)
    except Exception:
        return False
