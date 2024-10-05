from manim import *
import numpy as np

class SinWaveScene(Scene):
    def construct(self):
        """
        Constructs a scene displaying a sinusoidal wave using Manim.
        """
        # Create the axes
        axes = Axes(
            x_range=[0, 10, 1],
            y_range=[-2, 2, 1],
            axis_config={"color": BLUE},
        )

        # Label the axes
        axes_labels = axes.get_axis_labels(x_label="x", y_label="sin(x)")

        # Create the sine curve
        sine_wave = axes.plot(lambda x: np.sin(x), color=RED)
        sine_label = axes.get_graph_label(sine_wave, label="sin(x)")

        # Add all elements to the scene
        self.play(Create(axes), Create(axes_labels))
        self.play(Create(sine_wave), Write(sine_label))
        self.wait(2)

        # Add comments explaining each step
        comments = Tex(
            "This is a sine wave, represented by the function sin(x).").to_edge(DOWN)
        self.play(Write(comments))
        self.wait(2)