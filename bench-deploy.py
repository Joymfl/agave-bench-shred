import subprocess
import time
import os
import numpy as np
from typing_extensions import DefaultDict
import csv

script_dir = os.path.dirname(os.path.abspath(__file__))
solana_cli = os.path.join(script_dir,"target","full-dev","solana")
program_so = os.path.join(script_dir,"program-deploy-test","token-2022.so")

latencies = []

for i in range(100):
    print(f"Run {i + 1}/100")

    validator = subprocess.Popen(
            ["solana-test-validator", "--reset"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            )

    while True:
        check = subprocess.run(
                ["solana", "cluster-version"],
                capture_output=True,
                )
        if check.returncode == 0:
            break
        time.sleep(1)

    result = subprocess.run(
            [solana_cli,"program","deploy",program_so],
            capture_output=True,
            text=True
            )

    if result.returncode == 0:
        for line in result.stderr.splitlines():
            if line.startswith("deploy_metric,"):
                parts = line.split(",")
                latencies.append({"run": i, "op": parts[1],"us":int(parts[2])})
    else:
        print(f"   FAILED: {result.stderr[-200:]}")

    validator.terminate()
    validator.wait()

by_op = DefaultDict(list)
for d in latencies:
    by_op[d["op"]].append(d["us"])

for op, values in by_op.items():
    print(f"\n{op}:")
    print(f" p50  = {np.percentile(values, 50): .0f} us")
    print(f" p99  = {np.percentile(values, 99): .0f} us")
    print(f" mean = {np.mean(values): .0f} us")
    print(f" n    = {len(values)}")

with open("results.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["run", "op", "us"])
    writer.writeheader()
    for d in latencies:
        writer.writerow(d)

