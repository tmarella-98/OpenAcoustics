from acoustics.driver import Driver
from plots.sealed_box_plot import plot_volume_slider


driver = Driver.load("examples/SB17NBAC35-8.json")

plot_volume_slider(
    driver=driver,
    initial_volume_l=10.0,
    minimum_volume_l=2.0,
    maximum_volume_l=40.0,
    volume_step_l=0.1,
)