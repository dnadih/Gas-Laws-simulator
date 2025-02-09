import pygame
import random
import math
import pygame.gfxdraw

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
        ratio = (value - self.min_val) / (self.max_val - self.min_val)
        return self.x + int(ratio * self.width)

    def pos_to_value(self, pos):
        ratio = (pos - self.x) / self.width
        value = self.min_val + ratio * (self.max_val - self.min_val)
        return max(self.min_val, min(self.max_val, value))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if math.hypot(mx - self.handle_x, my - (self.y + self.height//2)) <= self.handle_radius:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mx, _ = event.pos
            mx = max(self.x, min(self.x + self.width, mx))
            self.handle_x = mx
            self.value = self.pos_to_value(mx)

# -------------------------------
# Enhanced Molecule Class with Temperature Coloring
# -------------------------------
class Molecule:
    def __init__(self, container_rect, temperature):
        self.container_rect = container_rect
        self.x = random.uniform(container_rect[0] + 5, container_rect[2] - 5)
        self.y = random.uniform(container_rect[1] + 5, container_rect[3] - 5)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = math.cos(angle)
        self.vy = math.sin(angle)
        self.speed = 0.5 * temperature
        self.radius = 3

    def update(self, dt, temperature, container_rect):
        self.speed = 0.5 * temperature
        self.x += self.vx * self.speed * dt
        self.y += self.vy * self.speed * dt

        left, top, right, bottom = container_rect
        if self.x - self.radius < left:
            self.x = left + self.radius
            self.vx = -self.vx
        if self.y - self.radius < top:
            self.y = top + self.radius
            self.vy = -self.vy
        if self.y + self.radius > bottom:
            self.y = bottom - self.radius
            self.vy = -self.vy
        if self.x + self.radius > right:
            self.x = right - self.radius
            self.vx = -self.vx

        norm = math.sqrt(self.vx**2 + self.vy**2)
        if norm:
            self.vx /= norm
            self.vy /= norm

    def draw(self, surface, color=None):
        # Color will be handled in main drawing loop
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.radius)

# -------------------------------
# Main Simulation Function (with graphical enhancements)
# -------------------------------
def main():
    pygame.init()
    screen_width, screen_height = 1000, 700
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Gas Laws Simulation - Enhanced")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18, bold=True)
    large_font = pygame.font.SysFont("Arial", 24, bold=True)
    
    # Colors
    BACKGROUND_COLOR = (245, 245, 250)
    CONTAINER_COLOR = (144, 238, 144)  # LightGreen
    PISTON_COLOR = (150, 160, 180)
    ACCENT_COLOR = (50, 80, 150)
    HOT_COLOR = (255, 80, 80)
    COLD_COLOR = (80, 150, 255)

    # Improved container dimensions
    container_left = 100
    container_top = 100
    container_bottom = 500
    container_height = container_bottom - container_top

    # Create sliders with new positions
    piston_slider = Slider(x=100, y=580, width=400, height=25,
                         min_val=container_left + 100, max_val=800, initial_val=500)
    temp_slider = Slider(x=550, y=580, width=400, height=25,
                       min_val=1, max_val=400, initial_val=30)

    # Set the coupling parameters.
    # Here we use an adiabatic-like relation: T * L^(gamma-1) = K,
    # where L = piston_slider.value - container_left (the effective length).
    gamma = 1.4  # Heat capacity ratio.
    L0 = piston_slider.value - container_left
    T0 = temp_slider.value
    K = T0 * (L0 ** (gamma - 1))  # Energy state constant.

    num_molecules = 80
    container_rect = (container_left, container_top, piston_slider.value, container_bottom)
    molecules = [Molecule(container_rect, temp_slider.value) for _ in range(num_molecules)]

    # Gradient background surface
    background = pygame.Surface((screen_width, screen_height))
    for y in range(screen_height):
        alpha = int(255 * (1 - y/screen_height))
        pygame.draw.line(background, (230 - y//30, 235 - y//30, 255), (0, y), (screen_width, y))

    # Glass effect for container
    container_glass = pygame.Surface((1, container_height), pygame.SRCALPHA) # Initial width set to 1, will be updated dynamically
    pygame.draw.rect(container_glass, (255, 255, 255, 50), (0, 0, 1, container_height), border_radius=10) # Initial width set to 1
    for i in range(5):
        pygame.draw.line(container_glass, (255, 255, 255, 100),
                        (i*80, 0), (i*80, container_height), 2)

    # Piston appearance
    piston_texture = pygame.Surface((20, container_height), pygame.SRCALPHA)
    pygame.draw.rect(piston_texture, (180, 190, 200), (0, 0, 20, container_height), border_radius=3)
    pygame.draw.rect(piston_texture, (200, 210, 220), (2, 2, 16, container_height-4), border_radius=2)
    
    # Particle trail surfaces
    trail_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    trail_surface.set_alpha(50)  # Semi-transparent trails

    # Gauges setup
    gauge_bg = pygame.Surface((300, 210), pygame.SRCALPHA)
    pygame.draw.rect(gauge_bg, (255, 255, 255, 200), (0, 0, 300, 150), border_radius=15)
    pygame.draw.rect(gauge_bg, (0, 0, 0, 30), (0, 0, 300, 150), 2, border_radius=15)

    running = True
    while running:
        dt = clock.tick(60)
        dt_sec = dt / 1000.0

        # Event handling
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


        # Update physics and relationships
        volume = (piston_slider.value - container_left) * container_height


        # Update molecules
        container_rect = (container_left, container_top, piston_slider.value, container_bottom)
        for molecule in molecules:
            molecule.update(dt_sec, temp_slider.value, container_rect)

        # Calculate metrics
        volume = (piston_slider.value - container_left) * container_height
        pressure = (num_molecules * temp_slider.value / volume) * 50 if volume != 0 else 0

        # --- Drawing ---
        screen.blit(background, (0, 0))
        
        # Draw container
        container_surface = pygame.Surface((piston_slider.value - container_left, container_height), pygame.SRCALPHA)
        container_surface.fill(CONTAINER_COLOR + (50,))
        pygame.draw.rect(container_surface, (255, 255, 255, 30),
                       (0, 0, piston_slider.value - container_left, container_height), 3)
        screen.blit(container_surface, (container_left, container_top))
        
        # Draw glass effect
        screen.blit(container_glass, (container_left, container_top),
                  (0, 0, piston_slider.value - container_left, container_height))
        
        # Draw piston
        piston_pos = piston_slider.value
        screen.blit(piston_texture, (piston_pos - 10, container_top))
        pygame.draw.line(screen, (200, 210, 220), (piston_pos, container_top),
                        (piston_pos, container_bottom), 4)
        
        # Draw molecules with trails
        trail_surface.fill((0, 0, 0, 0))  # Clear trail surface
        for molecule in molecules:
            # Color based on speed (temperature)
            max_speed = 0.2 * temp_slider.max_val  # Calculate based on max temperature
            speed_ratio = molecule.speed / max_speed
            #speed_ratio = molecule.speed / (5 * temp_slider.max_val)
            speed_ratio = max(0.0, min(speed_ratio, 1.0))
            color = tuple(int(a + (b-a)*speed_ratio) for a, b in zip(COLD_COLOR, HOT_COLOR))
            
            # Draw trail
            pygame.gfxdraw.filled_circle(trail_surface, int(molecule.x), int(molecule.y),
                                       molecule.radius + 1, (*color, 30))
            
            # Draw molecule
            pygame.gfxdraw.filled_circle(screen, int(molecule.x), int(molecule.y),
                                       molecule.radius + 2, (*color, 200))
            pygame.gfxdraw.aacircle(screen, int(molecule.x), int(molecule.y),
                                  molecule.radius + 2, (*color, 200))
        
        screen.blit(trail_surface, (0, 0))
        
        # Draw sliders with new style
        def draw_modern_slider(slider, label):
            # Track
            pygame.draw.rect(screen, (220, 220, 230),
                           (slider.x, slider.y + slider.height//2 - 8, slider.width, 16),
                           border_radius=8)
            # Handle
            pygame.draw.circle(screen, ACCENT_COLOR, (slider.handle_x, slider.y + slider.height//2),
                             slider.handle_radius + 2)
            pygame.draw.circle(screen, (255, 255, 255), (slider.handle_x, slider.y + slider.height//2),
                             slider.handle_radius - 2)
            # Label
            text = font.render(label, True, (50, 50, 70))
            screen.blit(text, (slider.x, slider.y - 30))

        draw_modern_slider(piston_slider, "VOLUME")
        draw_modern_slider(temp_slider, "TEMPERATURE (K)")

        # Draw gauges
        screen.blit(gauge_bg, (650, 50))

        # Pressure gauge improvements
        gauge_center_x, gauge_center_y = 710, 110
        gauge_radius = 40
        
        # Background circle for gauge
        pygame.draw.circle(screen, (230, 230, 230), (gauge_center_x, gauge_center_y), gauge_radius)
        pygame.draw.circle(screen, ACCENT_COLOR, (gauge_center_x, gauge_center_y), gauge_radius, 2)

        # Tick marks
        for angle_deg in range(220, -61, -40): # More ticks for clarity
            angle_rad = math.radians(angle_deg)
            tick_length = 8
            tick_start_x = gauge_center_x + (gauge_radius - tick_length) * math.cos(angle_rad)
            tick_start_y = gauge_center_y + (gauge_radius - tick_length) * math.sin(angle_rad)
            tick_end_x = gauge_center_x + gauge_radius * math.cos(angle_rad)
            tick_end_y = gauge_center_y + gauge_radius * math.sin(angle_rad)
            pygame.draw.line(screen, ACCENT_COLOR, (tick_start_x, tick_start_y), (tick_end_x, tick_end_y), 2)
        
        # Pressure needle - more pronounced needle
        pressure_angle = 220 - (pressure/150)*280
        needle_length = gauge_radius - 5
        needle_end_x = gauge_center_x + needle_length * math.cos(math.radians(pressure_angle))
        needle_end_y = gauge_center_y + needle_length * math.sin(math.radians(pressure_angle))
        pygame.draw.line(screen, HOT_COLOR, (gauge_center_x, gauge_center_y), (needle_end_x, needle_end_y), 3)
        pygame.draw.circle(screen, HOT_COLOR, (gauge_center_x, gauge_center_y), 5) # Needle base

        # Text labels
        pressure_text = large_font.render(f"{pressure:.1f} kPa", True, ACCENT_COLOR)
        screen.blit(pressure_text, (760, 80))
        temp_text = large_font.render(f"{temp_slider.value:.0f} K", True, HOT_COLOR)
        screen.blit(temp_text, (760, 120))
        vol_text = large_font.render(f"V: {volume//1000:.1f} L", True, COLD_COLOR)
        screen.blit(vol_text, (760, 160))

        # Add subtle shadow under piston
        shadow = pygame.Surface((20, container_height), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 30))
        screen.blit(shadow, (piston_slider.value - 5, container_top + 5))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
