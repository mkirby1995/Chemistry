import pandas as pd
import numpy as np

def balance(equation_str):
    return_dict = {}
    for species in equation.replace('->', '+').split('+'):
        return_dict[species.strip()] = {}
        for element in species.strip().split(' '):
            if len(element) < 3:
                element += '_1'
            return_dict[species.strip()][element.split('_')[0]] = element.split('_')[1]


    # Lawrence R. Thorne: Simplified Matrix Null-Space Method

    # Step 0
    chem_comp_table = pd.DataFrame(return_dict, dtype = 'float').fillna(0)
    #print("Step 0\n", chem_comp_table)
    #print('\n')

    # Step 1
    chem_comp_matrix = chem_comp_table.values
    #print("Step 1\n", chem_comp_matrix)
    #print('\n')

    # Step 2
    nullity = len(chem_comp_table.columns) - np.linalg.matrix_rank(chem_comp_matrix)
    if nullity == 0:
        return "No solution"
    #print("Step 2\n", nullity)
    #print('\n')

    # Step 3
    a = np.zeros((nullity, chem_comp_matrix.shape[1]))
    b = np.identity(nullity)
    augmentation = np.append(a[:, :a.shape[1] - b.shape[1]], b, axis = 1)
    augmented_ccm = np.append(chem_comp_matrix, augmentation, axis = 0)
    #print("Step 3\n", augmented_ccm)
    #print('\n')

    # Step 4
    inverted_ccm = np.linalg.inv(augmented_ccm)
    #print("Step 4\n", inverted_ccm)
    #print('\n')

    # Step 5 & 6
    null_space_vec = inverted_ccm[:, -nullity].T
    #print("Step 5 & 6\n", null_space_vec)
    #print('\n')

    # Step 7
    coefs = null_space_vec / min([abs(i) for i in list(null_space_vec)])
    if (float("inf") in coefs) or (float("-inf") in coefs):
        return "Infinite solutions"
    coefs = [int(round(abs(i))) for i in coefs]
    #print("Step 7\n", coefs)
    #print('\n')

    # Step 8
    species = [i.strip() for i in equation.replace('->', '+').split('+')]
    for i in range(len(species)):
        return_dict[species[i]] = coefs[i]

    return_eq = []

    for side in equation.split('->'):
        new_side = []
        for species in side.split('+'):
            #print(return_dict[species.strip()], species.strip())
            new_side.append(str(return_dict[species.strip()]) + str(species.strip()))
        return_eq.append(' + '.join(new_side))

    return ' -> '.join(return_eq)

"""
Examples


equation = 'C H_4 + H_2 O -> C O_2 + H_2'
balance(equation)

'1C H_4 + 2H_2 O -> 1C O_2 + 4H_2'


equation = 'K I + K Cl O_3 + H Cl -> I_2 + H_2 O + K Cl'
balance(equation)

'6K I + 1K Cl O_3 + 6H Cl -> 3I_2 + 3H_2 O + 7K Cl'


equation = 'Fe S_2 + H N O_3 -> Fe_2 S_3 O_12 + N O + H_2 S O_4'
balance(equation)

'No solution'
"""




avogadro = 6.0221409E23


def atoms_to_moles(atoms):
    return atoms / avogadro


def moles_to_mass(moles, molar_mass):
    return moles * molar_mass


def mass_to_moles(mass, molar_mass):
    return mass / molar_mass


def moles_to_atoms(moles):
    return moles * avogadro




def chem_spliter(chem):
    """
    Input: Chemical formula in form (H_2 O)
    Output: Array of tuples shape (Chem abbv, ,moles)
    """
    return_array = []
    for i in chem.split(' '):
        return_array.append((i.split('_')[0],i.split('_')[1]))
    return return_array

def percent_composition(chemical):
    """
    Input: Chemical formula in form (H_2 O)
    Output: Dict in form {Element: %comp}
    """
    return_dict = {}
    masses = []
    chem_spliter(chemical)

    for i in chem_spliter(chemical):
        masses.append(elements[i[0]]['atomic_mass'] * int(i[1]))

    chemical_mass = sum(masses)

    for k, v in zip(chem_spliter(chemical), masses):
        return_dict[k[0]] = (v / chemical_mass) * 100

    return return_dict
