import json
import os
import pathlib
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=pathlib.Path(__file__).parent.parent.parent / ".env")

# Map LLM_API_KEY to OPENAI_API_KEY for Ragas
if "OPENAI_API_KEY" not in os.environ and "LLM_API_KEY" in os.environ:
    os.environ["OPENAI_API_KEY"] = os.environ["LLM_API_KEY"]

from ragas import evaluate, EvaluationDataset
from ragas.metrics import (
    Faithfulness,
    ResponseRelevancy,
    LLMContextPrecisionWithoutReference,
)

GATEWAY = "http://localhost:3000"
GOLDEN = pathlib.Path(__file__).parent / "golden.jsonl"

def load_golden():
    return [json.loads(l) for l in GOLDEN.read_text().splitlines() if l.strip()]

def run_system(question: str) -> dict:
    r = requests.post(f"{GATEWAY}/query", json={"question": question}, timeout=120)
    r.raise_for_status()
    return r.json()

def main():
    rows = []
    for item in load_golden():
        out = run_system(item["question"])
        rows.append({
            "user_input":         item["question"],
            "response":           out["answer"],
            "retrieved_contexts": [c["text"] for c in out.get("citations", [])],
        })
        print(f"  ran: {item['question'][:60]}")

    ds = EvaluationDataset.from_list(rows)
    result = evaluate(ds, metrics=[
        Faithfulness(),
        ResponseRelevancy(),
        LLMContextPrecisionWithoutReference(),
    ])
    print("\n=== RAGAS RESULTS ===")
    print(result)
    df = result.to_pandas()
    df.to_csv(pathlib.Path(__file__).parent / "last_run.csv", index=False)
    print("per-question scores -> evals/last_run.csv")

if __name__ == "__main__":
    main()