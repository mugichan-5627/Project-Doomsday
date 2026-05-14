import re
import os

def clean_code(text):
    # Remove line numbers in format "123: "
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        match = re.match(r'^\d+:\s?(.*)', line)
        if match:
            cleaned_lines.append(match.group(1))
        else:
            cleaned_lines.append(line)
    
    cleaned_text = "\n".join(cleaned_lines)
    # Remove non-ASCII characters
    return cleaned_text.encode("ascii", "ignore").decode("ascii")

def extract_and_save(src_file, start_line, end_line, dest_file, append=False):
    with open(src_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        content = "".join(lines[start_line-1:end_line])
        cleaned = clean_code(content)
        mode = 'a' if append else 'w'
        with open(dest_file, mode, encoding='ascii') as out:
            out.write(cleaned)

# Extract filing_intelligence.py
extract_and_save('further_fix_part1.md', 12, 530, 'filing_intelligence.py')

# Extract valuation_engine.py
# Part 1 has some content? No, Part 2 starts from beginning of valuation_engine.py
extract_and_save('further_fix_part2.md', 3, 823, 'valuation_engine.py')

# Extract app.py
extract_and_save('app in python.md', 1, 1945, 'app.py')

print("Extraction complete.")
