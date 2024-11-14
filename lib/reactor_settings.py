from dataclasses import dataclass


@dataclass
class ReactorSettings:
    molar_mass_CO2: float = 44.01
    molar_mass_H2: float = 2.016
    molar_mass_CH4: float = 16.04
    molar_mass_H2O: float = 18.015
    molar_mass_O2: float = 32
    energy_per_mole_CH4: float = 165  # kJ per mole CH4
    energy_per_mole_H2O: float = 285.8  # kJ per mole H2O
