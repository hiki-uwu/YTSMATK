from transformers import pipeline

classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment", truncation=True)

def analyze_sentiments(comments):
    sentiment_results = []
    sentiment_distribution = {"positive": 0, "neutral": 0, "negative": 0}

    for comment in comments:
        if len(comment.strip()) == 0:
            continue

        try:
            result = classifier(comment[:500])[0]  # Truncate to avoid >512 token error
            sentiment = result['label'].lower()  # e.g., 'POSITIVE' → 'positive'
            score = result['score']

            sentiment_results.append((comment, sentiment, score))

            if sentiment in sentiment_distribution:
                sentiment_distribution[sentiment] += 1
            else:
                sentiment_distribution[sentiment] = 1

        except Exception as e:
            print(f"Error analyzing comment: {e}")

    return sentiment_results, sentiment_distribution
