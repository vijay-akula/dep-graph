import networkx as nx
from sqlalchemy import create_engine, Column, String, Table, MetaData, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio

DATABASE_URL = "sqlite+aiosqlite:///./graph.db"
engine = create_async_engine(DATABASE_URL, echo=True)
metadata = MetaData()

status_table = Table(
    "status_map", metadata,
    Column("node", String, primary_key=True),
    Column("status", String)
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

    # preload base status map
    base_map = {
        "auth_service.py": "pending",
        "auth_repo.py": "done",
        "db_connector.py": "done",
        "payment_service.py": "pending",
        "payment_repo.py": "pending",
        "order_service.py": "pending",
        "order_repo.py": "pending",
        "main.py": "pending"
    }
    async with AsyncSession(engine) as session:
        for k, v in base_map.items():
            stmt = select(status_table).where(status_table.c.node == k)
            result = await session.execute(stmt)
            if result.scalar() is None:
                await session.execute(status_table.insert().values(node=k, status=v))
        await session.commit()

SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

STATUS_COLORS = {
    "done": "#a0d911",
    "pending": "#faad14",
    "eligible": "#1890ff",
    "default": "#d9d9d9"
}

def build_graph(file_dependencies):
    G = nx.DiGraph()
    for file, deps in file_dependencies.items():
        for dep in deps:
            G.add_edge(dep, file)
        if not deps:
            G.add_node(file)
    return G

async def get_status_map():
    async with SessionLocal() as session:
        result = await session.execute(select(status_table))
        return {row.node: row.status for row in result.fetchall()}

async def update_node_status(node, status):
    async with SessionLocal() as session:
        await session.execute(
            status_table.update().where(status_table.c.node == node).values(status=status)
        )
        await session.commit()

async def get_next_file_to_convert(G):
    status_map = await get_status_map()
    return [n for n in G.nodes if G.in_degree(n) == 0 and status_map.get(n) != "done"]