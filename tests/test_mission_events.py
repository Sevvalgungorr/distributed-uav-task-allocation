import json
import socket

import pytest

from swarm_sim.mission_events import MissionEventSender, build_assignment, build_event


def test_build_assignment_manual():
    msg = build_assignment({1: [1, 2, 3, 4], 2: []}, "manual", "scenarios/AC10_0000.json", now=10.0)
    assert msg == {
        "type": "assignment",
        "time": 10.0,
        "scenario": "scenarios/AC10_0000.json",
        "source": "manual",
        "assignment": {"1": [1, 2, 3, 4], "2": []},
    }
    assert "reversed" not in msg  # isteğe bağlı alan verilmezse eklenmez


def test_build_assignment_cbba_with_reversed():
    msg = build_assignment({1: [5, 2]}, "cbba", "s.json", reversed_flags={1: [False, True]}, now=0.0)
    assert msg["source"] == "cbba"
    assert msg["reversed"] == {"1": [False, True]}


def test_build_assignment_rejects_unknown_source():
    with pytest.raises(ValueError):
        build_assignment({1: [1]}, "auction", "s.json")


def test_build_assignment_rejects_reversed_length_mismatch():
    with pytest.raises(ValueError):
        build_assignment({1: [1, 2]}, "cbba", "s.json", reversed_flags={1: [True]})


def test_build_event_task_and_status():
    assert build_event(1, "task_started", 3, now=1.0) == {
        "type": "event", "time": 1.0, "uav": 1, "event": "task_started", "task": 3,
    }
    assert build_event(2, "landed", now=2.0) == {"type": "event", "time": 2.0, "uav": 2, "event": "landed"}


@pytest.mark.parametrize("args", [(1, "task_finished", None), (1, "takeoff", 3), (1, "exploded", None)])
def test_build_event_rejects_invalid(args):
    with pytest.raises(ValueError):
        build_event(*args)


def test_sender_delivers_json_over_udp():
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver.bind(("127.0.0.1", 0))  # işletim sisteminin seçtiği boş port
    receiver.settimeout(2.0)
    port = receiver.getsockname()[1]

    sender = MissionEventSender(port=port)
    sender.send_assignment({1: [1, 2]}, "manual", "s.json")
    sender.send_event(1, "task_finished", 2)

    first = json.loads(receiver.recv(65535))
    second = json.loads(receiver.recv(65535))
    assert first["type"] == "assignment" and first["assignment"] == {"1": [1, 2]}
    assert second == {**second, "type": "event", "uav": 1, "event": "task_finished", "task": 2}

    sender.close()
    receiver.close()


def test_sender_without_listener_does_not_raise():
    # Boş bir port bul ve kapat: o portta dinleyen yok.
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()

    sender = MissionEventSender(port=port)
    for _ in range(5):  # Linux bir önceki gönderimin ICMP hatasını sonrakinde bildirebilir
        sender.send_event(1, "takeoff")
    sender.close()
