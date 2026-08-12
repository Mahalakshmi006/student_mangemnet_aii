import requests

def generate_feedback(name, subject, mark, attendance):

    prompt = f"""
Student Name: {name}
Subject: {subject}
Mark: {mark}
Attendance: {attendance}

Give friendly and simple feedback to the student.

IMPORTANT RULES:
- Write EXACTLY 3 short lines.
- Use SIMPLE English only.
- Use EXACTLY 2 emojis.
- Put an emoji naturally at the end of line 1 and line 3.
- Allowed emojis: 😊 👍 💪 🌟 🎉 📚
- Mention the mark.
- Mention the attendance.
- If mark is good, appreciate and encourage the student.
- If mark is low, motivate the student and give one simple suggestion.
- If attendance is good, appreciate it.
- If attendance is low, encourage better attendance.
- Do NOT write a paragraph.
- Do NOT add "AI Feedback:".
- Return ONLY 3 lines.

Example:
Great job! You scored 93 marks. Keep up the good work! 🎉
Your attendance is also excellent, so keep attending regularly. 👍
Keep practicing and aim even higher next time! 🌟
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    data = response.json()

    return data["response"]