"""
Этот файл — как книга жалоб и предложений для нашего приложения.
Здесь мы говорим программе, что делать, если что-то пойдет не так.
"""
import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

# Это как диктофон для записи проблем
logger = logging.getLogger(__name__)

def setup_exception_handlers(app: FastAPI) -> None:
    """
    Вешаем таблички "Куда бежать, если...":
    - если сломалось вообще всё
    - если неправильно заполнили форму
    - если проблемы с базой данных
    - если страница не найдена
    """

    # Если случилась непредвиденная ошибка
    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(f"Произошла ошибка: {exc}", exc_info=True, extra={
            "path": request.url.path,
            "method": request.method,
        })

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Ошибка сервера",
                "message": "Что-то пошло не так. Попробуйте позже.",
            }
        )

    # Если пользователь неправильно заполнил форму
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        logger.warning(f"Ошибка в форме: {exc.errors()}", extra={
            "path": request.url.path,
            "method": request.method,
        })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Ошибка в данных",
                "errors": exc.errors(),
            }
        )

    # Если проблемы с базой данных
    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        logger.error(f"Проблема с базой данных: {exc}", exc_info=True, extra={
            "path": request.url.path,
            "method": request.method,
        })

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Ошибка базы данных",
                "message": "Проблема с хранением данных. Попробуйте позже.",
            }
        )

    # Если страница не найдена (ошибка 404)
    @app.exception_handler(404)
    async def not_found_exception_handler(request: Request, exc: Any) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": "Не найдено",
                "message": f"Страница {request.url.path} не существует.",
            }
        )
