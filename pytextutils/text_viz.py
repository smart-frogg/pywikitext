import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import pickle
import numpy as np

from sklearn.decomposition import PCA as sklearnPCA
from sklearn.preprocessing import StandardScaler
from pytextutils.text_stat import TEXT_STAT_KEYS
from sklearn.decomposition import PCA as sklearnPCA
from sklearn.preprocessing import StandardScaler
from pytextutils.text_stat import normalize,normalizeMaxMin

class TextVisualizator:
    def __init__(self,fileName=None,rawData=None, output_type='file'):
        if fileName:
            self.data = self.load(fileName)
        else:  
            self.data = pickle.loads(rawData)
        self.outputType = output_type
    def load(self,fileName="C:/WORK/science/onpositive_data/python/texts/sule2.txt-surface.pcl"):
        with open(fileName,'rb') as f:
            return pickle.load(f)    
    def heatMap(self,PARAM):
        data = []
        size = None
        
        for dEl in sorted(self.data[PARAM]):
            if len(self.data[PARAM][dEl]) == 0:
                break
            self.data[PARAM][dEl] = normalizeMaxMin(self.data[PARAM][dEl])
            if not size:
                size = len(self.data[PARAM][dEl])
            else:
                while len(self.data[PARAM][dEl]) < size:
                    self.data[PARAM][dEl].append(0)
                    self.data[PARAM][dEl].insert(0,0)
                if len(self.data[PARAM][dEl]) > size:
                    self.data[PARAM][dEl].pop(0)   
            data.append(self.data[PARAM][dEl])
        
        trace = go.Heatmap(z=data)
        picture=[trace]
        if self.outputType=='file':
            print(py.plot(picture, filename='labelled-heatmap.html'))
        else:
            return py.plot(picture, output_type='div')
    def pca(self,winSize):
        data = np.zeros((len(self.data),len(self.data['FUNC'][winSize])))
        i=0
        for dEl in sorted(self.data):
            self.data[dEl][winSize] = normalizeMaxMin(self.data[dEl][winSize])
            data[i] = self.data[dEl][winSize]
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
        if self.outputType=='file':
            print(py.plot(fig, filename='pca.html'))
        else:
            return py.plot(fig, output_type='div')


     
if __name__ =="__main__":
    from pywikiaccessor.wiki_accessor import WikiAccessor
    directory = "C:\\WORK\\science\\onpositive_data\\python\\"
    accessor = WikiAccessor(directory)
    #TextVisualizator(accessor,'miph_',output_type="div").getStat()
    #PCAWikiVisualizator(accessor,'miph_').getHists("UNIQUE_VERBS")

    #PCAWikiVisualizator(accessor,'miph_').getHists("VERBS")
    #PCAWikiVisualizator(accessor,'miph_').getHists("UNIQUE_NOUNS")
    #PCAWikiVisualizator(accessor,'miph_').getRelativeHists("UNIQUE_VERBS")