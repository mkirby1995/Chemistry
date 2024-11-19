import logging
from typing import List
import pandas as pd
from lib.storage_tank import StorageTank
from lib.power_system import PowerConsumingSubsystem

logger = logging.getLogger(__name__)


class AtmosphereIntakeSystem(PowerConsumingSubsystem):
    def __init__(
        self,
        name: str,
        power_demand_kj: float,
        criticality_level: int,
        operational_hours: List,
        CO2_tank: StorageTank,
        max_flow_rate_grams_per_hour: float,
    ):
        """
        Initialize an atmosphere intake system with a given power demand and CO₂ tank.

        :param name: Name of the atmosphere intake system
        :param power_demand_kj: Power demand of the system in kJ
        :param criticality_level: Criticality level of the system (1 = most critical, higher numbers = less critical)
        :param operational_hours: List of hours when the system is operational
        :param CO2_tank: CO₂ storage tank
        :param max_flow_rate_grams_per_hour: Maximum flow rate of CO₂ intake in grams per hour
        :param atmospheric_pressure_kilo_pascal: Atmospheric pressure in kilo pascals (default is 0.61 kPa)
        """
        super().__init__(name, power_demand_kj, criticality_level, operational_hours)
        self.CO2_tank = CO2_tank
        self.max_flow_rate = max_flow_rate_grams_per_hour
        self.metrics = pd.DataFrame(columns=["hour", "co2_added_grams", "power_used_kj"])

    def run_cycle(self, hour):
        # Calculate the amount of CO₂ to intake
        tank_space_available_grams = self.CO2_tank.available_capacity_grams()
        intake_amount_grams = min(self.max_flow_rate, tank_space_available_grams)
        power_used_kj = 0

        if intake_amount_grams > 0:
            # Consume power
            base_power_per_gram = self.power_demand_kj / self.max_flow_rate  # kJ/g
            power_used_kj = base_power_per_gram * intake_amount_grams

            # Add CO₂ to the tank
            self.CO2_tank.add(intake_amount_grams, hour)

            logger.info(f"Atmosphere intake system added {intake_amount_grams}g CO2 at hour {hour}.")
        else:
            logger.warning(f"Insufficient tank capacity for atmosphere intake at hour {hour}.")

        self.log_metrics(hour, intake_amount_grams, power_used_kj)

    def log_metrics(self, hour, intake_amount_grams, power_used):
        self.metrics.loc[len(self.metrics)] = {
            "hour": hour,
            "co2_added_grams": intake_amount_grams,
            "power_used_kj": power_used,
        }