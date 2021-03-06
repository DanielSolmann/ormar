# type: ignore
from datetime import date
from typing import List, Optional, Union

import databases
import pytest
import sqlalchemy
from sqlalchemy import create_engine

import ormar
from ormar import ModelDefinitionError
from tests.settings import DATABASE_URL

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


class MainMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Role(ormar.Model):
    class Meta(MainMeta):
        pass

    name: str = ormar.String(primary_key=True, max_length=1000)
    order: int = ormar.Integer(default=0, name="sort_order")
    description: str = ormar.Text()


class Company(ormar.Model):
    class Meta(MainMeta):
        pass

    name: str = ormar.String(primary_key=True, max_length=1000)


class UserRoleCompany(ormar.Model):
    class Meta(MainMeta):
        pass


class User(ormar.Model):
    class Meta(MainMeta):
        pass

    registrationnumber: str = ormar.String(primary_key=True, max_length=1000)
    company: Company = ormar.ForeignKey(Company)
    company2: Company = ormar.ForeignKey(Company, related_name="secondary_users")
    name: str = ormar.Text()
    role: Optional[Role] = ormar.ForeignKey(Role)
    roleforcompanies: Optional[Union[Company, List[Company]]] = ormar.ManyToMany(
        Company, through=UserRoleCompany, related_name="role_users"
    )
    lastupdate: date = ormar.DateTime(server_default=sqlalchemy.func.now())


@pytest.fixture(autouse=True, scope="module")
def create_test_database():
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


def test_wrong_model():
    with pytest.raises(ModelDefinitionError):

        class User(ormar.Model):
            class Meta(MainMeta):
                pass

            registrationnumber: str = ormar.Text(primary_key=True)
            company: Company = ormar.ForeignKey(Company)
            company2: Company = ormar.ForeignKey(Company)


@pytest.mark.asyncio
async def test_create_primary_models():
    async with database:
        await Role.objects.create(
            name="user", order=0, description="no administration right"
        )
        role_1 = await Role.objects.create(
            name="admin", order=1, description="standard administration right"
        )
        await Role.objects.create(
            name="super_admin", order=2, description="super administration right"
        )
        assert await Role.objects.count() == 3

        company_0 = await Company.objects.create(name="Company")
        company_1 = await Company.objects.create(name="Subsidiary Company 1")
        company_2 = await Company.objects.create(name="Subsidiary Company 2")
        company_3 = await Company.objects.create(name="Subsidiary Company 3")
        assert await Company.objects.count() == 4

        user = await User.objects.create(
            registrationnumber="00-00000", company=company_0, name="admin", role=role_1
        )
        assert await User.objects.count() == 1

        await user.delete()
        assert await User.objects.count() == 0

        user = await User.objects.create(
            registrationnumber="00-00000",
            company=company_0,
            company2=company_3,
            name="admin",
            role=role_1,
        )
        await user.roleforcompanies.add(company_1)
        await user.roleforcompanies.add(company_2)

        users = await User.objects.select_related(
            ["company", "company2", "roleforcompanies"]
        ).all()
        assert len(users) == 1
        assert len(users[0].roleforcompanies) == 2
        assert len(users[0].roleforcompanies[0].role_users) == 1
        assert users[0].company.name == "Company"
        assert len(users[0].company.users) == 1
        assert users[0].company2.name == "Subsidiary Company 3"
        assert len(users[0].company2.secondary_users) == 1

        users = await User.objects.select_related("roleforcompanies").all()
        assert len(users) == 1
        assert len(users[0].roleforcompanies) == 2
