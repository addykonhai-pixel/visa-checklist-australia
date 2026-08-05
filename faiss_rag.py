"""
FAISS RAG Vector Store & Similarity Search Engine (Python)
Implements dense query vectorization, L2 normalization, Cosine & L2 distance metrics,
top-K retrieval, and RAG answer synthesis for Australian visa regulations.
"""

import math
import re
import numpy as np
from kb_data import AU_VISA_KB


class FAISSVectorStore:
    def __init__(self, documents=None):
        self.dimension = 64
        self.documents = documents if documents is not None else AU_VISA_KB
        self.index = []
        self._build_index()

    def _normalize_vector(self, vec):
        arr = np.array(vec, dtype=np.float32)
        norm = np.linalg.norm(arr)
        if norm > 0:
            arr = arr / norm
        return arr

    def _build_index(self):
        self.index = []
        for doc in self.documents:
            raw_vec = doc.get("vector")
            if not raw_vec or len(raw_vec) != self.dimension:
                raw_vec = self.vectorize_text(doc.get("title", "") + " " + doc.get("content", ""))
            norm_vec = self._normalize_vector(raw_vec)
            self.index.append({
                "doc": doc,
                "vector": norm_vec
            })

    def vectorize_text(self, text):
        text_lower = text.lower()
        vec = np.zeros(self.dimension, dtype=np.float32)

        keywords = [
            "student", "subclass", "500", "600", "482", "189", "190", "417", "462", "820",
            "financial", "bank", "funds", "aud", "29710", "5000", "living", "cost", "tuition",
            "genuine", "gs", "gte", "statement", "sop", "ties", "home", "return",
            "health", "insurance", "oshc", "ovhc", "bupa", "medibank", "allianz", "nib",
            "character", "police", "afp", "clearance", "form 80", "1221", "penal",
            "naati", "translation", "passport", "6 month", "validity", "mrz",
            "work", "tss", "tsmit", "skills", "assessment", "vetassess", "acs", "points"
        ]

        for idx, kw in enumerate(keywords):
            if kw in text_lower:
                dim = (idx * 3) % self.dimension
                vec[dim] += 0.85
                vec[(dim + 1) % self.dimension] += 0.45
                vec[(dim + 7) % self.dimension] += 0.35

        for i in range(len(text_lower) - 2):
            code = ord(text_lower[i]) + ord(text_lower[i+1]) * 31 + ord(text_lower[i+2]) * 97
            dim = abs(code) % self.dimension
            vec[dim] += 0.05

        return self._normalize_vector(vec)

    def search(self, query_text, top_k=3, target_subclass=None):
        query_vec = self.vectorize_text(query_text)
        candidates = self.index

        if target_subclass and target_subclass not in ["ALL", "SELECT"]:
            candidates = [
                item for item in candidates
                if item["doc"]["subclass"] == target_subclass or item["doc"]["subclass"] == "ALL" or target_subclass in item["doc"]["subclass"]
            ]

        results = []
        for item in candidates:
            doc_vec = item["vector"]
            cosine_sim = float(np.dot(query_vec, doc_vec))
            l2_dist = float(np.linalg.norm(query_vec - doc_vec))

            # Keyword match boost
            boost = 0.0
            tokens = re.split(r'\s+', query_text.lower())
            for t in tokens:
                if len(t) > 2 and any(t in tag.lower() for tag in item["doc"]["tags"]):
                    boost += 0.15

            final_score = min(0.99, max(0.01, cosine_sim + boost))

            results.append({
                "doc": item["doc"],
                "similarity_score": round(final_score, 4),
                "l2_distance": round(l2_dist, 4),
                "vector_preview": [round(float(x), 3) for x in doc_vec[:8]]
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)

        return {
            "query_text": query_text,
            "query_vector_preview": [round(float(x), 3) for x in query_vec[:8]],
            "results": results[:top_k]
        }

    def generate_rag_answer(self, query_text, target_subclass="ALL"):
        search_res = self.search(query_text, top_k=3, target_subclass=target_subclass)
        top_hits = search_res["results"]

        if not top_hits or top_hits[0]["similarity_score"] < 0.25:
            return {
                "answer": "No high-confidence match found in the Australian Department of Home Affairs knowledge base for your query. Try specifying your Subclass (500, 600, 482) or keywords like 'bank statement AUD', 'OSHC insurance', or 'NAATI translation'.",
                "confidence": 0.20,
                "sources": [],
                "raw_retrieval": search_res
            }

        primary_doc = top_hits[0]["doc"]
        confidence = top_hits[0]["similarity_score"]

        answer_lines = [
            f"Based on official Department of Home Affairs rules for {primary_doc['subclass_name']}:\n",
            f"📌 {primary_doc['title']}",
            f"{primary_doc['content']}\n"
        ]

        if len(top_hits) > 1 and top_hits[1]["similarity_score"] > 0.35:
            sec_doc = top_hits[1]["doc"]
            answer_lines.append(f"💡 Additional Requirement ({sec_doc['category']}):")
            answer_lines.append(f"{sec_doc['content']}\n")

        answer_lines.append("> Key Takeaway: Attach all original or NAATI-certified documents to your ImmiAccount application portal.")

        sources = [
            {
                "title": hit["doc"]["title"],
                "subclass": hit["doc"]["subclass_name"],
                "category": hit["doc"]["category"],
                "url": hit["doc"]["source"],
                "similarity": hit["similarity_score"]
            }
            for hit in top_hits
        ]

        return {
            "answer": "\n".join(answer_lines),
            "confidence": confidence,
            "sources": sources,
            "raw_retrieval": search_res
        }
