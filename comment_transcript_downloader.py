import os
import json
import argparse
from youtube_comment_downloader import YoutubeCommentDownloader
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    parsed_url = urlparse(url)
    video_id = None

    if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
        video_id = parse_qs(parsed_url.query).get("v", [None])[0]
    elif parsed_url.netloc in ["youtu.be"]:
        video_id = parsed_url.path.lstrip("/")

    return video_id

def download_comments(video_id, output_dir):
    """Downloads YouTube comments and saves them as a JSON file."""
    downloader = YoutubeCommentDownloader()
    comments = list(downloader.get_comments(video_id, sort_by=1))
    comments_file = os.path.join(output_dir, f"{video_id}_comments.json")
    with open(comments_file, "w", encoding="utf-8") as f:
        json.dump(comments, f, indent=4, ensure_ascii=False)
    print("comments downloaded")

def download_transcript(video_id, output_dir):
    """Downloads YouTube transcript (if available) and saves it as a JSON file."""
    transcript_file = os.path.join(output_dir, f"{video_id}_transcript.json")
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine transcript lines into a single text
        lines = []
        for line in transcript:
            lines.append(line['text'].replace("\n", " "))
        paragraph = " ".join(lines)
        with open(transcript_file, "w", encoding="utf-8") as f:
            json.dump(paragraph, f, indent=4, ensure_ascii=False)
        print("transcript downloaded")
    except Exception as e:
        print(f"⚠️ Transcript not available: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download YouTube comments and transcript.")
    parser.add_argument("url", help="YouTube video URL")
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    if not video_id:
        print("❌ Invalid YouTube URL.")
    else:
        output_dir = os.path.join("processed_results", video_id)
        os.makedirs(output_dir, exist_ok=True)
        print(f"📥 Processing video: {video_id}")
        download_comments(video_id, output_dir)
        download_transcript(video_id, output_dir)
