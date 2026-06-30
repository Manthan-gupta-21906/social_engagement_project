# Module 4: A/B Testing Framework

import pandas as pd
import re
from scipy import stats
import os

os.makedirs("reports", exist_ok=True)

print("Loading virality data...")
df = pd.read_csv("data/video_virality_scores.csv")
print(f"Loaded {len(df)} videos")

def parse_duration(duration_str):
    if not isinstance(duration_str, str):
        return 0
    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
    match = pattern.match(duration_str)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds

df["duration_seconds"] = df["duration"].apply(parse_duration)

# TEST 1: Short vs Long Content
# Short = under 5 minutes (300s), Long = 5+ minutes

df["length_category"] = df["duration_seconds"].apply(
    lambda x: "Short (<5min)" if x < 300 else "Long (5min+)"
)

short_videos = df[df["length_category"] == "Short (<5min)"]["viral_coefficient"]
long_videos = df[df["length_category"] == "Long (5min+)"]["viral_coefficient"]

print("\n" + "="*50)
print("TEST 1: Short vs Long Content")
print("="*50)
print(f"Short videos (n={len(short_videos)}): Avg Viral Score = {short_videos.mean():.2f}")
print(f"Long videos (n={len(long_videos)}): Avg Viral Score = {long_videos.mean():.2f}")

if len(short_videos) > 1 and len(long_videos) > 1:
    t_stat, p_value = stats.ttest_ind(short_videos, long_videos, equal_var=False)
    print(f"T-statistic: {t_stat:.3f} | P-value: {p_value:.3f}")
    significant = "YES - Statistically Significant" if p_value < 0.05 else "No significant difference"
    print(f"Result: {significant}")
else:
    print("Not enough data in one group for a valid t-test")

# TEST 2: Question-style Title vs Statement-style Title
# Hook type proxy: does title contain "?" or "you"/"your" (direct address)

def classify_hook(title):
    if not isinstance(title, str):
        return "Statement"
    title_lower = title.lower()
    if "?" in title or "you" in title_lower or "your" in title_lower:
        return "Direct/Question Hook"
    return "Statement Hook"

df["hook_type"] = df["title"].apply(classify_hook)

direct_hook = df[df["hook_type"] == "Direct/Question Hook"]["viral_coefficient"]
statement_hook = df[df["hook_type"] == "Statement Hook"]["viral_coefficient"]

print("\n" + "="*50)
print("TEST 2: Direct/Question Hook vs Statement Hook")
print("="*50)
print(f"Direct/Question Hook (n={len(direct_hook)}): Avg Viral Score = {direct_hook.mean():.2f}")
print(f"Statement Hook (n={len(statement_hook)}): Avg Viral Score = {statement_hook.mean():.2f}")

if len(direct_hook) > 1 and len(statement_hook) > 1:
    t_stat2, p_value2 = stats.ttest_ind(direct_hook, statement_hook, equal_var=False)
    print(f"T-statistic: {t_stat2:.3f} | P-value: {p_value2:.3f}")
    significant2 = "YES - Statistically Significant" if p_value2 < 0.05 else "No significant difference"
    print(f"Result: {significant2}")
else:
    print("Not enough data in one group for a valid t-test")


# TEST 3: High Relatability vs Low Relatability — Does it drive views?

df_sorted = df.sort_values("relatability_rate", ascending=False).reset_index(drop=True)
midpoint = len(df_sorted) // 2
df_sorted["relatability_group"] = ["High Relatability"] * midpoint + ["Low Relatability"] * (len(df_sorted) - midpoint)
df = df_sorted

high_rel = df[df["relatability_group"] == "High Relatability"]["viral_coefficient"]
low_rel = df[df["relatability_group"] == "Low Relatability"]["viral_coefficient"]

print("\n" + "="*50)
print("TEST 3: High vs Low Relatability Content")
print("="*50)
print(f"High Relatability (n={len(high_rel)}): Avg Viral Score = {high_rel.mean():.2f}")
print(f"Low Relatability (n={len(low_rel)}): Avg Viral Score = {low_rel.mean():.2f}")

if len(high_rel) > 1 and len(low_rel) > 1:
    t_stat3, p_value3 = stats.ttest_ind(high_rel, low_rel, equal_var=False)
    print(f"T-statistic: {t_stat3:.3f} | P-value: {p_value3:.3f}")
    significant3 = "YES - Statistically Significant" if p_value3 < 0.05 else "No significant difference"
    print(f"Result: {significant3}")


df.to_csv("data/ab_test_results.csv", index=False)
print(f"\nSaved A/B test results to data/ab_test_results.csv")


with open("reports/ab_test_summary.txt", "w", encoding="utf-8") as f:
    f.write("A/B TESTING FRAMEWORK - SUMMARY REPORT\n")
    f.write("="*50 + "\n\n")
    f.write(f"Test 1 - Short vs Long: Short={short_videos.mean():.2f}, Long={long_videos.mean():.2f}\n")
    f.write(f"Test 2 - Hook Type: Direct/Question={direct_hook.mean():.2f}, Statement={statement_hook.mean():.2f}\n")
    f.write(f"Test 3 - Relatability: High={high_rel.mean():.2f}, Low={low_rel.mean():.2f}\n")

print("Summary saved to reports/ab_test_summary.txt")