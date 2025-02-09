import pygame
import random
import math

# -------------------------------
# Slider class for interactive controls
# -------------------------------
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handle_radius = height // 2
        self.handle_x = self.value_to_pos(self.value)
        self.dragging = False

    def value_to_pos(self, value):
        # Map a value to a position along the slider track.
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.x + int(ratio * self.width)

    def pos_to_value(self, pos):
        # Map a horizontal position to a slider value.
        ratio = (pos - self.x) / self.width
        value = self.min_val + ratio * (self.max_val - self.min_val)
        return max(self.min_val, min(self.max_val, value))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            # If the mouse is on the handle, start dragging.
            if math.hypot(mx - self.handle_x, my - (self.y + self.height // 2)) <= self.handle_radius:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, _ = event.pos
            # Clamp the handle position to the slider bounds.
            mx = max(self.x, min(self.x + self.width, mx))
            self.handle_x = mx
            self.value = self.pos_to_value(mx)

    def draw(self, surface, color_slider=(180, 180, 180), color_handle=(100, 100, 100)):
        # Draw the slider track.
        pygame.draw.rect(surface, color_slider, (self.x, self.y + self.height // 2 - 5, self.width, 10))
        # Draw the handle.
        pygame.draw.circle(surface, color_handle, (self.handle_x, self.y + self.height // 2), self.handle_radius)


# -------------------------------
# Molecule class for gas particles
# -------------------------------
class Molecule:
    def __init__(self, container_rect, temperature):
        self.container_rect = container_rect  # (left, top, right, bottom)
        # Start at a random position inside the container.
        self.x = random.uniform(container_rect[0] + 5, container_rect[2] - 5)
        self.y = random.uniform(container_rect[1] + 5, container_rect[3] - 5)
        # Choose a random direction.
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle)
        self.vy = math.sin(angle)
        # Speed is proportional to temperature.
        self.speed = 0.002 * temperature  # Adjust factor for visualization.
        self.radius = 3

    def update(self, dt, temperature, container_rect):
        # Update speed based on the current temperature.
        self.speed = 0.002 * temperature
        # Move the molecule.
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt

        left, top, right, bottom = container_rect

        # Bounce off the left wall.
        if self.x - self.radius < left:
            self.x = left + self.radius
            self.vx = -self.vx
        # Bounce off the top wall.
        if self.y - self.radius < top:
            self.y = top + self.radius
            self.vy = -self.vy
        # Bounce off the bottom wall.
        if self.y + self.radius > bottom:
            self.y = bottom - self.radius
            self.vy = -self.vy
        # Bounce off the piston (right wall).
        if self.x + self.radius > right:
            self.x = right - self.radius
            self.vx = -self.vx

        # Normalize the velocity vector.
        norm = math.sqrt(self.vx**2 + self.vy**2)
        if norm:
            self.vx /= norm
            self.vy /= norm

    def draw(self, surface, color=(0, 0, 255)):
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)


# -------------------------------
# Main simulation function
# -------------------------------
def main():
    pygame.init()
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Gas Laws Simulation: Coupled Volume/Temp")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 16)
    large_font = pygame.font.SysFont("Arial", 20)

    # Define container boundaries.
    container_left = 50
    container_top = 50
    container_bottom = 450
    container_height = container_bottom - container_top

    # Create two sliders:
    # 1. Piston slider: controls volume (by moving the piston).
    piston_slider = Slider(x=50, y=500, width=300, height=20, min_val=150, max_val=750, initial_val=500)
    # 2. Temperature slider: simulates adding or removing energy (without changing volume).
    temp_slider = Slider(x=400, y=500, width=300, height=20, min_val=10, max_val=300, initial_val=30)

    # Set the coupling parameters.
    # Here we use an adiabatic-like relation: T * L^(gamma-1) = K,
    # where L = piston_slider.value - container_left (the effective length).
    gamma = 1.4  # Heat capacity ratio.
    L0 = piston_slider.value - container_left
    T0 = temp_slider.value
    K = T0 * (L0 ** (gamma - 1))  # Energy state constant.

    # Create gas molecules.
    num_molecules = 50
    container_rect = (container_left, container_top, piston_slider.value, container_bottom)
    molecules = [Molecule(container_rect, temp_slider.value) for _ in range(num_molecules)]

    running = True
    while running:
        dt = clock.tick(60)  # Milliseconds since last frame.
        dt_sec = dt / 1000.0  # Convert to seconds.

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            piston_slider.handle_event(event)
            temp_slider.handle_event(event)

        # --- Coupling Logic ---
        # Effective length (analogous to volume) of the container:
        L = piston_slider.value - container_left
        if L < 1:  # Prevent division by zero.
            L = 1

        if temp_slider.dragging:
            # Temperature slider is active:
            # This simulates adding/removing energy.
            # Update the energy state K without changing the volume.
            K = temp_slider.value * (L ** (gamma - 1))
        elif piston_slider.dragging:
            # Piston slider is active:
            # Change in volume causes an adiabatic change in temperature.
            # Calculate the new temperature from the current energy state.
            new_T = K / (L ** (gamma - 1))
            # Update the temperature slider value accordingly.
            temp_slider.value = new_T
            temp_slider.handle_x = temp_slider.value_to_pos(new_T)

        # --- Update Simulation ---
        # Update the container's right wall (piston) from the piston slider.
        container_rect = (container_left, container_top, piston_slider.value, container_bottom)
        for molecule in molecules:
            molecule.update(dt, temp_slider.value, container_rect)

        # Compute the (2D) "volume" (area) of the container.
        volume = (piston_slider.value - container_left) * container_height
        # Compute pressure using a simplified ideal gas law: P ~ (n * T) / V.
        pressure = (num_molecules * temp_slider.value / volume) * 50  # scaling factor for visualization

        # --- Drawing ---
        screen.fill((255, 255, 255))
        # Draw container walls.
        pygame.draw.line(screen, (0, 0, 0), (container_left, container_top), (container_left, container_bottom), 2)
        pygame.draw.line(screen, (0, 0, 0), (container_left, container_top), (piston_slider.value, container_top), 2)
        pygame.draw.line(screen, (0, 0, 0), (container_left, container_bottom), (piston_slider.value, container_bottom), 2)
        # Draw the piston.
        pygame.draw.line(screen, (150, 0, 0), (piston_slider.value, container_top), (piston_slider.value, container_bottom), 4)

        # Draw gas molecules.
        for molecule in molecules:
            molecule.draw(screen)

        # Draw sliders and their labels.
        piston_slider.draw(screen)
        temp_slider.draw(screen)
        piston_label = font.render("Piston Position (Volume)", True, (0, 0, 0))
        screen.blit(piston_label, (piston_slider.x, piston_slider.y - 20))
        temp_label = font.render("Temperature (Energy Added)", True, (0, 0, 0))
        screen.blit(temp_label, (temp_slider.x, temp_slider.y - 20))

        # Draw gauges.
        pressure_text = large_font.render(f"Pressure: {pressure:.2f}", True, (0, 0, 0))
        screen.blit(pressure_text, (600, 50))
        temperature_text = large_font.render(f"Temperature: {temp_slider.value:.1f}", True, (0, 0, 0))
        screen.blit(temperature_text, (600, 80))
        volume_text = large_font.render(f"Volume: {volume:.0f}", True, (0, 0, 0))
        screen.blit(volume_text, (600, 110))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
