from pydantic import BaseModel

class TaskSchema(BaseModel):
    title: str
    description: str
    is_completed: bool = False

class TaskResponseSchema(BaseModel):
    id: int
    user_id: int | None = 0
    title: str
    description: str
    is_completed: bool