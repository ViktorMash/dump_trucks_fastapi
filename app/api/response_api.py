import math
from typing import Optional, Any, Dict
from fastapi import status, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.schemas.http_response import (
    ResponseSchema, ResponseMetaSchema, ResponseLinksSchema, ErrorResponseSchema
)


class ApiResponse:
    """ Класс для JSON-ответов API """

    @classmethod
    def success(
            cls, *,
            data: Optional[Any] = None,
            total: Optional[int] = None,
            page: Optional[int] = None,
            per_page: Optional[int] = None,
            request: Optional[Request] = None,
            status_code: int = status.HTTP_200_OK,
    ) -> JSONResponse:
        """ Успешный ответ """

        # Вычисляем метаданные пагинации
        meta = None
        links = None

        if total is not None and per_page is not None and page is not None:
            total_pages = math.ceil(total / per_page) if per_page > 0 else 1

            meta = ResponseMetaSchema(
                total=total,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
            )

            # Генерируем ссылки для навигации
            if request:
                links = cls._generate_links(request, page, total_pages, per_page)

        prepared_data = cls._prepare_data(data) if data is not None else None

        response_obj = ResponseSchema(
            data=prepared_data,
            meta=meta,
            links=links
        )

        return JSONResponse(
            content=jsonable_encoder(response_obj.model_dump(exclude_none=True)),
            status_code=status_code,
        )

    @classmethod
    def error(
            cls, *,
            error: str,
            message: str,
            details: Optional[str] = None,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            headers: Optional[Dict[str, str]] = None,
    ) -> JSONResponse:
        """ Ответ с ошибкой """

        error_obj = ErrorResponseSchema(
            error=error,
            message=message,
            details=details,
            status_code=status_code,
        )

        return JSONResponse(
            content=jsonable_encoder(error_obj.model_dump(exclude_none=True)),
            status_code=status_code,
            headers=headers,
        )

    @classmethod
    def _generate_links(
            cls,
            request: Request,
            current_page: int,
            total_pages: int,
            per_page: int
    ) -> ResponseLinksSchema:
        """ Генерация ссылок для навигации """

        base_url = str(request.url).split('?')[0]
        query_params = dict(request.query_params)

        def build_url(page_num: int) -> str:
            query_params['page'] = str(page_num)
            query_params['per_page'] = str(per_page)
            query_string = '&'.join([f"{k}={v}" for k, v in query_params.items()])
            return f"{base_url}?{query_string}"

        links = ResponseLinksSchema(
            self=build_url(current_page),
            first=build_url(1) if total_pages > 0 else None,
            last=build_url(total_pages) if total_pages > 0 else None,
        )

        if current_page > 1:
            links.prev = build_url(current_page - 1)

        if current_page < total_pages:
            links.next = build_url(current_page + 1)

        return links

    @classmethod
    def _prepare_data(cls, data: Any) -> Any:
        """ Подготовка данных для сериализации """
        if data is None:
            return None

        # ORM-объект
        if hasattr(data, "__table__") and hasattr(data, "__dict__"):
            result = {}

            for column in data.__table__.columns:
                try:
                    # Проверяем, загружен ли атрибут
                    if column.name in data.__dict__:
                        result[column.name] = getattr(data, column.name, None)
                except Exception:
                    # Пропускаем атрибуты, которые не могут быть загружены
                    continue

            # Добавляем вычисляемые параметры для DumpTruck
            try:
                if hasattr(data, 'load_percentage'):
                    result['load_percentage'] = data.load_percentage
            except Exception:
                pass

            try:
                if hasattr(data, 'overload_percentage'):
                    result['overload_percentage'] = data.overload_percentage
            except Exception:
                pass

            try:
                if hasattr(data, 'is_overloaded'):
                    result['is_overloaded'] = data.is_overloaded
            except Exception:
                pass

            # Добавляем связанные объекты
            try:
                if hasattr(data, 'model') and 'model' in data.__dict__ and data.model:
                    result['model'] = cls._prepare_data(data.model)
            except Exception:
                # Если model не загружен, пропускаем
                pass

            return result

        # словарь
        if isinstance(data, dict):
            return {k: cls._prepare_data(v) for k, v in data.items()}

        # список / кортеж / сет
        if isinstance(data, (list, tuple, set)):
            return [cls._prepare_data(item) for item in data]

        # остальное возвращаем как есть
        return data


api_response = ApiResponse()