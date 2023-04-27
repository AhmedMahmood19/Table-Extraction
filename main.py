from auth import firebase_auth
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, status, Depends
from fastapi.responses import StreamingResponse
import tableextraction
import os
import zipfile
from io import BytesIO
import firebase_admin

# Use the service account keys to create a credentials.Certificate to connect to firebase
cred = firebase_admin.credentials.Certificate('table_service_account_keys.json')
# Use those credentials to initialize the firebase_admin app which will verify the JWT
firebase_admin.initialize_app(cred)

app = FastAPI()

@app.post("/extract", dependencies=[Depends(firebase_auth)])
async def extract_csv(file: UploadFile, 
                      Table_detection_threshold: Optional[float] = 0.6, 
                      Table_structure_recognition_threshold: Optional[float] = 0.8, 
                      padding_top: Optional[int] = 20, 
                      padding_left: Optional[int] = 20, 
                      padding_right: Optional[int] = 20,
                      padding_bottom: Optional[int] = 20):
    
    if Table_detection_threshold<0 or Table_detection_threshold>1 or Table_structure_recognition_threshold<0 or Table_structure_recognition_threshold>1:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Table_detection_threshold and Table_structure_recognition_threshold must be floats in the range 0 to 1.0 inclusive")
    if not (0 <= padding_top <= 200 and 0 <= padding_left <= 200 and 0 <= padding_right <= 200 and 0 <= padding_bottom <= 200):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="padding_top, padding_left, padding_right, and padding_bottom must be integers in the range of 0 to 200 inclusive")
    if 'image' not in file.content_type:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is not an image.")       
    
    try:
        image = await file.read()
        result = await tableextraction.image_to_csv(image, Table_detection_threshold, Table_structure_recognition_threshold, padding_top, padding_left, padding_right, padding_bottom)
        if result==0:
            return HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No table was detected in the image.")
        else:
            file_list = [f'ExtractedTable{i}.csv' for i in range(result)]
            zip_response = zipfiles(file_list)
            for file_path in file_list:
                os.remove(file_path)
            return zip_response
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Internal Server Error. {err}")


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