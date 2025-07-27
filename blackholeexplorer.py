import tkinter as tk
from math import sqrt, pi

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 400
BLACK_HOLE_RADIUS = 20
BALL_RADIUS = 5
BLACK_HOLE_POSITION = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
GRAVITATIONAL_CONSTANT = 0.1
MAX_AURA_SIZE = 100
AURA_GROWTH_RATE = 2
AURA_ROTATION_SPEED = 5
SPAGHETTIFICATION_THRESHOLD = 100

class BlackHoleSimulator:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='black')
        self.canvas.pack()

        self.balls = []
        self.consumed_mass = 0
        self.aura_size = BLACK_HOLE_RADIUS
        self.aura_angle = 0

        self.black_hole_id = self._draw_black_hole()
        self.aura_ids = self._draw_aura()

        reset_button = tk.Button(master, text="Reset Black Hole", command=self._reset)
        reset_button.pack()

        self.master.bind("<Button-1>", self._spawn_ball)
        self._update()

    def _draw_black_hole(self):
        x, y = BLACK_HOLE_POSITION
        return self.canvas.create_oval(
            x - BLACK_HOLE_RADIUS, y - BLACK_HOLE_RADIUS,
            x + BLACK_HOLE_RADIUS, y + BLACK_HOLE_RADIUS,
            fill='white'
        )

    def _draw_aura(self):
        aura_ids = []
        for i in range(1, 4):
            start_angle = self.aura_angle + 90 * i
            aura_id = self.canvas.create_arc(
                BLACK_HOLE_POSITION[0] - self.aura_size * i,
                BLACK_HOLE_POSITION[1] - self.aura_size * i,
                BLACK_HOLE_POSITION[0] + self.aura_size * i,
                BLACK_HOLE_POSITION[1] + self.aura_size * i,
                start=start_angle,
                extent=90,
                style=tk.ARC,
                outline="blue"
            )
            aura_ids.append(aura_id)
        return aura_ids

    def _update_aura(self):
        self.aura_size = BLACK_HOLE_RADIUS + min(MAX_AURA_SIZE, self.consumed_mass * AURA_GROWTH_RATE)

    def _rotate_aura(self):
        self.aura_angle = (self.aura_angle + AURA_ROTATION_SPEED) % 360
        for aura_id in self.aura_ids:
            self.canvas.delete(aura_id)
        self.aura_ids = self._draw_aura()

    def _spawn_ball(self, event):
        velocity = self._calculate_velocity((event.x, event.y), BLACK_HOLE_POSITION, (0, 0))
        ball_id = self.canvas.create_oval(
            event.x - BALL_RADIUS, event.y - BALL_RADIUS,
            event.x + BALL_RADIUS, event.y + BALL_RADIUS,
            fill='red'
        )
        self.balls.append((ball_id, velocity, BALL_RADIUS))

    def _reset(self):
        self.consumed_mass = 0
        self.aura_size = BLACK_HOLE_RADIUS
        for ball_id, _, _ in self.balls:
            self.canvas.delete(ball_id)
        self.balls.clear()
        for aura_id in self.aura_ids:
            self.canvas.delete(aura_id)
        self.aura_ids = self._draw_aura()

    def _calculate_velocity(self, start_pos, end_pos, speed):
        dx, dy = end_pos[0] - start_pos[0], end_pos[1] - start_pos[1]
        distance = sqrt(dx**2 + dy**2)
        if distance == 0:
            return 0, 0
        normalized_dx, normalized_dy = dx / distance, dy / distance
        force = GRAVITATIONAL_CONSTANT * (1 / (distance / 50))
        return normalized_dx * force + speed[0], normalized_dy * force + speed[1]

    def _calculate_spaghettification(self, radius, distance):
        if distance > SPAGHETTIFICATION_THRESHOLD:
            return radius, radius
        stretch_factor = max(1, (SPAGHETTIFICATION_THRESHOLD - distance) / 20)
        shrink_factor = max(0.2, distance / SPAGHETTIFICATION_THRESHOLD)
        new_radius = radius * shrink_factor
        return new_radius * stretch_factor, new_radius / stretch_factor

    def _update(self):
        for i, (ball_id, velocity, radius) in enumerate(self.balls):
            self.canvas.move(ball_id, *velocity)
            pos = self.canvas.coords(ball_id)
            center_x, center_y = (pos[0] + pos[2]) / 2, (pos[1] + pos[3]) / 2
            distance = sqrt((center_x - BLACK_HOLE_POSITION[0]) ** 2 + (center_y - BLACK_HOLE_POSITION[1]) ** 2)
            velocity = self._calculate_velocity((center_x, center_y), BLACK_HOLE_POSITION, velocity)
            stretched_radius, _ = self._calculate_spaghettification(radius, distance)

            self.canvas.delete(ball_id)
            if distance < SPAGHETTIFICATION_THRESHOLD:
                ball_id = self.canvas.create_oval(
                    center_x - stretched_radius, center_y - radius / 2,
                    center_x + stretched_radius, center_y + radius / 2,
                    fill='red'
                )
            else:
                ball_id = self.canvas.create_oval(
                    center_x - radius, center_y - radius,
                    center_x + radius, center_y + radius,
                    fill='red'
                )

            self.balls[i] = (ball_id, velocity, radius)

            if distance < BLACK_HOLE_RADIUS + radius:
                self.canvas.delete(ball_id)
                self.balls.pop(i)
                self.consumed_mass += 1
                self._update_aura()

        self._rotate_aura()
        self.master.after(50, self._update)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Black Hole Simulator")
    app = BlackHoleSimulator(root)
    root.mainloop()

