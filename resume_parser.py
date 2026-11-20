import pymupdf


def extract_text_from_pdf(pdf_path):

    text = ""

    try:
        with pymupdf.open(pdf_path) as document:

            if document.is_encrypted:
                raise ValueError("The PDF is password-protected.")

            for page in document:

                # Extract text while preserving page layout
                page_text = page.get_text("text", sort=True)

                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            raise ValueError("No readable text found in this PDF.")

        return text.strip()

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(f"Unable to extract text from PDF: {error}")