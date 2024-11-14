import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class StorageTank:
    name: str
    capacity: float
    level: float = 0
    is_low: bool = False

    def add(self, amount):
        if self.level + amount > self.capacity:
            logger.warning(f"{self.name} tank is full. Cannot add more.")
            self.level = self.capacity
        self.level = min(self.capacity, self.level + amount)

    def remove(self, amount):
        if amount > self.level:
            logger.warning(
                f"Attempting to remove more than available in the {self.name} tank"
            )
            amount = self.level  # Only remove what is available
        removed = min(self.level, amount)
        self.level -= removed
        if self.level < 0.1 * self.capacity:
            logger.warning(
                f"{self.name} tank is almost empty. Consider refilling soon."
            )
            self.is_low = True
        return removed
