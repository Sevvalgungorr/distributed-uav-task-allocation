
from swarm_core.models import UAV, Task
from swarm_core.coverage import generate_zigzag



# 500x400 metrelik alani 20 gorev bolgesine ayiriyoruz
#20 göreve ayırmamızın sebebi, 5 İHA'nın tarayacağı alanı küçük parçalara bölerek görev paylaşımını kolaylaştırmak.
#Ileride CBBA algoritmasi bu gorevleri IHA'lar arasinda paylastiracak.

def create_tasks():
    tasks = []
    task_id = 1

    for row in range(4):
        for col in range(5):
            x = col * 100 + 50
            y = row * 100 + 50

            waypoints = generate_zigzag(x, y)

            task = Task(task_id=task_id, x=x, y=y, waypoints=waypoints)
            tasks.append(task)

            task_id += 1

    return tasks
# Bu blok sadece main.py dogrudan calistirildiginda calisir.
# Test dosyasindan import edildiginde IHA olusturma ve yazdirma islemleri calismaz.
if __name__ == "__main__":
    #5 ihayi olusturuyoruz 
    uavs = []

    for i in range(1, 6):
         uav = UAV(uav_id=i, x=0, y=0)
         uavs.append(uav)

    tasks = create_tasks()  
    # Olusturulan IHA ve gorevleri ekrana yazdiriyoruz
    print("IHA sayisi:", len(uavs))
    print("Gorev sayisi:", len(tasks))
    print("\nIHA'lar:")
    for uav in uavs:
         print(uav)
    print("\nGorevler:")
    for task in tasks:
         print(task)
    print("Toplam görev sayısı:", len(tasks))
    print("İlk görevin rota noktası sayısı:", len(tasks[0].waypoints))




