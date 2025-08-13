from newclid.agent.follow_deductions import FollowDeductions
from newclid.api import APIDefault, DeductiveAgent, Deductor, RuleMatcher
from newclid.problem import predicate_to_construction
from newclid.proof_state import ProofState

from py_yuclid.omni_matcher import OmniMatcher
from py_yuclid.yuclid_adapter import YuclidAdapter


class HEDefault(APIDefault):
    def __init__(self, he_adapter: YuclidAdapter | None = None) -> None:
        self._he_adapter = he_adapter

    @property
    def he_adapter(self) -> YuclidAdapter:
        if self._he_adapter is None:
            self._he_adapter = YuclidAdapter()
        return self._he_adapter

    def default_rule_matcher(self) -> RuleMatcher:
        return OmniMatcher(self.he_adapter)

    def default_deductors(self) -> list[Deductor]:
        return []

    def default_deductive_agent(self) -> DeductiveAgent:
        return FollowDeductions(self.he_adapter)

    def callback(self, proof_state: ProofState) -> None:
        self.he_adapter.reset()
        self.he_adapter.goals = [
            predicate_to_construction(goal) for goal in proof_state.goals
        ]
        self.he_adapter.problem_name = proof_state.problem.name
