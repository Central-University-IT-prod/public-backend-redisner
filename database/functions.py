import datetime
from typing import List

from async_lru import alru_cache
from sqlalchemy import update, func
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from config import config
from database.models import Base, UserTravel, Travel, Location, User


@alru_cache()
async def get_session_maker():
    user = config.POSTGRES_USER.get_secret_value()
    password = config.POSTGRES_PASSWORD.get_secret_value()
    host = config.POSTGRES_HOST.get_secret_value()
    port = config.POSTGRES_PORT
    database = config.POSTGRES_DB.get_secret_value()

    database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

    engine = create_async_engine(database_url,
                                 pool_size=20, max_overflow=-1)

    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    return async_sessionmaker(bind=engine, autocommit=False, autoflush=True, expire_on_commit=False)


async def get_data(model: Base, condition: bool = True, session: AsyncSession = None):
    query = select(model).where(condition)

    if session is None:
        async_session = await get_session_maker()

        session = async_session()

    result = await session.execute(query)

    return result.scalars()


async def update_data(model: Base,
                      condition: bool,
                      update_values: dict,
                      session: AsyncSession = None):
    if session is None:
        async_session = await get_session_maker()

        session = async_session()

    async with session.begin():
        query = (
            update(model)
            .where(condition)
            .values(**update_values)
        )

        await session.execute(query)

    await session.commit()


async def add_data(model: Base,
                   check_condition: bool,
                   session: AsyncSession = None, **kwargs):
    if session is None:
        async_session = await get_session_maker()

        session = async_session()

    instance = await get_data(model, condition=check_condition, session=session)

    if instance.first() is None:
        instance = model(**kwargs)
        session.add(instance)

        await session.commit()

    return instance


async def delete_data(model: Base,
                      check_condition: bool,
                      session: AsyncSession = None, **kwargs) -> None:
    if session is None:
        async_session = await get_session_maker()

        session = async_session()

    instance = (await session.scalars(select(model).where(check_condition))).first()

    if instance is not None:
        await session.delete(instance)

        await session.commit()


async def create_travel_with_locations(creator_id: int,
                                       travel_name: str,
                                       description: str | None,
                                       locations: List[dict],
                                       start_date: str,
                                       end_date: str) -> str:
    async_session = await get_session_maker()

    async with async_session() as session:
        async with session.begin():
            new_travel = Travel(
                name=travel_name,
                description=description,
                creator_id=creator_id
            )

            session.add(new_travel)

            await session.flush()

            await session.refresh(new_travel)

            start_date = datetime.datetime.strptime(start_date, '%d.%m.%Y').date()
            end_date = datetime.datetime.strptime(end_date, '%d.%m.%Y').date()

            first_location = Location(
                travel_id=new_travel.id,
                longitude=locations[0]["longitude"],
                latitude=locations[0]["latitude"],
                country=locations[0]["country"],
                city=locations[0]["city"],
                start_date=start_date,
                end_date=start_date
            )

            session.add(first_location)

            last_location = Location(
                travel_id=new_travel.id,
                longitude=locations[1]["longitude"],
                latitude=locations[1]["latitude"],
                country=locations[1]["country"],
                city=locations[1]["city"],
                start_date=start_date,
                end_date=end_date
            )

            session.add(last_location)

            new_user_travel = UserTravel(
                user_id=creator_id,
                travel_id=new_travel.id,
            )

            session.add(new_user_travel)

            await session.commit()

            return new_travel.id


async def get_travels(user_id: int,
                      travel_id: str = None) -> List[dict]:
    async_session = await get_session_maker()

    async with async_session() as session:
        async with session.begin():
            query = (select(Travel)
                     .options(joinedload(Travel.locations), joinedload(Travel.participants))
                     .where(Travel.participants.any(id=user_id)))

            if travel_id:
                query = query.where(Travel.id == travel_id)

            result = await session.execute(query)

            travels = result.scalars().unique()

    travels_info = []

    for travel in travels:
        travel_data = {
            "id": travel.id,
            "name": travel.name,
            "description": travel.description,
            "creator_id": travel.creator_id,
            "locations": [
                {
                    "id": location.id,
                    "country": location.country,
                    "city": location.city,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "start_date": location.start_date,
                    "end_date": location.end_date
                } for location in travel.locations
            ],
            "participants": [
                {
                    "user_id": participant.id,
                    "age": participant.age,
                    "country": participant.country,
                    "city": participant.city,
                    "longitude": participant.longitude,
                    "latitude": participant.latitude,
                    "bio": participant.bio
                }
                for participant in travel.participants
            ]
        }

        travels_info.append(travel_data)

    return travels_info


async def find_matching_users(user_id: int):
    async_session = await get_session_maker()

    async with async_session() as session:
        async with session.begin():
            pre_result = await session.execute(select(User.interests, User.age)
                                               .where(User.id == user_id))

            user = pre_result.first()

            matching_users_query = (
                select(User)
                .where(User.id != user_id)
                .where(User.interests.op('&&')(array(user.interests)))
                .where(func.abs(User.age - user.age) <= 5)
            )

            result = await session.execute(matching_users_query)
            matching_users = result.scalars().all()

            return matching_users
