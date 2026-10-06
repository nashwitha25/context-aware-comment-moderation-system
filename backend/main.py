from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from db import get_db_connection
import joblib
import os
import numpy as np
from transformers import pipeline
negation_words = [
    "not",
    "never",
    "no",
    "isn't",
    "aren't",
    "wasn't",
    "weren't",
    "don't",
    "doesn't",
    "didn't",
    "can't",
    "couldn't"
]
# ---------- IMPLICIT INSULT LIST ----------
implicit_insults = [
    "waste",
    "useless",
    "worthless",
    "failure",
    "burden",
    "pathetic",
    "disappointment",
    "good for nothing",
    "nobody needs you",
    "nobody respects you",
    "people regret knowing you",
    "everything you touch becomes a disaster",
    "embarrassing",
    "joke",
    "ruin everything",
    "not capable",
    "bring no value",
    "mess things up"
]
contextual_sarcasm = [
    "i'm not saying",
    "not saying you are",
    "the results speak",
    "just saying",
    "you might want to",
    "i wouldn't say",
]
positive_words = [
    "great",
    "nice",
    "amazing",
    "brilliant",
    "genius",
    "wonderful",
    "excellent",
    "fantastic",
    "impressive"
]

negative_words = [
    "fail",
    "ruin",
    "mess",
    "disaster",
    "wrong",
    "worse",
    "useless",
    "pathetic"
]
mild_criticism = [
    "not your brightest idea",
    "interesting choice",
    "not sure it worked",
    "thanks for making things worse",
]

classifier = None
app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- LOAD HYBRID MODEL ----------
hybrid_models = joblib.load(os.path.join(BASE_DIR, "model", "hybrid_models.pkl"))
vectorizer = joblib.load(os.path.join(BASE_DIR, "model", "hybrid_vectorizer.pkl"))

logreg = hybrid_models["logreg"]
sgd = hybrid_models["sgd"]
nb = hybrid_models["nb"]

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- SCHEMAS ----------
class RegisterUser(BaseModel):
    username: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class CreatePost(BaseModel):
    user_id: int
    content: str

class CreateComment(BaseModel):
    post_id: int
    user_id: int
    text: str

# ---------- REGISTER ----------
@app.post("/register")
def register(user: RegisterUser):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (user.username, user.email, user.password)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        conn.close()

    return {"message": "User registered successfully"}

# ---------- LOGIN ----------
@app.post("/login")
def login(user: LoginUser):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, username, email FROM users WHERE email=%s AND password=%s",
        (user.email, user.password)
    )
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return {"error": "Invalid email or password"}

    return {
        "message": "Login successful",
        "user_id": result["id"],
        "username": result["username"],
        "email": result["email"]
    }

# ---------- CREATE POST ----------
@app.post("/posts")
def create_post(post: CreatePost):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO posts (user_id, content) VALUES (%s, %s)",
        (post.user_id, post.content)
    )
    conn.commit()
    conn.close()

    return {"message": "Post created successfully"}

# ---------- FEED ----------
@app.get("/feed")
def get_feed():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT posts.id, posts.content, posts.created_at, users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)
    posts = cursor.fetchall()
    conn.close()

    return posts

# ---------- CREATE COMMENT (TRANSFORMER + CALIBRATION) ----------
@app.post("/comments")
def create_comment(comment: CreateComment):
    global classifier

    if classifier is None:
        classifier = pipeline("text-classification", model="unitary/toxic-bert", top_k = None)

    # ---------- Transformer Prediction ----------
    results = classifier(comment.text)[0]

    toxic_score = 0.0
    for item in results:
        if item["label"].lower() == "toxic":
            toxic_score = item["score"]

    toxicity_score = round(float(toxic_score), 3)

    text_lower = comment.text.lower()

    # ------------------------------
    # Rule List
    # ------------------------------
    mild_insults = [
        "unworthy",
        "worthless",
        "pathetic",
        "useless",
        "burden",
        "disappointment",
        "failure",
        "nobody likes you",
        "nobody respects you"
    ]

    # ------------------------------
    # Rule 1: Negation Handling
    # ------------------------------
    for insult in mild_insults:
        if f"not {insult}" in text_lower:
            toxicity_score = min(toxicity_score, 0.55)

    # ------------------------------
    # Rule 2: Direct Insult Softening
    # ------------------------------
    for insult in mild_insults:
        if (
            f"not {insult}" in text_lower
            or f"not that {insult}" in text_lower
            or f"not really {insult}" in text_lower
            or f"not very {insult}" in text_lower
        ):
            toxicity_score = min(toxicity_score, 0.55)

    # ------------------------------
    # Rule 3: Contextual sarcasm detection
    # ------------------------------
    if any(phrase in text_lower for phrase in contextual_sarcasm):
        toxicity_score = max(toxicity_score, 0.35)

    # ------------------------------
    # Rule 4: Positive + negative sarcasm pattern
    # ------------------------------
    if any(p in text_lower for p in positive_words) and any(n in text_lower for n in negative_words):
        toxicity_score = max(toxicity_score, 0.45)

    # ------------------------------
    # Rule 5: Implicit insult override
    # ------------------------------
    for phrase in implicit_insults:
        if phrase in text_lower:
            toxicity_score = max(toxicity_score, 0.75)
        # Rule: Mild criticism detection
    for phrase in mild_criticism:
        if phrase in text_lower:
            toxicity_score = max(toxicity_score, 0.35)

    # Ensure score valid
    toxicity_score = min(max(toxicity_score, 0), 1)

    # ------------------------------
    # Final Decision
    # ------------------------------
    if toxicity_score < 0.25:
        toxicity_type = "Non-Toxic"
        status = "approved"
        message = "✅ Non-toxic comment. Posted successfully."
    elif toxicity_score < 0.60:
        toxicity_type = "Mild Toxicity"
        status = "pending"
        message = "⚠️ Mild toxic content detected. Sent for review."
    else:
        toxicity_type = "Severe Toxicity"
        status = "pending"
        message = "❌ Toxic comment detected. Sent for review."

    # ---------- Save to DB ----------
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO comments (post_id, user_id, text, toxicity_score, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            comment.post_id,
            comment.user_id,
            comment.text,
            round(float(toxicity_score), 3),
            status
        )
    )

    conn.commit()
    conn.close()

    return {
        "status": status,
        "toxicity_score": round(float(toxicity_score), 3),
        "toxicity_type": toxicity_type,
        "message": message
    }


# ---------- REJECT COMMENT ----------
@app.post("/comments/reject/{comment_id}")
def reject_comment(comment_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT comments.user_id, comments.text, posts.content, users.username
        FROM comments
        JOIN posts ON comments.post_id = posts.id
        JOIN users ON posts.user_id = users.id
        WHERE comments.id = %s
    """, (comment_id,))

    data = cursor.fetchone()

    if data is None:
        conn.close()
        return {"error": "Comment not found"}

    message = f'{data["username"]} rejected your comment "{data["text"]}" for the post "{data["content"]}"'

    cursor.execute("UPDATE comments SET status='rejected' WHERE id=%s", (comment_id,))
    cursor.execute(
        "INSERT INTO notifications (user_id, message) VALUES (%s, %s)",
        (data["user_id"], message)
    )

    conn.commit()
    conn.close()

    return {"message": "Comment rejected"}

# ---------- NOTIFICATIONS ----------
@app.get("/notifications/{user_id}")
def get_notifications(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT message, created_at FROM notifications WHERE user_id=%s ORDER BY created_at DESC",
        (user_id,)
    )
    data = cursor.fetchall()
    conn.close()

    return data

# ---------- MY POSTS ----------
@app.get("/my-posts/{user_id}")
def get_my_posts(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, content, created_at
        FROM posts
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))

    posts = cursor.fetchall()
    conn.close()
    return posts

# ---------- APPROVED COMMENTS ----------
@app.get("/comments/approved/{post_id}")
def get_approved_comments(post_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT comments.text, comments.toxicity_score, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = %s AND comments.status = 'approved'
        ORDER BY comments.created_at ASC
    """, (post_id,))

    comments = cursor.fetchall()
    conn.close()
    return comments
# ---------- PENDING COMMENTS FOR MY POSTS ----------
@app.get("/my-posts/comments/{user_id}")
def get_pending_comments(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            comments.id AS comment_id,
            comments.text,
            comments.toxicity_score,
            users.username AS commenter
        FROM comments
        JOIN posts ON comments.post_id = posts.id
        JOIN users ON comments.user_id = users.id
        WHERE posts.user_id = %s
          AND comments.status = 'pending'
        ORDER BY comments.created_at ASC
    """, (user_id,))

    data = cursor.fetchall()
    conn.close()
    return data
