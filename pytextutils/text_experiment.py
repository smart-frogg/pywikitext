import plotly.offline as py
import plotly.graph_objs as go
import plotly.tools as tls
import pickle
import numpy as np

def load(fileName="C:/WORK/science/onpositive_data/python/texts/sule1.txt-surface.pcl"):
    with open(fileName) as f:
        return pickle.load(f)

def heatMap(PARAM = "FUNC"):
    allData = load()
    data = []
    size = None
    
    for dEl in sorted(allData[PARAM]):
        if len(allData[PARAM][dEl]) == 0:
            break
        max_value = max(allData[PARAM][dEl])
        min_value = min(allData[PARAM][dEl])
        allData[PARAM][dEl] = [(x-min_value)/(max_value-min_value) for x in allData[PARAM][dEl]] 
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

def pca(winSize):
    allData = load()
    data = np.zeros((len(allData),len[allData['FUNC'][winSize]]))
    i=0
    for dEl in sorted(allData):
        data[i] = allData[dEl][winSize]
        
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA as sklearnPCA
    X_std = StandardScaler().fit_transform(data)
    sklearn_pca = sklearnPCA(n_components=2)
    Y_sklearn = sklearn_pca.fit_transform(X_std)
    traces = []
    
    trace = go.Scatter(
        x=Y_sklearn[0],
        y=Y_sklearn[1],
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
    print(py.iplot(fig, filename='pca.html'))
    
pca()
#py.plot(picture, image='png',image_filename='a-simple-plot.png')
#from IPython.display import Image
#Image('a-simple-plot.png')             



