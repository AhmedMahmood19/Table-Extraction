from fastapi.responses import StreamingResponse
import zipfile
from io import BytesIO

def zipfiles(file_list):
    io = BytesIO()
    zip_filename = "tables.zip"
    with zipfile.ZipFile(io, mode='w', compression=zipfile.ZIP_DEFLATED) as zip:
        for fpath in file_list:
            zip.write(fpath)
        zip.close()
    return StreamingResponse(
        iter([io.getvalue()]),
        media_type="application/x-zip-compressed",
        headers = { "Content-Disposition":f"attachment;filename=%s" % zip_filename}
    )