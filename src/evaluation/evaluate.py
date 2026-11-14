import csv
import sys
from collections import Counter

from src.processing.skills import SKILLS, extract_skills

LABELS_PATH = "data/labels.csv"


def parse_true_skills(cell):
    return {s.strip() for s in (cell or "").split(";") if s.strip()}


def score(true_sets, pred_sets):
    tp = fp = fn = 0
    for true, pred in zip(true_sets, pred_sets):
        tp += len(true & pred)
        fp += len(pred - true)
        fn += len(true - pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return tp, fp, fn, precision, recall, f1


def main() -> None:
    try:
        with open(LABELS_PATH, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"{LABELS_PATH} not found. Run the export script first.")
        sys.exit(1)

    done = [r for r in rows if (r.get("done") or "").strip().lower() == "y"]
    if not done:
        print("No rows are marked done=y yet.")
        sys.exit(1)

    true_sets, pred_sets = [], []
    unknown = set()
    fp_counter, fn_counter = Counter(), Counter()

    for r in done:
        true = parse_true_skills(r["true_skills"])
        unknown |= true - set(SKILLS)
        pred = extract_skills(r["title"], r["description"])
        true_sets.append(true)
        pred_sets.append(pred)
        fp_counter.update(pred - true)
        fn_counter.update(true - pred)

    if unknown:
        print("Warning - these labels are not in the skills dictionary:")
        print(", ".join(sorted(unknown)))
        print()

    tp, fp, fn, p, r_, f1 = score(true_sets, pred_sets)
    print(f"Jobs evaluated: {len(done)}")
    print(f"True positives: {tp}  False positives: {fp}  False negatives: {fn}")
    print(f"Precision: {p:.2%}")
    print(f"Recall:    {r_:.2%}")
    print(f"F1:        {f1:.2%}")
    print()
    print("Most common false positives (extractor found it, you did not):")
    for skill, n in fp_counter.most_common(5) or [("none", 0)]:
        print(f"  {skill}: {n}")
    print("Most common false negatives (you labelled it, extractor missed it):")
    for skill, n in fn_counter.most_common(5) or [("none", 0)]:
        print(f"  {skill}: {n}")


if __name__ == "__main__":
    main()
