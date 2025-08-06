import barcode
from barcode.writer import ImageWriter
from io import BytesIO
import re
from fastapi.responses import Response
from fastapi import HTTPException


def generate_laetus_barcode(patient_id: str, sample_id: str, lab_code: str = "LAB") -> Response:
    """Generate Laetus-style medical barcode"""
    try:
        # Laetus format: LAB-PATIENTID-SAMPLEID
        laetus_data = f"{lab_code}-{patient_id}-{sample_id}"

        # Validate format
        if not re.match(r"^[A-Z0-9]+-[A-Z0-9]+-[A-Z0-9]+$", laetus_data):
            raise ValueError("Invalid Laetus format")

        code128 = barcode.get_barcode_class("code128")
        barcode_instance = code128(laetus_data, writer=ImageWriter())

        buffer = BytesIO()
        barcode_instance.write(
            buffer,
            options={
                "module_width": 0.2,
                "module_height": 15,
                "text_distance": 5,
                "font_size": 10,
            },
        )
        buffer.seek(0)

        return Response(
            content=buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"inline; filename=laetus_{laetus_data}.png"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Error generating Laetus barcode: {str(e)}"
        )
