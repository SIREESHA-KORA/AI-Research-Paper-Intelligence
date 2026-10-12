
from pathlib import Path
import csv
import json
import pymupdf

PDF_DIR = Path("data/uploads")
OUTPUT_DIR = Path("data/processed")
METADATA_FILE = Path("metadata/papers.csv")


def extract_pdf(pdf_path: Path) -> list[dict]:
    """Extract text from a PDF and preserve page numbers."""
    pages = []

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text", sort=True).strip()

            pages.append({
                "page": page_number,
                "text": text,
            })

    return pages


def load_metadata() -> dict:
    """Load paper metadata indexed by PDF filename."""
    with METADATA_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        reader = csv.DictReader(file)
        return {
            row["filename"]: row
            for row in reader
            if row.get("filename")
        }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not METADATA_FILE.exists():
        print(f"Metadata file not found: {METADATA_FILE}")
        return

    metadata = load_metadata()
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDFs found in {PDF_DIR}")
        return

    for pdf_path in pdf_files:
        paper = metadata.get(pdf_path.name)

        if paper is None:
            print(f"Skipping {pdf_path.name}: missing metadata")
            continue

        try:
            pages = extract_pdf(pdf_path)
            total_chars = sum(len(page["text"]) for page in pages)

            if total_chars == 0:
                print(f"WARNING: No text extracted from {pdf_path.name}")
                continue

            result = {
                "paper_id": paper["paper_id"],
                "title": paper["title"],
                "year": int(paper["year"]),
                "arxiv_id": paper["arxiv_id"],
                "source_url": paper["source_url"],
                "filename": pdf_path.name,
                "pages": pages,
            }

            output_path = OUTPUT_DIR / f"{paper['paper_id']}.json"
            output_path.write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            print(
                f"SUCCESS: {paper['paper_id']} | "
                f"{len(pages)} pages | {total_chars} characters"
            )
            print(f"Saved: {output_path}")

        except Exception as error:
            print(f"ERROR processing {pdf_path.name}: {error}")


if __name__ == "__main__":
    main()
