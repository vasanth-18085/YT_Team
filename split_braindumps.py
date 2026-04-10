import re

with open("YouTube Team/Quant-Trading/03 - Scripting/Task 6 - Brain Dump Organiser/V13-V25_Complete_Series.md") as f:
    content = f.read()

parts = re.split(r'(?=^# V\d+ )', content, flags=re.MULTILINE)
for p in parts:
    m = re.match(r'^# (V\d+)', p)
    if m:
        vid = m.group(1)
        print(f"{vid}: {len(p.split())} words")
