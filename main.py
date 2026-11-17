
from swarm_core.models import UAV
from swarm_core.tasks import create_tasks


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




