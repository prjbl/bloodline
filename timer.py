import time as t

class Timer:
    
    __start_time: float = 0.0
    __end_time: float = 0.0
    __cache: float = 0
    __timer_active: bool = False
    __timer_toggled: bool = False
    
    
    def start(self) -> None:
        self.__timer_active = True
        self.__start_time = t.time()
    
    
    def toggle_pause(self) -> None:
        if self.__timer_active:
            self.__timer_toggled = not self.__timer_toggled
            
            if self.__timer_toggled:
                print("paused")
                self.end() # problem with timer active = false
                self.__cache = self.get_end_time()
            else:
                print("resumed")
                self.reset()
                self.start()
                self.__start_time -= self.__cache
    
    
    def end(self) -> None:
        if self.__timer_active:
            self.__end_time = t.time()
        
        self.__timer_active = False
    
    
    def get_end_time(self) -> float:
        return self.__end_time - self.__start_time
    
    
    def reset(self) -> None:
        self.__start_time, self.__end_time = 0, 0