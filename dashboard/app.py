# Module 6: Growth Visualization Dashboard

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Social Engagement Analytics", layout="wide")

# Load Data

@st.cache_data
def load_data():
    videos = pd.read_csv("data/ab_test_results.csv")
    comments = pd.read_csv("data/comments_with_sentiment.csv")
    return videos, comments

videos_df, comments_df = load_data()

# Header

st.title("Data-Driven Social Engagement Initiative")
st.markdown("**Decoding the Science of Relatability** — Analyzing 30 YouTube videos & 633 comments on *Feeling Lonely in College*")
st.divider()

# KPI Row

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Videos Analyzed", len(videos_df))
col2.metric("Total Comments", len(comments_df))
col3.metric("Avg Viral Coefficient", f"{videos_df['viral_coefficient'].mean():.2f}")
col4.metric("Overall Relatability Rate", f"{comments_df['has_relatable_trigger'].mean()*100:.1f}%")

st.divider()

# Row 1: Sentiment + Viral Score Distribution

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sentiment Distribution")
    sentiment_counts = comments_df["sentiment_label"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(5, 4))
    ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%", startangle=90)
    st.pyplot(fig1)

with col2:
    st.subheader("Viral Coefficient Distribution")
    fig2, ax2 = plt.subplots(figsize=(5, 4))
    ax2.hist(videos_df["viral_coefficient"], bins=15, edgecolor="white")
    ax2.set_xlabel("Viral Coefficient")
    ax2.set_ylabel("Number of Videos")
    st.pyplot(fig2)

st.divider()

# Row 2: Relatability vs Viral Score (Scatter)

st.subheader("Relatability Rate vs Viral Coefficient")
fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.scatterplot(data=videos_df, x="relatability_rate", y="viral_coefficient",
                 size="views", hue="length_category", ax=ax3, sizes=(50, 400), alpha=0.7)
ax3.set_xlabel("Relatability Rate (%)")
ax3.set_ylabel("Viral Coefficient")
st.pyplot(fig3)
st.caption("Bubble size = views | Color = video length category")

st.divider()

# Row 3: A/B Test Results

st.subheader("A/B Test Results")
colA, colB, colC = st.columns(3)

short_avg = videos_df[videos_df["length_category"] == "Short (<5min)"]["viral_coefficient"].mean()
long_avg = videos_df[videos_df["length_category"] == "Long (5min+)"]["viral_coefficient"].mean()
colA.metric("Long-form videos", f"{long_avg:.2f}", f"+{((long_avg/short_avg)-1)*100:.0f}% vs short")

high_rel = videos_df[videos_df["relatability_group"] == "High Relatability"]["viral_coefficient"].mean()
low_rel = videos_df[videos_df["relatability_group"] == "Low Relatability"]["viral_coefficient"].mean()
colB.metric("High Relatability videos", f"{high_rel:.2f}", f"{(high_rel/low_rel):.1f}x vs low relatability")

direct_avg = videos_df[videos_df["hook_type"] == "Direct/Question Hook"]["viral_coefficient"].mean()
colC.metric("Direct/Question Hooks", f"{direct_avg:.2f}")

st.divider()

# Row 4: Top 10 Videos Table

st.subheader("Top 10 Most Viral Videos")
top10 = videos_df.sort_values("viral_coefficient", ascending=False).head(10)
st.dataframe(
    top10[["title", "views", "likes", "comments_count", "relatability_rate", "viral_coefficient"]],
    use_container_width=True,
    hide_index=True
)

st.divider()

# Row 5: Recommendations

st.subheader("Engagement Optimization Recommendations")
try:
    with open("reports/recommendations.txt", "r", encoding="utf-8") as f:
        recs = f.read()
    st.text(recs)
except FileNotFoundError:
    st.warning("Run recommender.py first to generate recommendations.")

st.divider()
st.caption("Built for the Data-Driven Social Engagement Initiative | Data Science Major Project")