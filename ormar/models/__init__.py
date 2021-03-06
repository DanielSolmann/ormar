"""
Definition of Model, it's parents NewBaseModel and mixins used by models.
Also defines a Metaclass that handles all constructions and relations registration,
ass well as vast number of helper functions for pydantic, sqlalchemy and relations.
"""

from ormar.models.newbasemodel import NewBaseModel  # noqa I100
from ormar.models.model import Model  # noqa I100

__all__ = ["NewBaseModel", "Model"]
