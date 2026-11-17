from swarm_core.coverage import generate_zigzag
def test_zigzag():
    waypoint=generate_zigzag(50,50)
    assert len(waypoint)==10
    assert waypoint[0]==(10,0)
    assert waypoint[len(waypoint)-1] == (90, 100)
    
def test_second_region():
    #ikinci bölgeyi kontrol ediyor 
    waypoint = generate_zigzag(150, 50)
    assert len(waypoint)==10
    assert waypoint[0]==(110,0)
    assert waypoint[len(waypoint)-1] == (190, 100)
