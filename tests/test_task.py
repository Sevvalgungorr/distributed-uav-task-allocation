from main import create_tasks 
def test_task_count():
    assert len (create_tasks())==20
def test_task_waypoints():
    tasks = create_tasks()

    for task in tasks:
        assert len(task.waypoints) == 12
#görevin sınırlarını kontrol ediyoruz 
def test_task_boundaries():
    #rota noktalarını kpntrol ediyoruz 
    tasks = create_tasks()
    for task in tasks:
        min_x = task.x - 50
        max_x = task.x + 50
        min_y = task.y - 50
        max_y = task.y + 50
        for x, y in task.waypoints:
           assert min_x <= x <= max_x
           assert min_y <= y <= max_y