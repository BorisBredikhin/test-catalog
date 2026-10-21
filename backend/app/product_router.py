from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Product
from app.schemas import Product as ProductSchema
from app.schemas import ProductList

router = APIRouter()


@router.get("", response_model=ProductList)
async def list_products(
    session: Annotated[AsyncSession, Depends(get_session)],
):
    result = await session.scalars(select(Product).order_by(Product.id))
    products = [ProductSchema.model_validate(product) for product in result]
    return {"products": products}
