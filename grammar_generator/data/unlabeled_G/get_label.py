import json
from collections import Counter

def categorize_by_phrase(description):
    desc = description.lower()

    has_only_line = "the only line" in desc # 55
    has_next_line = "the next line" in desc # 18

    if has_only_line and not has_next_line:
        return 1
    elif has_next_line and not has_only_line:
        return 3
    elif has_only_line and has_next_line:
        return 4
    else:
        return 5

def process_file(file_path, output_file_path):
    level_counter = Counter()
    output_data = []

    with open(file_path, 'r', encoding='utf-8') as infile:
        for line_number, line in enumerate(infile, 1):
            try:
                data = json.loads(line)
                name = data.get("name", "Unknown Problem")
                description = data.get("description", "")
                productions = data.get("grammar", {}).get("productions", [])

                level = categorize_by_phrase(description)
                level_counter[level] += 1

                output_data.append({
                    "name": name,
                    "grammar": productions,
                    "max_level": level
                })

            except json.JSONDecodeError as e:
                print(f"Skipping line {line_number} due to JSONDecodeError: {e}")

    with open(output_file_path, 'w', encoding='utf-8') as outfile:
        for entry in output_data:
            outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')

    return level_counter

def main():
    file_path = 'Neural-Translation-of-Input-Specifications-into-Formal-Grammars-for-Test-Case-Generation/data/unlabeled/train.jsonl'
    output_file_path = 'Neural-Translation-of-Input-Specifications-into-Formal-Grammars-for-Test-Case-Generation/data/unlabeled/level/train.jsonl'

    level_counts = process_file(file_path, output_file_path)

    for level, count in sorted(level_counts.items()):
        print(f"Grammar Level {level}: {count} grammars")

if __name__ == "__main__":
    main()
