# Module 7: Trend Forecasting Module

import pandas as pd
from collections import Counter
import re
import matplotlib.pyplot as plt
import os

os.makedirs("reports", exist_ok=True)

print("Loading data...")
videos_df = pd.read_csv("data/ab_test_results.csv")
comments_df = pd.read_csv("data/comments_with_sentiment.csv")
print(f"Loaded {len(videos_df)} videos, {len(comments_df)} comments")

STOPWORDS = set([
    "the", "is", "a", "an", "and", "or", "to", "of", "in", "on", "for",
    "it", "this", "that", "i", "you", "your", "my", "me", "im", "so",
    "but", "be", "was", "are", "with", "have", "has", "not", "just",
    "at", "as", "if", "when", "what", "how", "why", "do", "did", "can",
    "video", "channel", "thank", "thanks", "really", "very", "much",
    "feel", "feeling", "feels", "lonely", "college"  # niche keywords excluded since they're the base topic
])

def extract_keywords(text_series):
    words = []
    for text in text_series.dropna():
        cleaned = re.sub(r'[^a-zA-Z\s]', '', str(text).lower())
        tokens = cleaned.split()
        words.extend([w for w in tokens if w not in STOPWORDS and len(w) > 3])
    return words


# Trend 1: Top keywords from HIGH viral score video titles

top_videos = videos_df.sort_values("viral_coefficient", ascending=False).head(15)
title_words = extract_keywords(top_videos["title"])
title_freq = Counter(title_words).most_common(10)

print("\n" + "="*50)
print("TOP TRENDING KEYWORDS IN HIGH-VIRAL TITLES")
print("="*50)
for word, count in title_freq:
    print(f"  {word}: {count} occurrences")


# Trend 2: Top keywords from RELATABLE comments

relatable_comments = comments_df[comments_df["has_relatable_trigger"] == True]
comment_words = extract_keywords(relatable_comments["comment"])
comment_freq = Counter(comment_words).most_common(15)

print("\n" + "="*50)
print("TOP EMERGING STRUGGLE KEYWORDS IN RELATABLE COMMENTS")
print("="*50)
for word, count in comment_freq:
    print(f"  {word}: {count} occurrences")


# Trend 3: Emerging topic signals (words gaining traction)

emerging_signals = [
    ("isolation", sum(1 for w in comment_words if "isolat" in w)),
    ("anxiety", sum(1 for w in comment_words if "anxi" in w)),
    ("friendship", sum(1 for w in comment_words if "friend" in w)),
    ("homesick", sum(1 for w in comment_words if "homesick" in w or "home" in w)),
    ("social media", sum(1 for w in comment_words if "social" in w)),
    ("introvert", sum(1 for w in comment_words if "introvert" in w)),
]
emerging_signals = [s for s in emerging_signals if s[1] > 0]
emerging_signals.sort(key=lambda x: x[1], reverse=True)

print("\n" + "="*50)
print("EMERGING RELATED STRUGGLE THEMES")
print("="*50)
for theme, count in emerging_signals:
    print(f"  {theme}: {count} mentions")


# Visualization

fig, ax = plt.subplots(figsize=(10, 6))
words, counts = zip(*comment_freq) if comment_freq else ([], [])
ax.barh(words[::-1], counts[::-1], color="#9B59B6")
ax.set_xlabel("Frequency in Relatable Comments")
ax.set_title("Top Emerging Struggle Keywords")
plt.tight_layout()
plt.savefig("reports/trend_keywords.png", dpi=150)
print("\nChart saved to reports/trend_keywords.png")


# Save report

with open("reports/trend_forecast.txt", "w", encoding="utf-8") as f:
    f.write("TREND FORECASTING MODULE - REPORT\n")
    f.write("="*50 + "\n\n")
    f.write("Top Keywords in High-Viral Titles:\n")
    for word, count in title_freq:
        f.write(f"  {word}: {count}\n")
    f.write("\nTop Emerging Keywords in Relatable Comments:\n")
    for word, count in comment_freq:
        f.write(f"  {word}: {count}\n")
    f.write("\nEmerging Related Struggle Themes:\n")
    for theme, count in emerging_signals:
        f.write(f"  {theme}: {count} mentions\n")

print("\nSaved full report to reports/trend_forecast.txt")