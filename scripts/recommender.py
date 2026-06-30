# Module 5: Engagement Optimization Recommender

import pandas as pd
import os

os.makedirs("reports", exist_ok=True)

print("Loading A/B test results...")
df = pd.read_csv("data/ab_test_results.csv")
print(f"Loaded {len(df)} videos")

recommendations = []

# Recommendation 1: Optimal Video Length

long_avg = df[df["length_category"] == "Long (5min+)"]["viral_coefficient"].mean()
short_avg = df[df["length_category"] == "Short (<5min)"]["viral_coefficient"].mean()

if long_avg > short_avg:
    rec1 = f"Prioritize LONG-FORM content (5+ min). It outperforms short content by {((long_avg/short_avg)-1)*100:.0f}% in viral coefficient."
else:
    rec1 = f"Prioritize SHORT-FORM content (<5 min). It outperforms long content by {((short_avg/long_avg)-1)*100:.0f}% in viral coefficient."
recommendations.append(rec1)

# Recommendation 2: Relatability Threshold

high_rel_avg = df[df["relatability_group"] == "High Relatability"]["viral_coefficient"].mean()
low_rel_avg = df[df["relatability_group"] == "Low Relatability"]["viral_coefficient"].mean()
threshold = df[df["relatability_group"] == "High Relatability"]["relatability_rate"].quantile(0.25)

rec2 = f"Target a Relatability Rate of {threshold:.0f}%+ in comments. Videos above this threshold scored {(high_rel_avg/low_rel_avg):.1f}x higher in viral coefficient."
recommendations.append(rec2)

# Recommendation 3: Top Performing Video as Template

top_video = df.sort_values("viral_coefficient", ascending=False).iloc[0]
rec3 = f"Use '{top_video['title'][:60]}...' as a content template — it achieved the highest viral coefficient ({top_video['viral_coefficient']}) with {top_video['relatability_rate']:.0f}% relatability."
recommendations.append(rec3)

# Recommendation 4: Sentiment Tone

avg_sentiment_top10 = df.sort_values("viral_coefficient", ascending=False).head(10)["avg_sentiment_score"].mean()
if avg_sentiment_top10 < 0:
    rec4 = f"Top-performing content leans emotionally vulnerable/struggle-focused (avg sentiment: {avg_sentiment_top10:.2f}). Avoid overly polished or purely motivational tone — raw honesty performs better."
else:
    rec4 = f"Top-performing content leans emotionally positive/uplifting (avg sentiment: {avg_sentiment_top10:.2f}). Hopeful, resolution-focused framing performs better than purely sad content."
recommendations.append(rec4)


# Recommendation 5: Hook Style

direct_avg = df[df["hook_type"] == "Direct/Question Hook"]["viral_coefficient"].mean()
statement_avg = df[df["hook_type"] == "Statement Hook"]["viral_coefficient"].mean()

if direct_avg > statement_avg:
    rec5 = f"Use direct address or question-style titles (e.g., 'Feeling lonely?'). They outperform generic statement titles."
else:
    rec5 = f"Use statement-style, narrative titles. They slightly outperform direct/question hooks, though the difference is not statistically significant — focus more on content depth than title format."
recommendations.append(rec5)


print("\n" + "="*60)
print("ENGAGEMENT OPTIMIZATION RECOMMENDATIONS")
print("="*60)
for i, rec in enumerate(recommendations, 1):
    print(f"\n{i}. {rec}")

with open("reports/recommendations.txt", "w", encoding="utf-8") as f:
    f.write("ENGAGEMENT OPTIMIZATION RECOMMENDATIONS\n")
    f.write("="*60 + "\n")
    f.write("Based on statistical analysis of 30 videos and 633 comments\n\n")
    for i, rec in enumerate(recommendations, 1):
        f.write(f"{i}. {rec}\n\n")

print(f"\nSaved recommendations to reports/recommendations.txt")
