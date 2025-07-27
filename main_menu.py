import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import math
import os


class FruitNinjaMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Fruit Ninja Menu")
        self.geometry("800x600")
        self.resizable(False, False)

        # Esta lista es crucial y ahora es un atributo de la clase
        self.image_references = []

        self.canvas = tk.Canvas(self, width=800, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.load_assets()
        self.create_widgets()

    def load_image(self, path, size=None):
        """Carga una imagen, la redimensiona y mantiene una referencia a ella."""
        if not os.path.exists(path):
            print(f"Error: No se encontró el archivo de imagen en '{path}'")
            return None

        try:
            pil_image = Image.open(path).convert("RGBA")
            if size:
                pil_image = pil_image.resize(size, Image.Resampling.LANCZOS)

            tk_image = ImageTk.PhotoImage(pil_image)
            self.image_references.append(tk_image)
            return tk_image
        except Exception as e:
            print(f"No se pudo cargar la imagen {path}: {e}")
            return None

    def load_assets(self):
        """Carga todas las imágenes necesarias para el menú."""
        self.bg_image = self.load_image("assets/background.png", (800, 600))
        self.title_image = self.load_image("assets/title.png", (400, 148))

        # Iconos para los botones, usando los nombres de archivo correctos
        self.icon_original = self.load_image("assets/watermelon.png", (90, 90))
        self.icon_multiplayer = self.load_image("assets/strawberry.png", (90, 90))
        self.icon_watch = self.load_image("assets/peach.png", (90, 90))

    def create_widgets(self):
        """Crea todos los elementos visuales en el canvas."""
        # 1. Fondo
        if self.bg_image:
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        else:
            self.canvas.config(bg="#1C1C1C")  # Fondo de respaldo

        # 2. Título
        if self.title_image:
            self.canvas.create_image(400, 120, image=self.title_image)
        else:
            title_font = tkfont.Font(family="Helvetica", size=48, weight="bold")
            self.canvas.create_text(400, 120, text="FRUIT NINJA", font=title_font, fill="#FFD700")

        # 3. Botones circulares
        self.create_circular_button(400, 350, 80, "#03A9F4", self.icon_original, "Original", self.start_game)
        self.create_circular_button(190, 350, 80, "#F44336", self.icon_multiplayer, "Multiplayer",
                                    self.show_multiplayer)
        self.create_circular_button(610, 350, 80, "#FFC107", self.icon_watch, "Watch", self.show_watch)

    def create_circular_button(self, x, y, radius, color, icon, text, command):
        """Crea un botón completo: anillo, icono y texto."""
        ring_width = 15

        # Anillo
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=color, width=ring_width)

        # Icono
        if icon:
            self.canvas.create_image(x, y, image=icon)

        # Texto en arco
        self.create_arc_text(x, y, radius, text, 135, 90, "white", font_size=16)

        # Área clickeable (invisible)
        click_area_id = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill="", outline="")
        self.canvas.tag_bind(click_area_id, "<Button-1>", lambda event: command())

    def create_arc_text(self, x, y, radius, text, angle_start, angle_extent, color, font_size=18):
        """Dibuja texto a lo largo de un arco."""
        text_font = tkfont.Font(family="Helvetica", size=font_size, weight="bold")
        text = text.upper()

        for start_angle_offset in [0, 180]:
            current_angle_start = math.radians(angle_start - start_angle_offset)
            angle_step = math.radians(angle_extent) / len(text)

            for i, char in enumerate(text):
                char_angle = current_angle_start - (i + 0.5) * angle_step
                char_x = x + radius * math.cos(char_angle)
                char_y = y - radius * math.sin(char_angle)
                self.canvas.create_text(char_x, char_y, text=char, font=text_font, fill=color)

    # --- Funciones de comando para los botones ---
    def start_game(self):
        print("Botón 'Original' presionado.")

    def show_multiplayer(self):
        print("Botón 'Multiplayer' presionado.")

    def show_watch(self):
        print("Botón 'Watch' presionado.")


if __name__ == "__main__":
    app = FruitNinjaMenu()
    app.mainloop()