import json, glob, os, collections

runs = os.path.expanduser("~/.local/share/garak/garak_runs/*.report.jsonl")
c = collections.defaultdict(collections.Counter)

for f in glob.glob(runs):
    tag = os.path.basename(f).split(".")[0]   # --report_prefix
    for line in open(f, encoding="utf-8"):
        e = json.loads(line)
        if e.get("entry_type") != "attempt" or e.get("status") != 2:
            continue
        for o in e["outputs"]:
            text = ((o or {}).get("text") or "").strip()
            c[(tag, e["probe_classname"])]["empty" if not text else "nonempty"] += 1

for (tag, probe), v in sorted(c.items()):
    total = v["empty"] + v["nonempty"]
    print(f"{tag:40} {probe:35} empty {v['empty']:3}/{total}")