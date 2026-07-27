class DocumentChunker:

    def __init__(self,
                 chunk_size=800,
                 overlap=200):

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split_text(self, text):

        chunks = []

        start = 0
        chunk_id = 1

        while start < len(text):

            end = start + self.chunk_size

            chunk = text[start:end]

            chunks.append({
                "chunk_id": chunk_id,
                "start": start,
                "end": min(end, len(text)),
                "text": chunk
            })

            start += self.chunk_size - self.overlap

            chunk_id += 1

        return chunks