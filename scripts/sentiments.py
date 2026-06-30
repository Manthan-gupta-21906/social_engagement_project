# Module 2: Audience Sentiment Analyzer (NLP Module)

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import seaborn as sns
import os

os.makedirs("data",exist_ok=True)
os.makedirs("reports",exist_ok=True)

print("Loading Comments...")
df=pd.read_csv(r"data\comments.csv")
print(f"Loaded {len(df)} comments")

# VADER Sentiment Analysis

analyzer=SentimentIntensityAnalyzer()

def analyze_sentiment(comment):
    """returns sentiment score and label"""
    if not isinstance(comment,str):
        return 0, "Neutral"
    score= analyzer.polarity_scores(comment)
    compound=score["compound"]

    if compound <= -0.3:
        label = "Relatable"      # struggling, feeling understood
    elif compound >= 0.3:
        label = "Positive"       # inspired, uplifted
    elif -0.1 <= compound <= 0.1:
        label = "Neutral"        # generic comments
    else:
        label = "Mixed"          # complex emotion

    return compound, label

print(f"\nRunning sentiment analysis on {len(df)} comments...")

df[["compound_score", "sentiment_label"]] = df["comment"].apply(lambda x: pd.Series(analyze_sentiment(x)))

RELATABLE_KEYWORDS = [
    "me", "same", "i feel", "this is me", "literally me",
    "so true", "i thought", "nobody talks about",
    "i can relate", "story of my life", "omg yes",
    "why is this so accurate", "i needed this", "felt this"
]

def has_relatable_trigger(comment):
    if not isinstance(comment, str):
        return False
    comment_lower = comment.lower()
    return any(kw in comment_lower for kw in RELATABLE_KEYWORDS)

df["has_relatable_trigger"] = df["comment"].apply(has_relatable_trigger)

df.to_csv(r"data\comments_with_sentiment.csv", index=False)
print(r" Saved sentiment results to data\comments_with_sentiment.csv")


print("\n Sentiment Breakdown:",end=' ')
print(df["sentiment_label"].value_counts())

print(f"\n Comments with Relatable Triggers: {df['has_relatable_trigger'].sum()} out of {len(df)}")

relatable_pct = (df['has_relatable_trigger'].sum() / len(df)) * 100
print(f"   Relatability Rate: {relatable_pct:.1f}%")

fig, axes= plt.subplots(1,2,figsize=(12,5))
fig.suptitle("Audience Sentiment Analysis — Feeling Lonely in College", fontsize=14)

# Chart 1: Sentiment Distribution
sentiment_counts = df["sentiment_label"].value_counts()
axes[0].pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%", startangle=90)
axes[0].set_title("Sentiment Distribution")

# Chart 2: Compound Score Distribution
axes[1].hist(df["compound_score"], bins=30)
axes[1].axvline(x=0, color="red", linestyle="--", label="Neutral line")
axes[1].set_xlabel("Compound Sentiment Score")
axes[1].set_ylabel("Number of Comments")
axes[1].set_title("Sentiment Score Distribution")
axes[1].legend()

plt.tight_layout()
plt.savefig(r"reports/sentiment_analysis.png", dpi=150)
plt.show()
print("Chart saved to reports/sentiment_analysis.png")