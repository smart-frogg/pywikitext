# -*- coding: utf-8 -*-
import random
import numpy as np

def tree(data, similarityFunction, avgFunction):
    dataIds = range(0,data.shape[0])
    tree = []
    for i in dataIds:
        tree.append(data[i])

    while len(tree) >1:  
        maxSim = 0
        maxSimId = 0 
        for i in range(0,len(tree)-1):
            curSim = similarityFunction(tree[i],tree[i+1])
            if(curSim > maxSim):
                maxSim = curSim
                maxSimId = i    
        tree[maxSimId] = {
            'data':[tree[maxSimId],tree[maxSimId+1]],
            'avg':avgFunction(tree[maxSimId],tree[maxSimId+1]),
            'sim':maxSim}
        del tree[maxSimId+1]
    return tree    

def evklidAvg(a,b):
    avgA = a
    avgB = b
    if type(a) == dict:
        avgA = a['avg']
    if type(b) == dict:
        avgB = b['avg']
    return (avgA+avgB)/2

def evklid(a,b):
    avgA = a
    avgB = b
    if type(a) == dict:
        avgA = a['avg']
    if type(b) == dict:
        avgB = b['avg']
    return 1/(np.linalg.norm(avgB-avgA)+1)

data = np.array([
    [1],
    [2],
    [5],
    [7],
    [8],
    [10],
    [15],
    [23],
    ])
res = tree(data,evklid,evklidAvg)
print(res)

    
def kMeans(data, clusterCount, iterations, similarityFunction):
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