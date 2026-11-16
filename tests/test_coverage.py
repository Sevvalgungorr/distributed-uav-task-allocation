from swarm_core.coverage import generate_zigzag
def test_zigzag():
    waypoint=generate_zigzag(50,50)
    assert len(waypoint)==12
    assert waypoint[0]==(0,0)
    assert waypoint[len(waypoint)-1] == (100, 0)
    
def test_second_region():
    #ikinci bölgeyi kontrol ediyor 
    waypoint = generate_zigzag(150, 50)
    assert len(waypoint)==12
    assert waypoint[0]==(100,0)
    assert waypoint[len(waypoint)-1] == (200, 0)
