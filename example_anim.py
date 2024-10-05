from manim import *

class PythagorasTheorem(Scene):
    def construct(self):
        # Timeframe: 0-5 seconds
        title = Text("Pythagoras Theorem", font_size=72, color=WHITE).set_color_by_gradient(BLUE, DARK_BLUE).to_edge(UP)
        triangle_image = ImageMobject("right_triangle.png").scale(0.5)

        self.play(Write(title))
        self.play(FadeIn(triangle_image))
        self.wait(3)

        # Timeframe: 6-15 seconds
        labeled_triangle = ImageMobject("right_triangle_labeled.png").scale(0.5)
        equation = MathTex("a^2 + b^2 = c^2", font_size=48).to_edge(DOWN)

        self.play(FadeOut(triangle_image))
        self.play(FadeIn(labeled_triangle))
        self.play(Write(equation))
        self.wait(7)

        # Timeframe: 16-25 seconds
        animation_gif = ImageMobject("squares_on_triangle.gif").scale(0.5)

        self.play(FadeOut(labeled_triangle))
        self.play(FadeIn(animation_gif))
        self.play(equation.animate.set_color(YELLOW))
        self.wait(7)

        # Timeframe: 26-35 seconds
        example_3_4_5 = ImageMobject("example_3_4_5.png").scale(0.5)
        example_text_1 = Text("3² + 4² = 9 + 16 = 25", font_size=48).to_edge(DOWN)

        self.play(FadeOut(animation_gif))
        self.play(FadeIn(example_3_4_5))
        self.play(Transform(equation, example_text_1))
        self.wait(7)

        # Timeframe: 36-45 seconds
        example_5_12_13 = ImageMobject("example_5_12_13.png").scale(0.5)
        example_text_2 = Text("5² + 12² = 25 + 144 = 169", font_size=48).to_edge(DOWN)

        self.play(FadeOut(example_3_4_5))
        self.play(FadeIn(example_5_12_13))
        self.play(Transform(equation, example_text_2))
        self.wait(7)

        # Timeframe: 46-55 seconds
        ladder_application = ImageMobject("ladder_application.png").scale(0.5)

        self.play(FadeOut(example_5_12_13))
        self.play(FadeIn(ladder_application))
        self.play(Transform(equation, MathTex("a^2 + b^2 = c^2", font_size=48).to_edge(DOWN)))
        self.wait(7)

        # Timeframe: 56-65 seconds
        summary_diagram = ImageMobject("summary_diagram.png").scale(0.5)
        historical_significance = ImageMobject("historical_significance.png").scale(0.3).to_edge(UR)

        self.play(FadeOut(ladder_application))
        self.play(FadeIn(summary_diagram), FadeIn(historical_significance))
        self.wait(7)

        # Timeframe: 66-75 seconds
        moving_labels_gif = ImageMobject("right_triangle_moving_labels.gif").scale(0.5)
        explore_text = Text("Explore more in mathematics and science", font_size=48).to_edge(DOWN)

        self.play(FadeOut(summary_diagram), FadeOut(historical_significance))
        self.play(FadeIn(moving_labels_gif))
        self.play(Transform(equation, explore_text))
        self.wait(7)

        # Timeframe: 76-85 seconds
        thank_you_text = Text("Thank you for watching", font_size=72, color=WHITE).set_color_by_gradient(BLUE, DARK_BLUE).to_edge(UP)
        contact_text = Text("Contact: example@email.com", font_size=48, color=WHITE).to_edge(DOWN)

        self.play(FadeOut(moving_labels_gif))
        self.play(Write(thank_you_text))
        self.play(Transform(equation, contact_text))
        self.wait(7)

        # Timeframe: 86-90 seconds
        stay_tuned_text = Text("Stay tuned for more", font_size=72, color=WHITE).set_color_by_gradient(BLUE, DARK_BLUE).to_edge(UP)
        social_icons = VGroup(
            ImageMobject("facebook.png").scale(0.2),
            ImageMobject("twitter.png").scale(0.2),
            ImageMobject("instagram.png").scale(0.2)
        ).arrange(RIGHT, buff=0.5).to_edge(DOWN)

        self.play(Transform(thank_you_text, stay_tuned_text))
        self.play(FadeOut(contact_text), FadeIn(social_icons))
        self.wait(4)