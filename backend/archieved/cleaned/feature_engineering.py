import pandas as pd
import re

# Load final dataset
df = pd.read_csv("backend/data/final/toxic_comments_final.csv")

# Feature 1: comment length
df["char_length"] = df["comment_text"].astype(str).apply(len)

# Feature 2: word count
df["word_count"] = df["comment_text"].astype(str).apply(lambda x: len(x.split()))

# Feature 3: uppercase ratio (aggression indicator)
def uppercase_ratio(text):
    text = str(text)
    if len(text) == 0:
        return 0
    return sum(1 for c in text if c.isupper()) / len(text)

df["uppercase_ratio"] = df["comment_text"].apply(uppercase_ratio)

# Feature 4: exclamation count
df["exclamation_count"] = df["comment_text"].astype(str).apply(lambda x: x.count("!"))

# Save feature-enhanced dataset
output_path = "backend/data/cleaned/features_ready.csv"
df.to_csv(output_path, index=False)

print("STEP 3.2 completed successfully")
print(df.head())
# Feature 5: presence of negation words (important for meaning reversal)
NEGATIONS = ["not", "no", "never", "none", "n't"]

def has_negation(text):
    text = str(text).lower()
    return int(any(word in text for word in NEGATIONS))

df["has_negation"] = df["comment_text"].apply(has_negation)

# Feature 6: profanity indicator (lightweight, ML-friendly)
PROFANITY = ["fuck", "shit", "bitch", "asshole", "cocksucker", "bastard"]

def has_profanity(text):
    text = str(text).lower()
    return int(any(word in text for word in PROFANITY))

df["has_profanity"] = df["comment_text"].apply(has_profanity)

# Save updated feature dataset
output_path = "backend/data/cleaned/features_ready.csv"
df.to_csv(output_path, index=False)

print("STEP 3.3 completed successfully")
print(df[[
    "has_negation",
    "has_profanity",
    "final_label"
]].head())
