import json, glob, os, datetime, collections, bisect, sys

log = sys.argv[1]       #proxy_thinking_on.jsonl
pattern = sys.argv[2]   #"run_thinkon_*.report.jsonl"
runs = os.path.expanduser("~/.local/share/garak/garak_runs/" + pattern)

starts = []
for f in glob.glob(runs):
    with open(f, encoding="utf-8") as fh:
        for line in fh:
            e = json.loads(line)
            if e.get("entry_type") == "init":
                t = datetime.datetime.fromisoformat(e["start_time"]).timestamp()
                starts.append((t, os.path.basename(f).split(".")[0]))
                break
starts.sort()
times = [s[0] for s in starts]

c = collections.defaultdict(collections.Counter)
toks = collections.defaultdict(list)
for line in open(log):
    r = json.loads(line)
    i = bisect.bisect_right(times, r["t"]) - 1
    run = starts[i][1] if i >= 0 else "before_first_run"
    key = (r.get("finish"), "empty" if r.get("content_empty") else "has_content")
    c[run][key] += 1
    if r.get("content_empty") and r.get("finish") != "length":
        toks[run].append(r.get("tokens"))

for run in sorted(c):
    print(run)
    for k, v in sorted(c[run].items(), key=lambda kv: str(kv[0])):
        print("   ", k, v)
    if toks[run]:
        print("    tokens for empty-but-not-capped:", sorted(toks[run]))