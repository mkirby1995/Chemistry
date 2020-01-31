import pandas as pd
import json


class Element:


  def __init__(self, name, abrivation, atomic_number,
               atomic_mass, period, group):

    self.name = name
    self.abrivation = abrivation
    self.atomic_number = atomic_number
    self.atomic_mass = atomic_mass
    self.period = period #row
    self.group = group #column
    self.protons = self.atomic_number
    self.neutrons = self.atomic_mass - self.protons


  def __repr__(self):
    return f"{self.abrivation}\n{self.atomic_number}\n{self.atomic_mass}"


df = pd.read_csv('elements.csv', header=None).dropna(axis = 0)
df[0] = df[0].str.strip("'")
df[1] = df[1].str.strip("'")

periodic = {}

for i in range(len(df)):
  element = Element(name = df[0][i],
                    abrivation = df[1][i],
                    atomic_number = df[2][i],
                    atomic_mass = df[3][i],
                    period = df[4][i],
                    group = df[5][i])


  periodic[element.abrivation] = {'name': element.name,
                    'atomic_number': element.atomic_number,
                    'atomic_mass': element.atomic_mass,
                    'period':element.period,
                    'group': element.group}


with open('periodic.json', 'w', encoding='utf-8') as f:
    json.dump(periodic, f, ensure_ascii=False, indent=4)
