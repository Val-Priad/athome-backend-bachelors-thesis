from enum import Enum


class VicinityType(str, Enum):
    bus_stop = "bus_stop"
    train_station = "train_station"
    post_office = "post_office"
    atm = "atm"
    clinic = "clinic"
    veterinarian = "veterinarian"
    school = "school"
    kindergarten = "kindergarten"
    supermarket = "supermarket"
    small_shop = "small_shop"
    restaurant_pub = "restaurant_pub"
    playground = "playground"
    metro = "metro"
    closest = "closest"
