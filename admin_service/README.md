# Chatty
 Социальная сеть «Chatty» — учебная платформа, предназначенная для обмена контентом между  пользователями, общения и получения персонализированных рекомендаций. Платформа позволяет  пользователям создавать собственные посты, делиться изображениями, ставить лайки и  комментировать публикации других участников.


1. Create virtual environment "python -m venv .venv"
2. load virtual environment ".venv\Scripts\activate"
3. load necessary libraries "pip install -r requirements.txt"
4. Apply 'alembic revision --autogenerate -m "*****.py"'
5.   Apply migration "alembic upgrade head" 
6.  Start the server "uvicorn main:app --reload"

7. Configure Docker-Compose to run subscription_service "docker-compose up -d --build"

8. 
