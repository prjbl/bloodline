class Counter:
    
    __counter: int = 0
    
    
    def count(self) -> None:
        self.__counter += 1
    
    
    def decount(self) -> None:
        if self.__counter > 0:
            self.__counter -= 1
    
    
    def reset(self) -> None:
        self.__counter = 0
        
    
    def get_counter(self) -> int:
        return self.__counter