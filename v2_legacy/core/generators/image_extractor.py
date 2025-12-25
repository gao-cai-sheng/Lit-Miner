
import fitz  # PyMuPDF
import os
from typing import List

class ImageExtractor:
    def __init__(self, output_dir: str = "data/temp/images"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_images(self, pdf_path: str, min_width: int = 100, min_height: int = 100) -> List[str]:
        """
        Extract images from PDF and save them to output_dir.
        Returns a list of saved image paths.
        Filters out small icons/logos based on size.
        """
        doc = fitz.open(pdf_path)
        saved_images = []

        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)

            for image_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                ext = base_image["ext"]
                width = base_image["width"]
                height = base_image["height"]

                # Filter small images
                if width < min_width or height < min_height:
                    continue

                image_filename = f"page{page_index+1}_img{image_index+1}.{ext}"
                image_path = os.path.join(self.output_dir, image_filename)

                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                
                saved_images.append(image_path)
        
        return saved_images

if __name__ == "__main__":
    # Mock test if a PDF exists, or just basic compilation check
    print("ImageExtractor ready.")
