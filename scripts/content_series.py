# scripts/content_series.py
# Module 8 (Deliverable 5): The Content Series Generator
# Uses findings from the analytics pipeline to generate AND score
# new content ideas before they're ever published.

import pandas as pd
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

os.makedirs("reports", exist_ok=True)
os.makedirs("content_series", exist_ok=True)

# ─────────────────────────────────────────
# Load benchmarks from your real pipeline results
# ─────────────────────────────────────────
print("Loading pipeline benchmarks...")
df = pd.read_csv("data/ab_test_results.csv")

RELATABILITY_THRESHOLD = 55.0   # from recommender.py
LONG_FORM_MIN_SECONDS = 300     # 5 minutes, from ab_test.py
TOP_VIDEO = df.sort_values("viral_coefficient", ascending=False).iloc[0]

print(f"Benchmarks loaded:")
print(f"  Relatability target: {RELATABILITY_THRESHOLD}%+")
print(f"  Length target: 5+ minutes")
print(f"  Template video: {TOP_VIDEO['title'][:60]}")

# ─────────────────────────────────────────
# Emerging themes from trend.py output (Module 7)
# Hardcoded from your real trend_forecast.txt results
# ─────────────────────────────────────────
EMERGING_THEMES = [
    "friendship",
    "homesickness",
    "social media comparison",
    "introversion",
    "isolation",
    "anxiety"
]

# ─────────────────────────────────────────
# Content Series: 6 video concepts generated from pipeline data
# Each one targets an emerging theme + follows the proven format
# (long-form, second-person address, hopeful resolution)
# ─────────────────────────────────────────
CONTENT_SERIES = [
    {
        "id": "CS-01",
        "title": "to anyone who lost their college friends | journal entry ep. 1",
        "theme": "friendship",
        "format": "Long-form (8-10 min)",
        "hook_type": "Direct/Question Hook",
        "tone": "Vulnerable, resolution-focused",
        "draft_caption": "you didn't do anything wrong. friendships change in college, and it's the loneliest kind of grief nobody talks about. this is for anyone who feels like they're starting over."
    },
    {
        "id": "CS-02",
        "title": "why going home doesn't feel like home anymore",
        "theme": "homesickness",
        "format": "Long-form (6-8 min)",
        "hook_type": "Statement Hook",
        "tone": "Vulnerable, resolution-focused",
        "draft_caption": "nobody prepares you for the version of homesickness where home itself feels different now. you're not broken, you're just becoming someone new."
    },
    {
        "id": "CS-03",
        "title": "stop comparing your real life to everyone's highlight reel",
        "theme": "social media comparison",
        "format": "Long-form (5-7 min)",
        "hook_type": "Direct/Question Hook",
        "tone": "Hopeful, resolution-focused",
        "draft_caption": "if scrolling makes you feel like everyone else has it figured out except you, watch this before you compare yourself again."
    },
    {
        "id": "CS-04",
        "title": "being an introvert in college doesn't mean you're lonely (here's the difference)",
        "theme": "introversion",
        "format": "Long-form (6-8 min)",
        "hook_type": "Statement Hook",
        "tone": "Hopeful, resolution-focused",
        "draft_caption": "needing alone time isn't the same as being lonely, but college makes it really hard to tell the difference. let's talk about it."
    },
    {
        "id": "CS-05",
        "title": "to anyone who eats lunch alone | journal entry ep. 2",
        "theme": "isolation",
        "format": "Long-form (7-9 min)",
        "hook_type": "Direct/Question Hook",
        "tone": "Vulnerable, resolution-focused",
        "draft_caption": "eating alone in a crowded dining hall is its own specific kind of lonely. you're not invisible, even when it feels that way."
    },
    {
        "id": "CS-06",
        "title": "the anxiety nobody warns you about before college",
        "theme": "anxiety",
        "format": "Long-form (6-8 min)",
        "hook_type": "Statement Hook",
        "tone": "Hopeful, resolution-focused",
        "draft_caption": "the anxious thoughts at 2am about whether anyone actually likes you are more common than you think. here's what helped me."
    }
]

# ─────────────────────────────────────────
# Scoring Engine: Predict relatability + viral potential
# using the SAME sentiment model from sentiments.py
# ─────────────────────────────────────────
analyzer = SentimentIntensityAnalyzer()

RELATABLE_KEYWORDS = [
    "me", "same", "i feel", "this is me", "literally me",
    "so true", "i thought", "nobody talks about",
    "i can relate", "story of my life", "you're not", "you didn't"
]

def predict_relatability_score(caption):
    """Estimate relatability potential of a caption based on
    sentiment polarity + presence of validated trigger language."""
    compound = analyzer.polarity_scores(caption)["compound"]
    caption_lower = caption.lower()
    trigger_hits = sum(1 for kw in RELATABLE_KEYWORDS if kw in caption_lower)

    # Score formula: trigger phrase density + sentiment alignment
    # Calibrated against findings: top video had 86% relatability,
    # hopeful/positive sentiment outperformed purely negative
    base_score = min(trigger_hits * 15, 60)
    sentiment_bonus = 25 if -0.2 <= compound <= 0.6 else 10  # vulnerable-but-hopeful range scores best
    predicted_relatability = min(base_score + sentiment_bonus, 95)

    return round(predicted_relatability, 1), round(compound, 2)

def predict_viral_readiness(item, predicted_relatability):
    """Combine format + theme + relatability into a readiness score,
    using the same weighting logic as virality.py"""
    format_bonus = 20 if "Long-form" in item["format"] else 0
    theme_bonus = 10  # all themes here are validated emerging themes from trend.py
    score = (predicted_relatability * 0.6) + format_bonus + theme_bonus
    return round(score, 1)

# ─────────────────────────────────────────
# Score each content piece
# ─────────────────────────────────────────
print("\nScoring content series against pipeline benchmarks...\n")
results = []
for item in CONTENT_SERIES:
    rel_score, sentiment = predict_relatability_score(item["draft_caption"])
    readiness = predict_viral_readiness(item, rel_score)
    meets_threshold = rel_score >= RELATABILITY_THRESHOLD

    results.append({
        **item,
        "predicted_relatability": rel_score,
        "predicted_sentiment": sentiment,
        "viral_readiness_score": readiness,
        "passes_benchmark": "YES" if meets_threshold else "NEEDS REVISION"
    })

    status = "PASS" if meets_threshold else "REVISE"
    print(f"[{status}] {item['id']} — {item['title'][:55]}")
    print(f"   Theme: {item['theme']} | Predicted Relatability: {rel_score}% | Readiness Score: {readiness}")

# ─────────────────────────────────────────
# Save outputs
# ─────────────────────────────────────────
results_df = pd.DataFrame(results)
results_df.to_csv("content_series/content_series_scored.csv", index=False)

with open("content_series/content_series_report.txt", "w", encoding="utf-8") as f:
    f.write("THE CONTENT SERIES — DATA-VALIDATED CONTENT PIPELINE\n")
    f.write("="*60 + "\n")
    f.write(f"Generated using benchmarks derived from {len(df)} analyzed videos\n")
    f.write(f"Relatability threshold: {RELATABILITY_THRESHOLD}%+\n\n")

    for r in results:
        f.write(f"{r['id']} — {r['title']}\n")
        f.write(f"  Theme: {r['theme']}\n")
        f.write(f"  Format: {r['format']} | Hook: {r['hook_type']} | Tone: {r['tone']}\n")
        f.write(f"  Draft Caption: {r['draft_caption']}\n")
        f.write(f"  Predicted Relatability: {r['predicted_relatability']}%\n")
        f.write(f"  Viral Readiness Score: {r['viral_readiness_score']}\n")
        f.write(f"  Status: {r['passes_benchmark']}\n\n")

print(f"\nSaved scored content series to content_series/content_series_scored.csv")
print(f"Saved full report to content_series/content_series_report.txt")

passing = sum(1 for r in results if r["passes_benchmark"] == "YES")
print(f"\n{passing}/{len(results)} content pieces meet the {RELATABILITY_THRESHOLD}%+ relatability benchmark before publishing.")