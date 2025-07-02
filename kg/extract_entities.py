import spacy
import re
import csv

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Read text from file
with open("data/mosdac_faqs.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Extract question-answer pairs
pairs = re.findall(r"Q:\s*(.*?)\s*A:\s*(.*?)\n\n", text, re.DOTALL)

triples = []

for question, answer in pairs:
    doc = nlp(question + " " + answer)

    # Filter entities of useful types
    entities = [ent.text.strip() for ent in doc.ents if ent.label_ in {"ORG", "PRODUCT", "GPE", "DATE", "TIME", "EVENT", "FAC", "LOC"}]

    # Generate triples using the question as the subject
    for obj in entities:
        triples.append((question.strip(), "refers_to", obj))

# Save triples to CSV
with open("kg/triples.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Subject", "Predicate", "Object"])
    writer.writerows(triples)

print("✅ Triples extracted and saved to kg/triples.csv")
