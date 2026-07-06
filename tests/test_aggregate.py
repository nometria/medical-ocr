"""Tests for entity aggregation + markdown export - no tesseract/LLM required."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def _timeline():
    return [
        {
            "doc_type": "Radiology Report",
            "icd_codes": ["M54.5"],
            "cpt_codes": ["72148"],
            "meds": [],
            "body_parts": ["lumbar spine"],
            "restrictions": [],
            "diagnoses": ["disc herniation"],
            "date": "2024-01-02",
            "title": "MRI Lumbar",
        },
        {
            "doc_type": "Clinic/Progress Note (SOAP)",
            "icd_codes": ["M54.5", "S33.5"],  # M54.5 is a duplicate
            "cpt_codes": [],
            "meds": ["ibuprofen"],
            "body_parts": ["back"],
            "restrictions": ["no lifting >10lb"],
            "diagnoses": [],
            "date": None,
            "title": "Follow-up",
        },
    ]


def test_aggregate_entities_dedups_and_orders():
    from medical_ocr.pipeline import aggregate_entities

    ent = aggregate_entities(_timeline())
    # Order preserved on first appearance, duplicates removed.
    assert ent["icd10"] == ["M54.5", "S33.5"]
    assert ent["cpt"] == ["72148"]
    assert ent["medications"] == ["ibuprofen"]
    assert ent["body_parts"] == ["lumbar spine", "back"]
    assert ent["restrictions"] == ["no lifting >10lb"]
    # Doc types are unique, in order of appearance.
    assert ent["doc_types"] == ["Radiology Report", "Clinic/Progress Note (SOAP)"]


def test_aggregate_entities_empty():
    from medical_ocr.pipeline import aggregate_entities

    ent = aggregate_entities([])
    assert ent["icd10"] == []
    assert ent["doc_types"] == []


def test_to_markdown_includes_status_entities_confidence():
    from medical_ocr.pipeline import aggregate_entities
    from medical_ocr.export_md import to_markdown

    tl = _timeline()
    md = to_markdown(
        {
            "summary_text": "Patient summary.",
            "timeline": tl,
            "artifacts": {
                "mmi_found": "Not at MMI",
                "impairment_found": "5% WPI",
                "last_restrictions": "no lifting",
                "last_visit": "2024-01-02",
            },
            "entities": aggregate_entities(tl),
            "confidence": {"overall": 0.83},
        }
    )
    assert "## Case Status" in md
    assert "**MMI:** Not at MMI" in md
    assert "## Coded Entities" in md
    assert "**ICD-10:** M54.5, S33.5" in md
    assert "## OCR Confidence" in md
    assert "83%" in md
    assert "## Chronological Timeline" in md


def test_to_markdown_minimal_without_optional_sections():
    """An empty timeline / no artifacts must not crash or emit empty sections."""
    from medical_ocr.export_md import to_markdown

    md = to_markdown({"summary_text": "Nothing.", "timeline": []})
    assert "# Medical Summary" in md
    assert "## Case Status" not in md
    assert "## Coded Entities" not in md
