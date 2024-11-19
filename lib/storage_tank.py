import logging
import pandas as pd

logger = logging.getLogger(__name__)


class StorageTank:

    def __init__(
        self,
        name: str,
        capacity_grams: float = 100_000,
        level_grams: float = 0,
        pressure_kilo_pascal: float = 0.61,
        max_pressure_kilo_pascal: float = 500.0,
    ):
        """
        Initialize a storage tank with a given capacity, level, and pressure.

        :param name: Name of the storage tank
        :param capacity_grams: Maximum capacity of the tank in grams (default is 1kg)
        :param level_grams: Initial level of the tank in grams (default is 0)
        :param pressure_kilo_pascal: Pressure of the tank in kilo pascals (default is 0.61 kPa)
        :param max_pressure_kilo_pascal: Maximum pressure of the tank in kilo pascal (default is 500.0 kPa)
        """
        self.name = name
        self.capacity_grams = capacity_grams
        self.level_grams = level_grams
        self.pressure_kilo_pascal = pressure_kilo_pascal
        self.max_pressure_kilo_pascal = max_pressure_kilo_pascal
        self.metrics = pd.DataFrame(
            columns=["hour", "level_grams", "percentage_full", "pressure_kilo_pascal"]
        )

    def add(self, amount: float, hour):
        if self.level_grams + amount > self.capacity_grams:
            logger.warning(f"{self.name} tank is full. Cannot add more.")
            self.level_grams = self.capacity_grams
        else:
            self.level_grams += amount

        self.update_pressure()
        self.log_metrics(hour)

    def remove(self, amount: float, hour):
        if amount > self.level_grams:
            logger.warning(
                f"Attempting to remove more than available in the {self.name} tank"
            )
            amount = self.level_grams  # Only remove what is available

        self.level_grams -= amount
        self.update_pressure()
        self.log_metrics(hour)
        return amount

    def update_pressure(self):
        # Assuming proportionality between level and pressure
        # For simplicity, we set pressure to a max when the tank is full
        self.pressure = (self.level_grams / self.capacity_grams) * self.max_pressure_kilo_pascal

    def available_capacity_grams(self):
        return self.capacity_grams - self.level_grams

    def log_metrics(self, hour):
        # Check if there's already an entry for the given hour
        existing_entries = self.metrics[self.metrics["hour"] == hour]

        if not existing_entries.empty:
            # Update the existing entry
            index = existing_entries.index[0]
            self.metrics.loc[index, "level_grams"] = self.level_grams
            self.metrics.loc[index, "percentage_full"] = (
                self.level_grams / self.capacity_grams
            )
        else:
            # Add a new entry
            self.metrics.loc[len(self.metrics)] = {
                "hour": hour,
                "level_grams": self.level_grams,
                "percentage_full": self.level_grams / self.capacity_grams,
            }
