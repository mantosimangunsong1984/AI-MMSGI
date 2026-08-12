import re


class DocumentChunker:

    def __init__(
        self,
        chunk_size=1200,
        overlap=150
    ):

        self.chunk_size = chunk_size
        self.overlap = overlap

    # ==========================================================
    # PUBLIC
    # ==========================================================

    def split_text(self, document):

        text = document["content"]

        if not text:
            return []

        # ------------------------------------------------------
        # Normalisasi line ending
        # ------------------------------------------------------

        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # ------------------------------------------------------
        # Pecah dokumen menjadi blok:
        #
        # 1. TABLE block
        # 2. TEXT block
        #
        # TABLE block tidak boleh dipotong.
        # ------------------------------------------------------

        blocks = self._extract_blocks(text)

        chunks = []

        current_text = ""

        for block in blocks:

            block_type = block["type"]
            block_text = block["text"].strip()

            if not block_text:
                continue

            # ==================================================
            # TABLE
            # ==================================================

            if block_type == "table":

                # Jika masih ada text sebelumnya,
                # selesaikan dulu sebagai chunk.
                if current_text.strip():

                    chunks.extend(
                        self._chunk_text(
                            current_text.strip()
                        )
                    )

                    current_text = ""

                # --------------------------------------------------
                # Tabel dibuat sebagai satu unit.
                #
                # Kalau tabel lebih besar dari chunk_size,
                # JANGAN memotong row secara sembarangan.
                # Pecah berdasarkan ROW.
                # --------------------------------------------------

                table_chunks = self._chunk_table(
                    block_text
                )

                chunks.extend(table_chunks)

                continue

            # ==================================================
            # TEXT
            # ==================================================

            # Jika text masih bisa ditambahkan ke current chunk
            candidate = (
                current_text + "\n\n" + block_text
                if current_text
                else block_text
            )

            if len(candidate) <= self.chunk_size:

                current_text = candidate

            else:

                # Simpan current chunk
                if current_text.strip():

                    chunks.extend(
                        self._chunk_text(
                            current_text.strip()
                        )
                    )

                current_text = block_text

        # ======================================================
        # Sisa text
        # ======================================================

        if current_text.strip():

            chunks.extend(
                self._chunk_text(
                    current_text.strip()
                )
            )

        # ======================================================
        # Build metadata
        # ======================================================

        result = []

        for index, chunk_text in enumerate(
            chunks,
            start=1
        ):

            result.append({

                "chunk_id": index,

                "filename": document["filename"],

                "document_name": document["document_name"],

                "extension": document["extension"],

                "size": document["size"],

                "text": chunk_text.strip()

            })

        return result

    # ==========================================================
    # EXTRACT BLOCKS
    # ==========================================================

    def _extract_blocks(self, text):

        blocks = []

        # ------------------------------------------------------
        # Cari blok:
        #
        # [TABLE 1]
        # ...
        # [/TABLE 1]
        #
        # [TABLE 2]
        # ...
        # [/TABLE 2]
        # ------------------------------------------------------

        pattern = re.compile(
            r"\[TABLE\s+\d+\].*?\[/TABLE\s+\d+\]",
            re.IGNORECASE | re.DOTALL
        )

        position = 0

        for match in pattern.finditer(text):

            # ----------------------------------------------
            # Text sebelum table
            # ----------------------------------------------

            before = text[
                position:
                match.start()
            ].strip()

            if before:

                blocks.append({

                    "type": "text",

                    "text": before

                })

            # ----------------------------------------------
            # Table
            # ----------------------------------------------

            table_text = match.group(0).strip()

            blocks.append({

                "type": "table",

                "text": table_text

            })

            position = match.end()

        # ------------------------------------------------------
        # Sisa text setelah table
        # ------------------------------------------------------

        remaining = text[position:].strip()

        if remaining:

            blocks.append({

                "type": "text",

                "text": remaining

            })

        # ------------------------------------------------------
        # Jika tidak ada table sama sekali
        # ------------------------------------------------------

        if not blocks and text.strip():

            blocks.append({

                "type": "text",

                "text": text.strip()

            })

        return blocks

    # ==========================================================
    # NORMAL TEXT CHUNKING
    # ==========================================================

    def _chunk_text(self, text):

        chunks = []

        if not text:
            return chunks

        start = 0

        text_length = len(text)

        while start < text_length:

            end = min(
                start + self.chunk_size,
                text_length
            )

            chunk_text = text[
                start:end
            ].strip()

            if chunk_text:

                chunks.append(
                    chunk_text
                )

            # --------------------------------------------------
            # Stop jika sudah sampai akhir
            # --------------------------------------------------

            if end >= text_length:
                break

            # --------------------------------------------------
            # Overlap
            # --------------------------------------------------

            next_start = (
                end - self.overlap
            )

            # Safety
            if next_start <= start:

                next_start = end

            start = next_start

        return chunks

    # ==========================================================
    # TABLE CHUNKING
    # ==========================================================

    def _chunk_table(self, table_text):

        # ------------------------------------------------------
        # Table harus dipertahankan sebagai satu unit.
        #
        # Untuk tabel kecil seperti tabel plafon kacamata,
        # seluruh tabel akan menjadi satu chunk.
        # ------------------------------------------------------

        if len(table_text) <= self.chunk_size:

            return [
                table_text
            ]

        # ------------------------------------------------------
        # Kalau tabel terlalu besar:
        # pecah berdasarkan ROW.
        # ------------------------------------------------------

        lines = table_text.splitlines()

        header = []
        rows = []

        current_row = []

        for line in lines:

            stripped = line.strip()

            if not stripped:
                continue

            # ----------------------------------------------
            # Header
            # ----------------------------------------------

            if stripped.startswith(
                "HEADER:"
            ):

                header.append(
                    stripped
                )

                continue

            # ----------------------------------------------
            # ROW
            # ----------------------------------------------

            if re.match(
                r"ROW\s+\d+\s*:",
                stripped,
                re.IGNORECASE
            ):

                if current_row:

                    rows.append(
                        current_row
                    )

                current_row = [
                    stripped
                ]

                continue

            # ----------------------------------------------
            # Isi row
            # ----------------------------------------------

            if current_row:

                current_row.append(
                    stripped
                )

            else:

                # Bagian table sebelum ROW
                header.append(
                    stripped
                )

        # Simpan row terakhir
        if current_row:

            rows.append(
                current_row
            )

        # ------------------------------------------------------
        # Buat table chunks berdasarkan ROW
        # ------------------------------------------------------

        chunks = []

        current = []

        # Header selalu dibawa ke setiap table chunk.
        base_header = "\n".join(
            header
        )

        for row in rows:

            row_text = "\n".join(
                row
            )

            candidate_parts = []

            if base_header:

                candidate_parts.append(
                    base_header
                )

            candidate_parts.extend(
                current
            )

            candidate_parts.append(
                row_text
            )

            candidate = "\n".join(
                candidate_parts
            )

            # ----------------------------------------------
            # Masih muat
            # ----------------------------------------------

            if len(candidate) <= self.chunk_size:

                current.append(
                    row_text
                )

                continue

            # ----------------------------------------------
            # Simpan chunk sebelumnya
            # ----------------------------------------------

            if current:

                chunk_parts = []

                if base_header:

                    chunk_parts.append(
                        base_header
                    )

                chunk_parts.extend(
                    current
                )

                chunks.append(
                    "\n".join(
                        chunk_parts
                    )
                )

            # ----------------------------------------------
            # Row baru
            # ----------------------------------------------

            current = [
                row_text
            ]

        # ------------------------------------------------------
        # Simpan chunk terakhir
        # ------------------------------------------------------

        if current:

            chunk_parts = []

            if base_header:

                chunk_parts.append(
                    base_header
                )

            chunk_parts.extend(
                current
            )

            chunks.append(
                "\n".join(
                    chunk_parts
                )
            )

        # ------------------------------------------------------
        # Safety fallback
        # ------------------------------------------------------

        if not chunks:

            return [
                table_text
            ]

        return chunks
