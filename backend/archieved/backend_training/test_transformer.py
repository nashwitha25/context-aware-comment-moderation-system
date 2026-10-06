from transformers import pipeline

# Load model with all scores
classifier = pipeline(
    "text-classification",
    model="unitary/toxic-bert",
    top_k=None  # IMPORTANT: this gives all class scores
)

text = "You are not that unworthy."

results = classifier(text)[0]

print("RAW OUTPUT:", results)

toxic_score = 0.0

for item in results:
    if item["label"].lower() == "toxic":
        toxic_score = item["score"]

print("TOXIC SCORE:", toxic_score)

if toxic_score > 0.5:
    print("FINAL: TOXIC")
else:
    print("FINAL: NON-TOXIC")