from typing import Annotated

from pydantic import UUID4, AnyHttpUrl, BaseModel, ConfigDict, Field


class Product(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: Annotated[str, Field(..., description="Название товара")]
    photo_url: AnyHttpUrl


class ProductList(BaseModel):
    products: list[Product]
