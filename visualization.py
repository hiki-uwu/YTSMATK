import json
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pathlib import Path

def generate_sentiment_visuals(video_id):
    """
    Reads processed_results/{video_id}/sentiment_results.json
    and writes:
      - sentiment_proportion_pie.png
      - sentiment_count_bar.png
      - wordcloud.png
    Returns:
      counts_dict, pie_path (str), bar_path (str), wordcloud_path (str)
    """
    base = Path("processed_results") / video_id
    base.mkdir(parents=True, exist_ok=True)

    # Load and normalize
    with open(base / "sentiment_results.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for e in data:
        # entry: [text, label, score, likes?, replies?]
        text = e[0]
        label = e[1]
        records.append({"text": text, "label": label})
    df = pd.DataFrame(records)
    df = df[df["text"].str.strip().astype(bool)]

    # Map to human labels
    label_map = {"label_1":"positive", "label_0":"negative", "label_2":"neutral"}
    df["sentiment"] = df["label"].map(label_map)

    # Compute counts & proportions
    counts = df["sentiment"].value_counts().to_dict()
    total = sum(counts.values()) or 1
    proportions = {k: counts.get(k,0)/total for k in ["positive","negative","neutral"]}

    # Pie chart of proportions
    pie_path = base / "sentiment_proportion_pie.png"
    plt.figure(figsize=(6,6))
    if all(v == 0 for v in proportions.values()):
        plt.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=14)
        plt.axis("off")
    else:
        plt.pie(
            proportions.values(),
            labels=proportions.keys(),
            autopct="%1.1f%%",
            startangle=140
        )
        plt.title("Average Sentiment Distribution")
    plt.tight_layout()
    plt.savefig(pie_path)
    plt.close()

    # Bar chart of raw counts
    bar_path = base / "sentiment_count_bar.png"
    plt.figure(figsize=(6,4))
    series = pd.Series({k: counts.get(k,0) for k in ["positive","negative","neutral"]})
    series.plot.bar()
    plt.ylabel("Number of Comments")
    plt.title("Sentiment Counts")
    plt.tight_layout()
    plt.savefig(bar_path)
    plt.close()

    # Word cloud of all comments
    wordcloud_path = base / "wordcloud.png"
    if not df.empty:
        text_blob = " ".join(df["text"].tolist())
        wc = WordCloud(width=800, height=400, background_color="white").generate(text_blob)
        wc.to_file(wordcloud_path)
    else:
        wordcloud_path = None

    # Format return paths
    pie_str = str(pie_path).replace("\\", "/")
    bar_str = str(bar_path).replace("\\", "/")
    wc_str = str(wordcloud_path).replace("\\", "/") if wordcloud_path else ""

    return counts, pie_str, bar_str, wc_str
