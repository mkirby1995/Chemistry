from dataclasses import dataclass
import numpy as np


@dataclass
class PowerSystem:
    solar_max_kw: float  # in kW
    nuclear_max_kw: float  # in kW
    battery_capacity_kj: float  # in kJ
    last_nuclear_power_kj: float = 0
    last_solar_power_kj: float = 0
    battery_level_kj: float = 0
    solar_efficiency: float = 0.85  # Efficiency of solar panel, due to dust and aging
    charge_efficiency: float = 0.95  # Battery charging efficiency
    discharge_efficiency: float = 0.95  # Battery discharging efficiency
    on_duration: int = 12
    off_duration: int = 12
    martian_year_hours: int = 687 * 24  # Martian year in hours

    def seasonal_solar_modifier(self, hour):
        """Calculate a seasonal modifier based on the Martian year to simulate solar variability."""
        season_cycle = (hour % self.martian_year_hours) / self.martian_year_hours
        seasonal_modifier = 0.5 * (
            1 + np.cos(2 * np.pi * season_cycle)
        )  # Ranges from 0 to 1
        return seasonal_modifier

    def available_power(self, hour):
        # Calculate solar and nuclear power in kJ for this hour
        seasonal_modifier = self.seasonal_solar_modifier(hour)
        variability = np.random.normal(1, 0.1)  # 10% random variation
        solar_power_kj = (
            self.solar_max_kw
            * seasonal_modifier
            * variability
            * self.solar_efficiency
            * 3600
        )  # kJ conversion
        solar_power_kj = solar_power_kj if (hour % 24) < self.on_duration else 0

        # Nuclear power in kJ
        nuclear_power_kj = (
            np.random.uniform(0.9, 1.0) * self.nuclear_max_kw * 3600
        )  # Convert kW to kJ

        # Total power available, prioritizing solar during the day
        self.last_solar_power_kj = solar_power_kj
        self.last_nuclear_power_kj = nuclear_power_kj
        return solar_power_kj + nuclear_power_kj

    def manage_battery(self, power_used, total_power_generated):
        surplus_power_kj = total_power_generated - power_used
        if surplus_power_kj > 0:
            self.battery_level_kj = min(
                self.battery_capacity_kj,
                self.battery_level_kj + surplus_power_kj * self.charge_efficiency,
            )
        else:
            deficit_kj = abs(surplus_power_kj) / self.discharge_efficiency
            actual_discharge = min(deficit_kj, self.battery_level_kj)
            self.battery_level_kj -= actual_discharge
            surplus_power_kj += actual_discharge * self.discharge_efficiency
        self.battery_level_kj = max(
            0, min(self.battery_capacity_kj, self.battery_level_kj)
        )
        return surplus_power_kj  # Net surplus after battery adjustments
