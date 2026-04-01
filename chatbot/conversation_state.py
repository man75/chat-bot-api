# conversation_state.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import json


class Intent(str, Enum):
    NONE = "none"
    RDV = "rdv"
    DEVIS = "devis"
    QUESTION = "question"


class Step(str, Enum):
    COLLECT_NOM = "collect_nom"
    COLLECT_PRENOM = "collect_prenom"

    DEVIS_MARQUE = "devis_marque"
    DEVIS_MODELE = "devis_modele"
    DEVIS_MATRICULE = "devis_matricule"
    DEVIS_ENERGIE = "devis_energie"
    DEVIS_SUJET = "devis_sujet"

    DEVIS_DONE = "devis_done"


LEGACY_STEP_MAP = {
    "collect_telephone": Step.COLLECT_NOM,
    "collect_mail": Step.COLLECT_NOM,
    "rdv_done": Step.DEVIS_DONE,
    "question_done": Step.DEVIS_DONE,
}


@dataclass
class ConversationState:
    intent: Intent = Intent.NONE
    step: Optional[Step] = None
    collected: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(
            {
                "intent": self.intent.value,
                "step": self.step.value if self.step else None,
                "collected": self.collected,
            }
        )

    @classmethod
    def _parse_step(cls, raw_step: Optional[str]) -> Optional[Step]:
        if not raw_step:
            return None

        if raw_step in LEGACY_STEP_MAP:
            return LEGACY_STEP_MAP[raw_step]

        try:
            return Step(raw_step)
        except ValueError:
            return None

    @classmethod
    def from_json(cls, raw: str) -> "ConversationState":
        data = json.loads(raw)

        raw_intent = data.get("intent", "none")
        try:
            intent = Intent(raw_intent)
        except ValueError:
            intent = Intent.NONE

        return cls(
            intent=intent,
            step=cls._parse_step(data.get("step")),
            collected=data.get("collected", {}),
        )
