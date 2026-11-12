
from dataclasses import dataclass
# __init__ gibi metotlari otomatik olusturarak sinifi daha kisa yazmamizi saglar
#nesneyi ekrana yazdırmamızı sağlar 
# IHA'nin temel bilgilerini tutan sinif
@dataclass
class UAV:
    uav_id: int
    x: float
    y: float
    battery: float = 100.0
    is_leader: bool = False

    def distance_to(self, x: float, y: float) -> float:
        dx = self.x - x
        dy = self.y - y
        return (dx**2 + dy**2) ** 0.5

# IHA'lara atanacak gorevlerin bilgilerini tutar
@dataclass
class Task:
    task_id: int           # Gorev numarasi
    x: float              # Gorevin X konumu
    y: float              # Gorevin Y konumu
    priority: int = 1     # Gorev onceligi
    status: str = "OPEN"  # Gorevin durumu
