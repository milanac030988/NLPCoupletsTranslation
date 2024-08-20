import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from api.request_handler import handler_instance as handler  # Import instance

app = FastAPI()

translate_request_count = 0
contribute_request_count = 0

class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/request_stats") == -1

# Filter out /endpoint
logging.getLogger("uvicorn.access").addFilter(EndpointFilter())

class TranslateRequest(BaseModel):
   type: str
   source: str
   method: str

class ContributeRequest(BaseModel):
   type: str
   cn: str
   sv: str
   vi: str

@app.post("/translate")
def translate_request(request: TranslateRequest):
   global translate_request_count
   translate_request_count += 1
   try:
      return handler.handle_translate(request.source, request.method)
   except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

@app.post("/contribute")
def contribute_request(request: ContributeRequest):
   global contribute_request_count
   contribute_request_count += 1
   try:
      return handler.handle_contribute(request.cn, request.sv, request.vi)
   except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))

@app.get("/request_stats")
def get_request_stats():
   return {
      "translate_request_count": translate_request_count,
      "contribute_request_count": contribute_request_count
   }

@app.post("/start")
def start_handler():
   handler.start()
   return {"status": "Handler started"}

@app.post("/stop")
def stop_handler():
   handler.stop()
   return {"status": "Handler stopped"}
