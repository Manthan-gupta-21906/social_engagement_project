# Module 2: Virality Prediction Engine

import pandas as pd
import os

os.makedirs("data", exist_ok=True)
os.makedirs("reports", exist_ok=True)

print("Loading video stats...")
videos_df = pd.read_csv("data/video_stats.csv")
print(f"Loaded {len(videos_df)} videos")

print("Loading sentiment data...")
comments_df = pd.read_csv("data/comments_with_sentiment.csv")
print(f"Loaded {len(comments_df)} comments")

sentiment_agg = comments_df.groupby("video_id").agg(avg_sentiment_score=("compound_score", "mean"),
    relatable_comment_count=("has_relatable_trigger", "sum"),
    total_comments_analyzed=("comment", "count")).reset_index()

sentiment_agg["relatability_rate"] = (
    sentiment_agg["relatable_comment_count"] / sentiment_agg["total_comments_analyzed"]
) * 100

df = videos_df.merge(sentiment_agg, on="video_id", how="left")
df["relatability_rate"] = df["relatability_rate"].fillna(0)
df["avg_sentiment_score"] = df["avg_sentiment_score"].fillna(0)

df["engagement_rate"] = (
    (df["comments_count"] * 3 + df["likes"] * 1) / df["views"].replace(0, 1)
) * 100

df["viral_coefficient"] = (
    (df["engagement_rate"] * 0.6) + (df["relatability_rate"] * 0.4)
).round(2)

df = df.sort_values("viral_coefficient", ascending=False).reset_index(drop=True)
df["rank"] = df.index + 1

df.to_csv(r"data\video_virality_scores.csv", index=False)
print(r"Saved virality scores to data\video_virality_scores.csv")

print("TOP 5 MOST VIRAL VIDEOS:")
top5 = df[["rank", "title", "views", "engagement_rate", "relatability_rate", "viral_coefficient"]].head(5)
for _, row in top5.iterrows():
    print(f"#{row['rank']} | Viral Score: {row['viral_coefficient']}")
    print(f"   {row['title'][:70]}")
    print(f"   Views: {row['views']:,} | Engagement: {row['engagement_rate']:.2f}% | Relatability: {row['relatability_rate']:.1f}%")

print(f"\nAverage Viral Coefficient across all videos: {df['viral_coefficient'].mean():.2f}")
