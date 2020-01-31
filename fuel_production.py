from ISRU import Atmospheric_processing_unit
import random
import matplotlib.pyplot as plt


apu = Atmospheric_processing_unit()

apu.hydrogen_addition(500)
apu.atmosphere_intake(50)



CO2_record = [apu.co2_stock]
H2O_record = [apu.h2o_stock]
CO_record = [apu.co_stock]
CH4_record = [apu.ch4_stock]
H2_record = [apu.h2_stock]
O2_record = [apu.o2_stock]

while apu.h2_stock >= 2:
  if apu.co2_stock < 10:
    apu.atmosphere_intake(25)

  apu.sabatier_rwgs()

  CO2_record.append(apu.co2_stock)
  H2O_record.append(apu.h2o_stock)
  CO_record.append(apu.co_stock)
  CH4_record.append(apu.ch4_stock)
  H2_record.append(apu.h2_stock)
  O2_record.append(apu.o2_stock)



plt.figure(num=None, figsize=(15, 6), dpi=80, facecolor='w', edgecolor='k')

x = range(0, len(CH4_record))

plt.plot(x, CO2_record, label = 'CO2')
plt.plot(x, H2O_record, label = 'H2O')
plt.plot(x, CO_record, label = 'CO')
plt.plot(x, CH4_record, label = 'CH4')
plt.plot(x, H2_record, label = 'H2')
plt.plot(x, O2_record, label = 'O2')

plt.legend()
plt.show();
