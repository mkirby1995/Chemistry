from dataclasses import dataclass
import logging
from lib.storage_tank import StorageTank
from lib.power_system import PowerSystem

logger = logging.getLogger(__name__)


@dataclass
class AtmosphereIntakeSystem:
    name: str
    CO2_tank: StorageTank
    power_system: PowerSystem
    intake_rate: float  # CO2 intake rate in grams per cycle
    power_per_cycle: float  # Power used per cycle in kJ
    interval_hours: int = 6  # Run every 6 hours by default

    def run_cycle(self, hour, total_power_available):
        if hour % self.interval_hours == 0:
            max_intake_possible = (
                total_power_available / self.power_per_cycle * self.intake_rate
            )
            tank_space_available = self.CO2_tank.capacity - self.CO2_tank.level
            intake_amount = min(
                self.intake_rate, max_intake_possible, tank_space_available
            )

            if intake_amount > 0:
                # Add CO₂ to the tank
                self.CO2_tank.add(intake_amount)

                # Consume power for the intake process
                power_used = (intake_amount / self.intake_rate) * self.power_per_cycle
                self.power_system.manage_battery(power_used, total_power_available)

                logger.info(
                    f"Atmosphere intake system added {intake_amount}g CO2 at hour {hour}."
                )
                return {"CO2 Added (g)": intake_amount, "Power Used (kJ)": power_used}
            else:
                logger.warning(
                    f"Insufficient power or tank capacity for atmosphere intake at hour {hour}."
                )
                return {"CO2 Added (g)": 0, "Power Used (kJ)": 0}
        return {"CO2 Added (g)": 0, "Power Used (kJ)": 0}
