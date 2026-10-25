import pymupdf
import re

def extract_pages(pdf_path):
    pages = []

    try:
        with pymupdf.open(pdf_path) as doc:

            for page in doc:
                page_data = {
                    "page": page.number + 1,
                    "text": clean_text(page.get_text())
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

def clean_text(text):
    #Ujednolicenie końców linii (Windows \r\n, Mac \r)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text) # usuwamy spacje i tabulatory
    text = re.sub(r" *\n *", "\n", text) # usuwamy spacje przed i po przejsciu do nowej lini
    text = re.sub(r"\n{3,}", "\n\n", text) # max jedna pusta linia miedzy akapitami
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text) # entery na spacje zamieniamy jeśli jeśli za i przed nie ma entera zachowujac przerwy miedzy akapitami

    return text.strip()