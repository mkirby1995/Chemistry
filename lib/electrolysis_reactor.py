from dataclasses import dataclass
import logging
from lib.reactor_settings import ReactorSettings
from lib.storage_tank import StorageTank
from lib.power_system import PowerDistributionManagementSystem

logger = logging.getLogger(__name__)


@dataclass
class ElectrolysisReactor:
    settings: ReactorSettings
    H2O_tank: StorageTank
    H2_tank: StorageTank
    O2_tank: StorageTank
    power_system: PowerDistributionManagementSystem
    efficiency: float = 0.8  # Default efficiency of 80%

    def run_cycle(self, hour, total_power_available):
        # Maximum moles of H₂O that can be processed based on power
        max_moles_power = (
            total_power_available * self.efficiency
        ) / self.settings.energy_per_mole_H2O

        # Moles of H₂O available in the tank
        moles_H2O_available = self.H2O_tank.level / self.settings.molar_mass_H2O

        # Determine moles of H₂O to process
        moles_H2O = min(max_moles_power, moles_H2O_available)

        if moles_H2O > 0:
            # Remove H₂O from the tank
            self.H2O_tank.remove(moles_H2O * self.settings.molar_mass_H2O)

            # Calculate hydrogen and oxygen produced
            hydrogen_produced = (
                moles_H2O * 2 * self.settings.molar_mass_H2
            )  # 2 moles H₂ per mole H₂O
            oxygen_produced = (
                moles_H2O * self.settings.molar_mass_O2
            )  # 1 mole O₂ per mole H₂O

            # Calculate power required
            power_required = (
                moles_H2O * self.settings.energy_per_mole_H2O
            ) / self.efficiency

            # Consume power and update battery
            self.power_system.manage_battery(power_required, total_power_available)

            # Add produced gases to tanks
            self.H2_tank.add(hydrogen_produced)
            self.O2_tank.add(oxygen_produced)

            logger.info(
                f"Electrolysis produced {hydrogen_produced}g H2 and {oxygen_produced}g O2 at hour {hour}."
            )

            return {
                "H2 Produced (g)": hydrogen_produced,
                "O2 Produced (g)": oxygen_produced,
                "Power Used (kJ)": power_required,
            }
        else:
            logger.warning(f"Insufficient resources for electrolysis at hour {hour}.")
            return {"H2 Produced (g)": 0, "O2 Produced (g)": 0, "Power Used (kJ)": 0}
