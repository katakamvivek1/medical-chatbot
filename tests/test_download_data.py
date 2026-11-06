"""Tests for turning MedlinePlus HTML summaries into plain text."""

from scripts.download_data import (
    BLOOD_PRESSURE_TABLE,
    FLAT_BLOOD_PRESSURE_TABLE,
    html_to_text,
)


def test_heading_without_tags_is_separated_from_next_paragraph():
    raw = "<p>Intro.</p>How is it diagnosed?<p>With a blood test.</p>"
    assert html_to_text(raw) == "Intro.\n\nHow is it diagnosed?\n\nWith a blood test."


def test_text_after_a_list_starts_on_its_own_line():
    raw = "<ul><li>Ulcers</li><li>Pregnancy</li></ul>Anemia can make you tired."
    assert html_to_text(raw) == "- Ulcers\n- Pregnancy\n\nAnemia can make you tired."


def test_flat_blood_pressure_table_becomes_readable_rows():
    raw = f"<p>Before.</p>{FLAT_BLOOD_PRESSURE_TABLE}<p>After.</p>"
    assert html_to_text(raw) == f"Before.\n\n{BLOOD_PRESSURE_TABLE}\n\nAfter."
