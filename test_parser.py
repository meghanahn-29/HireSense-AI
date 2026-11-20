from resume_parser import extract_text_from_pdf

pdf_path = "sample_resume.pdf"

try:
    extracted_text = extract_text_from_pdf(pdf_path)

    print("PDF extraction successful!")
    print("\nExtracted Resume Text:\n")
    print(extracted_text)

except ValueError as e:
    print("Error:", e)