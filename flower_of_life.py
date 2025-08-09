from tkinter import Tk, Canvas
from math import sqrt


class FlowerOfLifeApp:
    """Interactive 3‑D Flower of Life visualizer using Tkinter.

    * Drag the red handle to scale the entire pattern.
    * Press ``t`` to add a tetrahedron.
    * Press ``c`` to add a cube.
    """

    def __init__(self, layers: int = 2, spacing: int = 50) -> None:
        self.layers = layers
        self.spacing = spacing
        self.scale = 1.0

        self.root = Tk()
        self.root.title("3D Flower of Life")
        self.canvas = Canvas(self.root, width=800, height=600, bg="white")
        self.canvas.pack()
        self.center = (400, 300)

        self.extra_shapes: list[tuple[list[tuple[float, float, float]], list[tuple[int, int]]]] = []

        self._build_points()
        self._draw()

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("t", lambda _: self.add_tetrahedron())
        self.root.bind("c", lambda _: self.add_cube())

    # ------------------------------------------------------------------
    # Geometry construction
    # ------------------------------------------------------------------
    def _build_points(self) -> None:
        points2d: list[tuple[float, float]] = []
        L = self.layers
        for q in range(-L, L + 1):
            for r in range(-L, L + 1):
                s = -q - r
                if abs(s) <= L:
                    x = self.spacing * (q + r / 2)
                    y = self.spacing * (r * sqrt(3) / 2)
                    points2d.append((x, y))

        points3d: list[list[float]] = []
        for x, y in points2d:
            for k in range(-L, L + 1):
                z = self.spacing * k
                points3d.append([x, y, z])

        self.original_points = points3d
        self.points = [p[:] for p in points3d]

        distances = [self._distance(p) for p in self.points]
        self.handle_index = distances.index(max(distances))
        self.base_handle_distance = distances[self.handle_index]
        self.base_handle_screen_distance: float | None = None

    def _distance(self, p: list[float]) -> float:
        x, y, z = p
        return sqrt(x * x + y * y + z * z)

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _project(self, p: list[float]) -> tuple[float, float, float]:
        x, y, z = p
        d = 10 * self.spacing
        f = d / (d - z)
        sx = x * f + self.center[0]
        sy = -y * f + self.center[1]
        r = self.spacing * f * 0.5
        return sx, sy, r

    def _draw(self) -> None:
        self.canvas.delete("all")
        for idx, p in enumerate(self.points):
            sx, sy, r = self._project(p)
            self.canvas.create_oval(sx - r, sy - r, sx + r, sy + r, outline="blue")
            if idx == self.handle_index:
                self.canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, fill="red", outline="")
                if self.base_handle_screen_distance is None:
                    cx, cy = self.center
                    self.base_handle_screen_distance = sqrt((sx - cx) ** 2 + (sy - cy) ** 2)

        for verts, edges in self.extra_shapes:
            pts = [
                self._project(
                    [v[0] * self.scale * self.spacing,
                     v[1] * self.scale * self.spacing,
                     v[2] * self.scale * self.spacing]
                )
                for v in verts
            ]
            pts2d = [(x, y) for x, y, _ in pts]
            for a, b in edges:
                ax, ay = pts2d[a]
                bx, by = pts2d[b]
                self.canvas.create_line(ax, ay, bx, by, fill="green", width=2)

    # ------------------------------------------------------------------
    # Interaction events
    # ------------------------------------------------------------------
    def _on_press(self, event) -> None:
        hx, hy, _ = self._project(self.points[self.handle_index])
        if (event.x - hx) ** 2 + (event.y - hy) ** 2 <= 25:
            self.dragging = True
        else:
            self.dragging = False

    def _on_drag(self, event) -> None:
        if not getattr(self, "dragging", False):
            return
        cx, cy = self.center
        dist = sqrt((event.x - cx) ** 2 + (event.y - cy) ** 2)
        new_scale = dist / self.base_handle_screen_distance
        self.scale = new_scale
        self.points = [[x * new_scale, y * new_scale, z * new_scale] for x, y, z in self.original_points]
        self._draw()

    def _on_release(self, _event) -> None:
        self.dragging = False

    # ------------------------------------------------------------------
    # Additional sacred geometries
    # ------------------------------------------------------------------
    def add_tetrahedron(self) -> None:
        s = 1
        verts = [
            (0, 0, s),
            (2 * sqrt(2) / 3 * s, 0, -s / 3),
            (-sqrt(2) / 3 * s, sqrt(6) / 3 * s, -s / 3),
            (-sqrt(2) / 3 * s, -sqrt(6) / 3 * s, -s / 3),
        ]
        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3), (3, 1)]
        self.extra_shapes.append((verts, edges))
        self._draw()

    def add_cube(self) -> None:
        s = 1
        verts = [(x * s, y * s, z * s) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
        edges: list[tuple[int, int]] = []
        idx = lambda x, y, z: ((x + 1) // 2) * 4 + ((y + 1) // 2) * 2 + ((z + 1) // 2)
        for x in (-1, 1):
            for y in (-1, 1):
                edges.append((idx(x, y, -1), idx(x, y, 1)))
        for z in (-1, 1):
            for x in (-1, 1):
                edges.append((idx(x, -1, z), idx(x, 1, z)))
        for z in (-1, 1):
            for y in (-1, 1):
                edges.append((idx(-1, y, z), idx(1, y, z)))
        self.extra_shapes.append((verts, edges))
        self._draw()

    # ------------------------------------------------------------------
    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    app = FlowerOfLifeApp(layers=2, spacing=50)
    app.run()

