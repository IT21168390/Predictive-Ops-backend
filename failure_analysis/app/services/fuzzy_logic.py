import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define fuzzy variables
temperature = ctrl.Antecedent(np.arange(0, 101, 1), 'temperature')
vibration = ctrl.Antecedent(np.arange(0, 10, 1), 'vibration')
noise = ctrl.Antecedent(np.arange(0, 2, 1), 'noise')
alignment = ctrl.Antecedent(np.arange(0, 2, 1), 'alignment')
overheating = ctrl.Antecedent(np.arange(0, 2, 1), 'overheating')
cause = ctrl.Consequent(np.arange(0, 101, 1), 'cause')

# Define fuzzy membership functions
temperature['low'] = fuzz.trimf(temperature.universe, [0, 0, 50])
temperature['medium'] = fuzz.trimf(temperature.universe, [25, 50, 75])
temperature['high'] = fuzz.trimf(temperature.universe, [50, 100, 100])

vibration['low'] = fuzz.trimf(vibration.universe, [0, 0, 5])
vibration['medium'] = fuzz.trimf(vibration.universe, [2, 5, 8])
vibration['high'] = fuzz.trimf(vibration.universe, [6, 10, 10])

noise['no'] = fuzz.trimf(noise.universe, [0, 0, 1])
noise['yes'] = fuzz.trimf(noise.universe, [1, 2, 2])
alignment['aligned'] = fuzz.trimf(alignment.universe, [0, 0, 1])
alignment['misaligned'] = fuzz.trimf(alignment.universe, [1, 2, 2])
overheating['no'] = fuzz.trimf(overheating.universe, [0, 0, 1])
overheating['yes'] = fuzz.trimf(overheating.universe, [1, 2, 2])

cause['Drill Issue'] = fuzz.trimf(cause.universe, [75, 85, 100])
cause['Trimmer Bearing Fault'] = fuzz.trimf(cause.universe, [50, 65, 75])

# Define fuzzy rules
rules = [
    ctrl.Rule(temperature['high'] & vibration['high'], cause['Drill Issue']),
    ctrl.Rule(vibration['high'] & alignment['misaligned'], cause['Drill Issue']),
    ctrl.Rule(vibration['high'] & overheating['yes'], cause['Trimmer Bearing Fault']),
    ctrl.Rule(noise['yes'] & vibration['medium'], cause['Trimmer Bearing Fault'])
]

# Create control system
extended_cause_ctrl = ctrl.ControlSystem(rules)
extended_cause_system = ctrl.ControlSystemSimulation(extended_cause_ctrl)


# Diagnose with new observations
def diagnose_extended(temp, vib, noise_level=None, alignment_status=None, overheating_status=None):
    extended_cause_system.input['temperature'] = temp
    extended_cause_system.input['vibration'] = vib


    # Compute results
    extended_cause_system.compute()
    cause_value = extended_cause_system.output['cause']

    if cause_value >= 75:
        return "Drill Issue"
    elif 50 <= cause_value < 75:
        return "Trimmer Bearing Fault"
    else:
        return "No specific issue detected"
