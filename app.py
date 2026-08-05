"""
🇦🇺 AusVisa Assist Pro - Streamlit Web Application
College Showcase Project for Australian Visa Document Checklist & FAISS RAG Assistant
"""

import os
import sys

# Ensure local module path resolution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import numpy as np

# Import custom core modules
from faiss_rag import FAISSVectorStore
from checklist_builder import VisaChecklistGenerator
from doc_verifier import DocumentVerifierEngine
from timeline_estimator import TimelineEstimatorEngine
from kb_data import AU_VISA_KB, SAMPLE_TEST_DOCUMENTS

# Streamlit Page Config
st.set_page_config(
    page_title="AusVisa Assist Pro",
    page_icon="🇦🇺",
    layout="wide"
)

# Initialize Core Engines (cached in session state)
@st.cache_resource
def load_engines():
    rag = FAISSVectorStore()
    checklist_builder = VisaChecklistGenerator()
    verifier = DocumentVerifierEngine()
    timeline = TimelineEstimatorEngine()
    return rag, checklist_builder, verifier, timeline

rag_engine, checklist_engine, verifier_engine, timeline_engine = load_engines()

# Header & Banner
st.title("🇦🇺 AusVisa Assist Pro")
st.caption("AI-Powered Australian Visa Document Checklist & FAISS RAG Search Engine (2024-2026 DHA Rules)")

st.sidebar.title("📌 Navigation")
module = st.sidebar.radio(
    "Select Project Module:",
    [
        "🤖 AI Visa Search (RAG)",
        "📋 Visa Checklist Builder",
        "🔍 Document Verifier Audit",
        "⏳ Processing Timeline Estimator",
        "📚 Knowledge Base Database"
    ]
)

st.sidebar.divider()
st.sidebar.info("🎓 **College Showcase Project**\nBuilt with Python, Streamlit, NumPy, and FAISS Vector Search.")

# ---------------------------------------------------------
# MODULE 1: AI VISA SEARCH (FAISS RAG Q&A)
# ---------------------------------------------------------
if module == "🤖 AI Visa Search (RAG)":
    st.header("🤖 Module 1: AI Visa Rule Search (FAISS Vector RAG)")
    st.markdown("Ask questions about Australian visa rules, bank balance limits, NAATI translations, OSHC, or work rights.")

    col1, col2 = st.columns([3, 1])
    with col1:
        user_query = st.text_input("Enter your Question:", value="What is the minimum bank balance for Student Visa Subclass 500?")
    with col2:
        visa_filter = st.selectbox("Target Visa Subclass:", ["ALL", "500", "600", "482", "189/190"])

    if st.button("🔍 Search Knowledge Base", type="primary"):
        if user_query.strip():
            with st.spinner("Searching FAISS dense vector store..."):
                res = rag_engine.generate_rag_answer(user_query, target_subclass=visa_filter)
                
                st.subheader("💡 RAG Generated Answer")
                st.success(res["answer"])
                
                # Confidence Score Metric
                st.metric("Vector Match Confidence", f"{res['confidence']*100:.1f}%")

                # Grounded Sources
                if res.get("sources"):
                    st.subheader("📚 Grounded Knowledge Base Sources")
                    for src in res["sources"]:
                        with st.expander(f"📌 [{src['subclass']}] {src['title']} (Cosine Match: {src['similarity']*100:.1f}%)"):
                            st.write(f"**Category:** {src['category']}")
                            st.write(f"**Official Source:** {src['url']}")

                # Vector Inspector for Demo Showcase
                with st.expander("🔍 FAISS Dense Vector Inspector (College Demo Feature)"):
                    raw = res.get("raw_retrieval", {})
                    st.json({
                        "query_text": user_query,
                        "query_dense_vector_preview": raw.get("query_vector_preview", []),
                        "top_hits_count": len(raw.get("results", []))
                    })
        else:
            st.warning("Please enter a question to search.")

# ---------------------------------------------------------
# MODULE 2: VISA CHECKLIST BUILDER
# ---------------------------------------------------------
elif module == "📋 Visa Checklist Builder":
    st.header("📋 Module 2: Country-Specific Visa Checklist Generator")
    st.markdown("Generate official Department of Home Affairs document requirements based on your passport country.")

    col1, col2, col3 = st.columns(3)
    with col1:
        subclass = st.selectbox("Select Visa Subclass:", ["500", "600", "482", "189/190"])
    with col2:
        country = st.selectbox("Passport Country:", ["India", "Nepal", "China", "UK", "USA", "Vietnam", "Pakistan", "Other"])
    with col3:
        has_dependents = st.checkbox("Including Spouse / Dependents?")

    if st.button("📄 Generate Document Checklist", type="primary"):
        checklist_data = checklist_engine.generate_checklist(subclass, country, has_dependents=has_dependents)
        
        st.subheader(f"📋 Document Checklist for Subclass {subclass} ({country} Passport)")
        
        col_risk, col_docs = st.columns([1, 3])
        with col_risk:
            st.metric("Country Risk Level", checklist_data.get("assessment_level", "Level 2"))
            st.caption(f"Financial Requirement: {checklist_data.get('financial_requirement', 'AUD $29,710/yr')}")
        
        with col_docs:
            st.markdown("### Required Documents List:")
            for item in checklist_data.get("documents", []):
                st.checkbox(f"**{item['name']}** ({item['category']}) - *{item['description']}*", value=False)

# ---------------------------------------------------------
# MODULE 3: DOCUMENT VERIFIER AUDIT
# ---------------------------------------------------------
elif module == "🔍 Document Verifier Audit":
    st.header("🔍 Module 3: Document Compliance Audit Engine")
    st.markdown("Run automated compliance checks on passport validity, bank statement recency, OSHC health cover, and Form 80.")

    st.subheader("Select Sample Test Document to Audit:")
    doc_options = {f"Doc #{i+1}: {d.get('type', 'Unknown')} ({d.get('filename', '')})": d for i, d in enumerate(SAMPLE_TEST_DOCUMENTS)}
    selected_name = st.selectbox("Choose Document:", list(doc_options.keys()))
    selected_doc = doc_options[selected_name]

    if st.button("🧪 Run Compliance Audit", type="primary"):
        audit = verifier_engine.verify_document(selected_doc)
        
        st.subheader("📊 Audit Results")
        col_score, col_status = st.columns(2)
        with col_score:
            score = audit.get("score", 0)
            st.metric("Compliance Score", f"{score}%")
            st.progress(score / 100)
        with col_status:
            status = audit.get("status", "REJECTED")
            if status == "PASSED":
                st.success(f"STATUS: {status}")
            else:
                st.error(f"STATUS: {status}")

        st.markdown("### 📋 Verification Checklist Findings:")
        for check in audit.get("checks", []):
            if check["passed"]:
                st.success(f"✅ {check['name']}: {check['detail']}")
            else:
                st.error(f"❌ {check['name']}: {check['detail']}")

# ---------------------------------------------------------
# MODULE 4: PROCESSING TIMELINE ESTIMATOR
# ---------------------------------------------------------
elif module == "⏳ Processing Timeline Estimator":
    st.header("⏳ Module 4: DHA Processing Timeline & Milestone Estimator")
    st.markdown("Calculate estimated decision timeline based on Department of Home Affairs global processing statistics.")

    col1, col2 = st.columns(2)
    with col1:
        visa_type = st.selectbox("Visa Subclass:", ["500", "600", "482", "189/190"])
    with col2:
        app_date = st.date_input("Application Submission Date:")

    if st.button("📅 Calculate Processing Schedule", type="primary"):
        timeline_data = timeline_engine.estimate_timeline(visa_type, app_date.strftime("%Y-%m-%d"))
        
        st.subheader("⏱️ Processing Estimates")
        m1, m2, m3 = st.columns(3)
        m1.metric("50% Applications Processed In", f"{timeline_data.get('p50_days', 25)} days")
        m2.metric("90% Applications Processed In", f"{timeline_data.get('p90_days', 45)} days")
        m3.metric("Estimated Decision Date", timeline_data.get("est_decision_date", ""))

        st.markdown("### 🎯 Application Milestones:")
        for m in timeline_data.get("milestones", []):
            st.info(f"**Day {m['day']}:** {m['title']} — *{m['description']}* (Date: {m['date']})")

# ---------------------------------------------------------
# MODULE 5: KNOWLEDGE BASE DATABASE
# ---------------------------------------------------------
elif module == "📚 Knowledge Base Database":
    st.header("📚 Module 5: Australian Migration Knowledge Base")
    st.markdown("Browse all curated Home Affairs regulations, financial thresholds, and visa rules stored in the local index.")

    for idx, item in enumerate(AU_VISA_KB):
        with st.expander(f"📄 #{idx+1}: [{item['subclass_name']}] {item['title']}"):
            st.write(f"**Category:** {item['category']}")
            st.write(f"**Content:** {item['content']}")
            st.write(f"**Tags:** `{', '.join(item['tags'])}`")
            st.write(f"**Official Source:** {item['source']}")
