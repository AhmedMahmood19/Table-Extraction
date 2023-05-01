from fastapi.responses import FileResponse
import zipfile

def zipfiles(file_list, zip_filename):
    with zipfile.ZipFile(zip_filename, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for fpath in file_list:
            zipf.write(fpath)
    return FileResponse(path=zip_filename,media_type="application/x-zip-compressed",headers={"Content-Disposition":"attachment; filename=tables.zip"})