from typing import Any, Dict
import barcode
from barcode.writer import ImageWriter
from io import BytesIO
from fastapi.responses import Response
from fastapi import HTTPException


def generate_code128_barcode(data: str, width: int = 2, height: int = 30) -> Response:
    """Generate Code128 barcode image"""
    try:
        code128 = barcode.get_barcode_class("code128")
        barcode_instance = code128(data, writer=ImageWriter())

        buffer = BytesIO()
        options: Dict[str, Any] = {
            "module_width": width / 10,
            "module_height": height,
            "text_distance": 5,
            "font_size": 10,
        }
        barcode_instance.write(buffer, options=options)
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=barcode_{data}.png"},
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating barcode: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error generating barcode: {str(e)}")
