import csv
import sys

from src.processing.skills import _PATTERNS, SKILLS, extract_skills

LABELS_PATH = "data/labels.csv"
FIELDS = ["job_id", "title", "description", "true_skills", "done"]
LOOKUP = {name.lower(): name for name in SKILLS}


def load_rows():
    with open(LABELS_PATH, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save_rows(rows):
    with open(LABELS_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def contexts(text):
    """skill name -> short snippet around its first match."""
    low = text.lower()
    found = {}
    for name, rx in _PATTERNS:
        m = rx.search(low)
        if m:
            s = max(0, m.start() - 45)
            e = min(len(low), m.end() + 45)
            found[name] = "..." + low[s:e].replace("\n", " ") + "..."
    return found


def parse_names(text):
    valid, unknown = [], []
    for part in text.replace(";", ",").split(","):
        part = part.strip()
        if not part:
            continue
        name = LOOKUP.get(part.lower())
        if name:
            if name not in valid:
                valid.append(name)
        else:
            unknown.append(part)
    return valid, unknown


def main() -> None:
    try:
        rows = load_rows()
    except FileNotFoundError:
        print(f"{LABELS_PATH} not found.")
        sys.exit(1)

    todo = [r for r in rows if (r.get("done") or "").strip().lower() != "y"]
    print(f"{len(rows) - len(todo)} done, {len(todo)} to review.")
    print()
    print("For each job, read the text and the extractor's findings, then type ONE of:")
    print("  ok              the extractor's list is exactly right")
    print("  Skill, Skill    the correct full list (replaces the extractor's list)")
    print("  none            the job mentions no listed skill")
    print("  skip / quit     leave it for later / save and stop")
    print("Pressing Enter alone does nothing, on purpose.")

    for r in todo:
        text = f"{r['title']} {r['description']}"
        found = contexts(text)
        print("\n" + "=" * 70)
        print(f"Job {r['job_id']}: {r['title']}")
        print("-" * 70)
        print(r["description"])
        print("-" * 70)
        if found:
            print("Extractor found:")
            for name, snippet in found.items():
                print(f"  {name}: {snippet}")
        else:
            print("Extractor found: nothing")

        while True:
            answer = input("Your answer> ").strip()
            low = answer.lower()
            if not answer:
                print("Type ok, a list of skills, none, skip or quit.")
                continue
            if low == "quit":
                save_rows(rows)
                print("Saved. Run this script again to continue.")
                return
            if low == "skip":
                break
            if low == "ok":
                r["true_skills"] = ";".join(sorted(extract_skills(text)))
            elif low == "none":
                r["true_skills"] = ""
            else:
                valid, unknown = parse_names(answer)
                if unknown:
                    print("Not in the list:", ", ".join(unknown), "- try again.")
                    continue
                r["true_skills"] = ";".join(valid)
            r["done"] = "y"
            save_rows(rows)
            break

    save_rows(rows)
    print("\nAll jobs reviewed and saved.")


if __name__ == "__main__":
    main()
