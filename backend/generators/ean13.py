from typing import Any, Dict
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from fastapi.responses import Response
from fastapi import HTTPException
from models.barcode_models import EAN13Request


def generate_ean13_barcode(request: EAN13Request) -> Response:
    """Generate EAN13 barcode for medical products"""
    try:
        ean13 = barcode.get_barcode_class("ean13")
        barcode_instance = ean13(request.code[:12], writer=ImageWriter())

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
            headers={"Content-Disposition": f"inline; filename=ean13_{request.code}.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating EAN13 barcode: {str(e)}")
        headers={"Content-Disposition": f"inline; filename=ean13_{code}.png"},
        
