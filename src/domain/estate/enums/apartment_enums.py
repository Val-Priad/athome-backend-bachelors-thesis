from enum import Enum


class ApartmentLayout(str, Enum):
    studio_1 = "studio_1"
    one_plus_one = "one_plus_one"
    studio_2 = "studio_2"
    two_plus_one = "two_plus_one"
    studio_3 = "studio_3"
    three_plus_one = "three_plus_one"
    studio_4 = "studio_4"
    four_plus_one = "four_plus_one"
    studio_5 = "studio_5"
    five_plus_one = "five_plus_one"
    six_or_more = "six_or_more"
    atypical = "atypical"
    room = "room"
