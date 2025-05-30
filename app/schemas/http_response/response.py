from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class ResponseMetaSchema(BaseModel):
    """ Схема метаданных ответа API """

    total: Optional[int] = Field(
        default=None,
        description="Общее количество записей",
    )
    page: Optional[int] = Field(
        default=None,
        description="Текущая страница",
    )
    per_page: Optional[int] = Field(
        default=None,
        description="Количество записей на странице",
    )
    total_pages: Optional[int] = Field(
        default=None,
        description="Общее количество страниц",
    )


class ResponseLinksSchema(BaseModel):
    """ Схема ссылок для навигации """

    self: Optional[str] = Field(
        default=None,
        description="Ссылка на текущую страницу",
    )
    first: Optional[str] = Field(
        default=None,
        description="Ссылка на первую страницу",
    )
    prev: Optional[str] = Field(
        default=None,
        description="Ссылка на предыдущую страницу",
    )
    next: Optional[str] = Field(
        default=None,
        description="Ссылка на следующую страницу",
    )
    last: Optional[str] = Field(
        default=None,
        description="Ссылка на последнюю страницу",
    )


class ResponseSchema(BaseModel):
    """ Схема ответа API """

    data: Optional[Any] = Field(
        default=None,
        description="Данные ответа",
    )
    meta: Optional[ResponseMetaSchema] = Field(
        default=None,
        description="Метаданные пагинации",
    )
    links: Optional[ResponseLinksSchema] = Field(
        default=None,
        description="Ссылки для навигации",
    )


class ErrorResponseSchema(BaseModel):
    """ Схема ответа с ошибкой """

    error: str = Field(
        default=...,
        description="Тип ошибки",
    )
    message: str = Field(
        default=...,
        description="Сообщение об ошибке",
    )
    details: Optional[str] = Field(
        default=None,
        description="Дополнительные детали ошибки",
    )
    status_code: int = Field(
        default=...,
        description="HTTP статус код",
    )