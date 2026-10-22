import pymupdf
import re

#def extract_text(pdf_path):
#    try:
#        with pymupdf.open(pdf_path) as doc:
#            if doc.page_count == 0:
#                return ""
#            
#            text = []
#            for page in doc:
#                page_text = page.get_text()
#                text.append(page_text)
#
#            text_dict = dict(enumerate(text, start=1))
#            return text_dict
#
#    except pymupdf.FileNotFoundError:
#        print("Plik nie istnieje.")
#        return ""
#    
#    except pymupdf.EmptyFileError:
#        print("Plik jest pusty — ma 0 bajtów.")
#        return ""
#    except pymupdf.FileDataError:
#        print("Plik jest uszkodzony lub ma nieprawidłowy format.")
#        return ""
    

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

if __name__ == "__main__":
    pages = extract_pages("data/materialy01.pdf")

    print(f"Liczba stron: {len(pages)}")

    if pages:
        print(f"Numer strony: {pages[0]['page']}")
        print(pages[0]["text"][:1000]) 