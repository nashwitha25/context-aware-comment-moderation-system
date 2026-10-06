import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load main dataset
main_path = os.path.join(BASE_DIR, "..", "final", "features_ready.csv")
main_df = pd.read_csv(main_path)

# Keep only required columns
main_df = main_df[["comment_text", "final_label"]]

# Load implicit insults
implicit_path = os.path.join(BASE_DIR, "implicit_insults_extended.csv")
implicit_df = pd.read_csv(implicit_path)

# Load contextual insults
contextual_path = os.path.join(BASE_DIR, "contextual_insults_generated.csv")
contextual_df = pd.read_csv(contextual_path)

# Merge all
combined_df = pd.concat([main_df, implicit_df, contextual_df], ignore_index=True)

# Remove duplicates
combined_df = combined_df.drop_duplicates(subset=["comment_text"])

# Save back to final folder
output_path = os.path.join(BASE_DIR, "..", "final", "features_ready.csv")
combined_df.to_csv(output_path, index=False)

print("DATA MERGED SUCCESSFULLY")
print("Total rows:", len(combined_df))