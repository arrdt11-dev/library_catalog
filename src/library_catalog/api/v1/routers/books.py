"""
Роутер для работы с книгами.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ....api.deps import get_book_service
from ....domain.schemas.book import BookCreate, BookUpdate, BookResponse
from ....domain.services.book_service import BookService

router = APIRouter()


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_create: BookCreate,
    book_service: BookService = Depends(get_book_service),
):
    """
    Создать новую книгу.
    """
    try:
        book = await book_service.create_book(book_create)
        return book
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create book: {str(e)}"
        )


@router.get("/", response_model=List[BookResponse])
async def list_books(
    skip: int = 0,
    limit: int = 100,
    book_service: BookService = Depends(get_book_service),
):
    """
    Получить список книг с пагинацией.
    """
    try:
        books = await book_service.get_books(skip=skip, limit=limit)
        return books
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch books: {str(e)}"
        )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    book_service: BookService = Depends(get_book_service),
):
    """
    Получить книгу по ID.
    """
    try:
        book = await book_service.get_book_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch book: {str(e)}"
        )


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_update: BookUpdate,
    book_service: BookService = Depends(get_book_service),
):
    """
    Обновить книгу по ID.
    """
    try:
        book = await book_service.update_book(book_id, book_update)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update book: {str(e)}"
        )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    book_service: BookService = Depends(get_book_service),
):
    """
    Удалить книгу по ID.
    """
    try:
        deleted = await book_service.delete_book(book_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete book: {str(e)}"
        )
