"""
Dynamic Australia Visa Document Checklist Generator (Python)
Customized by Subclass, Passport Nationality, Stay Duration, and Financial Support Source.
"""

class VisaChecklistGenerator:
    def __init__(self):
        pass

    def generate_checklist(self, profile):
        subclass = profile.get("subclass", "500")
        passport_country = profile.get("passport_country", "India")
        stay_duration = int(profile.get("stay_duration_months", 12))
        financial_source = profile.get("financial_source", "self_savings")
        has_dependents = profile.get("has_dependents", False)
        is_non_english = passport_country not in ["United Kingdom", "Canada", "USA", "New Zealand", "Ireland"]

        items = []

        # 1. Identity & Legal Status
        items.append({
            "id": "doc-id-01",
            "category": "1. Identity & Legal Status",
            "title": "Current Valid Passport (Bio Page & Stamps)",
            "mandatory": True,
            "description": "Color scan of bio-data page, photograph, issue/expiry dates, signature page, and stamped visa pages.",
            "rule": "Must be valid for at least 6 months past intended departure date from Australia with 2 blank pages.",
            "status": "pending",
            "notes": ""
        })

        items.append({
            "id": "doc-id-02",
            "category": "1. Identity & Legal Status",
            "title": "National Identity Card & Birth Certificate",
            "mandatory": True,
            "description": "Government-issued National ID Card (Aadhaar, CNIC, SSN) and Birth Certificate.",
            "rule": "Must match legal name, date of birth, and parents' names matching passport exactly.",
            "status": "pending",
            "notes": ""
        })

        if is_non_english:
            items.append({
                "id": "doc-id-03",
                "category": "1. Identity & Legal Status",
                "title": "NAATI Certified English Translations",
                "mandatory": True,
                "description": "Official English translation for all non-English civil documents, police checks, or academic certificates.",
                "rule": "Must be translated by NAATI-accredited translator (if in Australia) or registered official translator with stamp.",
                "status": "pending",
                "notes": ""
            })

        # 2. Subclass Specific Core Requirements
        if subclass == "500":
            items.append({
                "id": "doc-500-01",
                "category": "2. Academic & Enrollment",
                "title": "Confirmation of Enrolment (CoE)",
                "mandatory": True,
                "description": "Official electronic Confirmation of Enrolment (CoE) issued by CRICOS registered provider in Australia.",
                "rule": "Reflects course start date, full tuition fees, and duration.",
                "status": "pending",
                "notes": ""
            })

            items.append({
                "id": "doc-500-02",
                "category": "2. Genuine Student (GS) Requirements",
                "title": "Genuine Student (GS) Statement & Supporting Proof",
                "mandatory": True,
                "description": "Targeted GS statement answering 4 key questions (circumstances, course choice, career benefits, Australian study history).",
                "rule": "Replaced GTE in March 2024. Every claim must be backed by documentary proof.",
                "status": "pending",
                "notes": ""
            })

            req_aud = 29710 + (10394 if has_dependents else 0) + 2000
            items.append({
                "id": "doc-500-03",
                "category": "3. Financial Capacity & Proof of Funds",
                "title": f"Bank Statements & Financial Proof (Min AUD ${req_aud:,})",
                "mandatory": True,
                "description": f"Proof covering 12 months living costs (AUD $29,710), tuition balance, and travel costs ($2,000). Source: {financial_source.replace('_', ' ').upper()}.",
                "rule": "Held in financial institution for 3+ months or backed by sanctioned education loan letter.",
                "status": "pending",
                "notes": ""
            })

            items.append({
                "id": "doc-500-04",
                "category": "4. Health & Insurance",
                "title": "Overseas Student Health Cover (OSHC) Certificate",
                "mandatory": True,
                "description": "OSHC Policy from Bupa, Medibank, Allianz, NIB, or CBHS.",
                "rule": "Start date must precede arrival date and cover full visa period.",
                "status": "pending",
                "notes": ""
            })

        elif subclass == "600":
            items.append({
                "id": "doc-600-01",
                "category": "2. Genuine Visitor Evidence",
                "title": "Evidence of Employment & Approved Leave Letter",
                "mandatory": True,
                "description": "Employer letter confirming job role, salary, approved leave dates, and expected return date.",
                "rule": "Crucial for demonstrating strong economic ties and incentive to return home.",
                "status": "pending",
                "notes": ""
            })

            items.append({
                "id": "doc-600-02",
                "category": "3. Financial Capacity",
                "title": "Bank Statements (Last 6 Months)",
                "mandatory": True,
                "description": "Personal savings account statements showing stable balance (minimum AUD $1,000 to $1,500/month of stay).",
                "rule": "Must show regular salary credits or income transactions.",
                "status": "pending",
                "notes": ""
            })

            if stay_duration > 3:
                items.append({
                    "id": "doc-600-03",
                    "category": "4. Health Insurance (8501)",
                    "title": "Overseas Visitor Health Cover (OVHC) Policy",
                    "mandatory": True,
                    "description": "Health insurance covering inpatient care and emergency repatriation for stays > 3 months.",
                    "rule": "Mandatory to satisfy Condition 8501 for extended visitor stays.",
                    "status": "pending",
                    "notes": ""
                })

        elif subclass == "482":
            items.append({
                "id": "doc-482-01",
                "category": "2. Employer Sponsorship & Nomination",
                "title": "Sponsor Nomination TRN & TSMIT Salary Compliance",
                "mandatory": True,
                "description": "Transaction Reference Number from approved SBS employer sponsor.",
                "rule": "Nominated salary must meet or exceed TSMIT floor of AUD $73,150/year + super.",
                "status": "pending",
                "notes": ""
            })

            items.append({
                "id": "doc-482-02",
                "category": "3. Work Experience & Skills",
                "title": "Skills Assessment & 2+ Years Experience Proof",
                "mandatory": True,
                "description": "Skills outcome (VETASSESS/ACS/TRA) plus employment contracts, tax returns, and reference letters.",
                "rule": "Minimum 2 years full-time relevant work experience required.",
                "status": "pending",
                "notes": ""
            })

        # Character & Health for Long-term
        if stay_duration >= 6 or subclass != "600":
            items.append({
                "id": "doc-gen-character",
                "category": "5. Character & Penal Certificates",
                "title": "Police Clearance Certificates (PCC) & Form 80",
                "mandatory": True,
                "description": "PCC from all countries resided in for 12+ months cumulatively over past 10 years.",
                "rule": "Must be issued within 12 months prior to decision date. Includes AFP Check Code 33 for Australia.",
                "status": "pending",
                "notes": ""
            })

            items.append({
                "id": "doc-gen-health",
                "category": "6. Health Examination",
                "title": "eMedical HAP ID Medical Examination",
                "mandatory": True,
                "description": "Medical referral letter with HAP ID for Panel Physician examination (Medical 501 + Chest X-Ray 502).",
                "rule": "Booked via Bupa Medical Visa Services or approved overseas Panel Clinic.",
                "status": "pending",
                "notes": ""
            })

        return {
            "profile": profile,
            "items": items
        }
