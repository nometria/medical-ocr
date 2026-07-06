from __future__ import annotations
from typing import Dict, Any

def to_markdown(result: Dict[str, Any]) -> str:
    s = ["# Medical Summary\n"]
    s.append(result["summary_text"])

    artifacts = result.get("artifacts") or {}
    entities = result.get("entities") or {}

    # Case status block — the facts an attorney pulls first.
    status_lines = []
    if artifacts.get("mmi_found"):
        status_lines.append(f"- **MMI:** {artifacts['mmi_found']}")
    if artifacts.get("impairment_found"):
        status_lines.append(f"- **Impairment rating:** {artifacts['impairment_found']}")
    if artifacts.get("last_restrictions"):
        status_lines.append(f"- **Last restrictions:** {artifacts['last_restrictions']}")
    if artifacts.get("last_visit"):
        status_lines.append(f"- **Last visit:** {artifacts['last_visit']}")
    if status_lines:
        s.append("\n## Case Status")
        s.extend(status_lines)

    # Coded entities block.
    ent_specs = [
        ("Document types", entities.get("doc_types")),
        ("ICD-10", entities.get("icd10")),
        ("CPT", entities.get("cpt")),
        ("Medications", entities.get("medications")),
        ("Body parts", entities.get("body_parts")),
        ("Work restrictions", entities.get("restrictions")),
    ]
    ent_lines = [f"- **{label}:** {', '.join(vals)}" for label, vals in ent_specs if vals]
    if ent_lines:
        s.append("\n## Coded Entities")
        s.extend(ent_lines)

    confidence = result.get("confidence") or {}
    if confidence.get("overall") is not None:
        pct = round(float(confidence["overall"]) * 100)
        s.append(f"\n## OCR Confidence\n- **Overall:** {pct}%")

    s.append("\n## Chronological Timeline")
    for e in result["timeline"]:
        dt = e.get("date") or "Undated"
        s.append(f"- {dt} - {e['doc_type']}: {e['title']}")
        if e.get("diagnoses"):
            s.append(f" - Dx: {', '.join(e['diagnoses'])}")
        if e.get("icd_codes"):
            s.append(f" - ICD: {', '.join(e['icd_codes'])}")
        if e.get("cpt_codes"):
            s.append(f" - CPT: {', '.join(e['cpt_codes'])}")
        if e.get("restrictions"):
            s.append(f" - Restrictions: {', '.join(e['restrictions'])}")
    return "\n".join(s)