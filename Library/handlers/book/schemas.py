from pydantic import BaseModel, conint, ConfigDict
from typing import List, Any

from config import MIN_DATA, MAX_DATA


class TunedModel(BaseModel):
    class Config:
        """tells pydantic to convert even non dict obj to json"""
        allow_population_by_field_name = True
        orm_mode = True


class CreateBook(TunedModel):
    title: str
    publication_year: conint(le=MAX_DATA, ge=MIN_DATA)
    genre: List[str]
    author: str | None = None
    description: str | None = None
    cover_image: str | None = None
    price: int | None = 0

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Example Book",
                "publication_year": 2022,
                "genre": ["fiction", "mystery"],
                "author": "John Doe",
                "description": "An example book description.",
                "cover_image": "https://example.com/cover-image.jpg"
            }
        }

    def json(self, **kwargs):
        return {
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
        }


class UpdateBook(TunedModel):
    """ class for patch update"""
    title: str | None = None
    publication_year: conint(le=MAX_DATA, ge=MIN_DATA) | None = None
    genre: List[str] | None = None
    price: int | None = None
    author: str | None = None
    description: str | None = None
    cover_image: str | None = None


class ShowBook(CreateBook):
    id: int


class DeleteBook(TunedModel):
    id: int


class SearchBook(DeleteBook):
    pass


class Book(CreateBook):
    id: int

    class Config:
        model_config = ConfigDict(from_attributes=True)
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Example Book",
                "publication_year": 2022,
                "genre": ["fiction", "mystery"],
                "author": "John Doe",
                "description": "An example book description.",
                "cover_image": "https://example.com/cover-image.jpg"
            }
        }


class ValidBook(CreateBook):

    def json(self, **kwargs):
        return {
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
            'error': self.error
        }


class InvalidBook(CreateBook):
    title: Any
    genre: Any
    author: Any
    description: Any
    price: Any
    publication_year: Any
    cover_image: Any
    error: Any

    def json(self, **kwargs):
        return {
            'title': self.title,
            'publication_year': self.publication_year,
            'genre': self.genre,
            'author': self.author,
            'description': self.description,
            'cover_image': self.cover_image,
            'price': self.price,
            'error': self.error
        }