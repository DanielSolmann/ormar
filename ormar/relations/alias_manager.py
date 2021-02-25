import string
import uuid
from random import choices
from typing import Any, Dict, List, TYPE_CHECKING, Type

import sqlalchemy
from sqlalchemy import text

if TYPE_CHECKING:  # pragma: no cover
    from ormar import Model


def get_table_alias() -> str:
    """
    Creates a random string that is used to alias tables in joins.
    It's necessary that each relation has it's own aliases cause you can link
    to the same target tables from multiple fields on one model as well as from
    multiple different models in one join.

    :return: randomly generated alias
    :rtype: str
    """
    alias = "".join(choices(string.ascii_uppercase, k=2)) + uuid.uuid4().hex[:4]
    return alias.lower()


class AliasManager:
    """
    Keep all aliases of relations between different tables.
    One global instance is shared between all models.
    """

    def __init__(self) -> None:
        self._aliases_new: Dict[str, str] = dict()

    def __contains__(self, item: str) -> bool:
        return self._aliases_new.__contains__(item)

    def __getitem__(self, key: str) -> Any:
        return self._aliases_new.__getitem__(key)

    @staticmethod
    def prefixed_columns(
        alias: str, table: sqlalchemy.Table, fields: List = None
    ) -> List[text]:
        """
        Creates a list of aliases sqlalchemy text clauses from
        string alias and sqlalchemy.Table.

        Optional list of fields to include can be passed to extract only those columns.
        List has to have sqlalchemy names of columns (ormar aliases) not the ormar ones.

        :param alias: alias of given table
        :type alias: str
        :param table: table from which fields should be aliased
        :type table: sqlalchemy.Table
        :param fields: fields to include
        :type fields: Optional[List[str]]
        :return: list of sqlalchemy text clauses with "column name as aliased name"
        :rtype: List[text]
        """
        alias = f"{alias}_" if alias else ""
        all_columns = (
            table.columns
            if not fields
            else [col for col in table.columns if col.name in fields]
        )
        return [
            text(f"{alias}{table.name}.{column.name} as {alias}{column.name}")
            for column in all_columns
        ]

    @staticmethod
    def prefixed_table_name(alias: str, name: str) -> text:
        """
        Creates text clause with table name with aliased name.

        :param alias: alias of given table
        :type alias: str
        :param name: table name
        :type name: str
        :return: sqlalchemy text clause as "table_name aliased_name"
        :rtype: sqlalchemy text clause
        """
        return text(f"{name} {alias}_{name}")

    def add_relation_type(
        self, source_model: Type["Model"], relation_name: str, reverse_name: str = None,
    ) -> None:
        """
        Registers the relations defined in ormar models.
        Given the relation it registers also the reverse side of this relation.

        Used by both ForeignKey and ManyToMany relations.

        Each relation is registered as Model name and relation name.
        Each alias registered has to be unique.

        Aliases are used to construct joins to assure proper links between tables.
        That way you can link to the same target tables from multiple fields
        on one model as well as from multiple different models in one join.

        :param source_model: model with relation defined
        :type source_model: source Model
        :param relation_name: name of the relation to define
        :type relation_name: str
        :param reverse_name: name of related_name fo given relation for m2m relations
        :type reverse_name: Optional[str]
        :return: none
        :rtype: None
        """
        parent_key = f"{source_model.get_name()}_{relation_name}"
        if parent_key not in self._aliases_new:
            self.add_alias(parent_key)

        to_field = source_model.Meta.model_fields[relation_name]
        child_model = to_field.to
        child_key = f"{child_model.get_name()}_{reverse_name}"
        if child_key not in self._aliases_new:
            self.add_alias(child_key)

    def add_alias(self, alias_key: str) -> str:
        """
        Adds alias to the dictionary of aliases under given key.

        :param alias_key: key of relation to generate alias for
        :type alias_key: str
        :return: generated alias
        :rtype: str
        """
        alias = get_table_alias()
        self._aliases_new[alias_key] = alias
        return alias

    def resolve_relation_alias(
        self, from_model: Type["Model"], relation_name: str
    ) -> str:
        """
        Given model and relation name returns the alias for this relation.

        :param from_model: model with relation defined
        :type from_model: source Model
        :param relation_name: name of the relation field
        :type relation_name: str
        :return: alias of the relation
        :rtype: str
        """
        alias = self._aliases_new.get(f"{from_model.get_name()}_{relation_name}", "")
        return alias