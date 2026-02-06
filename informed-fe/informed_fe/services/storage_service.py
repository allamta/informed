from io import BytesIO
from typing import Optional

from PIL import Image

from informed_fe.config.logging import get_logger
from informed_fe.config.settings import settings

logger = get_logger(__name__)

class StorageService:
    @staticmethod
    def process_image(file, compress: bool = True, quality: int = 85) -> bytes:
        image_bytes = file.read()
        if not image_bytes:
            logger.warning("Empty file uploaded")
            raise ValueError("Empty file uploaded")

        mime_type: Optional[str] = getattr(file, "type", None)
        if mime_type and not mime_type.startswith("image/"):
            logger.warning(f"Invalid image file type: {mime_type}")
            raise ValueError("File must be an image (e.g., JPEG, PNG)")

        if len(image_bytes) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
            raise ValueError(f"File size exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit")

        try:
            with BytesIO(image_bytes) as input_io:
                with Image.open(input_io) as img_probe:
                    img_probe.verify()
        except Exception as e:
            logger.warning(f"Invalid image: {str(e)}")
            raise ValueError("Uploaded file is not a valid image")

        if compress:
            try:
                with BytesIO(image_bytes) as input_io, BytesIO() as output_io:
                    with Image.open(input_io) as img:
                        img_format = (img.format or "").upper()

                        if not img_format:
                            if mime_type and "/" in mime_type:
                                subtype = mime_type.split("/", 1)[1].upper()
                                img_format = "JPEG" if subtype in {"JPG", "JPEG"} else subtype
                            else:
                                img_format = "JPEG"

                        if img_format in {"JPG", "JPEG"} and img.mode not in {"RGB", "L"}:
                            img = img.convert("RGB")

                        save_kwargs = {"optimize": True}
                        if img_format in {"JPG", "JPEG"}:
                            save_kwargs["quality"] = quality

                        img.save(output_io, format="JPEG" if img_format == "JPG" else img_format, **save_kwargs)
                        image_bytes = output_io.getvalue()
            except Exception as e:
                logger.error(f"Compression failed: {str(e)}")
                raise ValueError(f"Image compression failed: {str(e)}")

        return image_bytes
