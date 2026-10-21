import pymupdf

def extract_text(pdf_path):
    try:
        with pymupdf.open(pdf_path) as doc:
            if doc.page_count == 0:
                return ""
            
            text = []
            for page in doc:
                page_text = page.get_text()
                text.append(page_text)

            text_dict = dict(enumerate(text, start=1))
            return text_dict

    except pymupdf.FileNotFoundError:
        print("Plik nie istnieje.")
        return ""
    
    except pymupdf.EmptyFileError:
        print("Plik jest pusty — ma 0 bajtów.")
        return ""
    except pymupdf.FileDataError:
        print("Plik jest uszkodzony lub ma nieprawidłowy format.")
        return ""
    

def extract_pages(pdf_path):
    pages = []

    try:
        with pymupdf.open(pdf_path) as doc:

            for page in doc:
                page_data = {
                    "page": page.number + 1,
                    "text": page.get_text()
                }

                pages.append(page_data)

        return pages

    except pymupdf.FileNotFoundError:
        print("Plik nie istnieje.")
        return []

    except pymupdf.EmptyFileError:
        print("Plik jest pusty.")
        return []

    except pymupdf.FileDataError:
        print("Nieprawidłowy lub uszkodzony PDF.")
        return []

if __name__ == "__main__":
    pages = extract_pages("data/materialy01.pdf")

    print(f"Liczba stron: {len(pages)}")

    if pages:
        print(f"Numer strony: {pages[0]['page']}")
        print(pages[0]["text"][:1000]) 