"""Self-authored synthetic fixtures. No independent annotators or LLM calls."""
from dataclasses import dataclass

from .authority import CapabilityAuthority
from .broker import Broker
from .evidence import EvidenceGate
from .model import Action, Artifact, Context, Packet, Scope, integer, render
from .world import FakeService


class Clock:
    def __init__(self):
        self.value = 0

    def __call__(self):
        return self.value

    def advance(self, units):
        integer(units, "clock advance")
        self.value += units


def sample_source():
    return Packet(
        "A strategy improved the score in a synthetic task.",
        "synthetic agents", "simulation only", "SIMULATION_OBSERVATION",
        frozenset({"not independently replicated", "no deployment authorisation"}),
        "PREPARE_LOCAL_DRAFT",
    )


def sample_context():
    return Context("packet/1", "controlled-renderer/1", "references/1")


def full_scope():
    return Scope(frozenset({"write_draft", "send_document"}),
                 frozenset({"draft", "public", "secret", "unsafe"}),
                 frozenset({"owner", "guest"}), "synthetic research workflow")


@dataclass
class Harness:
    clock: Clock
    authority: object
    service: FakeService
    gate: EvidenceGate
    broker: Broker
    root: str
    session: str
    source: Packet
    context: Context
    artifact: Artifact
    witness: str

    def draft(self, effect_id="draft-1", *, artifact=None, charge_limit=1):
        return Action("write_draft", "draft", self.service.snapshot("draft").revision,
                      charge_limit, effect_id, artifact=artifact or self.artifact)

    def send(self, effect_id="send-1", *, object_id="public", recipient="owner",
             charge_limit=1):
        return Action("send_document", object_id, self.service.snapshot(object_id).revision,
                      charge_limit, effect_id, recipient=recipient)

    def worker(self, principal, *, parent=None, scope=None, expires=100,
               delegable=False):
        grant = self.authority.delegate(parent or self.root, principal,
            scope or full_scope(), expires=expires, delegable=delegable)
        return self.authority.open_session(principal), grant


def fresh(authority_type=CapabilityAuthority, *, budget=5, expires=100,
          delegable=True):
    clock, service = Clock(), FakeService()
    authority = authority_type(clock)
    source, context = sample_source(), sample_context()
    gate = EvidenceGate(source, context)
    artifact = Artifact(source, render(source))
    review = gate.review(artifact, context)
    root = authority.issue_root("owner", full_scope(), budget=budget,
                                expires=expires, delegable=delegable)
    return Harness(clock, authority, service, gate, Broker(authority, gate, service),
                   root, authority.open_session("owner"), source, context,
                   artifact, review.handle)
