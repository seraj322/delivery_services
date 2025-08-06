from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Приложение для заметок и отзывов",
    description="API для управления заметками и обработки отзывов пользователей",
    version="1.0.0"
)

# ==================== Модели данных ====================
class NoteCreate(BaseModel):
    text: str

class NoteUpdate(BaseModel):
    text: str

class NoteInDB(BaseModel):
    id: int
    text: str

class Feedback(BaseModel):
    name: str
    message: str

# ==================== Хранилища данных ====================
notes_db: List[NoteInDB] = []
feedback_db: List[Feedback] = []

# ==================== Репозитории ====================
class NoteRepository:
    @staticmethod
    async def create(note_data: NoteCreate) -> NoteInDB:
        new_note = NoteInDB(id=len(notes_db) + 1, text=note_data.text)
        notes_db.append(new_note)
        return new_note

    @staticmethod
    async def get_by_id(note_id: int) -> Optional[NoteInDB]:
        return next((note for note in notes_db if note.id == note_id), None)

    @staticmethod
    async def delete(note_id: int) -> None:
        global notes_db
        notes_db = [note for note in notes_db if note.id != note_id]

class FeedbackRepository:
    @staticmethod
    async def save_feedback(feedback: Feedback) -> Feedback:
        feedback_db.append(feedback)
        return feedback

    @staticmethod
    async def get_all_feedbacks() -> List[Feedback]:
        return feedback_db

# ==================== Сервисы ====================
class NoteService:
    @staticmethod
    async def create_note(note_data: NoteCreate):
        if len(note_data.text) > 1000:
            raise ValueError("Заметка слишком длинная!")
        return await NoteRepository.create(note_data)

    @staticmethod
    async def get_note(note_id: int):
        return await NoteRepository.get_by_id(note_id)

    @staticmethod
    async def delete_note(note_id: int):
        note = await NoteRepository.get_by_id(note_id)
        if not note:
            raise ValueError("Заметка не найдена")
        await NoteRepository.delete(note_id)

class FeedbackService:
    @staticmethod
    async def process_feedback(feedback: Feedback) -> dict:
        if len(feedback.message) > 1000:
            raise ValueError("Сообщение слишком длинное!")

        await FeedbackRepository.save_feedback(feedback)
        return {"message": f"Отзыв получен. Спасибо, {feedback.name}."}

# ==================== Роутеры ====================
@app.post("/notes/",
          summary="Создать новую заметку",
          description="Создает новую заметку с указанным текстом")
async def create_note(note_data: NoteCreate):
    return await NoteService.create_note(note_data)

@app.get("/notes/{note_id}",
         summary="Получить заметку",
         description="Возвращает заметку по указанному ID")
async def get_note(note_id: int):
    note = await NoteService.get_note(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Заметка не найдена")
    return note

@app.delete("/notes/{note_id}",
            summary="Удалить заметку",
            description="Удаляет заметку по указанному ID")
async def delete_note(note_id: int):
    await NoteService.delete_note(note_id)
    return {"message": "Заметка удалена"}

@app.post("/feedback/",
          summary="Отправить отзыв",
          description="Принимает отзыв от пользователя")
async def submit_feedback(feedback: Feedback):
    return await FeedbackService.process_feedback(feedback)

@app.get("/feedback/",
         summary="Получить все отзывы",
         description="Возвращает список всех полученных отзывов")
async def get_all_feedbacks():
    return await FeedbackRepository.get_all_feedbacks()

@app.get("/",
         summary="Главная страница",
         description="Основная информация о приложении")
async def root():
    return {"message": "Приложение для заметок и отзывов"}

# ==================== Запуск приложения ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)