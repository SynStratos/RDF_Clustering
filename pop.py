topop = []

with open('data/to_remove_raw.txt', 'r') as f:
    for line in f.readlines():
        line = line.strip().split(" ")[1]
        line = '"' + line + '"' + "\n"
        topop.append(line)

with open('data/bad_predicates.tsv', 'w+') as f:
    for line in topop:
        f.write(line)