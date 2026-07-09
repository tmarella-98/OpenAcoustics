from acoustics.driver import Driver


driver = Driver(
    manufacturer="SB Acoustics",
    model="SB17NBAC35-8",

    fs=33.0,
    qts=0.33,
    qes=0.36,
    qms=4.0,

    vas=33.0,

    re=5.8,
    le=0.40,

    sd=138.0,
    xmax=5.5,
    bl=7.2,
    mms=14.0,
    cms=1.7,
)

driver.save("examples/SB17NBAC35-8.json")

loaded_driver = Driver.load("examples/SB17NBAC35-8.json")

loaded_driver.summary()