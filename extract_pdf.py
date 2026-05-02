import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text

if __name__ == "__main__":
    pdf_path = "Orchids Handbook- Regular 10062023 (1).pdf"
    extracted_text = extract_text_from_pdf(pdf_path)
    with open("handbook_text.txt", "w", encoding="utf-8") as f:
        f.write(extracted_text)
    print("Text extracted and saved to handbook_text.txt")