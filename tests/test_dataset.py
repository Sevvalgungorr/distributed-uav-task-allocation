from pathlib import Path

from swarm_core.dataset import load_boundary, load_tasks

H1_PATH = Path(__file__).resolve().parent.parent / "scenarios" / "h1.json"


def test_h1_task_count():
    assert len(load_tasks(H1_PATH)) == 13


def test_h1_task_waypoints():
    for task in load_tasks(H1_PATH):
        assert len(task.waypoints) == 2
        (x1, y1), (x2, y2) = task.waypoints
        assert task.x == (x1 + x2) / 2
        assert task.y == (y1 + y2) / 2


def test_h1_task_ids():
    assert [task.task_id for task in load_tasks(H1_PATH)] == list(range(1, 14))


def test_h1_tasks_inside_boundary_box():
    boundary = load_boundary(H1_PATH)
    min_x = min(x for x, _ in boundary)
    max_x = max(x for x, _ in boundary)
    min_y = min(y for _, y in boundary)
    max_y = max(y for _, y in boundary)
    for task in load_tasks(H1_PATH):
        for x, y in task.waypoints:
            assert min_x <= x <= max_x
            assert min_y <= y <= max_y
