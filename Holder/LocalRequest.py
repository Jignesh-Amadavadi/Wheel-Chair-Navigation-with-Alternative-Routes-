class Request:
    def __init__(self,lat1,lon1,lat2,lon2,isWheelChair,isShortestPath,distance_weight,epsilon,gamma,alpha):
        self.lat1=lat1 
        self.lon1=lon1
        self.lat2=lat2
        self.lon2=lon2
        self.isWheelChair=isWheelChair
        self.isShortestPath=isShortestPath
        self.distance_weight=distance_weight
        self.epsilon=epsilon 
        self.gamma=gamma
        self.alpha=alpha
        
        
        