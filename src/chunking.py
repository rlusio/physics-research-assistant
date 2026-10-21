from pdf_reader import extract_text, extract_pages

def split_text(text, chunk_size=500, overlap=100):
    if chunk_size <= 0:
        raise ValueError("chunk_size musi być większe od 0")

    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap musi być mniejszy od chunk_size")

    fragments = []
    step = chunk_size - overlap
    
    for start in range(0, len(text), step):
        end = start + chunk_size
        fragment = text[start:end]
        fragments.append(fragment)

        if end >= len(text):
            break

    return fragments

def split_pages(pages, filename, chunk_size=500, overlap=100):
    if chunk_size <= 0:
        raise ValueError("chunk_size musi być większy od 0")

    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap musi być w zakresie od 0 do chunk_size - 1")

    chunks = []
    chunk_id = 0

    step = chunk_size - overlap

    for page in pages:
        page_text = page["text"]
        page_number = page["page"]

        for start in range(0, len(page_text), step):
            end = start + chunk_size
            fragment = page_text[start:end]     
            
            chunk_id += 1

            chunk = {
                "document": filename,
                "page": page_number,
                "chunk_id": chunk_id,
                "text": fragment
            }

            chunks.append(chunk)

            if end >= len(page_text):
                break

    return chunks

if __name__ == "__main__":
    pages = extract_pages("data/materialy01.pdf")
    chunks = split_pages(pages, "materialy01.pdf")

    print(f"Liczba stron: {len(pages)}")
    print(f"Liczba fragmentów: {len(chunks)}")

    for chunk in chunks[:3]:
        print(f"\nDokument: {chunk['document']}")
        print(f"Strona: {chunk['page']}")
        print(f"Fragment: {chunk['chunk_id']}")
        print(f"Tekst: {chunk['text'][:100]}")
