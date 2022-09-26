import tensorflow as tf
import os
os.environ['CUDA_VISIBLE_DEVICES'] = "0"

hello = tf.constant('Hello, TensorFlow!')
sess = tf.compat.v1.Session()