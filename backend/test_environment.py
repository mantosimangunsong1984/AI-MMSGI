import fastapi
import fitz
import docx
import numpy

print("=" * 50)
print("Environment Test")
print("=" * 50)

print(f"FastAPI      : {fastapi.__version__}")
print(f"NumPy        : {numpy.__version__}")
print("PyMuPDF      : OK")
print("python-docx  : OK")

print("\nSemua library berhasil di-load.")