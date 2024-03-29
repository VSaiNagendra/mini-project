import numpy as np
import os,io,math
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA,KernelPCA,TruncatedSVD
from sklearn.metrics.cluster import contingency_matrix
from sklearn import metrics
import time
import pandas as pd
from pandas.plotting import scatter_matrix


def write2d(file, header, arr, actuallabels, y):
	file.write(header+"\n")
	for i in arr:
		for j in i:
			file.write(str(j)+" ")
		file.write("\n")
	file.write("adjusted rank index: "+str(metrics.adjusted_rand_score(actuallabels,y))+"\n")
	file.write("completeness: "+str(metrics.completeness_score(actuallabels,y))+"\n")
	file.write("v-measure: "+str(metrics.v_measure_score(actuallabels,y))+"\n")
	file.write("homogeneity: "+str(metrics.homogeneity_score(actuallabels,y))+"\n")
	file.write("\n")

time_file = io.open("time_opt.txt", "w")
def doClusters(num_clusters, reducer, X, opt_file, i):
	start = time.time()
	if(reducer == 'pca'):
		pca = PCA(n_components=i)
		X = pca.fit_transform(X)
	elif(reducer == 'kpca,lin'):
		kpcal = KernelPCA(n_components=i,kernel='linear')
		X = kpcal.fit_transform(X)
	elif(reducer == 'kpca,poly'):
		kpcap = KernelPCA(n_components=i,kernel='poly')
		X = kpcap.fit_transform(X)
	elif(reducer == 'kpca,cos'):
		kpcac = KernelPCA(n_components=i,kernel='cosine')
		X = kpcac.fit_transform(X)
	elif(reducer == 'kpca,sig'):
		kpcas = KernelPCA(n_components=i,kernel='sigmoid')
		X = kpcas.fit_transform(X)
	elif(reducer == 'svd'):
		tsvd = TruncatedSVD(n_components=i)
		tsvc = tsvd.fit_transform(X)
	elif(reducer == 'none' and i != 141):
		return;
	rt = time.time()-start
	start = time.time()
	km = KMeans(n_clusters=num_clusters, init='k-means++', n_init=20, random_state= 0)
	y=km.fit_predict(X)
	if(i==141):
		data = pd.DataFrame(X[:,:10], columns=['x1', 'x2', 'x3',
		            'x4','x5','x6','x7','x8','x9','x10'])
		k = scatter_matrix(data, alpha=0.2, figsize=(6, 6), diagonal='hist')
		plt.show()
	ct = time.time()-start
	time_file.write("reducer: "+reducer+": "+str(i)+" dims - reduce time:"+str(rt)+
		", cluster time:"+str(ct)+", total time: "+str(rt+ct)+"\n");
	print("reducer: "+reducer+": "+str(i)+" dims - done")
	confusion=contingency_matrix(actuallabels,y)
	write2d(opt_file, reducer+"--"+str(i), confusion, actuallabels, y)

file_name = 't1ds141-3'
num_clusters = 3
opt_file = io.open("Toutput/t1output.txt", 'w')
reducers = ['none', 'pca', 'kpca,lin', 'kpca,poly', 'kpca,cos', 'kpca,sig', 'svd']
actuallabels=[0]*47 + [1]*47 + [2]*47


files=list()
cnt=0
dir=os.path.join(os.getcwd(),file_name)
for f in os.listdir(dir):
	if f.endswith(".txt"):
		cnt+=1
		files.append(os.path.join(dir,f))
file_iter = iter(files)

vectorizer = TfidfVectorizer(analyzer='word',input='filename',
	token_pattern='[^\n\,\.\s\!\'\?\"\:\;\`\~\)\(\-0123456789][^\n\?\,\.\s\!\'\"\;\:\`\~\)\(\-0123456789]+')
X=vectorizer.fit_transform(file_iter,file_name)  
X=X.toarray()

for reducer in reducers:
	for i in range(cnt-60,cnt+1,5):
		try:
			x = X
			doClusters(num_clusters, reducer, x, opt_file, i)
		except:
			print("error in: "+reducer+"--"+str(i))