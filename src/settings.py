class Setting:
    """
    Settings class. Singleton.

    Contains:
        - Sound
    """
    instance = None

    __sound: float = 0.0

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        self.__sound = 1.0

    def change_sound(self, amt: float) -> float:
        """
        Change level of sound
            Min 0.0
            Max 1.0
        """
        self.__sound = min(1.0, max(0.0, amt))
        return self.__sound

    def get_sound_level(self) -> float:
        """
        Get level of sound (0.0, 1.0)
        """
        return self.__sound


