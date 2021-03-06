<a name="models.mixins.relation_mixin"></a>
# models.mixins.relation\_mixin

<a name="models.mixins.relation_mixin.RelationMixin"></a>
## RelationMixin Objects

```python
class RelationMixin()
```

Used to return relation fields/names etc. from given model

<a name="models.mixins.relation_mixin.RelationMixin.extract_db_own_fields"></a>
#### extract\_db\_own\_fields

```python
 | @classmethod
 | extract_db_own_fields(cls) -> Set
```

Returns only fields that are stored in the own database table, exclude all
related fields.

**Returns**:

`(Set)`: set of model fields with relation fields excluded

<a name="models.mixins.relation_mixin.RelationMixin.extract_related_fields"></a>
#### extract\_related\_fields

```python
 | @classmethod
 | extract_related_fields(cls) -> List
```

Returns List of ormar Fields for all relations declared on a model.
List is cached in cls._related_fields for quicker access.

**Returns**:

`(List)`: list of related fields

<a name="models.mixins.relation_mixin.RelationMixin.extract_related_names"></a>
#### extract\_related\_names

```python
 | @classmethod
 | extract_related_names(cls) -> Set
```

Returns List of fields names for all relations declared on a model.
List is cached in cls._related_names for quicker access.

**Returns**:

`(List)`: list of related fields names

<a name="models.mixins.relation_mixin.RelationMixin._extract_db_related_names"></a>
#### \_extract\_db\_related\_names

```python
 | @classmethod
 | _extract_db_related_names(cls) -> Set
```

Returns only fields that are stored in the own database table, exclude
related fields that are not stored as foreign keys on given model.

**Returns**:

`(Set)`: set of model fields with non fk relation fields excluded

<a name="models.mixins.relation_mixin.RelationMixin._exclude_related_names_not_required"></a>
#### \_exclude\_related\_names\_not\_required

```python
 | @classmethod
 | _exclude_related_names_not_required(cls, nested: bool = False) -> Set
```

Returns a set of non mandatory related models field names.

For a main model (not nested) only nullable related field names are returned,
for nested models all related models are returned.

**Arguments**:

- `nested (bool)`: flag setting nested models (child of previous one, not main one)

**Returns**:

`(Set)`: set of non mandatory related fields

