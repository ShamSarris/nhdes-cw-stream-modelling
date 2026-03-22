import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

drain = pd.read_csv("./src/data/drain_to_waterbody.csv")
shp = pd.read_csv("./src/data/watersheds_with_area_based-on-shp.csv")

# Keep only the columns we need from each file
drain = drain[["Unique_ID", "WaterbodyName", "drain_area"]].dropna(subset=["drain_area"])
shp = shp[["Unique_ID", "area (sq mi)"]]

merged = pd.merge(drain, shp, on="Unique_ID", how="inner")
merged = merged.rename(columns={
    "drain_area": "drain_area_sq_mi",
    "area (sq mi)": "shp_area_sq_mi",
})

merged["difference_sq_mi"] = merged["shp_area_sq_mi"] - merged["drain_area_sq_mi"]
merged["pct_difference"] = (merged["difference_sq_mi"] / merged["drain_area_sq_mi"]) * 100

print(f"Matched {len(merged)} records out of {len(drain)} in drain file and {len(shp)} in shapefile\n")
print(merged[["Unique_ID", "WaterbodyName", "drain_area_sq_mi", "shp_area_sq_mi", "difference_sq_mi", "pct_difference"]].to_string(index=False))

print(f"\nSummary stats for difference (shp - drain):")
print(merged["difference_sq_mi"].describe())

unmatched_drain = drain[~drain["Unique_ID"].isin(merged["Unique_ID"])]
unmatched_shp = shp[~shp["Unique_ID"].isin(merged["Unique_ID"])]
if not unmatched_drain.empty:
    print(f"\nUnmatched in drain file ({len(unmatched_drain)}):")
    print(unmatched_drain["Unique_ID"].tolist())
if not unmatched_shp.empty:
    print(f"\nUnmatched in shapefile ({len(unmatched_shp)}):")
    print(unmatched_shp["Unique_ID"].tolist())

# --- Visualization ---
sorted_merged = merged.sort_values("drain_area_sq_mi")
labels = sorted_merged["WaterbodyName"]
x = np.arange(len(labels))
width = 0.4

fig, axes = plt.subplots(2, 1, figsize=(max(10, len(labels) * 0.5), 10))

# Top: side-by-side bar chart of both area sources
ax1 = axes[0]
ax1.bar(x - width / 2, sorted_merged["drain_area_sq_mi"], width, label="Drain area (CSV)", color="steelblue")
ax1.bar(x + width / 2, sorted_merged["shp_area_sq_mi"], width, label="Shapefile area", color="darkorange")
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
ax1.set_ylabel("Area (sq mi)")
ax1.set_title("Watershed Area: Drain CSV vs. Shapefile")
ax1.legend()

# Bottom: difference (shp - drain) per watershed
ax2 = axes[1]
colors = ["tomato" if d < 0 else "seagreen" for d in sorted_merged["difference_sq_mi"]]
ax2.bar(x, sorted_merged["difference_sq_mi"], color=colors)
ax2.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax2.set_xticks(x)
ax2.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
ax2.set_ylabel("Difference (sq mi)")
ax2.set_title("Difference: Shapefile − Drain CSV (green = shp larger, red = drain larger)")

plt.tight_layout()
plt.savefig("./src/data/area_comparison.png", dpi=150)
plt.show()
print("\nPlot saved to src/data/area_comparison.png")
