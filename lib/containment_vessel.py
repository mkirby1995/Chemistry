from dataclasses import dataclass
from .power_system import PowerSystem


@dataclass
class ContainmentVessel:
    target_temp_c: float  # Target internal temperature in Celsius
    vessel_volume_m3: float  # Volume of the containment vessel in cubic meters
    target_pressure_pa: float  # Target internal pressure in Pascals
    insulation_factor: (
        float  # Efficiency of insulation (0-1, where 1 is perfect insulation)
    )
    heating_power_kw: float  # Max power of the heating system in kW
    pressurization_power_kw: float  # Max power of the pressurization system in kW
    internal_temp_c: float  # Current internal temperature in Celsius
    internal_pressure_pa: float  # Current internal pressure in Pascals
    power_system: PowerSystem

    def adjust_temperature(self, external_temp_c, hour):
        # Mass of gas (assuming ideal gas)
        vessel_volume_m3 = self.vessel_volume_m3  # Define vessel volume
        pressure_pa = self.internal_pressure_pa
        temp_k = self.internal_temp_c + 273.15
        R_specific = 287  # J/(kg·K) for air (approximation)

        mass_kg = max((pressure_pa * vessel_volume_m3) / (R_specific * temp_k), 0.001)

        # Specific heat capacity (assumed average for gas mixture)
        cp = 1005  # J/(kg·K)

        # Energy required
        temp_diff = self.target_temp_c - self.internal_temp_c
        required_energy_j = mass_kg * cp * temp_diff
        required_energy_kj = required_energy_j / 1000

        # Check available power
        heating_power_kj = self.heating_power_kw * 3600
        available_energy = min(
            heating_power_kj, self.power_system.available_power(hour)
        )

        # Adjust internal temperature
        energy_used = min(available_energy, required_energy_kj)
        self.power_system.manage_battery(energy_used, available_energy)
        if required_energy_kj > 0:
            temp_increase = (energy_used * 1000) / (mass_kg * cp)
        else:
            temp_increase = 0

        self.internal_temp_c += temp_increase

        # Apply temperature drift
        temp_drift = (external_temp_c - self.internal_temp_c) * (
            1 - self.insulation_factor
        )
        self.internal_temp_c += temp_drift

        return {
            "Internal Temperature (°C)": self.internal_temp_c,
            "Heating Power Used (kJ)": energy_used,
        }

    def adjust_pressure(self, hour):
        # Pressure difference
        pressure_ratio = self.target_pressure_pa / self.internal_pressure_pa
        if pressure_ratio <= 1:
            return {
                "Internal Pressure (Pa)": self.internal_pressure_pa,
                "Pressurization Power Used (kJ)": 0,
            }

        # Calculate moles of gas to add using PV = nRT
        R = 8.314  # J/(mol·K)
        temp_k = self.internal_temp_c + 273.15
        delta_n = (
            (self.target_pressure_pa - self.internal_pressure_pa)
            * self.vessel_volume_m3
            / (R * temp_k)
        )

        # Energy required to compress gas into vessel (simplified)
        specific_energy_kj_per_mol = 1  # kJ/mol, adjust as necessary
        required_energy_kj = delta_n * specific_energy_kj_per_mol

        # Check available power
        pressurization_power_kj = self.pressurization_power_kw * 3600
        available_energy = min(
            pressurization_power_kj, self.power_system.available_power(hour)
        )

        # Adjust internal pressure
        energy_used = min(available_energy, required_energy_kj)
        self.power_system.manage_battery(energy_used, available_energy)
        pressure_increase = (energy_used / required_energy_kj) * (
            self.target_pressure_pa - self.internal_pressure_pa
        )
        self.internal_pressure_pa += pressure_increase

        return {
            "Internal Pressure (Pa)": self.internal_pressure_pa,
            "Pressurization Power Used (kJ)": energy_used,
        }
