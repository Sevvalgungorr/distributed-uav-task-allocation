import math

import pytest

from swarm_core.dataset import load_boundary, load_obstacles, load_tasks
from swarm_core.environment import Environment
from swarm_sim.fly_task import ARRIVAL_TOLERANCE_M, transit_waypoints

AC10 = "scenarios/AC10_0000.json"


@pytest.fixture(scope="module")
def env_tasks():
    return Environment(load_boundary(AC10), load_obstacles(AC10)), {t.task_id: t for t in load_tasks(AC10)}


def test_goal_is_always_last_and_start_is_dropped(env_tasks):
    env, tasks = env_tasks
    goal = tasks[2].waypoints[0]
    via, length = transit_waypoints(env, (0.0, 0.0), goal)
    assert via[-1] == goal and (0.0, 0.0) not in via
    assert length >= math.dist((0.0, 0.0), goal)


def test_blocked_transit_has_corner_waypoint(env_tasks):
    # görev 1 bitişi -> görev 2 başlangıcı: düz çizgi engele giriyor, yol bir köşeden dönmeli
    env, tasks = env_tasks
    via, length = transit_waypoints(env, tasks[1].waypoints[1], tasks[2].waypoints[0])
    assert len(via) == 2 and length > math.dist(tasks[1].waypoints[1], tasks[2].waypoints[0])


def test_tiny_snap_legs_are_skipped(env_tasks):
    # görev 61'in başlangıcı engel içinde kalıyor (environment.snap_out); birkaç cm'lik ayak uçulmaz
    env, tasks = env_tasks
    goal = tasks[61].waypoints[0]
    via, _ = transit_waypoints(env, goal, (88.2502, 41.7036))
    prev = goal
    for p in via[:-1]:
        assert math.dist(prev, p) >= ARRIVAL_TOLERANCE_M
        prev = p
