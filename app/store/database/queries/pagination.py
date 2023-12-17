from typing import Type

from tortoise import Model


class Paginator:
    @staticmethod
    async def paginate(model: Type[Model], page: int, page_size: int,
                       related=None) -> tuple:
        query = getattr(model, 'all')
        prefetch_related_query = query().prefetch_related
        total_items = await getattr(model, 'all')().count()

        if not related:
            items = await query().limit(
                page_size).offset((page - 1) * page_size)
        else:
            items = await prefetch_related_query(
                related).limit(page_size).offset((page - 1) * page_size)
        
        return  items, total_items
