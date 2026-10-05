mkdir user-management-api

cd user-management-api

python -m venv venv


venv\Scripts\activate

deactivate

uvicorn main:app --reload
