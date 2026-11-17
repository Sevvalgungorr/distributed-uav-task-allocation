from swarm_core.models import Task
from swarm_core.coverage import generate_zigzag

# 500x400 metrelik alanda 20 görev oluşturuyoruz
def create_tasks():
    tasks = []
    task_id = 1

    for row in range(4):
        for col in range(5):
            x = col * 100 + 50
            y = row * 100 + 50

            waypoints = generate_zigzag(x, y)

            task = Task(
                task_id=task_id,
                x=x,
                y=y,
                waypoints=waypoints
            )

            tasks.append(task)
            task_id += 1

    return tasks