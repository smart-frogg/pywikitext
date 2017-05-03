# -*- coding: utf-8 -*-
import random
import numpy as np

def clusterize(data, clusterCount, iterations, similarityFunction):
    '''
    np.array([
        [0,0,0,1,2],
        [0,0,0,4,2],
        [0,0,0,2,2],
        [0,0,3,1,2],
        [1,0,1,2,0],
        [1,3,1,2,0],
        [1,4,1,2,0],
        [1,5,1,2,0],
        ])
     
    '''
    
    alreadyChoosed = set()
    centers = np.zeros((clusterCount,data.shape[1]))
    dataToCenters = np.zeros((data.shape[0]),dtype=np.uint32)
    dataToCentersCount = np.zeros((clusterCount),dtype=np.uint32)
    dataIds = range(0,data.shape[0])
    centerIds = range(0,centers.shape[0])
    for i in range(0,clusterCount):
        verbId = random.randint(0,data.shape[0]-1)
        while verbId in alreadyChoosed:
            verbId = random.randint(0,data.shape[0]-1)
        alreadyChoosed.add(verbId)
        centers[i] = data[verbId].copy()
    for iteration in range(0,iterations):
        isChanged = False    
        for elId in dataIds:
            element = data[elId]
            maxSim = 0
            maxSimId = 0
            for cId in centerIds:
                sim = similarityFunction(element, centers[cId])
                if sim > maxSim:
                    maxSim = sim
                    maxSimId = cId
                    
            if dataToCenters[elId] != maxSimId:
                isChanged = True
            dataToCenters[elId] = maxSimId
        if not isChanged: break
        centers.fill(0)
        dataToCentersCount.fill(0)   
        for key in range(0,len(dataToCenters)):
            centers[dataToCenters[key]] = centers[dataToCenters[key]] + data[key]
            dataToCentersCount[dataToCenters[key]] += 1  
        for key in centerIds:
                centers[key] = centers[key]/dataToCentersCount[key]
        print(str(iteration)+" complete")        
    return centers,dataToCenters    