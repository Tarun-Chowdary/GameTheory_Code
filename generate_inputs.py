import random

def generate_input(n, seed=42):
    random.seed(seed)
    men_ids   = list(range(1, n+1))
    women_ids = list(range(1, n+1))
    lines = [f"{n} {n}", ""]
    lines.append("# Men's preferences")
    for _ in men_ids:
        pref = women_ids[:]
        random.shuffle(pref)
        lines.append(" ".join(map(str, pref)))
    lines.append("")
    lines.append("# Women's preferences")
    for _ in women_ids:
        pref = men_ids[:]
        random.shuffle(pref)
        lines.append(" ".join(map(str, pref)))
    return "\n".join(lines)

# Generate and save
for n in [100, 200, 1000]:
    with open(f"size_{n}.txt", "w") as f:
        f.write(generate_input(n))
    print(f"Generated size_{n}.txt")