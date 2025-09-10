# src/main.py
from __future__ import annotations
import argparse, os
from .services.app import build_coordinator
from dotenv import load_dotenv

load_dotenv()

def run_cli() -> None:
    co = build_coordinator()
    print("MultiAgent Chat System — type 'exit' to quit the chat.\n")
    while True:
        try:
            q = input("You: ").strip()
        except EOFError:
            break
        if not q:
            continue
        if q.lower() in {"exit","quit"}:
            break
        ans = co.handle_user_query(q)
        print("\nManager:", ans, "\n")

def run_scenarios() -> None:
    co = build_coordinator()
    outputs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
    os.makedirs(outputs_dir, exist_ok=True)
    scenarios = [
        ("simple_query.txt", "What are the main types of neural networks?"),
        ("complex_query.txt", "Research transformer architectures, analyze their computational efficiency, and summarize key trade-offs."),
        ("memory_test.txt", "What did we discuss about neural networks earlier?"),
        ("multi_step.txt", "Find recent papers on reinforcement learning, analyze their methodologies, and identify common challenges."),
        ("collaborative.txt", "Compare two machine-learning approaches and recommend which is better for our use case."),
    ]
    for fname, prompt in scenarios:
        ans = co.handle_user_query(prompt)
        path = os.path.join(outputs_dir, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"User: {prompt}\n\nManager:\n{ans}\n")
    print(f"Wrote outputs to: {outputs_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["cli","scenarios"], default="cli")
    args = parser.parse_args()
    if args.mode == "cli":
        run_cli()
    else:
        run_scenarios()
