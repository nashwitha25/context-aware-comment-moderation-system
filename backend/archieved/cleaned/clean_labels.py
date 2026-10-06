import pandas as pd

# Load dataset
df = pd.read_csv("backend/data/cleaned/train_cleaned.csv")

# Fill missing comments
df["comment_text"] = df["comment_text"].fillna("")

# Create final label
df["final_label"] = (
    (df["severe_toxic"] == 1) |
    (df["threat"] == 1) |
    (df["identity_hate"] == 1) |
    ((df["obscene"] == 1) & (df["insult"] == 1))
).astype(int)

# Keep only useful columns
final_df = df[["comment_text", "final_label"]]

# Save cleaned dataset
final_df.to_csv("backend/data/final/toxic_comments_final.csv", index=False)

print("STEP 2 completed successfully")
print(final_df["final_label"].value_counts())
