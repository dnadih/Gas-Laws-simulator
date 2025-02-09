Below is a sample Markdown description of the simulator app. You can use this in your project’s README or documentation on GitHub.

---

# Gas Laws Simulator

This simulator demonstrates key gas laws and thermodynamic principles by visualizing gas behavior in a 2D container with a movable piston. The simulation uses simplified physics to illustrate how changes in volume and temperature affect the gas pressure and the speed of its molecules.

## Features

- **2D Container & Piston:**  
  A rectangular container is drawn with a fixed left wall and a movable right wall (piston). The effective volume is adjusted by dragging the piston slider.

- **Gas Molecules:**  
  Gas is represented by small circles (molecules) that move randomly within the container. Their speed is proportional to the gas temperature.

- **Interactive Sliders:**
  - **Piston Slider (Volume):**  
    Moving the piston changes the container's volume. When the volume decreases (compression), the gas temperature increases, and vice versa.
  - **Temperature Slider (Energy):**  
    Adjusting the temperature slider simulates adding or removing energy from the system, directly setting the gas temperature without changing the volume.

- **Gauges:**  
  Real-time displays show the current **pressure**, **temperature**, and **volume** of the gas.

## Physics Behind the Simulator

### Adiabatic Process Coupling

When you move the piston, the simulator models an adiabatic-like process. In an adiabatic process (no heat exchange with the surroundings), the relation between temperature and volume is given by:

\[
T \, V^{\gamma - 1} = \text{constant}
\]

In this simulation:
- The effective length \( L \) is defined as:
  \[
  L = \texttt{piston\_slider.value} - \texttt{container\_left}
  \]
- The energy state of the gas is characterized by the constant:
  \[
  K = T \, L^{\gamma-1}
  \]
  where:
  - \( T \) is the temperature,
  - \( \gamma \) is the heat capacity ratio (typically \(\gamma = 1.4\) for diatomic gases).

Thus, when the **piston slider** is moved (changing \( L \)), the temperature is recalculated as:

\[
T = \frac{K}{L^{\gamma-1}}
\]

### Energy Addition Without Volume Change

When you move the **temperature slider**, you are directly adding or removing energy from the system:
- The temperature \( T \) is set directly by the slider.
- The energy constant \( K \) is updated accordingly:
  \[
  K = T \, L^{\gamma-1}
  \]
- The volume remains unchanged.

### Pressure Calculation

The pressure in the simulator is computed using a simplified version of the ideal gas law:

\[
P \sim \frac{n\,T}{V}
\]

where:
- \( n \) is the number of gas molecules,
- \( T \) is the temperature,
- \( V \) is the volume (computed as the effective length \( L \) times the container height).

A scaling factor is applied to ensure the numerical values are visually significant in the simulation.

## How to Run the Simulator

1. **Install Pygame:**  
   Make sure you have Pygame installed:
   ```bash
   pip install pygame
   ```

2. **Run the Application:**  
   Save the simulator code in a file (e.g., `gas_simulation.py`) and run it with:
   ```bash
   python gas_simulation.py
   ```

3. **Interact:**  
   - **Drag the Piston Slider:** Observe that reducing the volume increases the gas temperature (simulating adiabatic compression) and vice versa.
   - **Drag the Temperature Slider:** Directly add or remove energy from the gas. The volume remains fixed while the pressure and the motion of the gas molecules change.

Enjoy exploring the behavior of gases through this interactive simulation!

---
