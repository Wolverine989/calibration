#   Applies black and white, crop
#   Row average plot
from PIL import Image
from numpy import asarray
import numpy as np
import matplotlib.pyplot as plt
import os.path
import os
from statistics import mode
from statistics import median
import math


# crop parameters old //OCT 05,07 2021
# left = 1200
# # top = 200 # includes C
# top = 1000
# # right = 1450 
# right = 1300
# bottom = 1750

# # # crop parameters new //OCT 09 2021 
left = 1200
# top = 200 # includes C
top = 550
# right = 1450 
right = 1300
bottom = 1500

conc=[]
logconc=[]
obs=[]
images=[]
find_list=[]

def process(name): # convert to greyscale and crop
    img = Image.open(name+".jpeg")
    img = img.crop((left, top, right, bottom)) 

    # image_data = img.load()
    # height,width = img.size
    # for loop1 in range(height):
    #     for loop2 in range(width):
    #         r,g,b = image_data[loop1,loop2]
    #         image_data[loop1,loop2] = r,int(g/2),int(b/2)

    img = img.convert('L')
    img.save('temp/'+name+'.png')
    img.close()

def observe(image):
    img= Image.open('temp/'+image+'.png') 
    numpydata = asarray(img)
    a_data = np.average(numpydata, axis=1)
    img.close()


    ######## bend begin --> alin min values before & after peak
    x=np.where(a_data==max(a_data))
    x=x[0][0]
    if x == 0: x=1 # adjustment 
    min1=min(a_data[:x])
    x_min1=np.where(a_data==min1)
    x_min1=x_min1[0][0]
    min2=min(a_data[x:])
    x_min2=np.where(a_data==min2)
    x_min2=x_min2[0][-1]
    adjust=min2-min1
    length=x_min2-x_min1
    slope=adjust/length

    for i in range(x_min1,x_min2):
        a_data[i] = a_data[i]-int(slope*(i-x_min1))
    for i in range(x_min1):
        a_data[i]=min1
    for i in range(x_min2,len(a_data)):
        a_data[i]=min1

    min_a=min(a_data)
    #
    for i in range(len(a_data)):
        a_data[i]=a_data[i]-min_a
    
    ########bend end

    # for i in range(len(a_data)):
    #     a_data[i]=float("{:0.3f}".format(a_data[i]))

    # plt.legend()
    # x = [ i for i in range(len(a_data))]
    # plt.plot(x, a_data, label=image)

    min_a=min(a_data)
    # min_a=mode(a_data)
    # min_a=median(a_data)
    ret =max(a_data)- min_a
    cutoff = 0.1*ret
    integral = 0
    #area
    for i in range(len(a_data)):
        x = a_data[i] - min_a
        if x > cutoff:
            integral += x

    ret = ("{:0.3f}".format(integral))
    return float(ret)

def find(image):
    process(image)
    computed = observe(image)
    conc_found=0

    # print(conc)
    # print(logconc)
    # print(obs)
    # print(image)
    # print(computed)

    for i in range(len(obs)):
        if obs[i]>computed:
            print(obs[i])
            y=obs[i]-obs[i-1]
            x=conc[i]-conc[i-1]
            im=x/y #inverse of slope m
            conc_found=((computed-obs[i])*im)+conc[i]
            conc_found= ("{:0.3f}".format(conc_found))
            ##3log
            x=logconc[i]-logconc[i-1]
            im=x/y #inverse of slope m
            log_conc_found=((computed-obs[i])*im)+logconc[i]
            log_conc_found=math.exp(log_conc_found)
            log_conc_found= ("{:0.3f}".format(log_conc_found))
            
            ##3
            print(image+" score: "+str(computed)+", conc lin: "+str(conc_found)+"mIU, conc log :"+str(log_conc_found)+"mIU")
            break

def compute(filename):
    global conc
    global obs
    global obs2
    conc.append(float(filename))
    a_data = observe(filename)
    # observation = observe(filename)
    # obs.append(observation)
    obs.append(a_data)


    # computation in log
    name = float(filename)
    if name==0:
        logconc.append(0)
    else:
        logconc.append(math.log(float(filename)))

def debloat(line):
    global images
    line = line.strip()
    if line.startswith("u"):
        line = line[:-5]
        find_list.append(line)
        
    if line.endswith(".jpeg"):
        line = line[:-5]
        line = float(line)
        images.append(line)
    images = sorted(images)

def spitcalib(folder):
    global conc
    global obs
    calib_file = open(folder+"_calib.txt","w")
    for i in range(len(conc)):
        calib_file.write(str(conc[i])+"\t"+str(obs[i])+"\n")
    calib_file.close()

folder= input("Folder name: ")
os.chdir("tests/"+folder)
os.system("ls>ls.txt")
os.system("mkdir temp")

image_list=open('ls.txt')
for line in image_list.readlines():
    debloat(line)    
image_list.close()

for name in images:
    name=str(name)
    process(name)
    compute(name)

spitcalib(folder)

for name in find_list:
    find(name)

plt.legend()
plt.plot(conc, obs)
plt.ylabel('area 10% of max')
plt.xlabel('Concentration ')
plt.show()

# for name in find_list:
#     find(name)

os.system("rm ls.txt")
# os.system("rm -r temp")

# research@ubio.co.in