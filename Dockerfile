# Используем официальный образ Python
FROM python:3.8-slim

# Установим рабочую директорию
WORKDIR /app

# Скопируем зависимости и установим их
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Скопируем все остальное
COPY . .

# Запустим приложение с помощью uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



