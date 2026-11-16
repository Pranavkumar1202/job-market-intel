import csv
import sys

from src.processing.skills import SKILLS

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


def parse_input(text):
    """Return (valid_names, unknown_names) from 'sql, python; power bi'."""
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
        print(f"{LABELS_PATH} not found. Run the export script first.")
        sys.exit(1)

    todo = [r for r in rows if (r.get("done") or "").strip().lower() != "y"]
    done_count = len(rows) - len(todo)
    print(f"{done_count} done, {len(todo)} to go.")
    print("Allowed skills:")
    print("; ".join(sorted(SKILLS)))
    print()
    print("Type the skills the text mentions, separated by commas.")
    print("Press Enter on an empty line if NO listed skill appears.")
    print("Type 'skip' to leave a job for later, 'quit' to stop and save.")

    for r in todo:
        print("\n" + "=" * 70)
        print(f"Job {r['job_id']}: {r['title']}")
        print("-" * 70)
        print(r["description"])
        print("-" * 70)
        while True:
            answer = input("Skills> ").strip()
            low = answer.lower()
            if low == "quit":
                save_rows(rows)
                print("Saved. Run this script again to continue.")
                return
            if low == "skip":
                break
            valid, unknown = parse_input(answer)
            if unknown:
                print("Not in the list:", ", ".join(unknown), "- try again.")
                continue
            r["true_skills"] = ";".join(valid)
            r["done"] = "y"
            save_rows(rows)
            break

    save_rows(rows)
    print("\nAll jobs processed and saved.")


if __name__ == "__main__":
    main()
