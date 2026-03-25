from src.tasks.dtos import TaskSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from src.tasks.models import TaskModel
from fastapi import HTTPException

def create_task(body: TaskSchema, db: Session):
    try:
        new_task = TaskModel(**body.model_dump())

        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task
    
    except SQLAlchemyError as e:
        db.rollback()
        return {
            "success": False,
            "message": "Failed to create task",
            "error": str(e)
        }
    

def get_tasks(db: Session):
    try:
        tasks = db.query(TaskModel).all()

        return tasks
    
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch tasks"
        )
    

def get_task_by_id(task_id: int, db: Session):
    try:
        task = db.get(TaskModel, task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        return task
    except HTTPException:
        raise

    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to fetch task")


def update_task(body: TaskSchema, task_id: int, db: Session):
    try:
        task = db.get(TaskModel, task_id)

        # Not found
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    
        # Update field dynamically
        for key, value in body.model_dump().items():
            setattr(task, key, value)

        db.commit()
        db.refresh(task)

        return task
    
    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update task")
    
def delete_task(task_id: int, db: Session):
    try:
        task = db.get(TaskModel, task_id)

        # Not found
        if not task:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        
        db.delete(task)
        db.commit()

        return None
    
    except HTTPException:
        raise

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete task")