
from src.extract_text import extract_pdf


def test_extract_pdf_preserves_page_numbers(tmp_path):
    import pymupdf

    pdf_path = tmp_path / "sample.pdf"

    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text(
            (72, 72),
            "Machine learning test document"
        )
        document.save(pdf_path)

    pages = extract_pdf(pdf_path)

    assert len(pages) == 1
    assert pages[0]["page"] == 1
    assert "Machine learning" in pages[0]["text"]
