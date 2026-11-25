"""Görselleştirme arayüzünün gönderen tarafı: görev ataması ve görev olayları.

Arayüzün tanımı: docs/cbba_plan.md, bölüm A0.0.5.

- Mesajlar JSON'dur ve yerel UDP ile "gönder ve unut" biçiminde gönderilir.
- Dinleyen yoksa ya da ağ hatası olursa sessizce geçilir; uçuş kodu asla beklemez
  ve hata almaz. Böylece görselleştirme kapalıyken uçuş betikleri aynen çalışır.
- Yalnızca standart kütüphane kullanılır.
- Yanlış kullanım (bilinmeyen kaynak veya olay adı) ise programlama hatasıdır ve
  ValueError verir.
"""

import json
import socket
import time

# Arayüz ayarı: alıcı (2D harita) bu adresi dinler. Deney parametresi değildir.
MISSION_EVENTS_HOST = "127.0.0.1"
MISSION_EVENTS_PORT = 15600

ASSIGNMENT_SOURCES = ("manual", "cbba")
TASK_EVENTS = ("task_started", "task_finished")
STATUS_EVENTS = ("takeoff", "landed")


def build_assignment(assignment, source, scenario, reversed_flags=None, now=None):
    """`assignment` mesajını sözlük olarak oluşturur (ağa göndermeden).

    assignment: {iha_id: [görev_id, ...]} (uçuş sırasıyla)
    source: "manual" veya "cbba"
    reversed_flags: isteğe bağlı {iha_id: [bool, ...]}; her liste ilgili görev listesiyle aynı uzunlukta
    """
    if source not in ASSIGNMENT_SOURCES:
        raise ValueError(f"Bilinmeyen atama kaynagi: {source!r} (izin verilenler: {ASSIGNMENT_SOURCES})")

    message = {
        "type": "assignment",
        "time": time.time() if now is None else now,
        "scenario": str(scenario),
        "source": source,
        "assignment": {str(uav): [int(t) for t in tasks] for uav, tasks in assignment.items()},
    }

    if reversed_flags is not None:
        for uav, flags in reversed_flags.items():
            if len(flags) != len(assignment.get(uav, [])):
                raise ValueError(f"IHA {uav}: reversed listesi gorev listesiyle ayni uzunlukta olmali")
        message["reversed"] = {str(uav): [bool(f) for f in flags] for uav, flags in reversed_flags.items()}

    return message


def build_event(uav, event, task=None, now=None):
    """`event` mesajını sözlük olarak oluşturur (ağa göndermeden)."""
    if event in TASK_EVENTS:
        if task is None:
            raise ValueError(f"'{event}' olayi icin gorev numarasi gerekli")
    elif event in STATUS_EVENTS:
        if task is not None:
            raise ValueError(f"'{event}' olayi gorev numarasi almaz")
    else:
        raise ValueError(f"Bilinmeyen olay: {event!r} (izin verilenler: {TASK_EVENTS + STATUS_EVENTS})")

    message = {
        "type": "event",
        "time": time.time() if now is None else now,
        "uav": int(uav),
        "event": event,
    }
    if task is not None:
        message["task"] = int(task)
    return message


class MissionEventSender:
    """Atama ve olay mesajlarını yerel UDP'ye gönderir; ağ hatalarını yutar."""

    def __init__(self, host=MISSION_EVENTS_HOST, port=MISSION_EVENTS_PORT):
        self.address = (host, port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setblocking(False)

    def _send(self, message):
        try:
            self._sock.sendto(json.dumps(message).encode("utf-8"), self.address)
        except OSError:
            pass  # Dinleyen yok ya da ağ hatası: görselleştirme isteğe bağlıdır.

    def send_assignment(self, assignment, source, scenario, reversed_flags=None):
        self._send(build_assignment(assignment, source, scenario, reversed_flags))

    def send_event(self, uav, event, task=None):
        self._send(build_event(uav, event, task))

    def close(self):
        self._sock.close()
