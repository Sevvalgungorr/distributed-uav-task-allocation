
from swarm_core.models import UAV, Task

# Simulasyonda kullanilacak 5 IHA'yi olusturuyoruz
uavs = []

for i in range(1, 6):
    uav = UAV(uav_id=i, x=0, y=0)
    uavs.append(uav)


# 500x400 metrelik alani 20 gorev bolgesine ayiriyoruz
tasks = []
task_id = 1

for row in range(4):
    for col in range(5):
        x = col * 100 + 50
        y = row * 100 + 50

        task = Task(task_id=task_id, x=x, y=y)
        tasks.append(task)

        task_id += 1


# Olusturulan IHA ve gorevleri ekrana yazdiriyoruz
print("IHA sayisi:", len(uavs))
print("Gorev sayisi:", len(tasks))

print("\nIHA'lar:")
for uav in uavs:
    print(uav)

print("\nGorevler:")
for task in tasks:
    print(task)

