from typing import Any, Dict
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import re
from fastapi.responses import Response
from fastapi import HTTPException


def generate_ean13_barcode(code: str) -> Response:
    """Generate EAN13 barcode for medical products"""
    try:
        # Validate EAN13 format
        if not re.match(r"^\d{12,13}$", code):
            raise ValueError("EAN13 must be 12 or 13 digits")

        ean13 = barcode.get_barcode_class("ean13")
        barcode_instance = ean13(code[:12], writer=ImageWriter())

        buffer = BytesIO()
        options: Dict[str, Any] = {
            "module_width": 0.33,
            "module_height": 25,
            "text_distance": 5,
            "font_size": 12,
        }
        barcode_instance.write(buffer, options=options)
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=ean13_{code}.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating EAN13 barcode: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error generating EAN13 barcode: {str(e)}")
