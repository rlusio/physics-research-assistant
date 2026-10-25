def split_pages(pages, filename, chunk_size=500, overlap=100):
    if chunk_size <= 0:
        raise ValueError("chunk_size musi być większy od 0")

    if not 0 <= overlap < chunk_size:
        raise ValueError("overlap musi być w zakresie od 0 do chunk_size - 1")

    chunks = []
    chunk_id = 0

    for page in pages:
        page_text = page["text"]
        page_number = page["page"]
        start = 0

        while start < len(page_text):
            end = min(start + chunk_size, len(page_text))

            if end < len(page_text):
                dot = page_text.rfind(".", start, end)
                question = page_text.rfind("?", start, end)
                exclamation = page_text.rfind("!", start, end)

                boundary = max(dot, question, exclamation)

                if boundary >= start + chunk_size // 2:
                    end = boundary + 1

            fragment = page_text[start:end].strip()

            if fragment:
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

            next_start = max(start + 1, end - overlap)

            if (
                next_start > 0
                and next_start < len(page_text)
                and not page_text[next_start - 1].isspace()
                and not page_text[next_start].isspace()
            ):
                for i in range(next_start - 1, start - 1, -1):
                    if page_text[i].isspace():
                        next_start = i + 1
                        break
                    
            next_start = max(start + 1, next_start)                
            start = next_start
                    
    return chunks
