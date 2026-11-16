def generate_zigzag(center_x,center_y,size=100,spacing=20):
    min_x=center_x-size/2
    max_x=center_x+size/2
    min_y=center_y-size/2
    max_y=center_y+size/2
    list_waypoint=[]
    for i in range(0,int(size/spacing)+1):
        x=min_x+spacing*i
        if(i%2==0):
            #çift sayılarda aşağıdan yuarıya çıkar tekte tam tersi 
            list_waypoint.append((x, min_y))
            list_waypoint.append((x, max_y))
        else:
             list_waypoint.append((x, max_y))
             list_waypoint.append((x, min_y))
    return list_waypoint          

          



        





