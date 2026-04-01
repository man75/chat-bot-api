# conversation_state.py
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import json

class Intent(str, Enum):
    NONE     = "none"
    RDV      = "rdv"
    DEVIS    = "devis"
    QUESTION = "question"

class Step(str, Enum):
    # Collecte contact (commune aux 3 flux)
    COLLECT_NOM       = "collect_nom"
    COLLECT_TELEPHONE = "collect_telephone"
    COLLECT_MAIL      = "collect_mail"
    # Devis uniquement
    DEVIS_MARQUE      = "devis_marque"
    DEVIS_MODELE      = "devis_modele"
    DEVIS_MATRICULE   = "devis_matricule"
    DEVIS_ENERGIE     = "devis_energie"
    # Fins de flux
    RDV_DONE          = "rdv_done"
    DEVIS_DONE        = "devis_done"
    QUESTION_DONE     = "question_done"

@dataclass
class ConversationState:
    intent: Intent = Intent.NONE
    step: Optional[Step] = None
    collected: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({
            "intent":    self.intent.value,
            "step":      self.step.value if self.step else None,
            "collected": self.collected,
        })

    @classmethod
    def from_json(cls, raw: str) -> "ConversationState":
        data = json.loads(raw)
        return cls(
            intent=Intent(data.get("intent", "none")),
            step=Step(data["step"]) if data.get("step") else None,
            collected=data.get("collected", {}),
        )