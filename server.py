from flask import Flask, request, jsonify, render_template
import os, json
from comment_transcript_downloader import extract_video_id, download_comments, download_transcript
from preprocess import preprocess_text
from sentiment_analysis import analyze_sentiments
from deepseek_client import get_summary_feedback
from flask import send_from_directory



app = Flask(__name__, template_folder='templates')

@app.route('/processed_results/<path:filename>')
def processed_results(filename):
    return send_from_directory('processed_results', filename)

@app.route('/')
def index():
    return render_template("index.html")
    

@app.route('/results/')
def results():
    return render_template("results.html")
    

@app.route('/analyze/', methods=['POST'])
def analyze():
    data = request.get_json()
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "No video URL provided."}), 400

    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL."}), 400

    output_dir = os.path.join("processed_results", video_id)
    comments_file = os.path.join(output_dir, f"{video_id}_comments.json")
    transcript_file = os.path.join(output_dir, f"{video_id}_transcript.json")
    sentiment_file = os.path.join(output_dir, "sentiment_results.json")
    summary_file = os.path.join(output_dir, "summary_feedback.txt")

    # Only download if necessary
    if not (os.path.exists(comments_file) and os.path.exists(transcript_file) and os.path.exists(sentiment_file) and os.path.exists(summary_file)):
        print("Downloading and processing resources for video:", video_id)
        os.makedirs(output_dir, exist_ok=True)

        # Download comments and transcript
        print("Started downloading comments & transcript...")
        download_comments(video_id, output_dir)
        download_transcript(video_id, output_dir)
        print("Finished downloading!")

        # Load downloaded data
        with open(comments_file, "r", encoding="utf-8") as f:
            comments = json.load(f)
        with open(transcript_file, "r", encoding="utf-8") as f:
            transcript = json.load(f)

        # Preprocess
        cleaned_comments = preprocess_text(comments)
        cleaned_transcript = preprocess_text(transcript)

        with open(os.path.join(output_dir, "cleaned_comments.json"), "w", encoding="utf-8") as f:
            json.dump(cleaned_comments, f, indent=4, ensure_ascii=False)
        with open(os.path.join(output_dir, "cleaned_transcript.txt"), "w", encoding="utf-8") as f:
            f.write(cleaned_transcript)

        # Sentiment analysis
        sentiment_results, sentiment_distribution = analyze_sentiments(cleaned_comments)
        with open(sentiment_file, "w", encoding="utf-8") as f:
            json.dump(sentiment_results, f, indent=4, ensure_ascii=False)

        # LLM summarization
        print("Started subjective summary...")
        combined_text = cleaned_transcript + "\n" + " ".join(cleaned_comments)
        summary_feedback = get_summary_feedback(cleaned_transcript,cleaned_comments)
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_feedback)
        print("Subjective summary generated!")
    else:
        print("Resources already exist for video:", video_id)
        with open(os.path.join(output_dir, "cleaned_comments.json"), "r", encoding="utf-8") as f:
            cleaned_comments = json.load(f)
        with open(os.path.join(output_dir, "cleaned_transcript.txt"), "r", encoding="utf-8") as f:
            cleaned_transcript = f.read()
        with open(summary_file, "r", encoding="utf-8") as f:
            summary_feedback = f.read()


    # Load downloaded data
    print("Preproseeing Data....")
    comments_file = os.path.join(output_dir, f"{video_id}_comments.json")
    transcript_file = os.path.join(output_dir, f"{video_id}_transcript.json")
    with open(comments_file, "r", encoding="utf-8") as f:
        comments = json.load(f)
    with open(transcript_file, "r", encoding="utf-8") as f:
        transcript = json.load(f)

    # Preprocess texts
    cleaned_comments = preprocess_text(comments)
    cleaned_transcript = preprocess_text(transcript)

    # Save preprocessed texts
    with open(os.path.join(output_dir, "cleaned_comments.json"), "w", encoding="utf-8") as f:
        json.dump(cleaned_comments, f, indent=4, ensure_ascii=False)
    with open(os.path.join(output_dir, "cleaned_transcript.txt"), "w", encoding="utf-8") as f:
        f.write(cleaned_transcript)
    print("Data has been preprocessed!!")

    # Sentiment Analysis
    print("Started sentiment-analysis....")
    sentiment_results, sentiment_distribution = analyze_sentiments(cleaned_comments)
    with open(os.path.join(output_dir, "sentiment_results.json"), "w", encoding="utf-8") as f:
        json.dump(sentiment_results, f, indent=4, ensure_ascii=False)
    print("Sentiment-analysis completed!!")

    # LLM Summarization + Feedback
    print("Started subjective summary....")
    combined_text = cleaned_transcript + "\n" + " ".join(cleaned_comments)
    summary_feedback = get_summary_feedback(combined_text, cleaned_comments)
    with open(os.path.join(output_dir, "summary_feedback.txt"), "w", encoding="utf-8") as f:
        f.write(summary_feedback)
    print("subjective summary generated!!")

    from visualization import generate_sentiment_visuals

    # inside /analyze/ after summary_feedback
    sentiment_stats, pie_path, bar_path, wordcloud_path = generate_sentiment_visuals(video_id)

    # safety check
    if not pie_path or not bar_path:
        return jsonify({"error": "Visualization failed"}), 500

    results_data = {
        "video_id": video_id,
        "summary": summary_feedback,
        "sentiment_stats": sentiment_stats,
        "wordcloud":        wordcloud_path,
        "sentiment_chart":  pie_path,
        "bar_chart":        bar_path,
    }

    return jsonify(results_data)





if __name__ == "__main__":
    app.run(debug=True)
