from geopy.distance import vincenty
from zipfile import ZipFile
from xml.dom.minidom import parseString
import csv
import simplekml

imageData = {}
imageData2= []  #lists and dict storing images data

videoData= {}
videoData2 =[] #list and dict storing video data

ans={}
ans2={} # dicts storing time durations and images name 

ansPOI={} #dict storing images and name of the loaction 

DISTDEF=35 #distance for video 
DISTPOI=50 #distance for point of interest locations

PATHV='./videos/DJI_0301.SRT' #path of vode file 
PATHI='./images/Photo-Location.kmz' #path of images metadata file



'''
Function responsible of extracting metadata of images from kml file and storing it in 
imagesData lsit and dicts 
'''

def processKml():

	kmz=ZipFile(PATHI,'r')
	kml=kmz.open('doc.kml','r')
	data=kml.read()
	kml.close()  #reading the contents for the .kml file 

	dom=parseString(data) #parsing the read data to string

	tempName=[]
	tempCoor=[]


	#extracting names of the file from the discription tag
	for dis in dom.getElementsByTagName('description'):
		nm=dis.firstChild.nodeValue
		tempName.append(nm)


	#extracting coordiantes fot the images form the coordinates tag 
	for cord in dom.getElementsByTagName('coordinates'):
		coordinates = cord.firstChild.data.split(',')
		c=(float(coordinates[0]),float(coordinates[1]))
		tempCoor.append(c)


	imageData2=list(zip(tempName,tempCoor))

	for i in imageData2:
		imageData[i[0]]=i[1]

	return imageData2


'''
Function responsible for extracting time and coordinates of drone for the video srt file and storing it 
int videoData list and dict
'''

def processVideo():

	#reading video file
	file=open(PATHV)
	data=file.read()
	file.close()

	dataList=[]

	dataList=data.split('\n')
	
	for ch in dataList:
		if ch=='':
			dataList.remove(ch)

	del(dataList[len(dataList)-1])

	timeData=[]
	timeData2=[]
	coordData=[]
	coordData2=[]

	for i in range(0,len(dataList)-1,3):
		timeData.append(dataList[i+1])
		coordData.append(dataList[i+2])

	

	for timeD in timeData:
		timeD=timeD.split('-->')
		timeD=timeD[0].split(',')
		hms=timeD[0].split(':')
		mil=timeD[1]
		finalTime=(float(hms[0])*60*60)+(float(hms[1])*60)+(float(hms[2]))+float(mil)*.001
		timeData2.append(finalTime)


	for coordinates in coordData:
		coordinates=coordinates.split(',')
		crd=(float(coordinates[0]),float(coordinates[1]))
		coordData2.append(crd)



	videoData2=list(zip(timeData2,coordData2))

	for i in videoData2:
		videoData[i[0]]=i[1];


	return videoData2



'''
Function responsible for calculating distance od drone from the image ans 
writing the results into a csv file
'''
def final():

	#calculating distance between drone and images using vicenty formula
	for ins in videoData2:
		vidCoor=ins[1]

		temp=[]

		for imD in imageData2:
			
			if vincenty(ins[1],imD[1]).meters < DISTDEF:
				temp.append(imD[0])

		ans[ins[0]]=temp



	#wrting contens of dictionary to a csv file
	with open('dict.csv', 'w') as csv_file:

		writer = csv.writer(csv_file)

		for key, value in ans.items():
			writer.writerow([key, value])


'''
Function responsible for extracting data from asssets.csv file and calculating
the distance of poi form the images and writing the results to a csv file with the name poi.csv
'''
def poi():

	l=[]
	#reading data of csv file to a list
	with open('assets.csv', 'r') as f:
		reader=csv.reader(f)
		l=list(reader)


	name=[]
	poiCoord=[]

	#print(len(l))

	#extracting name and coordiantes of the poi form list
	for i in range(1,(len(l))):
		name.append((l[i])[0])

		c1=float((l[i])[1])
		c2=float((l[i])[2])

		poiCoord.append((c1,c2))

	temZip=list(zip(name,poiCoord))


	#calculating distance of poi from images
	for i in temZip:
		cordinatePOI=i[1]

		temp=[]
		for imD in imageData2:
			if vincenty(cordinatePOI,imD[1]).meters < DISTDEF:
				temp.append(imD[0])

		ansPOI[i[0]]=temp


	#writing contents of dict to a cvs file
	with open('poi.csv', 'w') as csv_file:

		writer = csv.writer(csv_file)

		for key, value in ansPOI.items():
			writer.writerow([key, value])


'''
Function responsible for plotting path of drone from the video into kml file
'''
def plotKML():

	kml = simplekml.Kml()

	#creating new points and adding it to .kml file
	for i in videoData2:
		kml.newpoint(name=str(i[0]), coords=[i[1]])
		kml.save("videoPath.kml")




imageData2=processKml()
videoData2=processVideo()
final()
poi()
plotKML()

print("Success!")