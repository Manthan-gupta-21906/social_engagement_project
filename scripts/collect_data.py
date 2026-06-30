#Module 1 : content performance tracker

from googleapiclient.discovery import build 
import pandas as pd
import os 

API_KEY = os.getenv("YOUTUBE_API_KEY")

SEARCH_QUERY= "feeling lonely in college"

MAX_VIDEOS=30

youtube = build("youtube","v3",developerKey=API_KEY,credentials=None)

def search_videos(query,max_results=30):
    """Search youtube video and return IDs"""
    print(f"Searching youtube for for:'{query}'")
    request= youtube.search().list(
        q=query,
        part="id,snippet",
        type="video",
        maxResults=max_results,
        relevanceLanguage="en"

    )
    response=request.execute()
    
    videos=[]
    for item in response["items"]:
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "published_at": item["snippet"]["publishedAt"],
            "description": item["snippet"]["description"][:200]
        })
    print(f"found {len(videos)} videos")
    return videos

def get_video_stats(video_ids):
    """get details of each video"""
    print("fetching video statistics....")
    ids_str=",".join(video_ids)
    request= youtube.videos().list(
        part="statistics,contentDetails",
        id=ids_str
    )
    response= request.execute()

    stats=[]
    for item in response["items"]:
        s= item["statistics"]
        stats.append({
            "video_id": item["id"],
            "views": int(s.get("viewCount", 0)),
            "likes": int(s.get("likeCount", 0)),
            "comments_count": int(s.get("commentCount", 0)),
            "duration": item["contentDetails"]["duration"]
        })
    return stats

def get_comments(video_id,max_comments=50):
    """get top comments of video"""
    try:
        request=youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_comments,
            order="relevance"
        )
        response=request.execute()
        comments = []
        for item in response["items"]:
            c = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "video_id": video_id,
                "comment": c["textDisplay"],
                "likes": c["likeCount"],
                "published_at": c["publishedAt"]
            })
        return comments
    except Exception as e:
        print(f" Could not fetch comments for {video_id}: {e}")
        return []
    
def main():
    os.makedirs("data",exist_ok=True)

    videos=search_videos(SEARCH_QUERY,MAX_VIDEOS)
    video_ids=[v["video_id"] for v in videos]

    stats= get_video_stats(video_ids)
    stats_df= pd.DataFrame(stats)

    videos_df=pd.DataFrame(videos)
    final_df=videos_df.merge(stats_df,on="video_id")

    final_df.to_csv("data/video_stats.csv",index=False)

    print(f"\n Saved {len(final_df)} videos to data/video_stats.csv")
    print(final_df[["title", "views", "likes", "comments_count"]].head())


    print("\n Fetching comments for each video...")
    all_comments = []
    for vid_id in video_ids[:15]:  # limit to 15 videos to save API quota
        comments = get_comments(vid_id)
        all_comments.extend(comments)
        print(f"  -> {vid_id}: {len(comments)} comments")

    comments_df = pd.DataFrame(all_comments)
    comments_df.to_csv("data/comments.csv", index=False)
    print(f"\n Saved {len(comments_df)} comments to data/comments.csv")


if __name__ == "__main__":
    main()