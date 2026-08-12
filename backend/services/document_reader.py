from pathlib import Path
from docx import Document
import fitz


class DocumentReader:

    def __init__(self):

        print("=" * 60)
        print("EVE DOCUMENT READER")
        print("=" * 60)
        print("Document Reader berhasil diinisialisasi.\n")

    # =========================================================
    # NORMALIZE TEXT
    # =========================================================

    def _clean_text(self, text):

        if text is None:
            return ""

        text = str(text)

        # Normalisasi whitespace
        text = text.replace("\xa0", " ")
        text = text.replace("\r", "\n")

        lines = []

        for line in text.split("\n"):

            line = " ".join(line.split())

            if line:
                lines.append(line)

        return "\n".join(lines)

    # =========================================================
    # READ TXT
    # =========================================================

    def read_txt(self, file_path):

        file_path = Path(file_path)

        print("\n" + "=" * 80)
        print("READ TXT")
        print("=" * 80)

        print("File :", file_path)

        encodings = [
            "utf-8",
            "utf-8-sig",
            "cp1252",
            "latin-1"
        ]

        for encoding in encodings:

            try:

                with open(
                    file_path,
                    "r",
                    encoding=encoding
                ) as file:

                    text = file.read()

                print("Encoding :", encoding)
                print("Length   :", len(text))

                return self._clean_text(text)

            except UnicodeDecodeError:

                continue

        raise Exception(
            f"Tidak dapat membaca file TXT: {file_path}"
        )

    # =========================================================
    # READ PDF
    # =========================================================

    def read_pdf(self, file_path):

        file_path = Path(file_path)

        print("\n" + "=" * 80)
        print("READ PDF")
        print("=" * 80)

        print("File :", file_path)

        document = fitz.open(file_path)

        pages = []

        for page_number, page in enumerate(
            document,
            start=1
        ):

            text = page.get_text("text")

            text = self._clean_text(text)

            if text:

                pages.append(
                    f"[PAGE {page_number}]\n{text}"
                )

        document.close()

        result = "\n\n".join(pages)

        print("Pages  :", len(pages))
        print("Length :", len(result))

        return result

    # =========================================================
    # DOCX BLOCK ITERATOR
    #
    # Membaca paragraph dan table sesuai urutan
    # kemunculannya di dokumen.
    # =========================================================

    def _iter_block_items(self, parent):

        from docx.document import Document as _Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph
        from docx.oxml.text.paragraph import CT_P
        from docx.oxml.table import CT_Tbl

        if isinstance(parent, _Document):

            parent_elm = parent.element.body

        else:

            parent_elm = parent._tc

        for child in parent_elm.iterchildren():

            if isinstance(child, CT_P):

                yield Paragraph(
                    child,
                    parent
                )

            elif isinstance(child, CT_Tbl):

                yield Table(
                    child,
                    parent
                )

    # =========================================================
    # READ DOCX TABLE
    # =========================================================

    def _read_table(self, table, table_number):

        print("\n" + "-" * 80)
        print(
            f"TABLE #{table_number}"
        )
        print("-" * 80)

        rows = []

        for row_index, row in enumerate(
            table.rows,
            start=1
        ):

            cells = []

            for cell in row.cells:

                cell_text = self._clean_text(
                    cell.text
                )

                cells.append(cell_text)

            # Buang baris kosong total
            if not any(cells):

                continue

            rows.append(cells)

            print(
                f"ROW {row_index}: {cells}"
            )

        print(
            f"TABLE #{table_number} "
            f"ROWS: {len(rows)}"
        )

        if not rows:

            return ""

        # =====================================================
        # TABLE → STRUCTURED TEXT
        # =====================================================

        output = []

        output.append(
            f"[TABLE {table_number}]"
        )

        # -----------------------------------------------------
        # Tentukan header
        # -----------------------------------------------------

        header = rows[0]

        # Apabila hanya 1 kolom, tetap simpan
        if len(rows) == 1:

            for cell in header:

                if cell:

                    output.append(cell)

            output.append(
                f"[/TABLE {table_number}]"
            )

            return "\n".join(output)

        # -----------------------------------------------------
        # Jika tabel memiliki 2 kolom atau lebih
        # -----------------------------------------------------

        if len(header) >= 2:

            # Cek apakah baris pertama memang header
            header_text = " | ".join(
                header
            )

            output.append(
                f"HEADER: {header_text}"
            )

            data_rows = rows[1:]

            for row_number, row in enumerate(
                data_rows,
                start=1
            ):

                # Pastikan jumlah kolom sama
                values = list(row)

                while len(values) < len(header):

                    values.append("")

                # Jika lebih, gabungkan sisanya
                if len(values) > len(header):

                    values = values[:len(header)]

                output.append(
                    f"ROW {row_number}:"
                )

                for column_name, value in zip(
                    header,
                    values
                ):

                    column_name = (
                        column_name.strip()
                    )

                    value = (
                        value.strip()
                    )

                    if column_name or value:

                        output.append(
                            f"{column_name}: {value}"
                        )

        else:

            # -------------------------------------------------
            # Tabel 1 kolom / layout khusus
            # -------------------------------------------------

            for row_number, row in enumerate(
                rows,
                start=1
            ):

                for value in row:

                    value = value.strip()

                    if value:

                        output.append(
                            f"ROW {row_number}: {value}"
                        )

        output.append(
            f"[/TABLE {table_number}]"
        )

        return "\n".join(output)

    # =========================================================
    # READ DOCX
    # =========================================================

    def read_docx(self, file_path):

        file_path = Path(file_path)

        print("\n" + "=" * 80)
        print("READ DOCX")
        print("=" * 80)

        print("File :", file_path)

        document = Document(
            file_path
        )

        blocks = []

        table_count = 0

        paragraph_count = 0

        # =====================================================
        # BACA PARAGRAPH + TABLE SESUAI URUTAN
        # =====================================================

        for block in self._iter_block_items(
            document
        ):

            # =================================================
            # PARAGRAPH
            # =================================================

            if block.__class__.__name__ == "Paragraph":

                text = self._clean_text(
                    block.text
                )

                if text:

                    paragraph_count += 1

                    blocks.append(text)

            # =================================================
            # TABLE
            # =================================================

            elif block.__class__.__name__ == "Table":

                table_count += 1

                table_text = self._read_table(
                    block,
                    table_count
                )

                if table_text:

                    blocks.append(
                        table_text
                    )

        # =====================================================
        # GABUNGKAN SEMUA
        # =====================================================

        result = "\n\n".join(
            blocks
        )

        # =====================================================
        # DEBUG
        # =====================================================

        print("\n" + "=" * 80)
        print("DOCX READER RESULT")
        print("=" * 80)

        print(
            "Paragraph count :",
            paragraph_count
        )

        print(
            "Table count     :",
            table_count
        )

        print(
            "Content length  :",
            len(result)
        )

        print("=" * 80)

        # =====================================================
        # KHUSUS DEBUG KACAMATA
        # =====================================================

        if "kacamata" in result.lower():

            print("\n>>> Kata 'kacamata' ditemukan.")

        else:

            print(
                "\n>>> WARNING: "
                "Kata 'kacamata' tidak ditemukan."
            )

        # =====================================================
        # DEBUG PLAFON
        # =====================================================

        keywords = [
            "6,000,000",
            "4,500,000",
            "3,000,000",
            "2,000,000",
            "1,500,000",
            "grade",
            "reimbursement",
            "penggantian maksimum"
        ]

        print(
            "\n===== TABLE KEYWORD CHECK ====="
        )

        for keyword in keywords:

            if keyword.lower() in result.lower():

                print(
                    f"[FOUND] {keyword}"
                )

            else:

                print(
                    f"[MISSING] {keyword}"
                )

        print(
            "================================"
        )

        return result

    # =========================================================
    # LOAD DOCUMENTS
    # =========================================================

    def load_documents(
        self,
        folder_path
    ):

        folder = Path(folder_path)

        if not folder.exists():

            print(
                f"Folder tidak ditemukan: {folder}"
            )

            return []

        documents = []

        supported_extensions = [
            ".pdf",
            ".docx",
            ".txt"
        ]

        for file_path in sorted(
            folder.iterdir()
        ):

            if not file_path.is_file():

                continue

            extension = (
                file_path.suffix.lower()
            )

            if extension not in supported_extensions:

                print(
                    "SKIP:",
                    file_path.name
                )

                continue

            print("\n" + "=" * 80)
            print(
                "PROCESSING:",
                file_path.name
            )
            print("=" * 80)

            try:

                if extension == ".pdf":

                    text = self.read_pdf(
                        file_path
                    )

                elif extension == ".docx":

                    text = self.read_docx(
                        file_path
                    )

                elif extension == ".txt":

                    text = self.read_txt(
                        file_path
                    )

                else:

                    continue

                document = {

                    "filename":
                        file_path.name,

                    "document_name":
                        file_path.stem,

                    "extension":
                        extension,

                    "size":
                        file_path.stat().st_size,

                    "content":
                        text
                }

                documents.append(
                    document
                )

                print(
                    "\nSUCCESS:",
                    file_path.name
                )

                print(
                    "Content length:",
                    len(text)
                )

            except Exception as e:

                print(
                    "\nERROR:",
                    file_path.name
                )

                print(
                    str(e)
                )

        print("\n" + "=" * 80)
        print("DOCUMENT LOADING COMPLETE")
        print("=" * 80)

        print(
            "Total documents:",
            len(documents)
        )

        return documents