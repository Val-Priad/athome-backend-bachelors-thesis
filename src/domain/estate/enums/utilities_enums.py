from enum import Enum


class HeatingSource(str, Enum):
    gas_boiler = "gas_boiler"
    electric_boiler = "electric_boiler"
    central_heating = "central_heating"
    fireplace = "fireplace"
    heat_pump = "heat_pump"
    other = "other"


class PrimaryInternetConnectionType(str, Enum):
    fiber = "fiber"
    cable = "cable"
    dsl = "dsl"
    mobile = "mobile"
    satellite = "satellite"
    fixed_wireless = "fixed_wireless"
    other = "other"
