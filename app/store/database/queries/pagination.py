from typing import List, Optional, Tuple, Type

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


class PaginatorRepo:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def paginate(self,
                       model: Type,
                       page: int,
                       page_size: int,
                       related: Optional[List[str]] = None) -> Tuple[
        List, int]:
        query = select(model)
        
        if related:
            for rel in related:
                query = query.options(joinedload(rel))
        
        total_items = await self.session.scalar(select(func.count()).select_from(model))
        
        result = await self.session.execute(query.limit(page_size).offset((page - 1) * page_size))
        items = result.scalars().all()
        
        return items, total_items
