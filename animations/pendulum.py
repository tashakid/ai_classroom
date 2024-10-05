from manim import *

class PendulumScene(Scene):
    def construct(self):
        """
        Constructs a scene displaying a pendulum to demonstrate periodic motion.
        """
        # Create the pivot point
        pivot = Dot(ORIGIN, color=YELLOW)
        
        # Create the pendulum rod as a line
        rod = Line(pivot.get_bottom(), DOWN * 2, color=WHITE)
        
        # Create the pendulum bob as a circle
        bob = Dot(rod.get_end(), color=RED).scale(0.5)
        
        # Group the rod and bob for easy animation
        pendulum = VGroup(rod, bob)
        
        # Add pivot and pendulum to the scene
        self.play(FadeIn(pivot), Create(pendulum))
        self.wait(1)
        
        # Animate the swinging motion
        swing = pendulum.animate.rotate(angle=PI / 4, about_point=pivot.get_center())
        swing_back = pendulum.animate.rotate(angle=-PI / 4, about_point=pivot.get_center())
        
        self.play(swing, run_time=2)
        self.play(swing_back, run_time=2)
        self.wait(1)
        
        # Add comments explaining periodic motion
        comments = Tex(
            "This pendulum exhibits periodic motion, swinging back and forth."
        ).to_edge(DOWN)
        self.play(Write(comments))
        self.wait(2)