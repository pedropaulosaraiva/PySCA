from abc import ABC, abstractmethod

class Cake(ABC):
    def __init__(self, flavor: str) -> None:
        self.flavor = flavor
        self.jump()
        
    @abstractmethod
    def jump(self):
        pass
    
    
class Chocolate(Cake):
    def __init__(self, flavor: str) -> None:
        super().__init__(flavor)
        
    def jump(self):
        print('jumping')
        

class Vanilla(Cake):
    def __init__(self, flavor: str) -> None:
        super().__init__(flavor)
        
    def jump(self):
        print('staying')
        

c = Chocolate('chocolate')
