import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define fuzzy variables with extended ranges
temperature = ctrl.Antecedent(np.arange(0, 101, 1), 'temperature')
vibration = ctrl.Antecedent(np.arange(0, 10, 1), 'vibration')
noise = ctrl.Antecedent(np.arange(0, 3, 1), 'noise')
alignment = ctrl.Antecedent(np.arange(0, 3, 1), 'alignment')
overheating = ctrl.Antecedent(np.arange(0, 3, 1), 'overheating')
cause = ctrl.Consequent(np.arange(0, 101, 1), 'cause')

# Define fuzzy membership functions with expanded granularity
temperature['low'] = fuzz.trimf(temperature.universe, [0, 0, 50])
temperature['medium'] = fuzz.trimf(temperature.universe, [30, 50, 70])
temperature['high'] = fuzz.trimf(temperature.universe, [50, 100, 100])

vibration['low'] = fuzz.trimf(vibration.universe, [0, 0, 3])
vibration['medium'] = fuzz.trimf(vibration.universe, [2, 5, 7])
vibration['high'] = fuzz.trimf(vibration.universe, [6, 10, 10])

noise['low'] = fuzz.trimf(noise.universe, [0, 0, 1])
noise['medium'] = fuzz.trimf(noise.universe, [0.5, 1, 1.5])
noise['high'] = fuzz.trimf(noise.universe, [1, 2, 2])

alignment['aligned'] = fuzz.trimf(alignment.universe, [0, 0, 1])
alignment['misaligned'] = fuzz.trimf(alignment.universe, [1, 2, 2])

overheating['no'] = fuzz.trimf(overheating.universe, [0, 0, 1])
overheating['yes'] = fuzz.trimf(overheating.universe, [1, 2, 2])

cause['Issue_with_low_priority'] = fuzz.trimf(cause.universe, [0, 0, 50])
cause['minor_issue'] = fuzz.trimf(cause.universe, [40, 50, 75])
cause['critical_issue'] = fuzz.trimf(cause.universe, [70, 85, 100])

# Define refined fuzzy rules
rules = [
    ctrl.Rule(temperature['high'] & vibration['high'], cause['critical_issue']),
    ctrl.Rule(vibration['high'] & alignment['misaligned'], cause['critical_issue']),
    ctrl.Rule(vibration['medium'] & overheating['yes'], cause['minor_issue']),
    ctrl.Rule(noise['high'] & vibration['medium'], cause['minor_issue']),
    ctrl.Rule(temperature['low'] & vibration['low'], cause['Issue_with_low_priority']),
]

# Create control system
refined_cause_ctrl = ctrl.ControlSystem(rules)
refined_cause_system = ctrl.ControlSystemSimulation(refined_cause_ctrl)

# Diagnose with extended observations
def diagnose_extended(temp, vib, noise_level=None, alignment_status=None, overheating_status=None):
    refined_cause_system.input['temperature'] = temp
    refined_cause_system.input['vibration'] = vib
    
    # Handle optional inputs
    if noise_level is not None:
        refined_cause_system.input['noise'] = 2 if noise_level == 'high' else (1 if noise_level == 'medium' else 0)
    if alignment_status is not None:
        refined_cause_system.input['alignment'] = 2 if alignment_status == 'misaligned' else 0
    if overheating_status is not None:
        refined_cause_system.input['overheating'] = 2 if overheating_status == 'yes' else 0

    # Compute results
    refined_cause_system.compute()
    cause_value = refined_cause_system.output['cause']

    if cause_value >= 70:
        return "Critical Issue"
    elif 40 <= cause_value < 70:
        return "Minor Issue"
    else:
        return "Issue with low priority"
