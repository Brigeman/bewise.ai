from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
import datetime as dt  # Переименовано для избежания конфликта с datetime из стандартной библиотеки

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

import logging

# Настройка логгера
logging.basicConfig(level=logging.DEBUG)

DATABASE_URL = "postgresql://postgres:!QAZ2wsx@bewiseai-db-1/db_questions"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# Модель данных для валидации входящего запроса
class QuestionRequest(BaseModel):
    questions_num: int

# Модель данных для вопросов
class QuestionResponse(BaseModel):
    id: int
    text: str
    answer: str
    created_at: dt.datetime

# Модель данных для таблицы в базе данных
Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    answer = Column(String)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Обработчик POST-запроса
@app.post("/questions/", response_model=None)
def create_questions(request: QuestionRequest, db: Session = Depends(get_db)):
    questions = []

    # Повторяем запросы к внешнему API, пока не получим нужное количество вопросов
    while len(questions) < request.questions_num:
        api_url = f"https://jservice.io/api/random?count={request.questions_num}"
        response = requests.get(api_url)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch questions")

        data = response.json()

        for item in data:
            # Проверяем, существует ли вопрос в базе данных
            existing_question = db.query(Question).filter(Question.text == item["question"]).first()
            if existing_question:
                continue  # Вопрос уже существует, пропускаем

            # Создаем новый объект вопроса и сохраняем его в базе данных
            new_question = Question(text=item["question"], answer=item["answer"])
            db.add(new_question)
            db.commit()

            question_response = QuestionResponse(
                id=new_question.id,
                text=new_question.text,
                answer=new_question.answer,
                created_at=new_question.created_at,
            )
            return question_response  # Возвращаем первый вопрос в виде QuestionResponse
