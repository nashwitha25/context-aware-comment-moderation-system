import pandas as pd

# Load cleaned dataset
df = pd.read_csv("backend/data/cleaned/train_cleaned.csv")

# Create final_label
df["final_label"] = (
    df["toxic"]
    | df["severe_toxic"]
    | df["obscene"]
    | df["threat"]
    | df["insult"]
    | df["identity_hate"]
)

# Keep only required columns
df = df[["comment_text", "final_label"]]

# Save back
df.to_csv("backend/data/cleaned/train_cleaned.csv", index=False)

print("final_label column created successfully")
print(df["final_label"].value_counts())
