from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os

from ingestion import upload_to_database
from answer_retriever import answer_query

app = FastAPI()

# Directory to store uploaded files
UPLOAD_DIRECTORY = "uploaded_files"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

@app.post("/upload-csv/")
async def upload_csv_file(file: UploadFile = File(...)):
    # Check if the file is a .csv file
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are allowed")

    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    try:
        # Save uploaded CSV to disk
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Ingest into FAISS vector DB
        upload_to_database(file_path)
        
        return JSONResponse(content={"message": "CSV uploaded and ingested successfully", "file_path": file_path})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

class QuestionRequest(BaseModel):
    question: str

@app.post("/ask-me/")
async def ask_me(request: QuestionRequest):
    result = answer_query(request.question)
    return {"response": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
