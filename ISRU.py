class Atmospheric_processing_unit:

  def __init__(self):
    self.co2_stock = 0
    self.h2o_stock = 0
    self.co_stock = 0
    self.ch4_stock = 0
    self.h2_stock = 0
    self.o2_stock = 0

  def __repr__(self):
    return (f"CO2:{self.co2_stock}\nH2O:{self.h2o_stock}\nCO:{self.co_stock}\nCH4:{self.ch4_stock}\nH2:{self.h2_stock}\nO2:{self.o2_stock}")


  def sabatier_rwgs(self):
    if self.co2_stock >= 3 and self.h2_stock >= 2:
      self.co2_stock -= 3
      self.h2_stock -= 2

      self.ch4_stock += 1
      self.o2_stock += 2
      self.co_stock += 2
    else:
      print("Not enough feedstock")

  def electrolysis(self):
    if self.h2o_stock >= 1:
      self.h20_stock -= 1
      self.h2_stock += 1
      self.o_stock += 1
    else:
      print("Not enough feedstock")

  def hydrogen_addition(self, ammount):
    self.h2_stock += ammount

  def atmosphere_intake(self, ammount):
    self.co2_stock += ammount

  def water_addition(self, ammount):
    self.h2o_stock += ammount
