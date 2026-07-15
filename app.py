from flask import Flask, render_template, request, redirect
# import pickle
import sqlite3
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification

import torch
import torch.nn.functional as F

label_map = {
    0: "Anxiety",
    1: "Depression",
    2: "Normal",
    3: "Stress"
}

suggestions = {
    "Anxiety": "Practice deep breathing exercises and focus on one task at a time.",
    "Depression": "Maintain a routine, stay connected with loved ones, and seek support when needed.",
    "Stress": "Take regular breaks, prioritize tasks, and ensure adequate sleep.",
    "Normal": "Keep maintaining healthy habits and a balanced lifestyle."
}


app = Flask(__name__)

# model = pickle.load(
#     open("mental_health_model.pkl", "rb")
# )

# le = pickle.load(
#     open("label_encoder.pkl", "rb")
# )

# transformer loaded
tokenizer = AutoTokenizer.from_pretrained(
    "mental_health_distilbert"
)

model = AutoModelForSequenceClassification.from_pretrained(
    "mental_health_distilbert"
)

model.eval()

@app.route("/", methods=["GET", "POST"])
def home():

    prediction = None
    confidence = None
    suggestion = None

    if request.method == "POST":

        journal_text = request.form["journal"]

        # pred = model.predict([journal_text])[0]

        # prediction = le.inverse_transform([pred])[0]

        # probs = model.predict_proba([journal_text])[0]

        # confidence = round(max(probs) * 100, 2)

        inputs = tokenizer(
            journal_text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=128
        )

        with torch.no_grad():

            outputs = model(**inputs)

            probabilities = F.softmax(
                outputs.logits,
                dim=1
            )

            pred = torch.argmax(
                probabilities,
                dim=1
            ).item()

        prediction = label_map[pred]

        confidence = round(
            probabilities.max().item() * 100,
            2
        )

        suggestion = suggestions.get(prediction, "")

        import os

        print("Current Directory:", os.getcwd())

        conn = sqlite3.connect("journal.db")

        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO journal_entries
        (entry_text, prediction, confidence)
        VALUES (?, ?, ?)
        """,
        (
            journal_text,
            prediction,
            confidence
        ))

        conn.commit()
        conn.close()

        print("Prediction:", prediction)

    return render_template(
    "journal.html",
    prediction=prediction,
    confidence=confidence,
    suggestion=suggestion
)

@app.route("/history")
def history():

    selected_emotion = request.args.get("emotion")

    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    if selected_emotion and selected_emotion != "All":

        cursor.execute("""
        SELECT id,
               created_at,
               prediction,
               confidence,
               entry_text
        FROM journal_entries
        WHERE prediction = ?
        ORDER BY id DESC
        """, (selected_emotion,))

    else:

        cursor.execute("""
        SELECT id,
               created_at,
               prediction,
               confidence,
               entry_text
        FROM journal_entries
        ORDER BY id DESC
        """)

    entries = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        entries=entries,
        selected_emotion=selected_emotion
    )

@app.route("/delete/<int:id>")
def delete_entry(id):

    conn = sqlite3.connect("journal.db")

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM journal_entries WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/history")

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("journal.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM journal_entries")
    total_entries = cursor.fetchone()[0]

    cursor.execute("""
    SELECT prediction, COUNT(*)
    FROM journal_entries
    GROUP BY prediction
    ORDER BY COUNT(*) DESC
    """)
    emotions = cursor.fetchall()

    cursor.execute("""
    SELECT AVG(confidence)
    FROM journal_entries
    """)
    avg_confidence = cursor.fetchone()[0]

    cursor.execute("""
    SELECT prediction, entry_text
    FROM journal_entries
    ORDER BY id DESC
    LIMIT 5
    """)
    recent_entries = cursor.fetchall()

    conn.close()

    most_common = emotions[0][0] if emotions else "None"
    labels = [emotion[0] for emotion in emotions]
    counts = [emotion[1] for emotion in emotions]

    return render_template(
        "dashboard.html",
        total_entries=total_entries,
        most_common=most_common,
        avg_confidence=round(avg_confidence or 0, 2),
        emotions=emotions,
        recent_entries=recent_entries,
        labels=labels,
        counts=counts
    )

if __name__ == "__main__":
    app.run(debug=True)

    
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# import streamlit as st
# import pickle
# import numpy as np

# # Load model and label encoder
# model = pickle.load(open("mental_health_model.pkl", "rb"))
# le = pickle.load(open("label_encoder.pkl", "rb"))

# st.title("🧠 Mental Wellness Detection System")

# user_input = st.text_area(
#     "Enter your thoughts:",
#     height=150
# )

# if st.button("Analyze"):

#     # Prediction
#     prediction = model.predict([user_input])
#     result = le.inverse_transform(prediction)[0]

#     # Probabilities
#     probs = model.predict_proba([user_input])[0]

#     st.subheader("Prediction")
#     st.success(f"Predicted Status: {result}")

#     st.subheader("Confidence Scores")

#     for label, prob in zip(le.classes_, probs):
#         st.write(f"{label}: {prob*100:.2f}%")
#         st.progress(float(prob))

#     # Top 2 predictions
#     st.subheader("Top Predictions")

#     top2 = np.argsort(probs)[-2:][::-1]

#     for idx in top2:
#         st.write(
#             f"**{le.classes_[idx]}:** {probs[idx]*100:.2f}%"
#         )

#     # Response messages
#     responses = {
#         "Normal":
#             "Your text appears emotionally balanced.",

#         "Stress":
#             "Your text contains signs of stress. Consider taking breaks, prioritizing tasks, and maintaining a healthy routine.",

#         "Anxiety":
#             "Your text contains anxiety-related patterns. Relaxation techniques and discussing concerns with trusted people may help.",

#         "Depression":
#             "Your text contains indicators associated with depression. Consider reaching out to trusted friends, family, or a mental health professional if these feelings persist."
#     }

#     st.subheader("Recommendation")
#     st.info(responses[result])

# import streamlit as st
# import pickle

# model = pickle.load(open("mental_health_model.pkl", "rb"))
# le = pickle.load(open("label_encoder.pkl", "rb"))

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# st.title("🧠 Mental Wellness Chatbot")

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.write(msg["content"])

# user_input = st.chat_input("Type your message...")

# if user_input:

#     st.session_state.messages.append(
#         {"role":"user","content":user_input}
#     )

#     prediction = model.predict([user_input])[0]
#     label = le.inverse_transform([prediction])[0]

#     if label == "Stress":
#         response = (
#             "I notice signs of stress. "
#             "Would you like to tell me what's causing it?"
#         )

#     elif label == "Anxiety":
#         response = (
#             "Your message shows anxiety-related patterns. "
#             "What thoughts are worrying you most?"
#         )

#     elif label == "Depression":
#         response = (
#             "Your message sounds emotionally heavy. "
#             "How long have you been feeling this way?"
#         )

#     else:
#         response = (
#             "You seem emotionally balanced today. "
#             "How has your day been?"
#         )

#     st.session_state.messages.append(
#         {"role":"assistant","content":response}
#     )

#     st.rerun()

# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pickle

# app = Flask(__name__)
# CORS(app)

# model = pickle.load(open("mental_health_model.pkl", "rb"))
# le = pickle.load(open("label_encoder.pkl", "rb"))

# @app.route("/predict", methods=["POST"])
# def predict():

#     text = request.json["text"]

#     pred = model.predict([text])[0]
#     label = le.inverse_transform([pred])[0]

#     probs = model.predict_proba([text])[0]

#     result = {
#         "prediction": label,
#         "probabilities": {
#             le.classes_[0]: float(probs[0]),
#             le.classes_[1]: float(probs[1]),
#             le.classes_[2]: float(probs[2]),
#             le.classes_[3]: float(probs[3]),
#         }
#     }

#     return jsonify(result)

# if __name__ == "__main__":
#     app.run(debug=True)