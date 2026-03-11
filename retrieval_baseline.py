"""
Minimal retrieval demo over /mnt/data/mbs_items.csv
Usage:
  python retrieval_baseline.py "patient transcript text here"
"""
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

items_path = "/mnt/data/mbs_items.csv"
items_df = pd.read_csv(items_path).fillna("")
vectorizer = TfidfVectorizer(min_df=2, ngram_range=(1,2))
X = vectorizer.fit_transform(items_df["description"].astype(str).tolist())

def query(transcript: str, topk: int = 10):
    q = vectorizer.transform([transcript])
    sims = linear_kernel(q, X).ravel()
    top_idx = sims.argsort()[::-1][:topk]
    results = []
    for i in top_idx:
        results.append({
            "rank": len(results)+1,
            "item_num": str(items_df.iloc[i]["item_num"]),
            "score": float(sims[i]),
            "description": items_df.iloc[i]["description"],
            "group": items_df.iloc[i]["group"],
            "category": items_df.iloc[i]["category"],
            "provider_type": items_df.iloc[i]["provider_type"]
        })
    return results

if __name__ == "__main__":
    txt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "consultation at consulting rooms 20 minutes general practitioner"
    for r in query(txt, topk=10):
        print(f'{r["rank"]:>2}. Item {r["item_num"]}  score={r["score"]:.4f}  provider={r["provider_type"]}')
        print("   ", r["description"][:160].replace("\n"," ").strip())
