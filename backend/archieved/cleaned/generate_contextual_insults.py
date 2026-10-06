import pandas as pd
import random

# Base insult phrases
subjects = [
    "You are",
    "Nobody thinks you are",
    "Everyone knows you are",
    "It is obvious you are",
    "People say you are"
]

traits = [
    "a complete failure",
    "useless",
    "a waste of space",
    "pathetic",
    "a disappointment",
    "a burden",
    "worthless",
    "incompetent",
    "good for nothing",
    "a joke"
]

extensions = [
    "",
    " and nobody respects you",
    " and everyone avoids you",
    " and you ruin everything",
    " and nothing you do works",
    " and people regret trusting you",
    " and you embarrass yourself",
    " and you always fail",
]

data = []

for _ in range(3000):
    sentence = random.choice(subjects) + " " + random.choice(traits) + random.choice(extensions)
    data.append([sentence, 1])

df = pd.DataFrame(data, columns=["comment_text", "final_label"])

df.to_csv("backend/data/raw/contextual_insults_generated.csv", index=False)

print("3,000 contextual insults generated successfully!")