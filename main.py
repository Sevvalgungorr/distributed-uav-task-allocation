
from swarm_core.models import UAV

uav1 = UAV(uav_id=1, x=0, y=0)
uav2 = UAV(uav_id=2, x=30, y=40)

print("İHA 1:", uav1)
print("İHA 2:", uav2)

distance = uav1.distance_to(uav2.x, uav2.y)
print("İki İHA arasındaki mesafe:", distance, "metre")
