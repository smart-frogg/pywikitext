import plotly.offline as py
import plotly.graph_objs as go
import plotly.tools as tls
import pickle
import numpy as np
from pytextutils.text_stat import normalize,normalizeMaxMin
#py.sign_in('krayvanova', 'dcQej0HCbyoNcfakPXLm')

def load(fileName="C:/WORK/science/onpositive_data/python/texts/sule2.txt-surface.pcl"):
    with open(fileName,'rb') as f:
        return pickle.load(f)

def heatMap(PARAM = "FUNC"):
    allData = load()
    data = []
    size = None
    
    for dEl in sorted(allData[PARAM]):
        if len(allData[PARAM][dEl]) == 0:
            break
        allData[PARAM][dEl] = normalize(allData[PARAM][dEl])
        if not size:
            size = len(allData[PARAM][dEl])
        else:
            while len(allData[PARAM][dEl]) < size:
                allData[PARAM][dEl].append(0)
                allData[PARAM][dEl].insert(0,0)
            if len(allData[PARAM][dEl]) > size:
                allData[PARAM][dEl].pop(0)   
        data.append(allData[PARAM][dEl])
    
    trace = go.Heatmap(z=data)
    picture=[trace]
    print(py.plot(picture, filename='labelled-heatmap.html'))

from sklearn.decomposition import PCA as sklearnPCA
from sklearn.preprocessing import StandardScaler

def pca(winSize):
    allData = load()
    data = np.zeros((len(allData),len(allData['FUNC'][winSize])))
    i=0
    for dEl in sorted(allData):
        allData[dEl][winSize] = normalizeMaxMin(allData[dEl][winSize])
        data[i] = allData[dEl][winSize]
        i+=1
        
    X_std = StandardScaler().fit_transform(np.transpose(data))
    sklearn_pca = sklearnPCA(n_components=2)
    Y_sklearn = sklearn_pca.fit_transform(X_std)
    traces = []
    
    trace = go.Scatter(
        x=Y_sklearn[:,0],
        y=Y_sklearn[:,1],
        mode='markers',
        marker = go.Marker(
            size=12,
            line= go.Line(
                color='rgba(217, 217, 217, 0.14)',
                width=0.5),
            opacity=0.8))
    traces.append(trace)
    
    
    data = go.Data(traces)
    layout = go.Layout(xaxis = go.XAxis(title='PC1', showline=False),
                       yaxis = go.YAxis(title='PC2', showline=False))
    fig = go.Figure(data=data, layout=layout)
    print(py.plot(fig, filename='pca.html'))


def pcaWiki(directory):
    with open(directory+'math_stat.pcl', 'rb') as f:
        fragmentTypes = pickle.load(f)
    
    exampleLen = None
    totalLen = 0
    names = np.zeros((len(fragmentTypes)),dtype=str)
    iName = 0
    for fType in fragmentTypes:
        totalLen += len(fragmentTypes[fType])
        names[iName] = fType
        iName+=1 
        if not exampleLen:
            exampleLen = len(fragmentTypes[fType][0])
    
    print(totalLen)
    y = np.zeros((totalLen),dtype=str)    
    X = np.zeros((totalLen,exampleLen),dtype=float)
    
    for fType in fragmentTypes:
        for iEx in range(len(fragmentTypes[fType])):
            iPar = 0
            y[iEx] = fType 
            for param in fragmentTypes[fType][iEx]:
                X[iEx,iPar] = fragmentTypes[fType][iEx][param]
                iPar +=1
               
    X_std = StandardScaler().fit_transform(X)
    sklearn_pca = sklearnPCA(n_components=2)
    Y_sklearn = sklearn_pca.fit_transform(X_std)
    traces = []

    for name in names:
        trace = go.Scatter(
            x=Y_sklearn[y==name,0],
            y=Y_sklearn[y==name,1],
            mode='markers',
            name=name,
            marker=go.Marker(
                size=12,
                line=go.Line(
                    color='rgba(217, 217, 217, 0.14)',
                    width=0.5),
                opacity=0.8))
        traces.append(trace)
    data = go.Data(traces)
    layout = go.Layout(xaxis=go.XAxis(title='PC1', showline=False),
                    yaxis=go.YAxis(title='PC2', showline=False))
    fig = go.Figure(data=data, layout=layout)
    #print(py.plot(fig))
    print(py.plot(fig, image='jpeg', image_filename='test')) 
    #print(py.plot(fig, image='png', filename='pca.html', image_filename='plot_image',
    #              image_width=800,  image_height=600)) 
              
#py.init_notebook_mode()

#py.plot({"data": [go.Scatter(x=[1, 2, 3, 4], y=[4, 3, 2, 1])],    
#"layout": go.Layout(title="hello world")},
#image='jpeg', image_filename='test')
pca(450)
#pcaWiki('C:\\WORK\\science\\onpositive_data\\python\\')
'''
from plotly.offline import  iplot, init_notebook_mode

# Make plotly work with Jupyter notebook

keys=['one','two','three']
values=[1,2,3]

init_notebook_mode()
py.plot({
    "data": [go.Bar(x=keys, y=values)],
    "layout": go.Layout(title="Sample Bar Chart",)
},image='png', filename='pca.png')
'''
#py.plot(picture, image='png',image_filename='a-simple-plot.png')
#from IPython.display import Image
#Image('a-simple-plot.png')             



