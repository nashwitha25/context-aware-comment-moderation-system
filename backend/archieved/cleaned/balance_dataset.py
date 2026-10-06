import pandas as pd

# Load features dataset
df = pd.read_csv("backend/data/cleaned/features_ready.csv")

# Separate classes
toxic = df[df["final_label"] == 1]
non_toxic = df[df["final_label"] == 0]

# Downsample non-toxic to match toxic count
non_toxic_sampled = non_toxic.sample(n=len(toxic), random_state=42)

# Combine and shuffle
balanced_df = pd.concat([toxic, non_toxic_sampled]).sample(frac=1, random_state=42)

# Save balanced dataset
output_path = "backend/data/final/balanced_toxic_comments.csv"
balanced_df.to_csv(output_path, index=False)

print("STEP 4.1 completed successfully")
print(balanced_df["final_label"].value_counts())
