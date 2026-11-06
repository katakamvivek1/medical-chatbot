"""Tests for Day 2: loading and chunking."""

import pytest

from src.ingest import clean_text, load_documents, split_documents, split_text


def test_clean_text_fixes_pdf_mess():
    messy = "treat-\nment   of   diabetes\n\n\n\nnext"
    assert clean_text(messy) == "treatment of diabetes\n\nnext"


def test_load_documents_reads_txt_and_ignores_other_files(tmp_path):
    (tmp_path / "flu.txt").write_text("Influenza is a viral infection.")
    (tmp_path / "notes.docx").write_text("should be ignored")
    docs = load_documents(tmp_path)
    assert len(docs) == 1
    assert docs[0].source == "flu.txt"
    assert docs[0].page == 1


def test_load_documents_missing_folder_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_documents(tmp_path / "does-not-exist")


def test_split_documents_respects_size_and_keeps_metadata(tmp_path):
    sentence = "Diabetes is a condition where blood sugar stays too high. "
    (tmp_path / "diabetes.txt").write_text(sentence * 60)  # ~3,500 characters
    chunks = split_documents(load_documents(tmp_path), chunk_size=500, chunk_overlap=50)

    assert len(chunks) > 1
    assert all(len(c.text) <= 500 for c in chunks)
    assert all(c.source == "diabetes.txt" for c in chunks)
    assert len({c.chunk_id for c in chunks}) == len(chunks)  # ids are unique


def test_split_text_repeats_text_between_neighbouring_chunks():
    pieces = split_text("alpha beta gamma delta epsilon zeta", chunk_size=16, chunk_overlap=6)
    assert pieces == ["alpha beta", "beta gamma", "gamma delta", "delta epsilon", "zeta"]


def test_split_text_cuts_long_text_without_separators():
    pieces = split_text("x" * 25, chunk_size=10, chunk_overlap=0)
    assert pieces == ["x" * 10, "x" * 10, "x" * 5]