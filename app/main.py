from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List

from database import engine, get_db, check_database_connection, Base
import models
import schemas

@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_database_connection()
    
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Раскомментируйте для сброса БД
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Financial Tracker API"}


@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database connection failed: {str(e)}"
        )


@app.post("/users/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли пользователь с таким email
    existing_user = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создаем нового пользователя
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=f"hashed_{user.password}"  # Заглушка, нужно реализовать хеширование
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@app.get("/users/", response_model=List[schemas.UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    return users


@app.get("/currencies/", response_model=List[schemas.CurrencyResponse])
async def get_currencies(db : AsyncSession = Depends(get_db)) -> List:
    result = await db.execute(select(models.Currency))
    curs = result.scalars().all()
    return curs
