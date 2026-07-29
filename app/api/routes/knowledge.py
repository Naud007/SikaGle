@router.post("/process")
def process_pdf(
    pdf_path: str,
):

    try:

        result = service.process_pdf(
            Path(pdf_path)
        )

        return {
            "status": "success",
            "txt_file": str(
                result["txt_path"]
            ),
            "characters": result[
                "characters"
            ],
            "chunks": result[
                "chunks_count"
            ],
            "preview": (
                result["chunks"][0][:500]
                if result["chunks"]
                else ""
            ),
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
