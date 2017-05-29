import plotly.offline as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
import pickle
import numpy as np

from sklearn.decomposition import PCA as sklearnPCA
from sklearn.preprocessing import StandardScaler
from pytextutils.text_stat import TEXT_STAT_KEYS

class PCAWikiVisualizator:
    def __init__(self,accessor,prefix,output_type='file'):
        self.accessor = accessor
        self.prefix = prefix
        self.outputType = output_type
    def readAndCalcLen(self,file):
        with open(self.__getFullFileName(file), 'rb') as f:
            self.fragmentTypes = pickle.load(f)
        
        exampleLen = None
        self.totalLen = 0
        self.fTypeList = list(self.fragmentTypes.keys())
        self.fTypeList.sort()
        
        for fType in self.fTypeList:
            self.totalLen += len(self.fragmentTypes[fType])
            if not exampleLen:
                self.exampleLen = len(self.fragmentTypes[fType][0])
                
    def __getFullFileName(self,fileName):
        return self.accessor.directory+self.prefix+fileName
    def getStat(self):
        return self.pcaWiki('stat.pcl')
    def getHists(self,metric):
        return self.wikiHists('stat.pcl',metric)
    def getRelativeStat(self):
        return self.pcaWiki('relativeStat.pcl')
    def getRelativeHists(self,metric):
        return self.wikiHists('relativeStat.pcl',metric)
    def formDataPCA(self,file):
        self.readAndCalcLen(file)
        self.y = np.zeros((self.totalLen),dtype='|U20')    
        self.X = np.zeros((self.totalLen,self.exampleLen),dtype=float)
        self.names = np.array(self.fTypeList,dtype='|U20')
        
        totalId = 0
        for fType in self.fTypeList:
            for iEx in range(len(self.fragmentTypes[fType])):
                iPar = 0
                self.y[totalId] = fType 
                for param in TEXT_STAT_KEYS:
                    self.X[totalId,iPar] = self.fragmentTypes[fType][iEx][param]
                    iPar +=1
                totalId += 1    
        
    def pcaWiki(self,file):
        self.formDataPCA(file)           
        X_std = StandardScaler().fit_transform(self.X)
        sklearn_pca = sklearnPCA(n_components=2)
        Y_sklearn = sklearn_pca.fit_transform(X_std)
        traces = []
    
        for name in self.names:
            trace = go.Scatter(
                x=Y_sklearn[self.y==name,0],
                y=Y_sklearn[self.y==name,1],
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
        if (self.outputType == 'file'):
            print(py.plot(fig,filename='pca')) 
        else:
            return (py.plot(fig,include_plotlyjs='False',output_type='div')) 
        #print(py.plot(fig, image='png', filename='pca.html', image_filename='plot_image',
        #              image_width=800,  image_height=600)) 

    def formDataHist(self,file,metric):
        self.readAndCalcLen(file)
        self.X = []
        self.names = np.array(self.fTypeList,dtype='|U20')
        
        for fType in self.fTypeList:
            curX = np.zeros((len(self.fragmentTypes[fType])),dtype=float)
            for iEx in range(len(self.fragmentTypes[fType])):
                curX[iEx] = self.fragmentTypes[fType][iEx][metric]
            self.X.append(curX)        
    def wikiHists(self,file,metric):
        self.formDataHist(file,metric)
        colors = ['#1f78b4', '#33a02c','#e31a1c','#ff7f00']
        fig = ff.create_distplot(self.X, self.names, bin_size=.05,colors=colors)    
        #print(py.plot(fig, image='jpeg', image_filename='test_hist'))
        if (self.outputType == 'file'):
            print(py.plot(fig,filename='hist')) 
        else:
            return (py.plot(fig,include_plotlyjs='False',output_type='div')) 

     
if __name__ =="__main__":
    from pywikiaccessor.wiki_accessor import WikiAccessor
    directory = "C:\\WORK\\science\\onpositive_data\\python\\"
    accessor = WikiAccessor(directory)
    PCAWikiVisualizator(accessor,'miph_',output_type="div").getStat()
    #PCAWikiVisualizator(accessor,'miph_').getHists("UNIQUE_VERBS")
    #PCAWikiVisualizator(accessor,'miph_').getHists("VERBS")
    #PCAWikiVisualizator(accessor,'miph_').getHists("UNIQUE_NOUNS")
    #PCAWikiVisualizator(accessor,'miph_').getRelativeHists("UNIQUE_VERBS")