"""Implements DAG-level traceback."""

from typing import TYPE_CHECKING, Optional

from newclid.predicates import NUMERICAL_PREDICATES, Predicate
from newclid.geometry import Point
from newclid.problem import CONSTRUCTION_RULE
from newclid.statements.statement import Statement
from newclid.dependencies.dependency import Dependency

if TYPE_CHECKING:
    from newclid.proof import Proof


def point_levels(
    setup: list["Dependency"], existing_points: list[Point]
) -> list[tuple[set[Point], list["Dependency"]]]:
    """Reformat setup into levels of point constructions."""
    levels = []
    for con in setup:
        plevel = max([p.plevel for p in con.statement.args if isinstance(p, Point)])

        while len(levels) - 1 < plevel:
            levels.append((set(), []))

        for p in con.statement.args:
            if not isinstance(p, Point):
                continue
            if existing_points and p in existing_points:
                continue

            levels[p.plevel][0].add(p)

        cons = levels[plevel][1]
        cons.append(con)

    return [(p, c) for p, c in levels if p or c]


def point_log(
    setup: list["Dependency"],
    ref_id: dict[tuple[str, ...], int],
    existing_points=list[Point],
) -> list[tuple[list[Point], list["Dependency"]]]:
    """Reformat setup into groups of point constructions."""
    log = []

    levels = point_levels(setup, existing_points)

    for points, cons in levels:
        for con in cons:
            con_hash = con.statement.hash_tuple
            if con_hash not in ref_id:
                ref_id[con_hash] = len(ref_id)

        log.append((points, cons))

    return log


def setup_to_levels(
    setup: list["Dependency"],
) -> list[list["Dependency"]]:
    """Reformat setup into levels of point constructions."""
    levels = []
    for d in setup:
        plevel = max([p.plevel for p in d.statement.args if isinstance(p, Point)])
        while len(levels) - 1 < plevel:
            levels.append([])

        levels[plevel].append(d)

    levels = [lvl for lvl in levels if lvl]
    return levels


def separate_dependency_difference(
    query: "Dependency",
    log: list[tuple[list["Dependency"], list["Dependency"]]],
) -> tuple[
    list[tuple[list["Dependency"], list["Dependency"]]],
    list["Dependency"],
    list["Dependency"],
    set[Point],
    set[Point],
]:
    """Identify and separate the dependency difference."""
    setup: list[Dependency] = []
    log_, log = log, []
    for prems, cons in log_:
        if not prems:
            setup.extend(cons)
            continue
        cons_ = []
        for con in cons:
            if con.reason and con.reason.object is CONSTRUCTION_RULE:
                setup.append(con)
            else:
                cons_.append(con)
        if not cons_:
            continue

        prems = [p for p in prems if p.statement.predicate != Predicate.IND]
        log.append((prems, cons_))

    points = set(query.statement.args)
    queue = list(query.statement.args)
    i = 0
    while i < len(queue):
        q = queue[i]
        i += 1
        if not isinstance(q, Point):
            continue
        for p in q.rely_on:
            if p not in points:
                points.add(p)
                queue.append(p)

    setup_, setup, aux_setup, aux_points = setup, [], [], set()
    for con in setup_:
        if con.statement.predicate is Predicate.IND:
            continue
        elif any([p not in points for p in con.statement.args if isinstance(p, Point)]):
            aux_setup.append(con)
            aux_points.update(
                [
                    p
                    for p in con.statement.args
                    if isinstance(p, Point) and p not in points
                ]
            )
        else:
            setup.append(con)

    return log, setup, aux_setup, points, aux_points


def recursive_traceback(
    query: "Dependency",
) -> list[tuple[list["Dependency"], list["Dependency"]]]:
    """Recursively traceback from the query, i.e. the conclusion."""
    visited = set()
    log = []
    stack = []

    def read(query_dep: "Dependency") -> None:
        query_dep = remove_loop(query_dep)
        hashed = query_dep.statement.hash_tuple
        if hashed in visited:
            return

        if query_dep.statement.predicate in NUMERICAL_PREDICATES:
            return

        nonlocal stack

        stack.append(hashed)
        prems: list["Dependency"] = []

        if (
            not query_dep.reason
            or query_dep.reason.object is not CONSTRUCTION_RULE
            and query_dep.why
        ):
            all_deps: list["Dependency"] = []
            dep_names = set()
            for dep in query_dep.why:
                dep_hash = dep.statement.hash_tuple
                if dep_hash in dep_names:
                    continue
                dep_names.add(dep_hash)
                all_deps.append(dep)

            for dep in all_deps:
                dep_hash = dep.statement.hash_tuple
                if dep_hash not in visited:
                    read(dep)
                if dep_hash in visited:
                    prems.append(dep)

        visited.add(hashed)
        hashs = sorted([d.statement.hash_tuple for d in prems])
        found = False
        for ps, qs in log:
            if sorted([d.statement.hash_tuple for d in ps]) == hashs:
                qs += [query_dep]
                found = True
                break
        if not found:
            log.append((prems, [query_dep]))

        stack.pop(-1)

    read(query)

    # post process log: separate multi-conclusion lines
    log_, log = log, []
    for ps, qs in log_:
        for q in qs:
            log.append((ps, [q]))

    return log


def remove_loop(dependency: "Dependency") -> "Dependency":
    shortcut_found = _find_dependency_shortcut(dependency)
    if shortcut_found:
        return shortcut_found
    return dependency


def _find_dependency_shortcut(dependency: "Dependency") -> Optional["Dependency"]:
    initial_hash_tuple = dependency.statement.hash_tuple
    stack = [dependency]

    while stack:
        current_dep = stack.pop(0)
        if current_dep.why is None:
            continue
        for why_dep in current_dep.why:
            if why_dep.statement.hash_tuple == initial_hash_tuple:
                return why_dep
            stack.append(why_dep)
    return None


def collx_to_coll_setup(
    setup: list["Dependency"],
) -> list["Dependency"]:
    """Convert collx to coll in setups."""
    result = []
    for level in setup_to_levels(setup):
        hashs = set()
        for dep in level:
            if dep.statement.predicate == Predicate.COLLINEAR_X:
                dep.statement.predicate = Predicate.COLLINEAR
                dep.statement.args = list(set(dep.statement.args))

            dep_hash = dep.statement.hash_tuple
            if dep_hash in hashs:
                continue
            hashs.add(dep_hash)
            result.append(dep)

    return result


def collx_to_coll(
    setup: list["Dependency"],
    aux_setup: list["Dependency"],
    log: list[tuple[list["Dependency"], list["Dependency"]]],
) -> tuple[
    list["Dependency"],
    list["Dependency"],
    list[tuple[list["Dependency"], list["Dependency"]]],
]:
    """Convert collx to coll and dedup."""
    setup = collx_to_coll_setup(setup)
    aux_setup = collx_to_coll_setup(aux_setup)

    con_set = set([p.statement.hash_tuple for p in setup + aux_setup])
    log_, log = log, []
    for prems, cons in log_:
        prem_set = set()
        prems_, prems = prems, []
        for p in prems_:
            p = _dep_coll_to_collx(p)
            prem_hash = p.statement.hash_tuple
            if prem_hash in prem_set:
                continue
            prem_set.add(prem_hash)
            prems.append(p)

        cons_, cons = cons, []
        for c in cons_:
            c = _dep_coll_to_collx(c)
            con_hash = c.statement.hash_tuple
            if con_hash in con_set:
                continue
            con_set.add(con_hash)
            cons.append(c)

        if not cons or not prems:
            continue

        log.append((prems, cons))

    return setup, aux_setup, log


def _dep_coll_to_collx(dep: "Dependency"):
    if dep.statement.predicate == Predicate.COLLINEAR_X:
        coll_statement = Statement(Predicate.COLLINEAR, list(set(dep.statement.args)))
        return Dependency(coll_statement, why=dep.why, reason=dep.reason)
    return dep


def get_logs(
    goal: "Statement", proof: "Proof", merge_trivials: bool = False
) -> tuple[
    list["Dependency"],
    list["Dependency"],
    list[tuple[list["Dependency"], list["Dependency"]]],
    set[Point],
]:
    """Given a DAG and conclusion N, return the premise, aux, proof."""
    goal_dep = proof.statements.graph.build_resolved_dependency(goal)
    log = recursive_traceback(goal_dep)
    log, setup, aux_setup, setup_points, _ = separate_dependency_difference(
        goal_dep, log
    )

    setup, aux_setup, log = collx_to_coll(setup, aux_setup, log)

    setup, aux_setup, log = shorten_and_shave(setup, aux_setup, log, merge_trivials)

    return setup, aux_setup, log, setup_points


def shorten_and_shave(
    setup: list["Dependency"],
    aux_setup: list["Dependency"],
    log: list[tuple[list["Dependency"], list["Dependency"]]],
    merge_trivials: bool = False,
) -> tuple[
    list["Dependency"],
    list["Dependency"],
    list[tuple[list["Dependency"], list["Dependency"]]],
]:
    """Shorten the proof by removing unused predicates."""
    log, _ = shorten_proof(log, merge_trivials=merge_trivials)

    all_prems = sum([list(prems) for prems, _ in log], [])
    all_prems = set([p.statement.hash_tuple for p in all_prems])
    setup = [d for d in setup if d.statement.hash_tuple in all_prems]
    aux_setup = [d for d in aux_setup if d.statement.hash_tuple in all_prems]
    return setup, aux_setup, log


def join_prems(
    con: "Dependency",
    con2prems: dict[tuple[str, ...], list["Dependency"]],
    expanded: set[tuple[str, ...]],
) -> list["Dependency"]:
    """Join proof steps with the same premises."""
    con_hash = con.statement.hash_tuple
    if con_hash in expanded or con_hash not in con2prems:
        return [con]

    result = []
    for p in con2prems[con_hash]:
        result += join_prems(p, con2prems, expanded)
    return result


def shorten_proof(
    log: list[tuple[list["Dependency"], list["Dependency"]]],
    merge_trivials: bool = False,
) -> tuple[
    list[tuple[list["Dependency"], list["Dependency"]]],
    dict[tuple[str, ...], list["Dependency"]],
]:
    """Join multiple trivials proof steps into one."""
    pops = set()
    con2prem = {}
    for prems, cons in log:
        assert len(cons) == 1
        con = cons[0]
        if not con.reason:
            con2prem[con.statement.hash_tuple] = prems
        elif not merge_trivials:
            # except for the ones that are premises to non-trivial steps.
            pops.update({p.statement.hash_tuple for p in prems})

    for p in pops:
        if p in con2prem:
            con2prem.pop(p)

    expanded = set()
    log2 = []
    for i, (prems, cons) in enumerate(log):
        con = cons[0]
        con_hash = con.statement.hash_tuple
        if i < len(log) - 1 and con_hash in con2prem:
            continue

        hashs = set()
        new_prems = []

        for p in sum([join_prems(p, con2prem, expanded) for p in prems], []):
            p_hash = p.statement.hash_tuple
            if p_hash not in hashs:
                new_prems.append(p)
                hashs.add(p_hash)

        log2 += [(new_prems, [con])]
        expanded.add(con_hash)

    return log2, con2prem
