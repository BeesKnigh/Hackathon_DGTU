from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from request_queue import RequestQueue
import logging
import uuid

app = FastAPI(
    title="Student Assistant API",
    description="API для ассистента, помогающего студентам с вопросами по учебе и взрослой жизни.",
    version="1.0.0"
)

# Инициализация очереди запросов
queue = RequestQueue()

class Query(BaseModel):
    prompt: str

@app.post("/submit_request", summary="Добавление запроса в очередь", description="Добавляет запрос в очередь для дальнейшей обработки.")
async def submit_request(query: Query):
    try:
        request_id = str(uuid.uuid4())
        
        queue.add_request_to_queue(request_id, query.prompt)
        
        return {"request_id": request_id, "message": "Ваш запрос был добавлен в очередь и будет обработан."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_response/{request_id}", summary="Получение ответа на запрос", description="Получает ответ на запрос по request_id.")
async def get_response(request_id: str):
    try:
        response = queue.get_response(request_id)
        
        if response is None:
            return {"status": "ожидание", "message": "Ваш запрос все еще обрабатывается. Пожалуйста, попробуйте позже."}
        
        return {"status": "готов", "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", summary="Главная страница API")
async def root():
    return {"message": "Добро пожаловать в Student Assistant API"}

@app.get("/queue_length", summary="Длина очереди", description="Возвращает текущую длину очереди запросов.")
async def queue_length():
    return {"queue_length": queue.get_queue_length()}
