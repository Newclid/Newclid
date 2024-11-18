from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from newclid.statements.statement import Statement

if TYPE_CHECKING:
    from newclid.dependencies.dependency import Dependency


class DependencyCache:
    def __init__(self):
        self.cache: dict[
            tuple[str, ...], Dependency
        ] = {}  # Statement hash -> Dependency

    def add_dependency(self, statement: Statement, dep: "Dependency"):
        dep_hash = statement.hash_tuple
        if dep_hash in self.cache:
            return
        self.cache[dep_hash] = dep

    def get(self, statement: Statement) -> Optional["Dependency"]:
        return self.cache.get(statement.hash_tuple)

    def get_cached(self, dep: "Dependency") -> Optional["Dependency"]:
        return self.cache.get(dep.statement.hash_tuple)

    def contains(self, statement: Statement) -> Optional["Dependency"]:
        return statement.hash_tuple in self.cache

    def __contains__(self, obj: object):
        if not isinstance(obj, "Dependency"):
            return False
        return self.contains(obj.statement)
