class Setting:
    """
    Settings class. Singleton.

    Contains:
        - Sound
    """

    instance = None

    __sound: float = 0.0
    __vehicle: str = "car"
    __color: str = "default"

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.__sound = 1.0
            self.__vehicle = "car"
            self.__color = "default"
            self._initialized = True

    def set_vehicle(self, vehicle: str, color: str):
        self.__vehicle = vehicle
        self.__color = color

    def get_vehicle(self) -> str:
        return self.__vehicle

    def get_color(self) -> str:
        return self.__color

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
