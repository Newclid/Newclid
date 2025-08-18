from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, cast

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from newclid.animation.artists_in_animation import init_point_name_to_artist
from newclid.animation.clause import ClauseArtists, init_clauses_to_draw
from newclid.animation.goal import init_goals_to_draw
from newclid.animation.justifications import init_justifications_to_draw
from newclid.animation.text_animation import TextAnimation
from newclid.draw.figure import init_figure
from newclid.draw.theme import DrawTheme
from newclid.jgex.clause import JGEXClause
from newclid.jgex.formulation import JGEXFormulation
from newclid.justifications._index import JustificationType
from newclid.predicate_types import PredicateArgument
from newclid.proof_data import ProofData
from newclid.symbols.symbols_registry import SymbolsRegistry


class ProofAnimationParts(Enum):
    SHOWCASE = "Showcase of the final figure"
    CONSTRUCTION = "Construction of the initial figure"
    PROOF = "Proof"
    GOAL = "Summary of proven goals"


class ProofAnimation:
    def __init__(
        self,
        proof_data: ProofData,
        symbols: SymbolsRegistry,
        theme: DrawTheme,
        jgex_problem: JGEXFormulation | None = None,
        figure_kwargs: dict[str, Any] | None = None,
    ):
        self.jgex_problem = jgex_problem
        self.symbols = symbols
        self.theme = theme

        figure_kwargs = figure_kwargs or {"figsize": (24, 12), "dpi": 80}
        self.fig, axes = cast(
            tuple[Figure, dict[str, Axes]],
            plt.subplot_mosaic(  # pyright: ignore
                [
                    ["figure", "figure", "text", "text"],
                    ["figure", "figure", "text", "text"],
                ],
                **figure_kwargs,
            ),
        )

        self.figure_ax = axes["figure"]
        self.text_ax = axes["text"]

        init_figure(self.figure_ax, list(self.symbols.points))

        self.aux_point_names: set[PredicateArgument] = set()
        if self.jgex_problem is not None:
            self.aux_point_names = set(
                pname
                for clause in self.jgex_problem.auxiliary_clauses
                for pname in clause.points
            )

        self.point_name_to_artist = init_point_name_to_artist(
            ax=self.figure_ax,
            color_theme=self.theme,
            aux_point_names=self.aux_point_names,
            symbols=self.symbols,
        )

        self.goals_artists = init_goals_to_draw(
            ax=self.figure_ax,
            proven_goals=proof_data.proven_goals,
            point_name_to_artist=self.point_name_to_artist,
            symbols=self.symbols,
            theme=self.theme,
        )

        self.artists_by_clause: dict[JGEXClause, ClauseArtists] = {}
        self.clauses_to_draw: list[JGEXClause] = []
        if self.jgex_problem is not None:
            self.artists_by_clause = init_clauses_to_draw(
                ax=self.figure_ax,
                jgex_problem=self.jgex_problem,
                point_name_to_artist=self.point_name_to_artist,
                symbols=self.symbols,
                theme=self.theme,
            )
            self.clauses_to_draw = list(self.artists_by_clause.keys())

        (self.justifications_to_draw, self.justification_artists) = (
            init_justifications_to_draw(
                ax=self.figure_ax,
                point_name_to_artist=self.point_name_to_artist,
                symbols=self.symbols,
                proof_data=proof_data,
                theme=self.theme,
            )
        )

        text_lines: list[str] = [ProofAnimationParts.SHOWCASE.value]
        if self.jgex_problem is not None:
            text_lines.extend(
                [ProofAnimationParts.CONSTRUCTION.value]
                + [str(clause) for clause in self.clauses_to_draw]
            )

        text_lines.extend(
            [ProofAnimationParts.PROOF.value]
            + [
                justification_to_draw.text
                for justification_to_draw in self.justifications_to_draw
            ]
        )
        text_lines.extend([ProofAnimationParts.GOAL.value])

        self.text_animation = TextAnimation(
            self.text_ax,
            text_lines,
            theme=self.theme,
            n_lines_shown=21,
            fontsize=18,
        )
        self.text_animation.init()

        self.current_part = ProofAnimationParts.SHOWCASE
        self._has_done_showcase_transition: bool = False
        self._has_done_construction_transition: bool = False
        self._has_done_proof_transition: bool = False

        problem_name = (
            self.jgex_problem.name if self.jgex_problem is not None else "Problem"
        )
        plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
        self.fig.suptitle(  # pyright: ignore
            f"Newclid solution for {problem_name} | Goals: {', '.join(str(goal_in_proof.predicate) for goal_in_proof in proof_data.proven_goals)}",
            fontsize=30,
            # fontweight="bold",
            color=self.theme.title_color,
            family=["DejaVu Sans", "STIXGeneral"],
        )
        self.title = self.figure_ax.text(  # pyright: ignore
            0.01,
            0.01,
            self.current_part.value,
            transform=self.figure_ax.transAxes,
            fontsize=22,
            fontweight="bold",
            ha="left",
            va="bottom",
            color=self.theme.title_color,
            family=["DejaVu Sans", "STIXGeneral"],
        )

    def animate(self) -> FuncAnimation:
        return FuncAnimation(
            self.fig,
            self._next_step,
            init_func=self._init,
            frames=len(self.text_animation.proof_lines) + 1,
            interval=400,
            blit=True,
        )

    def _init(self) -> Iterable[Artist]:
        self.current_part = ProofAnimationParts.SHOWCASE
        return set()

    def _next_step(self, frame: int) -> Iterable[Artist]:
        match self.current_part:
            case ProofAnimationParts.SHOWCASE:
                return self._showcase(frame)
            case ProofAnimationParts.CONSTRUCTION:
                return self._construction(frame)
            case ProofAnimationParts.PROOF:
                return self._proof(frame)
            case ProofAnimationParts.GOAL:
                return self._goals(frame)

    def _showcase(self, frame: int) -> set[Artist]:
        if self._has_done_showcase_transition:
            return set()

        updated_artists: set[Artist] = set()
        updated_artists.update(self.text_animation.update(frame))
        updated_artists.update(self._hide_all_rule_applications())
        updated_artists.update(self._hide_all_extra_applications())
        updated_artists.update(self._hide_goals())
        self._has_done_showcase_transition = True
        if self.jgex_problem is not None:
            self.current_part = ProofAnimationParts.CONSTRUCTION
        else:
            self.current_part = ProofAnimationParts.PROOF
        return updated_artists

    def _construction(self, frame: int) -> set[Artist]:
        updated_artists: set[Artist] = set()
        if not self._has_done_construction_transition:
            self.title.set_text(ProofAnimationParts.CONSTRUCTION.value)
            updated_artists.add(self.title)
            updated_artists.update(self.text_animation.update(frame))
            for _pname, point_artists in self.point_name_to_artist.items():
                updated_artists.update(point_artists.hide())
            for clause, clause_artists in self.artists_by_clause.items():
                updated_artists.update(clause_artists.hide())

            self._has_done_construction_transition = True
            return updated_artists

        if not self.clauses_to_draw:
            raise ValueError("Should have done transition to proof")
        clause = self.clauses_to_draw.pop(0)
        if not self.clauses_to_draw:
            self.current_part = ProofAnimationParts.PROOF

        for other_clause, other_clause_artists in self.artists_by_clause.items():
            if other_clause == clause:
                continue
            updated_artists.update(other_clause_artists.gray_out())

        updated_artists.update(self.text_animation.update(frame))
        clause_artists = self.artists_by_clause[clause]
        if self.jgex_problem is None:
            raise ValueError("Should have a jgex problem to draw construction")

        is_aux = clause in self.jgex_problem.auxiliary_clauses
        highlight_color = (
            self.theme.aux_point_color if is_aux else self.theme.construction_color
        )
        new_point_color = self.theme.new_point_color
        updated_artists.update(
            clause_artists.manifest(
                aux_point_names=self.aux_point_names,
                highlight_color=highlight_color,
                new_point_color=new_point_color,
            )
        )
        return updated_artists

    def _proof(self, frame: int) -> set[Artist]:
        updated_artists: set[Artist] = set()
        if not self._has_done_proof_transition:
            self.title.set_text(ProofAnimationParts.PROOF.value)
            updated_artists.add(self.title)
            updated_artists.update(self.text_animation.update(frame))
            updated_artists.update(self._gray_out_all_constructions())
            updated_artists.update(self._highlight_goals())
            self._has_done_proof_transition = True
            return updated_artists

        if not self.justifications_to_draw:
            raise ValueError("Should have done transition to goals")

        updated_artists.update(self._gray_out_all_constructions())
        updated_artists.update(self._gray_out_all_rule_applications())
        updated_artists.update(self._hide_goals())
        updated_artists.update(self._hide_all_extra_applications())

        next_justification = self.justifications_to_draw.pop(0)
        if not self.justifications_to_draw:
            self.current_part = ProofAnimationParts.GOAL

        self.text_animation.update(frame)
        justification_artists = self.justification_artists[
            next_justification.justification
        ]
        updated_artists.update(
            justification_artists.highlight(aux_point_names=self.aux_point_names)
        )
        return updated_artists

    def _goals(self, frame: int) -> set[Artist]:
        updated_artists: set[Artist] = set()
        updated_artists.update(self._gray_out_all_constructions())
        updated_artists.update(self._gray_out_all_rule_applications())
        updated_artists.update(self._hide_all_extra_applications())
        updated_artists.update(self.text_animation.update(frame))
        updated_artists.update(self._highlight_goals())
        return updated_artists

    def _gray_out_all_constructions(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for clause_artists in self.artists_by_clause.values():
            updated_artists.update(clause_artists.gray_out())
        return updated_artists

    def _gray_out_all_rule_applications(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for _, rule_application in self.justification_artists.items():
            if (
                rule_application.justification.dependency_type
                == JustificationType.RULE_APPLICATION
            ):
                updated_artists.update(rule_application.gray_out())
        return updated_artists

    def _hide_goals(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for _, goal_artists in self.goals_artists.items():
            updated_artists.update(goal_artists.hide())
        return updated_artists

    def _highlight_goals(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for _, goal_artists in self.goals_artists.items():
            updated_artists.update(
                goal_artists.highlight(
                    aux_point_names=self.aux_point_names,
                    highlight_color=self.theme.goal_color,
                )
            )
        return updated_artists

    def _hide_all_rule_applications(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for _, rule_application in self.justification_artists.items():
            if (
                rule_application.justification.dependency_type
                == JustificationType.RULE_APPLICATION
            ):
                updated_artists.update(rule_application.hide())
        return updated_artists

    def _hide_all_extra_applications(self) -> set[Artist]:
        updated_artists: set[Artist] = set()
        for _dep, extra_application in self.justification_artists.items():
            if (
                extra_application.justification.dependency_type
                != JustificationType.RULE_APPLICATION
            ):
                updated_artists.update(extra_application.hide())
        return updated_artists
