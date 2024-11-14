from dataclasses import dataclass
import logging
import numpy as np
from lib.reactor_settings import ReactorSettings
from lib.containment_vessel import ContainmentVessel
from lib.storage_tank import StorageTank
from lib.power_system import PowerSystem

logger = logging.getLogger(__name__)


@dataclass
class SabatierReactor:
    settings: ReactorSettings
    efficiency: float
    catalyst_degradation_rate: float
    vessel: ContainmentVessel
    temperature_cycle_c: np.ndarray
    pressure_cycle_pa: np.ndarray
    CO2_tank: StorageTank
    H2_tank: StorageTank
    CH4_tank: StorageTank
    H2O_tank: StorageTank
    power_system: PowerSystem
    min_operational_efficiency: float = 0.1  # Minimum efficiency required to operate

    # Activation energy in kJ/mol (approximate for the Sabatier reaction)
    activation_energy_kj: float = 50  # adjustable parameter

    def temp_factor(self, temp_c):
        R = 8.314  # Gas constant in J/(mol·K)
        temp_k = temp_c + 273.15  # Convert to Kelvin
        E_a = self.activation_energy_kj * 1000  # Convert kJ/mol to J/mol
        A = 1  # Pre-exponential factor for normalization

        k_T = A * np.exp(-E_a / (R * temp_k))

        # Normalize to reaction rate at target temperature
        target_temp_k = self.vessel.target_temp_c + 273.15
        k_target = A * np.exp(-E_a / (R * target_temp_k))
        temp_effect = k_T / k_target

        return temp_effect

    def pressure_factor(self, pressure_pa):
        # Convert pressure to atmospheres
        pressure_atm = pressure_pa / 101325
        target_pressure_atm = self.vessel.target_pressure_pa / 101325
        pressure_effect = pressure_atm / target_pressure_atm
        pressure_effect = min(max(pressure_effect, 0), 1)  # Clamp between 0 and 1
        return pressure_effect

    def run_cycle(self, hour, total_power_available):
        # Degrade efficiency over time
        self.current_efficiency = self.efficiency * np.exp(
            -self.catalyst_degradation_rate * hour
        )
        reaction_efficiency = max(self.current_efficiency, 0)
        logger.info(
            f"Running Sabatier reactor cycle with catalyst efficiency at {reaction_efficiency:.2f}"
        )

        if reaction_efficiency < self.min_operational_efficiency:
            logger.warning("Catalyst efficiency too low. Replacing catalyst.")
            self.current_efficiency = self.efficiency

        # Adjust temperature and pressure
        external_temp_c = self.temperature_cycle_c[hour]
        heating_info = self.vessel.adjust_temperature(external_temp_c, hour)
        pressurization_info = self.vessel.adjust_pressure(hour)

        # Retrieve internal conditions and power used
        internal_temp_c = heating_info["Internal Temperature (°C)"]
        internal_pressure_pa = pressurization_info["Internal Pressure (Pa)"]
        heating_power_used = heating_info["Heating Power Used (kJ)"]
        pressurization_power_used = pressurization_info[
            "Pressurization Power Used (kJ)"
        ]

        # Calculate effects on reaction efficiency
        temp_effect = self.temp_factor(internal_temp_c)
        pressure_effect = self.pressure_factor(internal_pressure_pa)
        adjusted_efficiency = reaction_efficiency * temp_effect * pressure_effect
        adjusted_efficiency = min(
            max(adjusted_efficiency, 0), 1
        )  # Clamp between 0 and 1
        logger.info(f"Adjusted efficiency: {adjusted_efficiency:.2f}")

        # Total power available
        logger.info(f"Total power available: {total_power_available:.2f} kJ")

        # Calculate total power required for heating and pressurization
        power_needed = heating_power_used + pressurization_power_used

        if total_power_available >= power_needed:
            # Proceed as normal
            result = self.process_reaction(adjusted_efficiency)
            power_used = power_needed
        else:
            # Scale down based on available power
            scaling_factor = total_power_available / power_needed
            adjusted_efficiency *= scaling_factor
            result = self.process_reaction(adjusted_efficiency)
            power_used = total_power_available
            logger.warning(
                f"Scaled down operation due to limited power at hour {hour}."
            )

        # Manage battery and store outputs
        self.power_system.manage_battery(power_used, total_power_available)
        self.store_outputs(result)
        return {
            "CH4 Produced (g)": result["CH4 Produced (g)"],
            "H2O Produced (g)": result["H2O Produced (g)"],
            "Heating Power Used (kJ)": heating_power_used,
            "Pressurization Power Used (kJ)": pressurization_power_used,
        }, self.power_system.battery_level_kj

    def process_reaction(self, efficiency):
        # Calculate available moles of reactants
        available_moles_CO2 = self.CO2_tank.level / self.settings.molar_mass_CO2
        available_moles_H2 = (
            self.H2_tank.level / self.settings.molar_mass_H2 / 4
        )  # 4 H2 per CO2

        # Determine the limiting reactant
        max_moles_reactable = min(available_moles_CO2, available_moles_H2)

        # Scale reaction based on efficiency and available power
        moles_CH4 = max_moles_reactable * efficiency

        # Ensure moles_CH4 is non-negative
        moles_CH4 = max(moles_CH4, 0)

        # Remove the reactants
        self.CO2_tank.remove(moles_CH4 * self.settings.molar_mass_CO2)
        self.H2_tank.remove(moles_CH4 * 4 * self.settings.molar_mass_H2)

        # Log the reaction details
        logger.info(
            f"Sabatier reactor produced {moles_CH4 * self.settings.molar_mass_CH4:.2f} g of CH4."
        )

        return {
            "CH4 Produced (g)": moles_CH4 * self.settings.molar_mass_CH4,
            "H2O Produced (g)": moles_CH4 * 2 * self.settings.molar_mass_H2O,
        }

    def store_outputs(self, result):
        # Store the reaction outputs
        self.CH4_tank.add(result["CH4 Produced (g)"])
        self.H2O_tank.add(result["H2O Produced (g)"])
