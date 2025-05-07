from pydantic import BaseModel
from typing import List, Dict

class DependencyRequest(BaseModel):
    file_dependencies: Dict[str, List[str]]

class NodeUpdateRequest(BaseModel):
    status: str
