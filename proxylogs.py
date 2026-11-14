import json, glob, os, datetime, collections, bisect

# run start times from Garak reports
starts = []
runs = os.path.expanduser("~/.local/share/garak/garak_runs/run_thinkoff_*.report.jsonl")
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
for line in open("proxy_thinking_off.jsonl"):
    r = json.loads(line)
    i = bisect.bisect_right(times, r["t"]) - 1
    run = starts[i][1] if i >= 0 else "before_first_run"
    c[run]["total"] += 1
    c[run]["hit_cap"] += r.get("finish") == "length"

for run, v in sorted(c.items()):
    print(run, dict(v))