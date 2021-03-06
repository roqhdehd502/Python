import os, random
import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

"""
    Namin Neural Network
    -----------------
    conv1 - relu1 - pool1 -
    conv2 - relu2 - pool2 -
    affine - softmax

    Parameters
    ----------
    Input Layer(Input Size): 100*100*3
    First Layer: Conv1(8EA, 8*8*3, Strides=4, Padding=0)
                - 23*23*8 - Pool1(3*3, Strides=2. Padding=0) - 11*11*8
    Second Layer: Conv2(16EA, 25*25*8, Strides=1, Padding=2)
                - 11*11*16 - Pool1(3*3, Strides=2, Padding=0) - 5*5*16
    Output Layer: Affine(W=5*5*16, B=16) - Output Nodes = 3(Frank, Mike, T)
 """

# Load to Franklin, Michael, Trevor Images
trainlist, testlist = [], []
with open('train.txt') as f:
    for line in f:
        tmp = line.strip().split()
        trainlist.append([tmp[0], tmp[1]])
        
with open('test.txt') as f:
    for line in f:
        tmp = line.strip().split()
        testlist.append([tmp[0], tmp[1]])

# Image Preprocessing
IMG_H = 100
IMG_W = 100
IMG_C = 3

def readimg(path):
    img = plt.imread(path)
    return img

def batch(path, batch_size):
    img, label, paths = [], [], []
    for i in range(batch_size):
        img.append(readimg(path[0][0]))
        label.append(int(path[0][1]))
        path.append(path.pop(0))
        
    return img, label

# Neural Network
num_class = 3 # Franklin Clinton, Trevor Philips, Michael De Santa

with tf.Graph().as_default() as g:
    X = tf.placeholder(tf.float32, [None, IMG_H, IMG_W, IMG_C]) # Input Layer
    Y = tf.placeholder(tf.int32, [None])
    
    with tf.variable_scope('CNN'):
        # 1st Layer(Conv1 - relu1 - maxpool1) = 11*11*8
        conv1 = tf.layers.conv2d(X, 8, 3, (4, 4), padding='VALID', activation=tf.nn.relu)
        pool1 = tf.layers.max_pooling2d(conv1, 3, (2, 2), padding='VALID')
        # 2nd Layer(Conv2 - relu2 - maxpool2) = 5*5*16
        conv2 = tf.layers.conv2d(pool1, 16, 25, (1, 1), padding='SAME', activation=tf.nn.relu)
        pool2 = tf.layers.max_pooling2d(conv2, 3, (2, 2), padding='VALID')
        # Fully Connected Layer(Affine)
        affine1 = tf.layers.flatten(pool2)
        # Output Layer
        output = tf.layers.dense(affine1, num_class)
        
    # Softmax with Loss
    with tf.variable_scope('Loss'):
        Loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels= Y, logits=output))
    
    # Training with Adam    
    train_step = tf.train.AdamOptimizer(1e-3).minimize(Loss) 
    saver = tf.train.Saver()

# Size
np.sum([np.product(var.shape) for var in g.get_collection('trainable_variables')]).value

# Setting Batch with Training
batch_size = 1080
with tf.Session(graph=g) as sess:
    sess.run(tf.global_variables_initializer())
    for i in range(1000):
        batch_data, batch_label = batch(trainlist, batch_size)     
        _, l = sess.run([train_step, Loss], feed_dict = {X: batch_data, Y: batch_label}) # Problem line
        print(_, l)
        
    saver.save(sess, 'logs/model.ckpt', global_step = i+1)

# Print an Accuracy
acc = 0
with tf.Session(graph=g) as sess:
    sess.run(tf.global_variables_initializer())
    checkpoint = tf.train.latest_checkpoint('logs')
    if checkpoint:
        saver.restore(sess, checkpoint)
    for i in range(len(testlist)):
        batch_data, batch_label = batch(testlist, 1)
        logit = sess.run(output, feed_dict = {X:batch_data})
        if np.argmax(logit[0]) == batch_label[0]:
            acc += 1
        else:
            print(logit[0], batch_label[0])
            
    print(acc/len(testlist))
