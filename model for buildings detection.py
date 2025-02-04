
# Setting

#pip install h5py==2.10 -i https://pypi.tuna.tsinghua.edu.cn/simple/
! pip install h5py-2.10.0-cp37-cp37m-manylinux1_x86_64.whl

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow as tf
tf.__version__

#!pip install -i https://pypi.tuna.tsinghua.edu.cn/simple rasterio
! pip install rasterio-1.2.8-cp37-cp37m-manylinux1_x86_64.whl


import os
import sys
import random
import itertools
import colorsys

import numpy as np
from skimage.measure import find_contours
import matplotlib.pyplot as plt
from matplotlib import patches,  lines
from matplotlib.patches import Polygon
import IPython.display

import rasterio
import gdal
import cv2
from rasterio.plot import show
from google.colab.patches import cv2_imshow

"""# Train files generate"""



import os
import random 
 
segfilepath=r'/content/drive/MyDrive/val/label'
saveBasePath=r"/content/drive/MyDrive/val"
 

train_percent=1

temp_seg = os.listdir(segfilepath)
total_seg = []
for seg in temp_seg:
    if seg.endswith(".tif"):
        total_seg.append(seg)

num=len(total_seg)  
list=range(num)  
tv=int(num*train_percent)  
trainval= random.sample(list,tv)  
  
 
print("The number of train samples:",tv)

ftrain = open(os.path.join(saveBasePath,'train_seg.txt'), 'w')  

for i  in list:  
    name=total_seg[i]+';'+total_seg[i]+'\n'  
    ftrain.write(name) 
  
 
ftrain.close()

"""# Boundingbox dataset Transform

import os
import random 
 
segfilepath=r'/content/drive/MyDrive/test3/label'
saveBasePath=r"/content/drive/MyDrive/test3"
 

train_percent=1

temp_seg = os.listdir(segfilepath)
total_seg = []
for seg in temp_seg:
    if seg.endswith(".TIF"):
        total_seg.append(seg)

num=len(total_seg)  
list=range(num)  
tv=int(num*train_percent)  
trainval= random.sample(list,tv)  
  
 
print("The number of train samples:",tv)

ftrain = open(os.path.join(saveBasePath,'train_name.txt'), 'w')  

for i  in list:  
    name=total_seg[i]+'\n' #+';'+total_seg[i] 
    ftrain.write(name) 
  
 
ftrain.close()
"""

# read bounding box coordinates

import numpy as np

txt_path = '/content/drive/MyDrive/test3/dataset_box.txt'	# txtpath
image_path = '/content/drive/MyDrive/test3/image/' 	# Image path
saveBasePath = '/content/drive/MyDrive/test3/'
f = open(txt_path)
ftrain = open(os.path.join(saveBasePath,'train.txt'), 'w')
data_lists = f.readlines()	#read out str type
#D=open('/content/drive/MyDrive/test3/train_name.txt' ).readlines()
dataset= [ ]
j=int(data_lists[0].split(',')[0])
k=0
# 
while k!=len(data_lists):

  ftrain.write(data_lists[k].split(',')[0])
  if data_lists[k].split(',')[1] == '\n':
    ftrain.write(" "+"0,0,0,0,0"+"\n")
    k=k+1
    j=int(data_lists[k].split(',')[0])
  else:

     while j ==int(data_lists[k].split(',')[0]) :

       data1 = data_lists[k].strip('\n').strip(',').split(',') #，as split symbols
       data2 = data_lists[k+1].strip('\n').strip(',').split(',')
       x1,y1=np.array(data1[2:4]).astype("float")
       x2,y2=np.array(data2[2:4]).astype("float")
       xmin, xmax= np.sort([x1,x2])
       ymin, ymax= np.sort([y1,y2])


       img_label=rasterio.open(image_path+data2[0]+".TIF")
       affineT=np.linalg.inv(np.asarray(img_label.transform).reshape(3,3))
       Y=np.array( [ [xmin, xmax],[ymin, ymax] ] )
       YT=np.dot(affineT,np.vstack(( Y,np.array([1,1]))) ) # d = np.hstack((a,b))
    
       ftrain.write(" "+",".join( [item for item in YT[0:2,:].reshape(1,4)[0].astype(np.str)])+ ','+"1" ) 

       k=k+2
       if k==len(data_lists):
         break


     if k==len(data_lists):
         break
     else:
       ftrain.write("\n")
       j=int(data_lists[k].split(',')[0])

 

ftrain.close()


#dataset = np.array(dataset).astype("float").reshape(-1,4)
#print('Bounding box coordinates shape:',dataset.shape)

from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')
def random_colors(N, bright=True):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors

# Test transformed data
from utils.utils import draw_gaussian, gaussian_radius
import math
img=rasterio.open("/content/drive/MyDrive/test3/image/155.TIF") #247 185 146 206
old_img=np.moveaxis(img.read()[0:3],0,2)
#old_img = np.uint8( (cv2.cvtColor(old_img[:,:,0:3], cv2.COLOR_BGR2RGB))*255 )
Boxex=open('/content/drive/MyDrive/test3/train.txt').readlines()
line=Boxex[82].split()

box=np.zeros((len(line[1:]),4))
j=0
fig, ax = plt.subplots(1, figsize=(10,10))
colors =  random_colors(box.shape[0])
heatmap=np.zeros((512,512))
for i in line[1:]:
   box[j]=np.asarray(i.split(',')).astype(float).reshape(1,5)[0][0:4]
   x1, x2, y1, y2 = box[j]
   #print(x1, x2, y1, y2 )
   color = colors[j]

   p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                                alpha=0.7, linestyle="dashed",
                                edgecolor=color, facecolor='none')
   ax.scatter([x1,x2], [y1,y2], c=color, marker='o')
   
   ax.add_patch(p)

   # getting heat maps
   h=y2-y1
   w=x2-x1
   ct = np.array([(x1+x2) / 2, (y1+y2) / 2], dtype=np.float32)
   ct_int = ct.astype(np.int32)
   radius = gaussian_radius((math.ceil(h), math.ceil(w)))
   radius = max(0, int(radius))
   heatmap = draw_gaussian(heatmap, ct_int, radius)

   
   j=j+1


ax.imshow(old_img)

plt.figure(figsize=(10,10))
plt.imshow(heatmap)
plt.scatter([(box[:,0]+box[:,1])/2], [(box[:,2]+box[:,3])/2], c='r', marker='o',linewidths=0.001)

"""# DeformROI"""

#from keras.engine.topology import Layer
from keras.layers import Layer

class DeformROIPooling(Layer):
    """ Implements Region Of Interest Max Pooling 
        for channel-first images and relative bounding box coordinates

        # Constructor parameters
            pooled_height, pooled_width (int) -- 
              specify height and width of layer outputs

        Shape of inputs
            [(batch_size, pooled_height, pooled_width, n_channels),
             (batch_size, num_rois, 4)]

        Shape of output
            (batch_size, num_rois, pooled_height, pooled_width, n_channels)

    """
    def __init__(self, filters, pooled_height, pooled_width, **kwargs):
        self.filters=filters
        self.pooled_height = pooled_height
        self.pooled_width = pooled_width
       
 

        super(DeformROIPooling, self).__init__(**kwargs)
        


    def compute_output_shape(self, input_shape):
        """ Returns the shape of the ROI Layer output
        """
        feature_map_shape, rois_shape = input_shape
        assert feature_map_shape[0] == rois_shape[0]      
        return (feature_map_shape[0],feature_map_shape[1],feature_map_shape[2], self.filters)

    def call(self, x):
        """ Maps the input tensor of the ROI layer to its output

            # Parameters
                x[0] -- Convolutional feature map tensor,
                        shape (batch_size, pooled_height, pooled_width, n_channels)
                x[1] -- Tensor of region of interests from candidate bounding boxes,
                        shape (batch_size, num_rois, 4)
                        Each region of interest is defined by four relative 
                        coordinates (x_min, y_min, x_max, y_max) between 0 and 1
            # Output
                pooled_areas -- Tensor with the pooled region of interest, shape
                    (batch_size, num_rois, pooled_height, pooled_width, n_channels)
        """
        def curried_pool_rois(x): 

          
          return DeformROIPooling._pool_rois(x[0],  x[1], 
                                    self.pooled_height, 
                                    self.pooled_width)
        
        roiss= DeformROIPooling.get_rois( x[1] )
        

        FX=[x[0],roiss]

        

        pooled_areas = tf.map_fn(curried_pool_rois, FX, dtype=tf.float32)
        pooled_areas = K.reshape( pooled_areas, [ -1, K.int_shape(x[0])[1]*self.pooled_height,
                              K.int_shape(x[0])[2]*self.pooled_width, K.int_shape(x[0])[3]])
        
        
        pooled_areas= Conv2D(self.filters, kernel_size= (self.pooled_height,self.pooled_width), 
                         strides=(self.pooled_height,self.pooled_width), padding='valid', 
                         use_bias=False, kernel_initializer='he_normal', 
                         kernel_regularizer=l2(5e-4))(pooled_areas)
        
        

        return pooled_areas
    @staticmethod
    def get_rois( y2 ):

       idy2_0,idy_1,idy_2,idy_3 = K.int_shape(y2) #y2.get_shape().as_list()
       #W=tf.cast( idy_2, dtype=tf.float32)
       #H=tf.cast( idy_1, dtype=tf.float32)
       W= idy_2
       H= idy_1
       x= K.clip( tf.sort(y2[:,:,:,0:4],direction='DESCENDING',axis=-1)[:,:,:,0:2], 1, W-1  )
       y= K.clip( tf.sort(y2[:,:,:,4: ],direction='DESCENDING',axis=-1)[:,:,:,0:2], 1, H-1 )
       
       w= K.reshape( K.arange(0, idy_2,dtype=tf.float32 ), [-1,1] )
       h= K.reshape( K.arange(0, idy_1,dtype=tf.float32 ),  [-1,1] )
       
       
       idx_0,idx_1,idx_2,idx_3 = K.int_shape( x)
       Xmax = w+ K.reshape( tf.transpose( tf.expand_dims(x[:,:,:,0],axis=-1), [2,0,1,3]), [idy_2, -1 ])
       Xmin = w- K.reshape( tf.transpose(tf.expand_dims(x[:,:,:,1],axis=-1), [2,0,1,3]), [idy_2, -1 ])      
       Xmax = tf.transpose(K.reshape( Xmax, [ idx_2, -1, idx_1, 1] ) , [1,2,0,3 ] ) 
       Xmin = tf.transpose(K.reshape( Xmin, [ idx_2, -1, idx_1, 1] ) , [1,2,0,3 ] ) 
       X   = tf.concat([Xmin, Xmax], axis=-1) 
       X = K.clip( X, 0, W-1 )
       

       idy_0,idy_1,idy_2,idy_3 = K.int_shape( y)
       Ymax = h+ K.reshape( tf.transpose(tf.expand_dims(y[:,:,:,0],axis=-1), [1,0,2,3]), [idy_1, -1 ])
       Ymin = h- K.reshape( tf.transpose(tf.expand_dims(y[:,:,:,1],axis=-1), [1,0,2,3]), [idy_1, -1 ])
        
       Ymax = tf.transpose(K.reshape( Ymax, [ idy_1, -1, idy_2, 1] ) , [1,0,2,3 ] )
       Ymin = tf.transpose(K.reshape( Ymin, [ idy_1, -1, idy_2, 1] ) , [1,0,2,3 ] )
       Y   = tf.concat([Ymin, Ymax], axis=-1)   
       Y = K.clip( Y, 0, H-1 ) 

       rois= K.reshape( tf.concat([Y, X], axis=-1), [-1, idy_1*idy_2, 4] )
       
       return rois   


    @staticmethod
    def _pool_rois(feature_map, rois, pooled_height, pooled_width):
        """ Applies ROI pooling for a single image and varios ROIs
        """
        def curried_pool_roi(roi): 
          return DeformROIPooling._pool_roi(feature_map, roi, 
                                           pooled_height, pooled_width)

        pooled_areas = tf.map_fn(curried_pool_roi, rois, dtype=tf.float32)
        return pooled_areas

    @staticmethod
    def _pool_roi(feature_map, roi, pooled_height, pooled_width):
        """ Applies ROI pooling to a single image and a single region of interest
        """

        # Compute the region of interest  

        h_start = tf.cast(roi[0], 'int32')
        w_start = tf.cast(roi[2], 'int32')
        h_end  = tf.cast(roi[1], 'int32')
        w_end  = tf.cast(roi[3], 'int32')
        

        region = feature_map[h_start:h_end+1, w_start:w_end+1, :]
        

        # Divide the region into non overlapping areas
        region_height = h_end - h_start+1
        region_width  = w_end - w_start+1
        h_step = tf.cast( region_height / pooled_height, 'int32')
        w_step = tf.cast( region_width  / pooled_width , 'int32')

        areas = [[(
                    i*h_step, 
                    j*w_step, 
                    (i+1)*h_step if i+1 < pooled_height else region_height, 
                    (j+1)*w_step if j+1 < pooled_width else region_width
                   ) 
                   for j in range(pooled_width)] 
                  for i in range(pooled_height)]


        # take the maximum of each area and stack the result
        def pool_area(x): 
          return tf.math.reduce_mean(region[x[0]:x[2]+1, x[1]:x[3]+1, :], axis=[0,1])

        pooled_features = tf.stack([[pool_area(x) for x in row] for row in areas])
       
        return pooled_features

get_roipooling=DeformROIPooling(1, pooled_height=3, pooled_width=3 )

#Test DeformROIPooling
    image=rasterio.open('/content/drive/MyDrive/test3/image/241.TIF') #247 185 146 206
    image=np.moveaxis(image.read()[0:3],0,2)
    

    photo = tf.cast(np.expand_dims(image, axis=0),dtype=tf.float32)
    photo = Lambda(lambda x: tf.image.resize_images(x, (128, 128), align_corners=True))(photo)
    y2 = Conv2D(64, 3, padding='same', use_bias=False, kernel_initializer='he_normal', 
                kernel_regularizer=l2(5e-4))(photo)
    x=y2
    y2 = BatchNormalization()(y2)
    y2 = Activation('relu')(y2)
    y2 = Conv2D(8, 1, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(y2)
    get_roipooling=DeformROIPooling(1, pooled_height=3, pooled_width=3 )
    y1=get_roipooling([x,y2]) 
    plt.imshow( K.eval(y1)[0][:,:,0])
    
    # Construct model
    image_input= Input( shape=(128,128,3))
    x = Conv2D(64, 3, padding='same', use_bias=False, kernel_initializer='he_normal', 
                kernel_regularizer=l2(5e-4))(image_input)
    y= Conv2D(8, 1, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(x)

    get_roipooling=DeformROIPooling(1, pooled_height=3, pooled_width=3 )
    y1_=get_roipooling([x,y]) 
    model=Model( inputs=image_input, outputs=y1_ )
    model.summary( )

"""# Deformoffset"""

import keras.backend as K
import tensorflow as tf
from keras.initializers import constant, normal, zeros
from keras.layers import (Activation, BatchNormalization, Conv2D,
                          Conv2DTranspose, Dropout, Input, Lambda,
                          MaxPooling2D, Reshape, ZeroPadding2D)
from keras.models import Model
from keras.regularizers import l2
from keras.engine.topology import get_source_inputs
#from nets.center_training import loss, focal_loss
from nets.hourglass import HourglassNetwork
#from nets.resnet import ResNet50, centernet_head


def Deformoffset( arg):

       fmap,y2 = arg
       filters=64 
       kernelsize=3 
       dilated_rates=1 
       
       B,H,W,C = K.int_shape(fmap) #y2.get_shape().as_list()
       
       x= K.clip( tf.sort(y2[:,:,:,0:4],direction='DESCENDING',axis=-1)[:,:,:,0:2], 1, W-1  )
       y= K.clip( tf.sort(y2[:,:,:,4: ],direction='DESCENDING',axis=-1)[:,:,:,0:2], 1, H-1 )
       rx=dilated_rates*kernelsize # dilated rates of abscissa
       ry=dilated_rates*kernelsize # ditated rates of ordinate
      
       w= tf.reduce_sum(x, axis =-1, keepdims=True ) 
       h= tf.reduce_sum(y, axis =-1, keepdims=True ) 

       # create coordinates grid
       row= K.reshape(K.arange(0,H, dtype=tf.float32),[-1,1])
       row=  K.expand_dims( K.tile( row, W), -1)
       row = K.reshape(row,[H*W,1])

       column= K.reshape( K.arange(0,W, dtype=tf.float32), [1,-1])
       column=  K.expand_dims( K.tile( column, [H,1]), -1)
       column = K.reshape(column,[H*W,1])

       # get the dilated grid coordinates
       x_1=column-1-K.reshape(w/rx, [-1,H*W,1])
       x_0=column+K.reshape(w*1e-10, [-1,H*W,1])
       x_2=column+1+K.reshape(w/rx, [-1,H*W,1])
       x = tf.concat([x_1, x_0, x_2], axis=-1) 
       x = tf.reshape(x,[-1,H,W,1])
       x = K.tile(x,[1,1,1,kernelsize])

       y_1= row-1-K.reshape(h/ry, [-1,H*W,1])
       y_0=row+K.reshape(h*1e-10, [-1,H*W,1])
       y_2= row+1+ K.reshape(h/ry, [-1,H*W,1])
       y=tf.concat([y_1, y_0, y_2], axis=-1)
       y= tf.reshape(y,[-1,H,W,1])
       y = K.tile(y,[1,1,1,kernelsize])


       # create coordinates of interploation

       x_left=K.clip(tf.math.floor(x),0,W-1)
       x_right=K.clip(tf.math.ceil(x),0,W-1)
       y_top=K.clip(tf.math.floor(y),0,H-1)
       y_bottom=K.clip(tf.math.ceil(y),0,H-1)
       # calculate coordinates increment of interploation 
       x_right_x=K.tile( K.expand_dims( tf.reshape(x_right-x,[-1,W*H*kernelsize*kernelsize]),-1), [1,1,C])
       x_left_x=K.tile( K.expand_dims(tf.reshape(x-x_left,[-1,W*H*kernelsize*kernelsize]),-1), [1,1,C])
       y_top_y=K.tile( K.expand_dims(tf.reshape(y-y_top,[-1,W*H*kernelsize*kernelsize]),-1), [1,1,C])
       y_bottom_y=K.tile( K.expand_dims( tf.reshape(y_bottom-y,[-1,W*H*kernelsize*kernelsize]),-1), [1,1,C])


       # indices of interplolation
       left_top=tf.cast(tf.reshape(y_top*W+x_left, [-1,W*H*kernelsize*kernelsize]),dtype=tf.int32)
       right_top=tf.cast(tf.reshape(y_top*W+x_right, [-1,W*H*kernelsize*kernelsize]),dtype=tf.int32)
       left_bottom=tf.cast(tf.reshape(y_bottom*W+x_left, [-1,W*H*kernelsize*kernelsize]),dtype=tf.int32)
       right_bottom=tf.cast(tf.reshape(y_bottom*W+x_right, [-1,W*H*kernelsize*kernelsize]),dtype=tf.int32)
       # get feature value from interplation coordinates
       fmap=tf.reshape(fmap,[-1,W*H,C])
       f_left_top=tf.gather(fmap, left_top, batch_dims=1)
       f_right_top=tf.gather(fmap, right_top, batch_dims=1)
       f_left_bottom=tf.gather(fmap, left_bottom, batch_dims=1)
       f_right_bottom=tf.gather(fmap, right_bottom, batch_dims=1)
       # calculate bilinear interpolation
       f_resize=(x_right_x*f_left_top+
            x_left_x*f_left_bottom)*y_bottom_y +(x_right_x*f_right_top+
            x_left_x*f_right_bottom)*y_top_y
       f_resize=K.reshape(f_resize,[-1,H*kernelsize,W*kernelsize,C])
       
       f_resize= Conv2D(filters=filters, kernel_size= kernelsize, 
                         strides=(kernelsize,kernelsize), padding='valid', 
                         use_bias=False, kernel_initializer='he_normal', 
                         kernel_regularizer=l2(5e-4))(f_resize)
       f_resize = BatchNormalization()(f_resize)
       f_resize= Activation('relu')(f_resize)
       
       return f_resize

"""#Test Deformoffset
    image=rasterio.open('/content/drive/MyDrive/test3/image/241.TIF') #247 185 146 206
    image=np.moveaxis(image.read()[0:3],0,2)
    

    photo = tf.cast(np.expand_dims(image, axis=0),dtype=tf.float32)
    photo = Lambda(lambda x: tf.image.resize_images(x, (128, 128), align_corners=True))(photo)
    y2 = Conv2D(64, 3, padding='same', use_bias=False, kernel_initializer='he_normal', 
                kernel_regularizer=l2(5e-4))(photo)
    x=y2
    y2 = BatchNormalization()(y2)
    y2 = Activation('relu')(y2)
    y2 = Conv2D(8, 1, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(y2)
    f_resize = Deformoffset( [x, y2])
    plt.imshow( K.eval(f_resize)[0][:,:,30])

# SpectralDepthawaregate
"""

def spatial_attention(channel_refined_feature):
    maxpool_spatial = Lambda(lambda x: K.max(x, axis=-1, keepdims=True))(channel_refined_feature)
    avgpool_spatial = Lambda(lambda x: K.mean(x, axis=-1, keepdims=True))(channel_refined_feature)
    max_avg_pool_spatial = tf.concat([maxpool_spatial, avgpool_spatial],axis=-1)
    return Conv2D(filters=1, kernel_size=(5, 5), padding="same", 
                     activation=None, kernel_initializer='he_normal', use_bias=False)(max_avg_pool_spatial)


def Depthawaregate( arg):

   fmapD,fmapS=arg
   B,H,W,C=K.int_shape(fmapS)
   kernelsize=3
   stride=1
   fmapD=spatial_attention(fmapD )
   a=-2

   res1=tf.image.extract_patches(
				images=fmapD, 
				sizes=[1, kernelsize, kernelsize, 1], 
				strides=[1, stride, stride, 1], 
				rates=[1, 1, 1, 1], 
				padding='SAME')
   res2=tf.image.extract_patches(
				images=fmapS, 
				sizes=[1, kernelsize, kernelsize, 1], 
				strides=[1, stride, stride, 1], 
				rates=[1, 1, 1, 1], 
				padding='SAME') 
   res2=K.reshape(res2,[-1,kernelsize*H,kernelsize*W,C])
    
   res1=K.reshape( res1,[-1,H*W*kernelsize*kernelsize])
   res1_=K.reshape(K.tile(fmapD,[1,1,1,kernelsize**2] ), [-1,H*W*kernelsize*kernelsize])
   depthaware=tf.reshape( tf.math.exp( a*tf.abs(res1-res1_) ), [-1,kernelsize*H,kernelsize*W,1] )
   refmap= res2*depthaware

   refmap = Conv2D(C, (3, 3), strides=(3, 3), use_bias=False)(refmap)
   refmap = BatchNormalization()(refmap)
   refmap = Activation('relu')(refmap)  
   refmap = layers.add([refmap,fmapS])
   return refmap

def Spectralawaregate( arg):
   
   fmapD,fmapS=arg
   B,H,W,C=K.int_shape(fmapD)
   kernelsize=3
   stride=1

   fmapS1=AveragePooling2D(pool_size=(kernelsize, kernelsize), 
              strides=stride, padding='same', data_format=None)(fmapS)
   fmapS2=MaxPooling2D(pool_size=(kernelsize, kernelsize), 
              strides=stride, padding='same', data_format=None)(fmapS)
   fmapS= layers.add([fmapS1, fmapS2])

   fmapS=Conv2D(filters=kernelsize**2, kernel_size=1, padding='same', use_bias=False, kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))( fmapS) 
   fmapS = BatchNormalization()(fmapS)
   fmapS = Activation('relu')(fmapS)             

   res1=K.reshape( fmapS, [-1,H*W*kernelsize*kernelsize,1])
   res2=tf.image.extract_patches(
				images=fmapD, 
				sizes=[1, kernelsize, kernelsize, 1], 
				strides=[1, stride, stride, 1], 
				rates=[1, 1, 1, 1], 
				padding='SAME')
   
   res2=K.reshape(res2,[-1,H*W*kernelsize*kernelsize,C])
   
   refmap = K.reshape(res1*res2, [-1,kernelsize*H,kernelsize*W,C])
   refmap = Conv2D(C, (3, 3), strides=(3, 3), use_bias=False)(refmap)
   refmap = BatchNormalization()(refmap)
   refmap = Activation('relu')(refmap)  
   refmap = layers.add([refmap,fmapD])
   return refmap

def pool_pyramid(feats,H,W, pool_factor,out_channel):
  pool_outs=[]
  for p in pool_factor:
      
      pool_size = strides = [int(np.round(float(H)/p)),int(np.round(float(W)/p))]
      pooled = AveragePooling2D(pool_size=pool_size,strides=strides,padding='same')(feats)
      pooled = tf.image.resize_images(pooled,(p,p))    
      pooled = K.reshape(pooled,[-1,p**2,out_channel] )
      pool_outs.append(pooled)

  pool_outs= tf.concat(pool_outs,axis=1)
  return pool_outs



def non_localgate( arg ):
   
   fmapD,fmapS=arg
   B,H,W,C_=K.int_shape(fmapD)
   C=C_//4
   kernelsize=3
   stride=1
   pool_factors= [2,3,6,8]
   
   fmapS1=Conv2D(C, kernel_size=1, padding='same', use_bias=False, kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))( fmapS) 
   fmapS1=K.reshape(fmapS1,[-1,H*W,C])
   fmapS2=Conv2D(C, kernel_size=1, padding='same', use_bias=False, kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))( fmapS)  
   fmapS2=pool_pyramid(feats=fmapS2,H=H,W=W, pool_factor=pool_factors, out_channel=C)
   fmapS2_=tf.transpose(fmapS2,[0,2,1] )
   non_localS=tf.matmul(fmapS1,fmapS2_ )

    
   fmapD1=Conv2D(C, kernel_size=1, padding='same', use_bias=False, kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))( fmapD) 
   fmapD1=K.reshape(fmapD1,[-1,H*W,C])
   fmapD2=Conv2D(C, kernel_size=1, padding='same', use_bias=False, kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))( fmapD)  
   fmapD2=pool_pyramid(feats=fmapD2,H=H,W=W, pool_factor=pool_factors, out_channel=C)
   fmapD2_=tf.transpose(fmapS2,[0,2,1] )
   non_localD=tf.matmul(fmapD1,fmapD2_ )  


   fmapSD=tf.concat([K.expand_dims(non_localS, axis=-1), K.expand_dims(non_localD, axis=-1 )], axis=-1)
   fmapSD=Conv2D(filters=2, kernel_size=1, padding='same', use_bias=False, 
       kernel_initializer='he_normal', activation='softmax',kernel_regularizer=l2(5e-4))( fmapSD) 


   fS=K.reshape( tf.matmul(fmapSD[:,:,:,0],fmapS2), [-1,H,W,C])
   fS=Conv2D(C_, kernel_size=1, padding='same', use_bias=False, kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))( fS) 
   fS = BatchNormalization()(fS)       
   fS=layers.add( [ fS,fmapS] ) 

   fD=K.reshape( tf.matmul(fmapSD[:,:,:,1],fmapD2), [-1,H,W,C])
   fD=Conv2D(C_, kernel_size=1, padding='same', use_bias=False, kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))( fD) 
   fD = BatchNormalization()(fD)        
   fD=layers.add( [ fD,fmapD])

   return [fS, fD]

"""# Model: SpectralDepthfusion"""

#-------------------------------------------------------------#
#   ResNet50 model
#-------------------------------------------------------------#
from __future__ import print_function

import keras.backend as K
import numpy as np
from keras import layers
from keras.applications.imagenet_utils import (decode_predictions,preprocess_input)
from keras.layers import (Activation, AveragePooling2D, BatchNormalization,Concatenate,
              Softmax,Conv2D,Reshape, Conv2DTranspose, Dense, Dropout, Flatten,
                    Input, MaxPooling2D, ZeroPadding2D, Lambda, AveragePooling2D)
import keras
from keras.models import Model
from keras.preprocessing import image
from keras.regularizers import l2
from keras.utils.data_utils import get_file



def identity_block(input_tensor, kernel_size, filters, stage, block):

    filters1, filters2, filters3 = filters

    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = Conv2D(filters1, (1, 1), name=conv_name_base + '2a', use_bias=False)(input_tensor)
    x = BatchNormalization(name=bn_name_base + '2a')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters2, kernel_size,padding='same', name=conv_name_base + '2b', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2b')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters3, (1, 1), name=conv_name_base + '2c', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2c')(x)

    x = layers.add([x, input_tensor])
    x = Activation('relu')(x)
    return x


def conv_block(input_tensor, kernel_size, filters, stage, block, strides=(2, 2)):

    filters1, filters2, filters3 = filters

    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = Conv2D(filters1, (1, 1), strides=strides,
               name=conv_name_base + '2a', use_bias=False)(input_tensor)
    x = BatchNormalization(name=bn_name_base + '2a')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters2, kernel_size, padding='same',
               name=conv_name_base + '2b', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2b')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters3, (1, 1), name=conv_name_base + '2c', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2c')(x)

    shortcut = Conv2D(filters3, (1, 1), strides=strides,
                      name=conv_name_base + '1', use_bias=False)(input_tensor)
    shortcut = BatchNormalization(name=bn_name_base + '1')(shortcut)

    x = layers.add([x, shortcut])
    x = Activation('relu')(x)
    return x


def ResNet50(inputs):


    # 512x512x6
    inputS=Lambda(lambda x: x[:,:,:,0:4])(inputs)
    inputD=Lambda(lambda x: K.expand_dims(x[:,:,:,5], axis=-1))(inputs)

    #-----------Spetral Feature------------#
    x = ZeroPadding2D((3, 3))(inputS)
    # 256,256,64
    x = Conv2D(64, (7, 7), strides=(2, 2), name='conv1', use_bias=False)(x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    # 256,256,64 -> 128,128,64
    x = MaxPooling2D((3, 3), strides=(2, 2), padding="same")(x)

    #-----------Depth Feature------------#
    y = ZeroPadding2D((3, 3))( inputD )
    # 256,256,64
    y = Conv2D(64, (7, 7), strides=(2, 2), use_bias=False)(y)
    y = BatchNormalization()(y)
    y = Activation('relu')(y)
    # 256,256,64 -> 128,128,256
    y = MaxPooling2D((3, 3), strides=(2, 2), padding="same")(y)
    y = Conv2D(256, (3, 3), strides=(1, 1),padding="same", use_bias=False)(y)
    y = BatchNormalization( )(y)
    y = Activation('relu')(y)

    x2 = Lambda(Depthawaregate)( [y,x])
    y2 = Lambda(Spectralawaregate)( [y,x])
    # 128,128,64 -> 128,128,256
    x = conv_block(x2, 3, [64, 64, 256], stage=2, block='a', strides=(1, 1))
    x = identity_block(x, 3, [64, 64, 256], stage=2, block='b')
    C2S = identity_block(x, 3, [64, 64, 256], stage=2, block='c')
    C2D = identity_block(y2, 3, [64, 64, 256], stage=2, block='C2D')
    C2S,C2D = Lambda( non_localgate )( [C2D,C2S] )
    C2 = layers.add([C2D,C2S])
    
    x3 = Lambda(Depthawaregate)( [C2D,C2S])
    y3 = Lambda(Spectralawaregate)( [C2D,C2S])
    # 128,128,256 -> 64,64,512
    x = conv_block(x3, 3, [128, 128, 512], stage=3, block='a')
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='b')
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='c')
    C3S = identity_block(x, 3, [128, 128, 512], stage=3, block='d')
    C3D = Conv2D(512, (3, 3), strides=(2, 2),padding="same", use_bias=False)(y3)
    C3D = identity_block(C3D, 3, [128, 128, 512], stage=3, block='C3D')
    C3S,C3D = Lambda( non_localgate )( [C3D,C3S] )
    C3 = layers.add([C3D,C3S])

    x4 = Lambda(Depthawaregate)( [C3D,C3S])
    y4 = Lambda(Spectralawaregate)( [C3D,C3S])
    # 64,64,512 -> 32,32,1024
    x = conv_block(x4, 3, [256, 256, 1024], stage=4, block='a')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='b')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='c')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='d')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='e')
    C4S = identity_block(x, 3, [256, 256, 1024], stage=4, block='f')
    C4D = Conv2D(1024, (3, 3), strides=(2, 2),padding="same", use_bias=False)(y4)
    C4D = identity_block(C4D, 3, [256, 256, 1024], stage=4, block='C4D')
    C4S,C4D = Lambda( non_localgate )( [C4D,C4S] )
    C4=layers.add([C4D,C4S])

    # 32,32,1024 -> 16,16,2048
    x = conv_block(C4, 3, [512, 512, 2048], stage=5, block='a')
    x = identity_block(x, 3, [512, 512, 2048], stage=5, block='b')
    C5 = identity_block(x, 3, [512, 512, 2048], stage=5, block='c')
    
    return C5,C4,C3,C2

def SpectralDepthfusion( input_shape,num_classes ): 

    image_input = Input(shape=input_shape )
    C5,C4,C3,C2 = ResNet50(image_input)

    # Feature fusion Pyramid
    x=Conv2D(1024, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( C5)
    x=Conv2D(1024, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( C5)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (32, 32), align_corners=True))(x)
    x=layers.add([C4, x])

    x=Conv2D(512, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x=Conv2D(512, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (64, 64), align_corners=True))(x)
    x=layers.add([C3, x])

    x=Conv2D(256, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x=Conv2D(256, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (128, 128), align_corners=True))(x)
    x=layers.add([C2, x])

    x = Dropout(rate=0.5)(x)
    size_before4 = K.int_shape(image_input)
    x = Lambda(lambda xx:tf.image.resize_images(xx,size_before4[1:3]))(x)

    x = Conv2D(num_classes, 3, padding='same', kernel_initializer='he_normal')(x)
    x = BatchNormalization()(x)
    x = Reshape((-1,num_classes))(x)
    activation = Softmax( )(x)
    """
    x = Conv2D(64, 3,padding='same', kernel_initializer='he_normal')(x)
    x = BatchNormalization()(x)
    x=Conv2D(num_classes, 1,padding='same', kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(x)
    activation = Softmax(axis=[1,2] )(x)
    activation = Reshape((-1,num_classes))(activation)
    """
    model = Model(inputs=image_input, outputs=activation)
    return model



"""# Model: Deformable Centernet"""

def Mean_WH(y2):
  x=tf.sort(y2[:,:,:,0:4],direction='DESCENDING',axis=-1)[:,:,:,0:2]
  x=tf.expand_dims(tf.math.reduce_mean(x,axis=-1 ), axis=-1)
  y=tf.sort(y2[:,:,:,4: ],direction='DESCENDING',axis=-1)[:,:,:,0:2]
  y=tf.expand_dims(tf.math.reduce_mean(y,axis=-1 ),axis=-1)
  y2_=tf.concat([x, y], axis=-1) 
  return  y2_

#-------------------------------------------------------------#
#   ResNet50
#-------------------------------------------------------------#
from __future__ import print_function

import keras.backend as K
import numpy as np
from keras import layers
from keras.applications.imagenet_utils import (decode_predictions,
                                               preprocess_input)
from keras.layers import (Activation, AveragePooling2D, BatchNormalization,Concatenate,
                          Conv2D, Conv2DTranspose, Dense, Dropout, Flatten,
                          Input, MaxPooling2D, ZeroPadding2D, Lambda, AveragePooling2D)
from keras.models import Model
from keras.preprocessing import image
from keras.regularizers import l2
from keras.utils.data_utils import get_file



def identity_block(input_tensor, kernel_size, filters, stage, block):

    filters1, filters2, filters3 = filters

    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = Conv2D(filters1, (1, 1), name=conv_name_base + '2a', use_bias=False)(input_tensor)
    x = BatchNormalization(name=bn_name_base + '2a')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters2, kernel_size,padding='same', name=conv_name_base + '2b', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2b')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters3, (1, 1), name=conv_name_base + '2c', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2c')(x)

    x = layers.add([x, input_tensor])
    x = Activation('relu')(x)
    return x


def conv_block(input_tensor, kernel_size, filters, stage, block, strides=(2, 2)):

    filters1, filters2, filters3 = filters

    conv_name_base = 'res' + str(stage) + block + '_branch'
    bn_name_base = 'bn' + str(stage) + block + '_branch'

    x = Conv2D(filters1, (1, 1), strides=strides,
               name=conv_name_base + '2a', use_bias=False)(input_tensor)
    x = BatchNormalization(name=bn_name_base + '2a')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters2, kernel_size, padding='same',
               name=conv_name_base + '2b', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2b')(x)
    x = Activation('relu')(x)

    x = Conv2D(filters3, (1, 1), name=conv_name_base + '2c', use_bias=False)(x)
    x = BatchNormalization(name=bn_name_base + '2c')(x)

    shortcut = Conv2D(filters3, (1, 1), strides=strides,
                      name=conv_name_base + '1', use_bias=False)(input_tensor)
    shortcut = BatchNormalization(name=bn_name_base + '1')(shortcut)

    x = layers.add([x, shortcut])
    x = Activation('relu')(x)
    return x


def ResNet50(inputs):
    # 512x512x3
    x = ZeroPadding2D((3, 3))(inputs)
    # 256,256,64
    x = Conv2D(64, (7, 7), strides=(2, 2), name='conv1', use_bias=False)(x)
    x = BatchNormalization(name='bn_conv1')(x)
    x = Activation('relu')(x)

    # 256,256,64 -> 128,128,64
    x = MaxPooling2D((3, 3), strides=(2, 2), padding="same")(x)

    # 128,128,64 -> 128,128,256
    x = conv_block(x, 3, [64, 64, 256], stage=2, block='a', strides=(1, 1))
    x = identity_block(x, 3, [64, 64, 256], stage=2, block='b')
    C2 = identity_block(x, 3, [64, 64, 256], stage=2, block='c')

    # 128,128,256 -> 64,64,512
    x = conv_block(C2, 3, [128, 128, 512], stage=3, block='a')
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='b')
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='c')
    C3 = identity_block(x, 3, [128, 128, 512], stage=3, block='d')

    # 64,64,512 -> 32,32,1024
    x = conv_block(C3, 3, [256, 256, 1024], stage=4, block='a')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='b')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='c')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='d')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='e')
    C4 = identity_block(x, 3, [256, 256, 1024], stage=4, block='f')

    # 32,32,1024 -> 16,16,2048
    x = conv_block(C4, 3, [512, 512, 2048], stage=5, block='a')
    x = identity_block(x, 3, [512, 512, 2048], stage=5, block='b')
    C5 = identity_block(x, 3, [512, 512, 2048], stage=5, block='c')

    return C5,C4,C3,C2

def centernet_head(image_input,num_classes):
    #-------------------------------#
    #   Decoder
    #-------------------------------#

    C5,C4,C3,C2 = ResNet50(image_input)
   
    # Feature fusion Pyramid
    x=Conv2D(1024, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( C5)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (32, 32), align_corners=True))(x)
    x=layers.add([C4, x])

    x=Conv2D(512, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (64, 64), align_corners=True))(x)
    x=layers.add([C3, x])

    x=Conv2D(256, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (128, 128), align_corners=True))(x)
    x=layers.add([C2, x])

    x = Dropout(rate=0.5)(x)

    """
    num_filters = 256
    # 16, 16, 2048  ->  32, 32, 256 -> 64, 64, 128 -> 128, 128, 64

    for i in range(3):
        # upsampling
        x = Conv2DTranspose(num_filters // pow(2, i), (4, 4), strides=2, use_bias=False, padding='same',
                            kernel_initializer='he_normal',
                            kernel_regularizer=l2(5e-4))(x)
        x = BatchNormalization()(x)
        x = Activation('relu')(x)
    """

    # Get the features from 128,128,64 layers
    # wh header
    y2 = Conv2D(64, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(x)
    y2 = BatchNormalization()(y2)
    y2 = Activation('relu')(y2)
    y2 = Conv2D(8, 1, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(y2) 
    y2_= Lambda(Mean_WH, name='Mean_WH')(y2)

 

    # hm header enhance
    
    y1 = Conv2D(64, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(x)

    
    #get_roipooling=DeformROIPooling( filters=64, pooled_height=3, pooled_width=3 )
    #y1_=get_roipooling([y1,y2]) 
   
    y1_= Lambda( Deformoffset, name='Deformoffset')( [ y1, y2])

    
    fusion = layers.add([y1, y1_]) #
    
    y1 = Conv2D(32, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(fusion)#fusion
    y1 = BatchNormalization()(y1)
    y1 = Activation('relu')(y1)
    y1 = Conv2D(num_classes, 1,padding='same', kernel_initializer='he_normal', kernel_regularizer=l2(5e-4), activation='sigmoid')(y1)
    
    # wh rectification
    y2_re = Conv2D(2, 3, padding='same', kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(fusion)
    y2  = layers.add([y2_,y2_re]) #


    # reg header
    y3 = Conv2D(64, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(x)
    y3 = BatchNormalization()(y3)
    y3 = Activation('relu')(y3)
    y3 = Conv2D(2, 1, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(y3)

    
    return y1, y2, y3

import keras.backend as K
import tensorflow as tf
from keras.initializers import constant, normal, zeros
from keras.layers import (Activation, BatchNormalization, Conv2D,
                          Conv2DTranspose, Dropout, Input, Lambda,
                          MaxPooling2D, Reshape, ZeroPadding2D)
from keras.models import Model
from keras.regularizers import l2
from keras.engine.topology import get_source_inputs
#from nets.center_training import loss, focal_loss
from nets.hourglass import HourglassNetwork
#from nets.resnet import ResNet50, centernet_head


def centernet(input_shape, num_classes, backbone='resnet50', max_objects=100, mode="train"):
    assert backbone in ['resnet50', 'hourglass']
    output_size = input_shape[0] // 4

    image_input = Input(shape=input_shape )
    hm_input = Input(shape=(output_size, output_size, num_classes)) 
    wh_input = Input(shape=(max_objects, 2))  
    reg_input = Input(shape=(max_objects, 2))  
    reg_mask_input = Input(shape=(max_objects,))  
    index_input = Input(shape=(max_objects,))
    

    if backbone=='resnet50':

        y1, y2, y3 = centernet_head(image_input,num_classes)

        if mode=="train":
            loss_ = Lambda(loss, name='centernet_loss')([y1, y2, y3, hm_input, wh_input, reg_input, reg_mask_input, index_input])
            model = Model(inputs=[image_input, hm_input, wh_input, reg_input, reg_mask_input, index_input], outputs=[loss_])
            
            return model
        else:
            detections = Lambda(lambda x: decode(*x, max_objects=max_objects,
                                                num_classes=num_classes))([y1, y2, y3])
            prediction_model = Model(inputs=image_input, outputs=detections)
            return prediction_model



"""# Model: SpectralDepthfusion1"""

def ResNet50(inputs):
    

    # 512x512x3
    x = ZeroPadding2D((3, 3))(inputs)
    # 256,256,64
    x = Conv2D(64, (7, 7), strides=(2, 2), name='conv1', use_bias=False)(x)
    x = BatchNormalization(name='bn_conv1')(x)
    x = Activation('relu')(x)

    # 256,256,64 -> 128,128,64
    x = MaxPooling2D((3, 3), strides=(2, 2), padding="same")(x)

    # 128,128,64 -> 128,128,256
    x = conv_block(x, 3, [64, 64, 256], stage=2, block='a', strides=(1, 1))
    x = identity_block(x, 3, [64, 64, 256], stage=2, block='b')
    C2 = identity_block(x, 3, [64, 64, 256], stage=2, block='c')

    # 128,128,256 -> 64,64,512
    x = conv_block(C2, 3, [128, 128, 512], stage=3, block='a')
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='b')
    x = identity_block(x, 3, [128, 128, 512], stage=3, block='c')
    C3 = identity_block(x, 3, [128, 128, 512], stage=3, block='d')

    # 64,64,512 -> 32,32,1024
    x = conv_block(C3, 3, [256, 256, 1024], stage=4, block='a')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='b')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='c')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='d')
    x = identity_block(x, 3, [256, 256, 1024], stage=4, block='e')
    C4 = identity_block(x, 3, [256, 256, 1024], stage=4, block='f')

    # 32,32,1024 -> 16,16,2048
    x = conv_block(C4, 3, [512, 512, 2048], stage=5, block='a')
    x = identity_block(x, 3, [512, 512, 2048], stage=5, block='b')
    C5 = identity_block(x, 3, [512, 512, 2048], stage=5, block='c')

    return C5,C4,C3,C2


def SpectralDepthfusion1( input_shape,num_classes ): 

    image_input = Input(shape=input_shape )
    C5,C4,C3,C2 = ResNet50(image_input)

    # Feature fusion Pyramid
    x=Conv2D(1024, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( C5)
    x=Conv2D(1024, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( C5)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (32, 32), align_corners=True))(x)
    x=layers.add([C4, x])

    x=Conv2D(512, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x=Conv2D(512, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (64, 64), align_corners=True))(x)
    x=layers.add([C3, x])

    x=Conv2D(256, 1, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x=Conv2D(256, 3, padding='same', use_bias=False, kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))( x)
    x = BatchNormalization()(x)
    x = Activation('relu')(x)
    x=Lambda(lambda x: tf.image.resize_images(x, (128, 128), align_corners=True))(x)
    x=layers.add([C2, x])

    x = Dropout(rate=0.5)(x)
    size_before4 = K.int_shape(image_input)
    x = Lambda(lambda xx:tf.image.resize_images(xx,size_before4[1:3]))(x)

    x = Conv2D(num_classes, 3, padding='same', kernel_initializer='he_normal')(x)
    x = BatchNormalization()(x)
    x = Reshape((-1,num_classes))(x)
    activation = Softmax( )(x)
    """
    x = Conv2D(64, 3,padding='same', kernel_initializer='he_normal')(x)
    x = BatchNormalization()(x)
    x=Conv2D(num_classes, 1,padding='same', kernel_initializer='he_normal', kernel_regularizer=l2(5e-4))(x)
    activation = Softmax(axis=[1,2] )(x)
    activation = Reshape((-1,num_classes))(activation)
    """
    model = Model(inputs=image_input, outputs=activation)
    return model

model = SpectralDepthfusion1( input_shape=[512, 512, 3],num_classes=2 )

model.summary()

"""# Taining Generator"""

import math
from random import shuffle

import cv2
import keras.backend as K
import numpy as np
import tensorflow as tf
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
from PIL import Image
from utils.utils import draw_gaussian, gaussian_radius


    
def focal_loss(hm_pred, hm_true):
    #-------------------------------------------------------------------------#
    #   find positive samples and negative samples in each image
    #    one ture anchor for the positive sample
    #  
    #-------------------------------------------------------------------------#
    pos_mask = tf.cast(tf.equal(hm_true, 1), tf.float32)
    neg_mask = tf.cast(tf.less(hm_true, 1), tf.float32)
    #-------------------------------------------------------------------------#
 
    #-------------------------------------------------------------------------#
    neg_weights = tf.pow(1 - hm_true, 4)

    #-------------------------------------------------------------------------#
    #   focal loss
    #-------------------------------------------------------------------------#
    pos_loss = -tf.log(tf.clip_by_value(hm_pred, 1e-6, 1.)) * tf.pow(1 - hm_pred, 2) * pos_mask
    neg_loss = -tf.log(tf.clip_by_value(1 - hm_pred, 1e-6, 1.)) * tf.pow(hm_pred, 2) * neg_weights * neg_mask

    num_pos = tf.reduce_sum(pos_mask)
    pos_loss = tf.reduce_sum(pos_loss)
    neg_loss = tf.reduce_sum(neg_loss)

    #-------------------------------------------------------------------------#
    #   loss normalaziton
    #-------------------------------------------------------------------------#
    cls_loss = tf.cond(tf.greater(num_pos, 0), lambda: (pos_loss + neg_loss) / num_pos, lambda: neg_loss)
    return cls_loss


def reg_l1_loss(y_pred, y_true, indices, mask):
    #b = tf.shape(y_pred)[0]

    #k = tf.shape(indices)[1]
    #c = tf.shape(y_pred)[-1]
    #y_pred = tf.reshape(y_pred, (b, -1, c))
    y_pred = tf.reshape(y_pred, (-1, K.int_shape(y_pred)[1]*K.int_shape(y_pred)[2], K.int_shape(y_pred)[3]))

    indices = tf.cast(indices, tf.int32)
    y_pred = tf.gather(y_pred, indices, batch_dims=1)
    mask = tf.tile(tf.expand_dims(mask, axis=-1), (1, 1, 2))
    total_loss = tf.reduce_sum(tf.abs(y_true * mask - y_pred * mask))
    reg_loss = total_loss / (tf.reduce_sum(mask) + 1e-4)
    return reg_loss

def loss(args):


    #-----------------------------------------------------------------------------------------------------------------#
    hm_pred, wh_pred, reg_pred, hm_true, wh_true, reg_true, reg_mask, indices = args
    hm_loss = focal_loss(hm_pred, hm_true)
    wh_loss = 0.1 * reg_l1_loss(wh_pred, wh_true, indices, reg_mask)
    reg_loss = reg_l1_loss(reg_pred, reg_true, indices, reg_mask)
    total_loss = hm_loss + wh_loss + reg_loss
    
    return total_loss


class Generator(object):
    def __init__(self,batch_size,train_lines,val_lines,
                input_size,num_classes,image_path,max_objects=100):
        
        self.batch_size = batch_size
        self.train_lines = train_lines
        self.val_lines = val_lines
        self.input_size = input_size
        self.output_size = (int(input_size[0]/4) , int(input_size[1]/4))
        self.num_classes = num_classes
        self.max_objects = max_objects
        
    def get_box( self, line ):
       j=0
       box=np.zeros((len(line[1:]),5))
       for i in line[1:]:
          a =np.asarray(i.split(',')).astype(np.float32).reshape(1,5)[0]
          box[j]=[a[0],a[3],a[1],a[2],a[4]]
          j=j+1
       return box


    def get_random_data(self, image_path,annotation_line):

        line = annotation_line.split( )
        #image = Image.open(image_path+line[0])
        image=rasterio.open(image_path+line[0]+".TIF") #247 185 146 206
        image=np.moveaxis(image.read()[0:3],0,2)
        #image = np.uint8( (cv2.cvtColor(image[:,:,0:3], cv2.COLOR_BGR2RGB))*255 )
        #box = np.array([np.array(list(map(int,box.split(',')))) for box in line[1:]])
        box = self.get_box( line )

        return image, box

    def generate(self, train=True):
        while True:
            if train:
               
                shuffle(self.train_lines)
                lines = self.train_lines
            else:
                shuffle(self.val_lines)
                lines = self.val_lines
                
            batch_images = np.zeros((self.batch_size, self.input_size[0], self.input_size[1], self.input_size[2]), dtype=np.float32)
            batch_hms = np.zeros((self.batch_size, self.output_size[0], self.output_size[1], self.num_classes), dtype=np.float32)
            batch_whs = np.zeros((self.batch_size, self.max_objects, 2), dtype=np.float32)
            batch_regs = np.zeros((self.batch_size, self.max_objects, 2), dtype=np.float32)
            batch_reg_masks = np.zeros((self.batch_size, self.max_objects), dtype=np.float32)
            batch_indices = np.zeros((self.batch_size, self.max_objects), dtype=np.float32)
            
            b = 0
            for annotation_line in lines: 


                img,y = self.get_random_data(image_path, annotation_line)


                if len(y)!=0:
                    boxes = np.array(y[:,:4],dtype=np.float32)
                    boxes[:,0] = boxes[:,0]/self.input_size[1]*self.output_size[1]
                    boxes[:,1] = boxes[:,1]/self.input_size[0]*self.output_size[0]
                    boxes[:,2] = boxes[:,2]/self.input_size[1]*self.output_size[1]
                    boxes[:,3] = boxes[:,3]/self.input_size[0]*self.output_size[0]

                for i in range(len(y)):
                    bbox = boxes[i].copy()
                    bbox = np.array(bbox)
                    bbox[[0, 2]] = np.clip(bbox[[0, 2]], 0, self.output_size[1] - 1)
                    bbox[[1, 3]] = np.clip(bbox[[1, 3]], 0, self.output_size[0] - 1)
                    cls_id = int(y[i,-1])-1
                    
                    h, w = bbox[3] - bbox[1], bbox[2] - bbox[0]
                    if h > 0 and w > 0:
                        ct = np.array([(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2], dtype=np.float32)
                        ct_int = ct.astype(np.int32)
                        
                        # heat maps
                        radius = gaussian_radius((math.ceil(h), math.ceil(w)))
                        radius = max(0, int(radius))
                        batch_hms[b, :, :, cls_id] = draw_gaussian(batch_hms[b, :, :, cls_id], ct_int, radius)
                        batch_whs[b, i] = 1. * w, 1. * h
                       
                       

                        # center offsets
			
                        batch_regs[b, i] = ct - ct_int


                    
                        batch_reg_masks[b, i] = 1
                    
                        batch_indices[b, i] = ct_int[1] * self.output_size[1] + ct_int[0]

                # origninal data BGR images
                batch_images[b] = img
                b = b + 1
                if b == self.batch_size:
                    b = 0
                    yield [batch_images, batch_hms, batch_whs, batch_regs, batch_reg_masks, batch_indices], np.zeros((self.batch_size,))              

                    batch_images = np.zeros((self.batch_size, self.input_size[0], self.input_size[1], 3), dtype=np.float32)

                    batch_hms = np.zeros((self.batch_size, self.output_size[0], self.output_size[1], self.num_classes),
                                        dtype=np.float32)
                    batch_whs = np.zeros((self.batch_size, self.max_objects, 2), dtype=np.float32)
                    batch_regs = np.zeros((self.batch_size, self.max_objects, 2), dtype=np.float32)
                    batch_reg_masks = np.zeros((self.batch_size, self.max_objects), dtype=np.float32)
                    batch_indices = np.zeros((self.batch_size, self.max_objects), dtype=np.float32)

"""# Test Generator
class Generator1(object):
    def __init__(self,batch_size,train_lines,val_lines,
                input_size,num_classes,image_path,max_objects=100):
        
        self.batch_size = batch_size
        self.train_lines = train_lines
        self.val_lines = val_lines
        self.input_size = input_size
        self.output_size = (int(input_size[0]/4) , int(input_size[1]/4))
        self.num_classes = num_classes
        self.max_objects = max_objects
    def get_box( self, line ):
       j=0
       box=np.zeros((len(line[1:]),5))
       for i in line[1:]:
          a =np.asarray(i.split(',')).astype(np.float32).reshape(1,5)[0]
          box[j]=[a[0],a[3],a[1],a[2],a[4]]
          j=j+1
       return box


    def get_random_data(self, image_path,annotation_line):

        line = annotation_line.split( )
        #image = Image.open(image_path+line[0])
        image=rasterio.open(image_path+line[0]+".TIF") #247 185 146 206
        image=np.moveaxis(image.read()[0:3],0,2)/255
        #image = np.uint8( (cv2.cvtColor(image[:,:,0:3], cv2.COLOR_BGR2RGB))*255 )
        #box = np.array([np.array(list(map(int,box.split(',')))) for box in line[1:]])
        box = self.get_box( line )

        return image, box

    def generate(self, train=True):
                    
            batch_images = np.zeros((self.batch_size, self.input_size[0], self.input_size[1], self.input_size[2]), dtype=np.float32)
            
            batch_hms = np.zeros((self.batch_size, self.output_size[0], self.output_size[1], self.num_classes), dtype=np.float32)
            batch_whs = np.zeros((self.batch_size, self.max_objects, 2), dtype=np.float32)
            batch_regs = np.zeros((self.batch_size, self.max_objects, 2), dtype=np.float32)
            batch_reg_masks = np.zeros((self.batch_size, self.max_objects), dtype=np.float32)
            batch_indices = np.zeros((self.batch_size, self.max_objects), dtype=np.float32)
            
            b = 0
            for annotation_line in lines: 




                img,y = self.get_random_data(image_path, annotation_line)


                if len(y)!=0:
                    boxes = np.array(y[:,:4],dtype=np.float32)
                    boxes[:,0] = boxes[:,0]/self.input_size[1]*self.output_size[1]
                    boxes[:,1] = boxes[:,1]/self.input_size[0]*self.output_size[0]
                    boxes[:,2] = boxes[:,2]/self.input_size[1]*self.output_size[1]
                    boxes[:,3] = boxes[:,3]/self.input_size[0]*self.output_size[0]
                    print(boxes)

                for i in range(len(y)):
                    bbox = boxes[i].copy()
                    bbox = np.array(bbox)
                    bbox[[0, 2]] = np.clip(bbox[[0, 2]], 0, self.output_size[1] - 1)
                    bbox[[1, 3]] = np.clip(bbox[[1, 3]], 0, self.output_size[0] - 1)
                    cls_id = int(y[i,-1])-1
                    
                    h, w = bbox[3] - bbox[1], bbox[2] - bbox[0]
                    if h > 0 and w > 0:
                        ct = np.array([(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2], dtype=np.float32)
                        ct_int = ct.astype(np.int32)
                        
                        # 
                        radius = gaussian_radius((math.ceil(h), math.ceil(w)))
                        radius = max(0, int(radius))
                        batch_hms[b, :, :, cls_id] = draw_gaussian(batch_hms[b, :, :, cls_id], ct_int, radius)
                        batch_whs[b, i] = 1. * w, 1. * h
                       
                       

                        # 
                        batch_regs[b, i] = ct - ct_int


                        # 
                        batch_reg_masks[b, i] = 1
                        # 
                        batch_indices[b, i] = ct_int[1] * self.output_size[1] + ct_int[0]

                # origninal data BGR images
                batch_images[b] = img
                b = b + 1
                if b == self.batch_size:

                    return [batch_images, batch_hms, batch_whs, batch_regs, batch_reg_masks, batch_indices]               

Batch_size=1
with open('/content/drive/MyDrive/test-WHU/train.txt') as f:
        lines = f.readlines()
lin=[lines[0]]
input_shape=[512,512,3]
num_classes=1
image_path="/content/drive/MyDrive/test-WHU/image/"
gen = Generator1(Batch_size, lin, lin, input_shape, num_classes,image_path)

# Training
"""

import keras
import numpy as np
import tensorflow as tf
from keras.backend.tensorflow_backend import set_session
from keras.callbacks import (EarlyStopping, ModelCheckpoint, ReduceLROnPlateau,
                             TensorBoard)

#from nets.center_training import Generator
#from nets.centernet import centernet

#---------------------------------------------------#

def get_classes(classes_path):
    '''loads the classes'''
    with open(classes_path) as f:
        class_names = f.readlines()
    class_names = [c.strip() for c in class_names]
    return class_names

#----------------------------------------------------#

#----------------------------------------------------#
if __name__ == "__main__": 
    #-----------------------------#

    #-----------------------------#
    input_shape = [512,512,3]
    #-----------------------------#


    #-----------------------------#
    classes_path = '/content/drive/MyDrive/test3/classex.txt'
    #----------------------------------------------------#

    #----------------------------------------------------#
    class_names = get_classes(classes_path)
    num_classes = len(class_names)

    #-------------------------------------------#
 
    #   resnet50 hourglass
    #-------------------------------------------#
    backbone = "resnet50"

    #----------------------------------------------------#

    #----------------------------------------------------#
   
    model = centernet(input_shape, num_classes=num_classes, backbone=backbone, mode='train')
    

    #------------------------------------------------------#
    #model_path ="/content/drive/MyDrive/centernet-keras/logs_newmodel2/ep054-loss0.245-val_loss1.892.h5" #"/content/drive/MyDrive/centernet-keras/model_data/centernet_resnet50_voc.h5"
    #model.load_weights(model_path)


    #----------------------------------------------------#
    annotation_path = '/content/drive/MyDrive/test3/train.txt'
    image_path = "/content/drive/MyDrive/test3/image/"
    #----------------------------------------------------------------------#

    #----------------------------------------------------------------------#
    val_split = 0.1
    with open(annotation_path) as f:
        lines = f.readlines()
    np.random.seed(10101)
    np.random.shuffle(lines)
    np.random.seed(None)
    num_val = int(len(lines)*val_split)
    num_train = len(lines) - num_val



    #-------------------------------------------------------------------------------#
    logs_path="/content/drive/MyDrive/centernet-keras/logs_newmodel/"
    #logging = TensorBoard(log_dir=logs_path)
    checkpoint = ModelCheckpoint(logs_path+'ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5',
        monitor='val_loss', save_weights_only=True, save_best_only=False, period=10)
    reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, verbose=1)
    early_stopping = EarlyStopping(monitor='val_loss', min_delta=0, patience=20, verbose=1)

    if backbone == "resnet50":
        freeze_layer = 171
    elif backbone == "hourglass":
        freeze_layer = 624
    else:
        raise ValueError('Unsupported backbone - `{}`, Use resnet50, hourglass.'.format(backbone))

lines[:num_train]

#model.summary( )


    #------------------------------------------------------#
    if True:
        Lr = 1e-3
        Batch_size = 6
        Init_Epoch = 0
        Freeze_Epoch = 300

        gen = Generator(Batch_size, lines[:num_train], lines[num_train:], input_shape, num_classes,image_path)

        model.compile(
            loss={'centernet_loss': lambda y_true, y_pred: y_pred},
            optimizer=keras.optimizers.Adam(Lr)
        )

        model.fit_generator(gen.generate(True), 
                steps_per_epoch=num_train//Batch_size,
                validation_data=gen.generate(False),
                validation_steps=num_val//Batch_size,
                epochs=Freeze_Epoch, 
                verbose=1,
                initial_epoch=Init_Epoch,
                callbacks=[checkpoint, reduce_lr, early_stopping])

for i in range(freeze_layer):
        model.layers[i].trainable = True

    if True:
        Lr = 1e-4
        Batch_size = 6
        Freeze_Epoch = 100
        Epoch = 300
        
        gen = Generator(Batch_size, lines[:num_train], lines[num_train:], input_shape, num_classes,image_path)

        model.compile(
            loss={'centernet_loss': lambda y_true, y_pred: y_pred},
            optimizer=keras.optimizers.Adam(Lr)
        )

        model.fit_generator(gen.generate(True), 
                steps_per_epoch=num_train//Batch_size,
                validation_data=gen.generate(False),
                validation_steps=num_val//Batch_size,
                epochs=Epoch, 
                verbose=1,
                initial_epoch=Freeze_Epoch,
                callbacks=[checkpoint, reduce_lr, early_stopping])

model.save_weights('/content/drive/MyDrive/centernet-keras/logs/ep68-loss1.4187-val_loss3.9767.h5' )

"""# Training2"""



#from nets.deeplab import Deeplabv3
#from nets.segnet import resnet50_segnet

from keras.utils.data_utils import get_file
from keras.optimizers import Adam
from keras.callbacks import TensorBoard, ModelCheckpoint, ReduceLROnPlateau, EarlyStopping
from PIL import Image
import keras
from keras import backend as K
import numpy as np
import cv2
ALPHA = 1.0
#WEIGHTS_PATH_X = "https://github.com/bonlime/keras-deeplab-v3-plus/releases/download/1.1/deeplabv3_xception_tf_dim_ordering_tf_kernels.h5"
                    
NCLASSES = 2
HEIGHT = 512
WIDTH = 512
NumChannels=3
batch_size = 3
load_pretrained_weights=0
n=4                   #n: rate of codebook 1/n
C=2                   #C: rate of reduction channels 1/C
log_dir = "/content/drive/MyDrive/SpectralDepthfusion/logs_Boston/" 

def generate_arrays_from_file(lines,batch_size):
  
    n = len(lines)
    i = 0
    while 1:
        X_train = []
        Y_train = []
     
        for _ in range(batch_size):
            if i==0:
                np.random.shuffle(lines)
            name = lines[i].split(';')[0]
          
            """
            img = Image.open(r"/content/drive/MyDrive/test3/image" + '/' + name)
            
            img = np.array(img)
            img = img/255
            X_train.append(img)
            """
            img=rasterio.open(r"/content/drive/MyDrive/test3/image" + '/' + name)
            
          
            img=np.moveaxis(img.read(),0,2)[:,:,0:3]
            #img = img/255
            X_train.append(img)
           
            name = (lines[i].split(';')[1]).replace("\n", "")
            
            label = rasterio.open(r"/content/drive/MyDrive/test3/label" + '/' + name)
          
            label = np.moveaxis(label.read(),0,2)
            #img=rasterio.open(r"/content/drive/MyDrive/test2/label" + '/' + name)
            #img=np.moveaxis(img.read()/255,0,2)
            
            
            seg_labels = np.zeros((int(HEIGHT),int(WIDTH),NCLASSES))
            for c in range(NCLASSES):
                seg_labels[: , : , c ] = (label[:,:,0] == c ).astype(int)
            
            seg_labels = np.reshape(seg_labels, (-1,NCLASSES))
            Y_train.append(seg_labels)
            
          
            i = (i+1) % n
        yield (np.array(X_train),np.array(Y_train))

def loss(y_true, y_pred):
    loss = K.binary_crossentropy(y_true,y_pred) #K.categorical_crossentropy(y_true,y_pred)
    return loss



  
if __name__ == "__main__":

    # 获取model
    #model = code_resnet101(HEIGHT, WIDTH, NumChannels, NCLASSES,n,C)
    model = SpectralDepthfusion1( input_shape=[HEIGHT, WIDTH, NumChannels],num_classes=NCLASSES )
    #model = Deeplabv3(input_shape=(HEIGHT, WIDTH, NumChannels), classes=2,n=4,C=2)
    #model = Deeplabv3(classes=2,input_shape=(HEIGHT,WIDTH,NumChannels))
    #model = resnet50_segnet(n_classes=NCLASSES,input_height=HEIGHT, input_width=WIDTH)
    #model = pspnet(NCLASSES,inputs_size=[512,512,3],downsample_factor=16,backbone="resnet50",aux_branch=False) # resnet50,molilenet

    model.load_weights('/content/drive/MyDrive/SpectralDepthfusion/logs_Boston/ep050-loss0.200-val_loss0.222.h5')


    # fine-tune model (train only last conv layers)
    if load_pretrained_weights:
      flag = 0
      print("START FINE TUNE")
      for k, l in enumerate(model.layers):
           l.trainable = False
           if l.name == 'fine_tune1'or'fine_tune2'or'fine_tune3': #'fine_tune1'or
              flag = 1
           if flag:
              l.trainable = True

 
    with open(r"/content/drive/MyDrive/test3/train_seg.txt","r") as f:
        lines = f.readlines()

 
    np.random.seed(10101)
    np.random.shuffle(lines)
    np.random.seed(None)

 
    num_val = int(len(lines)*0.1)
    num_train = len(lines) - num_val  #len(lines)

 
    checkpoint_period = ModelCheckpoint(
                log_dir + 'ep{epoch:03d}-loss{loss:.3f}-val_loss{val_loss:.3f}.h5',
                        monitor='loss', #'val_loss'
                        save_weights_only=True, 
                        save_best_only=True, 
                        period=1
                                )
 
    reduce_lr = ReduceLROnPlateau(
                            monitor='val_loss', 
                            factor=0.2, 
                            patience=5, 
                            verbose=1
                        )
 
    early_stopping = EarlyStopping(
                            monitor='val_loss', 
                            min_delta=0, 
                            patience=3, 
                            verbose=1)

 
    model.compile(loss = loss,
            optimizer = Adam(lr=1e-4, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0),   #1e-3
            metrics = ['binary_accuracy'])
            
    
    print('Train on {} samples, val on {} samples, with batch size {}.'.format(num_train, num_val, batch_size))
    #for i in range(200):
    #  model.layers[i].trainable = True
  
    model.fit_generator(generate_arrays_from_file(lines[:num_train], batch_size),
            steps_per_epoch=max(1, num_train//batch_size),
            validation_data=generate_arrays_from_file(lines[num_train:],batch_size), #(lines[num_train:]batch_size),
            validation_steps=max(1, num_val//batch_size),
            epochs=50,
            initial_epoch=0,
            callbacks=[checkpoint_period, reduce_lr])

"""# SpetralDepthfusion Predict"""

from PIL import Image
import numpy as np
import random
import copy
import os
import matplotlib.pyplot as plt
import cv2
from google.colab.patches import cv2_imshow
#from nets.deeplab import Deeplabv3

#class_colors = [[0,0,0],[255,255,255]]
class_colors = [[255,255,255],[0,0,0]]                  
NCLASSES = 2
HEIGHT = 512
WIDTH = 512
NumChannels=3

n=4
C=2
# Load model with weigths
#model = Deeplabv3(classes=2,input_shape=(HEIGHT,WIDTH,NumChannels))
#model = Deeplabv3(input_shape=(HEIGHT, WIDTH, NumChannels), classes=2,n=4,C=2) #+attention
#model = pspnet(NCLASSES,inputs_size=[512,512,3],downsample_factor=16,backbone="resnet50",aux_branch=False) #resnet50 mobilenet
#model = code_resnet101(HEIGHT, WIDTH, NumChannels, NCLASSES,n,C)
model = SpectralDepthfusion1( input_shape=[HEIGHT, WIDTH, NumChannels],num_classes=NCLASSES )
model.load_weights("/content/drive/MyDrive/SpectralDepthfusion/logs_WHU/ep028-loss0.053-val_loss0.057.h5")
#model.load_weights("/content/drive/MyDrive/deeplab_Xception/logs/ep032-loss0.082-val_loss0.089.h5")

model.summary()

img = Image.open('/content/drive/MyDrive/test-WHU/image/0028.TIF') #/content/drive/MyDrive/test1/image/2_34.tif
old_img = np.array(img)
img = np.array(img)

"""
img=rasterio.open("/content/drive/MyDrive/test3/image/146.TIF") #247 185 146 206
img=np.moveaxis(img.read(),0,2)
old_img = cv2.cvtColor(img[:,:,0:3], cv2.COLOR_BGR2RGB)
#old_img =img
"""
img = img.reshape(-1,HEIGHT,WIDTH,3)



pr1 = model.predict(img,verbose=1)[0]

pr = pr1.reshape((int(HEIGHT), int(WIDTH),NCLASSES)).argmax(axis=-1)

seg_img = np.zeros((int(HEIGHT), int(WIDTH),3))
colors = class_colors

for c in range(NCLASSES):
        seg_img[:,:,0] += ((pr[:,: ] == c )*( colors[c][0] )).astype('uint8')
        seg_img[:,:,1] += ((pr[:,: ] == c )*( colors[c][1] )).astype('uint8')
        seg_img[:,:,2] += ((pr[:,: ] == c )*( colors[c][2] )).astype('uint8')

old_img = Image.fromarray(np.uint8(old_img))

seg=np.zeros((512,512,3))

seg+=(seg_img==255)*([255,0,0])

seg = Image.fromarray(np.uint8(seg))
image = Image.blend(old_img,seg,0.3)
plt.figure(figsize=(10,10))
plt.imshow(image)


#image.save("./img_out/"+jpg)
"""
old_img = Image.fromarray(np.uint8(old_img))
#old_img = Image.fromarray(np.uint8(old_img*255))
seg=np.zeros((512,512,3))

seg+=(seg_img==255)*([255,0,0])

seg = Image.fromarray(np.uint8(seg))
image = Image.blend(old_img,seg,0.3)
plt.figure(figsize=(10,10))
plt.imshow(image)
"""

#image.save("./img_out/"+jpg)

old_img

"""# Centernet Prediction"""

import keras.backend as K
import tensorflow as tf
from keras.initializers import constant, normal, zeros
from keras.layers import (Activation, BatchNormalization, Conv2D, Layer,Concatenate,
                Conv1D,Softmax,Conv2DTranspose, Dropout, Input, Lambda,
                          MaxPooling2D, Reshape, ZeroPadding2D)
from keras.layers.pooling import  GlobalAveragePooling2D as GAP2D
from keras.models import Model
from keras.regularizers import l2
from keras import layers
from nets.center_training import loss
#from nets.hourglass import HourglassNetwork
#from nets.resnet import ResNet50, centernet_head


def nms(heat, kernel=3):
    hmax = MaxPooling2D((kernel, kernel), strides=1, padding='SAME')(heat)
    heat = tf.where(tf.equal(hmax, heat), heat, tf.zeros_like(heat))
    return heat

def topk(hm, max_objects=100):
    #-------------------------------------------------------------------------#

    hm1 = nms(hm)
    b, h, w, c = tf.shape(hm1)[0], tf.shape(hm1)[1], tf.shape(hm1)[2], tf.shape(hm1)[3]
    #-------------------------------------------#
    #  b, 128 * 128 * 80)
    #-------------------------------------------#
    hm = tf.reshape(hm1, (b, -1))
    #-----------------------------#
    #   (b, k), (b, k)
    #-----------------------------#
    scores, indices = tf.math.top_k(hm, k=max_objects, sorted=True)

    #--------------------------------------#

    #--------------------------------------#
    class_ids = indices % c
    xs = indices // c % w
    ys = indices // c // w
    indices = ys * w + xs
    return scores, indices, class_ids, xs, ys,hm1

def decode(hm, wh, reg, max_objects=100,num_classes=20):
    #-----------------------------------------------------#
    #   hm          b, 128, 128, num_classes 
    #   wh          b, 128, 128, 2 
    #   reg         b, 128, 128, 2 
    #   scores      b, max_objects
    #   indices     b, max_objects
    #   class_ids   b, max_objects
    #   xs          b, max_objects
    #   ys          b, max_objects
    #-----------------------------------------------------#
    scores, indices, class_ids, xs, ys,hm1 = topk(hm, max_objects=max_objects)
    b = tf.shape(hm)[0]
    
    #-----------------------------------------------------#
    #   wh          b, 128 * 128, 2
    #   reg         b, 128 * 128, 2
    #-----------------------------------------------------#
    reg = tf.reshape(reg, [b, -1, 2])
    wh = tf.reshape(wh, [b, -1, 2])
    length = tf.shape(wh)[1]

    #-----------------------------------------------------#

    #   batch_idx   b, max_objects
    #-----------------------------------------------------#
    batch_idx = tf.expand_dims(tf.range(0, b), 1)
    batch_idx = tf.tile(batch_idx, (1, max_objects))
    full_indices = tf.reshape(batch_idx, [-1]) * tf.to_int32(length) + tf.reshape(indices, [-1])
                    
    #-----------------------------------------------------#

    #-----------------------------------------------------#
    topk_reg = tf.gather(tf.reshape(reg, [-1,2]), full_indices)
    topk_reg = tf.reshape(topk_reg, [b, -1, 2])
    
    topk_wh = tf.gather(tf.reshape(wh, [-1,2]), full_indices)
    topk_wh = tf.reshape(topk_wh, [b, -1, 2])

    #-----------------------------------------------------#

    #   topk_cx     b,k,1
    #   topk_cy     b,k,1
    #-----------------------------------------------------#
    topk_cx = tf.cast(tf.expand_dims(xs, axis=-1), tf.float32) + topk_reg[..., 0:1]
    topk_cy = tf.cast(tf.expand_dims(ys, axis=-1), tf.float32) + topk_reg[..., 1:2]

    #-----------------------------------------------------#

    #   topk_x1     b,k,1      x0
    #   topk_y1     b,k,1      y1
    #   topk_x2     b,k,1      y2
    #   topk_y2     b,k,1      y3
    #-----------------------------------------------------#
    topk_x1, topk_y1 = topk_cx - topk_wh[..., 0:1] / 2, topk_cy - topk_wh[..., 1:2] / 2
    topk_x2, topk_y2 = topk_cx + topk_wh[..., 0:1] / 2, topk_cy + topk_wh[..., 1:2] / 2
    
    #-----------------------------------------------------#
    #   scores      b,k,1       
    #   class_ids   b,k,1       
    #-----------------------------------------------------#
    scores = tf.expand_dims(scores, axis=-1)
    class_ids = tf.cast(tf.expand_dims(class_ids, axis=-1), tf.float32)
    

    #-----------------------------------------------------#
    detections = tf.concat([topk_x1, topk_y1, topk_x2, topk_y2,scores, class_ids], axis=-1)
    output=[detections, hm,wh]
    return output




def centernet(input_shape, num_classes, backbone='resnet50', max_objects=100, mode="train", num_stacks=2):
    assert backbone in ['resnet50', 'hourglass']
    print('Max_objects:',max_objects )
    output_size = input_shape[0] // 4
    image_input = Input(shape=input_shape)
    hm_input = Input(shape=(output_size, output_size, num_classes))
    wh_input = Input(shape=(max_objects, 2))
    reg_input = Input(shape=(max_objects, 2))
    reg_mask_input = Input(shape=(max_objects,))
    index_input = Input(shape=(max_objects,))

    if backbone=='resnet50':
        #-----------------------------------#
   
        #   512, 512, 3 -> 16, 16, 2048
        #-----------------------------------#
        C5 = ResNet50(image_input)
        #--------------------------------------------------------------------------------------------------------#
     
        #   16, 16, 2048 -> 32, 32, 256 -> 64, 64, 128 -> 128, 128, 64 -> 128, 128, 64 -> 128, 128, num_classes
        #                                                              -> 128, 128, 64 -> 128, 128, 2
        #                                                              -> 128, 128, 64 -> 128, 128, 2
        #--------------------------------------------------------------------------------------------------------#
        y1, y2, y3 = centernet_head(C5, num_classes)


        detections = Lambda(lambda x: decode(*x, max_objects=max_objects,
                                        num_classes=num_classes))([y1, y2, y3])
        prediction_model = Model(inputs=image_input, outputs= detections)
        return prediction_model

import keras.engine as KE
from keras.layers import Layer
class ROIencoder(Layer):


    def __init__(self, pool_shape,encodersr, **kwargs):
        super( ROIencoder, self).__init__(**kwargs)
        self.pool_shape = tuple(pool_shape)
        self.encodersr = encodersr

    def call(self, inputs):
        # Crop boxes [batch, num_boxes, [y1, x1, y2, x2]] in normalized coords
        boxes = inputs[0][:,:,0:4] 
        feature_maps =inputs[1]
        
        self.Nins = K.int_shape(boxes)[1] 
        
        B,H,W,C=K.int_shape(feature_maps)

        y1, x1, y2, x2 = tf.split(boxes, 4, axis=2)
        h = y2 - y1
        w = x2 - x1
        
        box_indices= tf.cast( tf.where(y1)[:,0],tf.int32)
        level_boxes = tf.stop_gradient( K.reshape(boxes,[-1,4]) )
        box_indices = tf.stop_gradient(box_indices)

        # Crop and Resize
        # Result: [batch * num_boxes, pool_height, pool_width, channels]
        x=tf.image.crop_and_resize(
                feature_maps, level_boxes, box_indices, (32,32),
                method="bilinear")
        
        x = GAP2D()(x)
        
        shape = Concatenate(axis=0)([tf.shape(boxes)[:2], tf.shape(x)[1:]])
        x = tf.reshape(x, shape)
        #x= Reshape( shape)(x)
        
        x = Conv1D(filters=self.encodersr, kernel_size=1, strides=1, 
              padding='same',use_bias=False,kernel_initializer='he_normal', 
              kernel_regularizer=l2(5e-4))(x)
        x = Softmax(axis=-1)(x)
        x = tf.transpose(x,[0,2,1])
        y = Conv2D(filters=self.encodersr, kernel_size=1, strides=1, 
              padding='same',use_bias=False,kernel_initializer='he_normal', 
            kernel_regularizer=l2(5e-4))(feature_maps)
        y = BatchNormalization()(y)
        y = Reshape([-1,H*W,self.encodersr])(y)
        featurere = tf.matmul(y,x)
        featurere = Reshape([-1,H,W,self.Nins])(featurere)

        return feature_maps

    def compute_output_shape(self, input_shape):
        featuremaps_shape=input_shape[1][0:4]
        output_shape=(featuremaps_shape[0],featuremaps_shape[1],featuremaps_shape[2],self.Nins)
        print( output_shape) 
        return output_shape

#Test ROIencoder
    #   hm          b, 128, 128, num_classes 
    #   wh          b, 128, 128, 2 
    #   reg         b, 128, 128, 2 
    
    # Construct model
    feature_maps=Input( shape=(128,128,64) )

    feature_map=Conv2D(filters=64,kernel_size=3,padding='same')(feature_maps)
    hm = Conv2D(filters=1,kernel_size=3,padding='same')(feature_map)
    wh = Conv2D(filters=2,kernel_size=3,padding='same')(hm)
    reg = Conv2D(filters=2,kernel_size=3,padding='same')(wh)

    detections = Lambda(lambda x: decode(*x, max_objects=100,
                  num_classes=2))([hm, wh, reg])

    roi_encoder= ROIencoder(pool_shape=(32,32),encodersr=110)
    featurere=roi_encoder([detections[0],feature_map])
    #roi_encoder = ROIencoder( )
    #out = ROIencoder( )( [detections[0],feature_map])
 
    
    model=Model( inputs=feature_maps, outputs=featurere )
    model.summary( )

import cv2
from google.colab.patches import cv2_imshow
def centernetpre(input_shape, num_classes, backbone='resnet50', max_objects=100, mode="train", num_stacks=2):
    assert backbone in ['resnet50', 'hourglass']
    print('Max_objects:',max_objects )
    output_size = input_shape[0] // 4
    image_input = Input(shape=input_shape)


    if backbone=='resnet50':

        y1, y2, y3 = centernet_head(image_input, num_classes)
        detections = Lambda(lambda x: decode(*x, max_objects=max_objects,
                         num_classes=num_classes))([y1, y2, y3])
        prediction_model = Model(inputs=image_input, outputs= detections)
        return prediction_model

#from nets.centernet import centernet

        backbone       = 'resnet50'
        input_shape=[512,512,3]        
        model_path     = '/content/drive/MyDrive/centernet-keras/logs_newmodel_Boston/ep138-loss1.211-val_loss2.760.h5'
        Centernet= centernetpre(input_shape, num_classes=1, backbone=backbone ,max_objects=50,mode='predict')
        Centernet.load_weights(model_path)

image=rasterio.open('/content/drive/MyDrive/test3/image/145.TIF') #247 185 146 206
        image=np.moveaxis(image.read()[0:3],0,2)
        photo = np.reshape(image, [1, input_shape[0], input_shape[1], input_shape[2]])

        preds= Centernet.predict(photo)

plt.imshow(image)
plt.axis('off')

a=np.reshape(preds[2],[1,128,128,2])
plt.figure(figsize=(10,10))
b=a[0][:,:,1]+a[0][:,:,0]
plt.imshow( b)

preds1=preds[0]
plt.figure(figsize=(10,10))

plt.imshow( preds[1][0][:,:,0])
#plt.scatter( [ (preds1[0][:,0]+preds1[0][:,2])/2  ],[ (preds1[0][:,1]+preds1[0][:,3])/2 ],color="r" )
 
plt.axis('off')

from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')
def random_colors(N, bright=True):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors

# Test transformed data

colors =  random_colors(preds1.shape[1])

fig, ax = plt.subplots(1, figsize=(10,10))
print('Counting buildings:',preds1.shape[1] )

for i in np.arange(preds1.shape[1]):
  
   x1, y1, x2, y2 = (preds1[0][i][: 4])*4 # *4

 
   p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,alpha=0.7, linestyle="dashed",edgecolor=colors[i], facecolor='none')
   ax.scatter([x2], [y2], c=colors[i], marker='o')
   ax.scatter([x1], [y1], c=colors[i], marker='o')
   ax.scatter((x1+x2)/2, (y1+y2)/2, c=colors[i], marker='o')
   label = 'Bulding'+str(i+1)+':'
   caption = "{}  {:.3f}".format(label, preds1[0][i][4]*100)
   ax.text(x1, y2-2, caption,
                color='w', size=7, backgroundcolor='none',alpha=1,rotation=90,bbox ={'facecolor': colors[i],  
                   'alpha':0.3, 'pad':1})



   ax.add_patch(p)



#ax.imshow(cv2.resize(image, dsize=(32, 32)))
ax.imshow(image)

Centernet.summary()

x=photo

# This is the  prediction vector
output = Centernet.output[1][0][64,64,0]


# The is the output feature map 
last_conv_layer = Centernet.get_layer('activation_56') # activation_518 conv2d_223

# This is the gradient 
grads = K.gradients(output, last_conv_layer.output)[0]

# This is the mean intensity of the gradient over a specific feature map channel
pooled_grads = K.mean(grads, axis=(0, 1, 2))

# This function allows us to access the values of the quantities we just defined:
# `pooled_grads` and the output feature map 
# given a sample image
iterate = K.function([Centernet.input], [pooled_grads, last_conv_layer.output[0]])

# These are the values of these two quantities, as Numpy arrays,

pooled_grads_value, conv_layer_output_value = iterate([x])

# We multiply each channel in the feature map array
# by "how important this channel is" with regard to the elephant class
for i in range(25):
    conv_layer_output_value[:, :, i] *= pooled_grads_value[i]

# The channel-wise mean of the resulting feature map
# is our heatmap of class activation
heatmap = np.mean(conv_layer_output_value, axis=2)

import matplotlib.pyplot as plt
heatmap = np.maximum(heatmap, 0)
#heatmap= - heatmap
heatmap =(heatmap-np.min(heatmap))/ (np.max(heatmap)-np.min(heatmap))
plt.matshow(heatmap)
plt.show()
#print(heatmap)

# We use cv2 to load the original image
#img = cv2.imread('/content/drive/MyDrive/test3/image/247.TIF')
#heatmap=heatmap*255

# We resize the heatmap to have the same size as the original image
heatmap = cv2.resize(heatmap, (512, 512))

# We convert the heatmap to RGB
heatmap = np.uint8(heatmap*255)

# We apply the heatmap to the original image
heatmap1 = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET) # COLORMAP_HOT COLORMAP_JET COLORMAP_OCEAN COLORMAP_PINK COLORMAP_SPRING
# alpha here is a heatmap intensity factor
alpha=0.8
superimposed_img = heatmap1+image*255*alpha  
cv2_imshow(superimposed_img)

heap2=heatmap

# We convert the heatmap to RGB
heap2 = np.uint8(heap2*255)
# We apply the heatmap to the original image
heap2 = cv2.applyColorMap(heap2, cv2.COLORMAP_JET) # COLORMAP_HOT COLORMAP_JET COLORMAP_OCEAN COLORMAP_PINK COLORMAP_SPRING
# alpha here is a heatmap intensity factor
alpha=0.7
superimposed_img = heap2*0.5+image*255*alpha  
cv2_imshow(superimposed_img)

"""# Building Instance segmentation vision"""



from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')

def apply_mask(image, mask, color, alpha=0.7):
    """Apply the given mask to the image.
    """
    for c in range(3):
        image[:, :, c] = np.where(mask == 0 ,image[:, :, c],
                    image[:, :, c] *(1 - alpha) + alpha * color[c] * 255)
                        
    return image

def random_colors(N, bright=True):
    """
    Generate random colors.
    To get visually distinct colors, generate them in HSV space then
    convert to RGB.
    """
    brightness = 1.0 if bright else 0.7
    hsv = [(i / N, 1, brightness) for i in range(N)]
    colors = list(map(lambda c: colorsys.hsv_to_rgb(*c), hsv))
    random.shuffle(colors)
    return colors

def get_box(  line ):
       j=0
       box=np.zeros((len(line[1:]),4))
       for i in line[1:]:
          a =np.asarray(i.split(',')).astype(np.float32).reshape(1,5)[0]
          box[j]=[a[0],a[3],a[1],a[2]]
          j=j+1
       return box

# read bounding box coordinates

import numpy as np

txt_path = '/content/drive/MyDrive/test3/train.txt'	
f = open(txt_path)
data_lists = f.readlines()	

line=data_lists[73].strip('\n').split(' ')
dataset=get_box(  line )
print('Bounding box coordinates shape:',dataset.shape)

# transform bounding box coordinates
img=rasterio.open("/content/drive/MyDrive/test3/image/146.TIF") #247 185 146 206
img_label=rasterio.open("/content/drive/MyDrive/test3/label/146.TIF")
img_label=np.moveaxis(img_label.read(),0,2)[:,:,0] 
scores=np.random.randint(96,100,size= dataset.shape[0] )/100

old_img=np.moveaxis(img.read()[0:3],0,2)
old_img = np.uint8( (cv2.cvtColor(old_img[:,:,0:3], cv2.COLOR_BGR2RGB))*255 )

colors =  random_colors(dataset.shape[0])


height, width = old_img.shape[:2]
masks=np.zeros((old_img.shape[0],old_img.shape[1], dataset.shape[0] ))
masked_image = old_img 

fig, ax = plt.subplots(1, figsize=(10,10))

for i in range(dataset.shape[0]):
   color = colors[i]
   x1, y1, x2, y2 = dataset[i]

   
   p = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2,
                                alpha=0.7, linestyle="dashed",
                                edgecolor=color, facecolor='none')
   ax.add_patch(p)
   
   ax.scatter([x1,x2], [y1,y2], c=color, marker='o')
   ax.scatter([(x1+x2)/2], [(y1+y2)/2], c=color, marker='^')
             
   label = 'Bulding'+str(i+1)
   caption = "{}  {:.2f}".format(label, scores[i])
   """
   ax.text(x1, y2-2, caption,
                color='w', size=9, backgroundcolor='none',alpha=1,rotation=90,bbox ={'facecolor': color,  
                   'alpha':0.3, 'pad':1})
   """
   a= np.trunc(x1 ).astype(int)
   b= np.trunc(y1 ).astype(int)
   c= np.trunc(x2 ).astype(int)
   d= np.trunc(y2 ).astype(int)
   #print(a,b,c,d)

   masks[b:d+1,a:c+1,i]= img_label[b:d+1,a:c+1]/255

   masked_image = apply_mask(masked_image, masks[:, :, i], color,alpha=0.5)

   """
   padded_mask = np.zeros(
            (masks.shape[0] + 2, masks.shape[1] + 2), dtype=np.uint8)
   padded_mask[1:-1, 1:-1] = masks[:, :, i]
   contours = find_contours(padded_mask, 0.5)
   for verts in contours:
            # Subtract the padding and flip (y, x) to (x, y)
            verts = np.fliplr(verts) - 1
            p = Polygon(verts, facecolor="none", edgecolor=color)
            ax.add_patch(p)
   """


ax.set_ylim(height + 8, -8)
ax.set_xlim(-8, width + 8)
ax.axis('on')
#ax.set_title('Building Instance Segmentation')
ax.imshow(masked_image.astype(np.uint8))
ax.set_xticks([])
ax.set_yticks([])
#plt.scatter(datasetaffine[:,0],datasetaffine[:,2])
#plt.scatter(datasetaffine[:,1],datasetaffine[:,3])
#fig.savefig('/content/drive/MyDrive/146.jpg', dpi=150)

fig.savefig('/content/drive/MyDrive/Boston_samples/gr146.TIF', dpi=300)

"""# TEST"""

import tensorflow as tf
import matplotlib.pyplot as plt
import keras 
from keras import backend as K
img = plt.imread('/content/drive/MyDrive/test-WHU/image/0005.TIF')
shape = img.shape
img = img.reshape([1,shape[0], shape[1], shape[2]])
img=tf.concat([img, img], axis=0) 
box_indices=tf.cast( [0,0,1,0],dtype=tf.int32)
boxes=tf.cast( [[0.2,0.2,0.6,0.8],[0.5,0.5,1.3,0.9],[0.2,0.2,0.6,0.8],[0.2,0.2,0.6,0.8]],
         dtype=tf.float32 )

a = tf.image.crop_and_resize(img,boxes ,box_indices=box_indices,crop_size=(64,64))

b = K.eval(a)
# plt.imshow(b[0]/255)
plt.imshow(b[0].astype('uint8'))
plt.show()

test_a=tf.constant([ [[1],[1]], 
          [[1],[1]]]  )
c=tf.where(test_a)

image_input = Input(shape=[512,512,3] )

image_input

box_indices = tf.cast(c[:, 0], tf.int32)
a=tf.image.crop_and_resize(image_input ,boxes ,box_indices=box_indices,crop_size=(64,64))

a1=GAP2D()(a)



a1

K.reshape(a1, [1,2,2,3])

