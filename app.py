from acoustics.driver import Driver
from acoustics.sealed_box import SealedBox


driver = Driver.load("examples/SB17NBAC35-8.json")

simulation = SealedBox(
    driver=driver,
    volume_l=10.0,
)

simulation.calculate()
simulation.summary()