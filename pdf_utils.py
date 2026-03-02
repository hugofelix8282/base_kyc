from pdf2image import convert_from_path
from pathlib import Path
from PIL import Image
import tempfile

def extract_image_from_pdf(pdf_path: str, output_path: str = None) -> str:
    images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=200)
    
    if not images:
        raise ValueError("Nenhuma imagem encontrada no PDF")
    
    if output_path is None:
        temp_dir = tempfile.gettempdir()
        output_path = f"{temp_dir}/cnh_extracted.jpg"
    
    images[0].save(output_path, "JPEG")
    return output_path
