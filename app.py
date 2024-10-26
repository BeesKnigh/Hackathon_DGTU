from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from model import AssistantModel
import logging

app = FastAPI(
    title="Student Assistant API",
    description="API для ассистента, помогающего студентам с вопросами по учебе и взрослой жизни.",
    version="1.0.0"
)

# Глобальная переменная для модели
assistant_model = None

# Загрузка модели при старте сервера
@app.on_event("startup")
async def startup_event():
    global assistant_model
    logging.info("Запуск и загрузка модели ассистента...")
    try:
        assistant_model = AssistantModel()
        logging.info("Модель успешно загружена.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке модели: {e}")

class Query(BaseModel):
    prompt: str

@app.post("/generate_response", summary="Генерация ответа ассистента", description="Возвращает ответ на основе входного вопроса.")
async def generate_response(query: Query):
    if assistant_model is None:
        raise HTTPException(status_code=503, detail="Модель не загружена. Попробуйте позже.")
    try:
        response = assistant_model.generate_response(query.prompt)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", summary="Главная страница API")
async def root():
    return {"message": "Добро пожаловать в Student Assistant API"}
