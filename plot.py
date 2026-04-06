from numpy import percentile
import pandas as pd
import matplotlib.pyplot as plt

original = pd.read_csv("results_original.csv")
tpu_next = pd.read_csv("results_tpu_next.csv")

original["variant"] = "original"
tpu_next["variant"] = "tpu_next"

df = pd.concat([original, tpu_next])

for op, group in df.groupby("op"):
    fig, ax = plt.subplots()
    for variant, vgroup in group.groupby("variant"):
        values = sorted(vgroup["us"] / 1_000_000)
        percentiles = [i / len(values) for i in range(len(values))]
        ax.plot(values, percentiles, label=variant)

    ax.set_title(op)
    ax.set_xlabel("latency (s)")
    ax.set_ylabel("percentile")
    ax.legend()
    ax.grid(True)
    fig.savefig(f"{op}.png")
    print(f"Saved {op}.png")

