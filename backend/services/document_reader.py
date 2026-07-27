from pathlib import Path
import fitz
from docx import Document


class DocumentReader:

    def read_pdf(self, file_path):

        doc = fitz.open(file_path)

        text = ""

        for page in doc:
            text += page.get_text()

        doc.close()

        return text


    def read_docx(self, file_path):

        doc = Document(file_path)

        text = ""

        for paragraph in doc.paragraphs:

            if paragraph.text.strip():

                text += paragraph.text + "\n"

        return text


    def read_txt(self, file_path):

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


    def load_documents(self, folder):

        folder = Path(folder)

        documents = []

        for file in folder.iterdir():

            if file.suffix.lower() == ".pdf":

                content = self.read_pdf(file)

            elif file.suffix.lower() == ".docx":

                content = self.read_docx(file)

            elif file.suffix.lower() == ".txt":

                content = self.read_txt(file)

            else:

                continue

            documents.append({

                "filename": file.name,

                "type": file.suffix.lower(),

                "content": content

            })

        return documents