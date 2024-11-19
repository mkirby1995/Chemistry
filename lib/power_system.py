"""
# Example usage:

# Initialize components
solar_farm = SolarFarm(max_output_kw=1000)
krusty_reactors = [
    KRUSTYReactor(max_output_kw=500, maintenance_schedule=[100, 200]),
    KRUSTYReactor(max_output_kw=500)
]
battery = Battery(capacity_kj=1e6, level_kj=0.5e6, degradation_rate=0.0001)

# Create subsystems
subsystems = [
    PowerConsumingSubsystem(
        name='Life Support',
        power_demand_kj=10000,
        criticality_level=1,
        operational_hours=list(range(24))
    ),
    PowerConsumingSubsystem(
        name='Communications',
        power_demand_kj=5000,
        criticality_level=2,
        operational_hours=list(range(8, 20))
    ),
    # Add more subsystems as needed
]

# Initialize power distribution management system
pdms = PowerDistributionManagementSystem(solar_farm, krusty_reactors, battery)
for subsystem in subsystems:
    pdms.add_subsystem(subsystem)

# Simulation loop
total_simulation_hours = 1000
for hour in range(total_simulation_hours):
    pdms.distribute_power(hour)

# After simulation, access the metrics DataFrame
print(pdms.metrics)
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

@dataclass
class PowerConsumingSubsystem:
    name: str
    power_demand_kj: float  # Power demand in kJ
    criticality_level: int  # 1 = most critical, higher numbers = less critical
    operational_hours: list  # List of hours when the subsystem is operational

    def is_operational(self, hour):
        return hour % 24 in self.operational_hours

@dataclass
class PowerProductionSubsystem:
    name: str
    max_output_kw: float

    def available_power(self, hour):
        return np.random.uniform(0.9, 1.0) * self.max_output_kw * 3600

@dataclass
class SolarFarm(PowerProductionSubsystem):
    name: str = "Solar Farm"
    max_output_kw: float = 1000  # Maximum power output in kW
    efficiency: float = 0.85  # Solar panel efficiency, accounting for dust and aging
    martian_year_hours: int = 687 * 24  # Martian year in hours
    on_duration: int = 10  # Daylight duration in hours
    off_duration: int = 14  # Night duration in hours

    def available_power(self, hour):
        # Seasonal variation
        season_cycle = (hour % self.martian_year_hours) / self.martian_year_hours
        seasonal_modifier = 0.5 * (1 + np.cos(2 * np.pi * season_cycle))  # Ranges from 0 to 1

        # Dust storms
        dust_storm_probability = 0.05  # 5% chance per day
        if np.random.random() < dust_storm_probability:
            dust_storm_factor = np.random.uniform(0.1, 0.5)  # Reduce output significantly
        else:
            dust_storm_factor = 1.0

        # Day or night
        is_daytime = (hour % 24) < self.on_duration

        if is_daytime:
            variability = np.random.normal(1, 0.05)  # 5% random variation
            solar_power_kw = (
                self.max_output_kw * seasonal_modifier * variability * self.efficiency * dust_storm_factor
            )
        else:
            solar_power_kw = 0  # No power generation at night

        return max(0, solar_power_kw * 3600)  # Convert kW to kJ

@dataclass
class KRUSTYReactor(PowerProductionSubsystem):
    name: str = "KRUSTY Reactor"
    max_output_kw: float = 10  # Maximum power output in kW
    efficiency: float = 0.95  # Base efficiency
    burnup_rate: float = 0.0001  # Rate at which fuel is consumed
    operational_uptime: float = 0.98  # Operational uptime
    maintenance_schedule: list = None

    def available_power(self, hour):
        if self.maintenance_schedule and hour in self.maintenance_schedule:
            return 0  # Reactor down for scheduled maintenance
        
        # Unscheduled downtime based on operational uptime
        if np.random.random() > self.operational_uptime:
            return 0  # Reactor down for unscheduled maintenance
        
        # Simulate gradual burnup of the reactor, reducing output over time
        power_output = self.max_output_kw * (1 - self.burnup_rate * hour)
        return max(0, power_output) * 3600  # Convert kW to kJ

@dataclass
class Battery:
    capacity_kj: float  # Maximum capacity in kJ
    level_kj: float  # Current battery level in kJ
    charge_efficiency: float = 0.90  # Charging efficiency
    discharge_efficiency: float = 0.92  # Discharging efficiency
    degradation_rate: float = 0.0001  # Capacity loss per hour

    def charge(self, surplus_power_kj):
        actual_charge = surplus_power_kj * self.charge_efficiency
        self.level_kj = min(self.capacity_kj, self.level_kj + actual_charge)

    def discharge(self, deficit_kj):
        required_discharge = deficit_kj / self.discharge_efficiency
        actual_discharge = min(required_discharge, self.level_kj)
        self.level_kj -= actual_discharge
        return actual_discharge * self.discharge_efficiency

    def is_low(self, threshold):
        return self.level_kj < threshold * self.capacity_kj

    def update_degradation(self):
        self.capacity_kj *= (1 - self.degradation_rate)

class PowerDistributionManagementSystem:
    def __init__(self, solar_farm: SolarFarm, krusty_reactors: list, battery: Battery):
        self.solar_farm = solar_farm
        self.krusty_reactors = krusty_reactors
        self.battery = battery
        self.load_shedding_threshold = 0.1  # Threshold for load shedding
        self.subsystems = []  # List of PowerConsumingSubsystem instances
        self.metrics = pd.DataFrame(columns=['hour', 'total_generation_kj', 'total_consumption_kj', 'battery_soc', 'load_shedding'])

    def add_subsystem(self, subsystem: PowerConsumingSubsystem):
        self.subsystems.append(subsystem)

    def distribute_power(self, hour):
        total_generation = self.available_power(hour)
        load_shedding_events = []
        # Operational subsystems
        operational_subsystems = [s for s in self.subsystems if s.is_operational(hour)]
        total_demand = sum(s.power_demand_kj for s in operational_subsystems)

        # Manage battery and calculate surplus or deficit
        surplus_or_deficit = self.manage_battery(total_demand, total_generation)

        if surplus_or_deficit < 0:
            # Perform load shedding
            sorted_subsystems = sorted(operational_subsystems, key=lambda s: s.criticality_level, reverse=True)
            for subsystem in sorted_subsystems:
                if surplus_or_deficit >= 0:
                    break
                # Shed load for this subsystem
                logger.info(f"Load shedding initiated for {subsystem.name}")
                load_shedding_events.append(subsystem.name)
                surplus_or_deficit += subsystem.power_demand_kj
                total_demand -= subsystem.power_demand_kj

        total_consumption = total_demand
        battery_soc = self.battery.level_kj / self.battery.capacity_kj

        # Update battery degradation
        self.battery.update_degradation()

        # Log metrics
        self.log_metrics(hour, total_generation, total_consumption, battery_soc, load_shedding_events)

    def available_power(self, hour):
        # Power from solar farm
        solar_power = self.solar_farm.available_power(hour)
        # Power from reactors
        nuclear_power = sum(reactor.available_power(hour) for reactor in self.krusty_reactors)

        self.last_solar_power_kj = solar_power
        self.last_nuclear_power_kj = nuclear_power

        return solar_power + nuclear_power

    def manage_battery(self, total_demand_kj, total_generation_kj):
        surplus_power_kj = total_generation_kj - total_demand_kj
        if surplus_power_kj > 0:
            # Charge battery
            self.battery.charge(surplus_power_kj)
        else:
            # Discharge battery
            actual_discharge = self.battery.discharge(-surplus_power_kj)
            surplus_power_kj += actual_discharge  # Adjust surplus after discharge

            # Load shedding if battery is low
            if self.battery.is_low(self.load_shedding_threshold):
                logger.warning("Battery level critically low. Implementing load shedding.")
        return surplus_power_kj  # Net surplus after battery adjustments

    def log_metrics(self, hour, total_generation, total_consumption, battery_soc, load_shedding_events):
        self.metrics.loc[len(self.metrics)] = {
            'hour': hour,
            'total_generation_kj': total_generation,
            'total_consumption_kj': total_consumption,
            'battery_soc': battery_soc,
            'load_shedding': ', '.join(load_shedding_events),
        }

    def is_subsystem_in_load_shedding(self, subsystem_name, hour):
        return subsystem_name in self.metrics['load_shedding'].iloc[hour]
