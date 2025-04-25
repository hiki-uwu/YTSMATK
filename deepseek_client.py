import os
import json
import re
import sys
from pathlib import Path
import ollama

def get_summary_feedback(transcript_text, comments):
    """
    Uses a locally running DeepSeek R1 model via Ollama to generate structured feedback.
    """
    prompt = f"""
You are an advanced AI specialized in providing valuable feedback to the YouTube Creator using video transcripts and comments.
Provide a review from a third person and subjective POV.
The creator wants a structured feedback in bullet points with headings for the following areas:


1. Engagement & Audience Reception  
2. Memorable Moments  
3. Subjective (Humour if comedy, factual info if news, tech-facts if tech, etc)  
4. Potential Risk  
5. Actionable Tips  
6. Overall Thoughts  

Please read the transcript below and provide feedback in the requested format.
Make sure to keep the tone concise, but informative.

Draft your reply in this format given as an example:

"Feedback:
1. Engagement & Audience Reception

✅ Highly Positive Response: ...
✅ Memorable Moments: ...
🛠 Actionable Tip: ...

2. Humor Effectiveness & Tone
✅ Dark & Unexpected Humor Works: ...
⚠️ Potential Risk: ...
🛠 Actionable Tip: ...

3. Community Interaction & Engagement
✅ Strong Comment Engagement: ...
🛠 Actionable Tip: ...
⚠️ More Interactive Elements: ...
🛠 Actionable Tip: ...

Final Thoughts
🎯 Overall: "
Use symbols and formatting like above to make the output clean and professional.

Transcript (Use this for contextual awareness about the video):
{transcript_text}

Comments (Use this for the feedback and summary, noting improvements, reactions, suggestions, drawback and key highlights of the video):
{comments}
"""

    try:
        response = ollama.chat(
            model="deepseek-r1",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return re.sub(r'<think>.*?</think>', '', response['message']['content'].strip(), flags=re.DOTALL).strip()
    except Exception as e:
        print("Error using Ollama DeepSeek R1 model:", e)
        return "⚠️ Could not fetch summary from local DeepSeek R1."


if __name__ == "__main__":
    print("")