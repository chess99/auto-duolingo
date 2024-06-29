from enum import Enum


class Tabs(Enum):
    LEARN = ("com.duolingo:id/tabLearn", "Learn Tab")
    ALPHABETS = ("com.duolingo:id/tabAlphabets", "Alphabets Tab")
    PRACTICE_HUB = ("com.duolingo:id/tabPracticeHub", "练习基地选项卡")
    LEAGUES = ("com.duolingo:id/tabLeagues", "Leagues Tab")
    PROFILE = ("com.duolingo:id/tabProfile", "Profile Tab")

    def __init__(self, resource_id, desc):
        self.resource_id = resource_id
        self.desc = desc
