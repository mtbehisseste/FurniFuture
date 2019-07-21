#!/usr/bin/env python3

# --------------------------------------------------------
# Tensorflow Faster R-CNN
# Licensed under The MIT License [see LICENSE for details]
# Written by Xinlei Chen, based on code from Ross Girshick
# --------------------------------------------------------

"""
Demo script showing detections in sample images.

See README.md for installation instructions before running.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import _init_paths
from model.config import cfg
from model.test import im_detect
from model.nms_wrapper import nms

from utils.timer import Timer
import tensorflow as tf
old_v = tf.logging.get_verbosity()
tf.logging.set_verbosity(tf.logging.ERROR)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os, cv2
import argparse

from nets.vgg16 import vgg16
from nets.resnet_v1 import resnetv1

demo_result = []

'''
# should be same order with pascal_voc.py
CLASSES = ('__background__',
           'aeroplane', 'bicycle', 'bird', 'boat',
           'bottle', 'bus', 'car', 'cat', 'chair',
           'cow', 'diningtable', 'dog', 'horse',
           'motorbike', 'person', 'pottedplant',
           'sheep', 'sofa', 'train', 'tvmonitor')
'''
CLASSES = ('__background__',
           'box', 'chair', 'dehumidifier', 
           'diningtable', 'fan', 'mug', 'person', 
           'sun glasses', 'sweepingrobot')

# filter impossible classes
FILTERED_CLASSES = ('__background__', 'chair',
                    'dehumidifier', 'diningtable', 
                    'fan', 'mug', 'person', 
                    'sun glasses') 

# NETS = {'vgg16': ('vgg16_faster_rcnn_iter_70000.ckpt',),'res101': ('res101_faster_rcnn_iter_110000.ckpt',)}
# DATASETS= {'pascal_voc': ('voc_2007_trainval',),'pascal_voc_0712': ('voc_2007_trainval+voc_2012_trainval',)}
NETS = {'vgg16': ('vgg16_faster_rcnn_iter_70000.ckpt',),'res101': ('res101_faster_rcnn_iter_100000.ckpt',)}
DATASETS = {'pascal_voc': ('voc_2007_trainval',), 'pascal_voc_0712': ('voc_2007_trainval',)}

# def vis_detections(im, class_name, dets, thresh=0.5):
#     """Draw detected bounding boxes."""
#     inds = np.where(dets[:, -1] >= thresh)[0]
#     if len(inds) == 0:
#         return

#     if class_name in FILTERED_CLASSES:  # filtered objects
#         print('obj: ', class_name)
#         im = im[:, :, (2, 1, 0)]
#         fig, ax = plt.subplots(figsize=(6.66, 5))
#         ax.imshow(im, aspect='equal')
#         for i in inds:
#             bbox = dets[i, :4]
#             score = dets[i, -1]

#             w = (bbox[2] - bbox[0]) / 2
#             h = (bbox[3] - bbox[1])
#             if class_name == 'diningtable':
#                 result_obj = [class_name, bbox[0] + w, bbox[1] + h, w, h]
#             else:
#                 result_obj = [class_name, bbox[0] + w, bbox[1] + h]
#             demo_result.append(result_obj)
          
#             ax.add_patch(
#                 plt.Rectangle((bbox[0], bbox[1]),
#                             bbox[2] - bbox[0],
#                             bbox[3] - bbox[1], fill=False,
#                             edgecolor='red', linewidth=3.5)
#                 )
#             ax.text(bbox[0], bbox[1] - 2,
#                   '{:s} {:.3f}'.format(class_name, score),
#                        bbox=dict(facecolor='blue', alpha=0.5),
#                        fontsize=14, color='white')

#         ax.set_title(('{} detections with '
#                     'p({} | box) >= {:.1f}').format(class_name, class_name,
#                                                     thresh),
#                     fontsize=14)
#         # plt.axis('off')
#         plt.tight_layout()
#         plt.draw()
#         fig.savefig('{}_output_fig.jpg'.format(class_name))

def demo(sess, net, image_name):
    """Detect object classes in an image using pre-computed object proposals."""

    # Load the demo image
    im_file = os.path.join(cfg.DATA_DIR, 'demo', image_name)
    im = cv2.imread(im_file)

    # Detect all object classes and regress object bounds
    timer = Timer()
    timer.tic()
    scores, boxes = im_detect(sess, net, im)
    timer.toc()
    print('Detection took {:.3f}s for {:d} object proposals'.format(timer.total_time, boxes.shape[0]))

    # Visualize detections for each class
    CONF_THRESH = 0.8
    NMS_THRESH = 0.3
    
    im = im[:, :, (2, 1, 0)]
    fig, ax = plt.subplots(figsize=(6.66, 5))
    ax.imshow(im, aspect='equal')
    
    for cls_ind, cls in enumerate(CLASSES[1:]):
        cls_ind += 1 # because we skipped background
        cls_boxes = boxes[:, 4*cls_ind:4*(cls_ind + 1)]
        cls_scores = scores[:, cls_ind]
        dets = np.hstack((cls_boxes,
                          cls_scores[:, np.newaxis])).astype(np.float32)
        keep = nms(dets, NMS_THRESH)
        dets = dets[keep, :]
        #  vis_detections(im, cls, dets, thresh=CONF_THRESH)
        
        #  added for display all bboxes in one picture (origin vis_detections() code)    
        inds = np.where(dets[:, -1] >= CONF_THRESH)[0]        
        if len(inds) == 0:
            continue

        if cls in FILTERED_CLASSES:  # filtered objects
            print('obj: ', cls)
            for i in inds:
                bbox = dets[i, :4]
                score = dets[i, -1]

                w = (bbox[2] - bbox[0]) / 2
                h = (bbox[3] - bbox[1])
                if cls == 'diningtable':
                    result_obj = [cls, bbox[0] + w, bbox[1] + h, w, h]
                else:
                    result_obj = [cls, bbox[0] + w, bbox[1] + h]
                demo_result.append(result_obj)
            
                ax.add_patch(
                    plt.Rectangle((bbox[0], bbox[1]),
                                bbox[2] - bbox[0],
                                bbox[3] - bbox[1], fill=False,
                                edgecolor='red', linewidth=3.5)
                    )
                ax.text(bbox[0], bbox[1] - 2,
                    '{:s} {:.3f}'.format(cls, score),
                        bbox=dict(facecolor='blue', alpha=0.5),
                        fontsize=14, color='white')

            # ax.set_title('All detections with threshold >= {:.1f}'.format(CONF_THRESH), fontsize=14)
            plt.axis('off')
            plt.tight_layout()
            # plt.draw()
            # fig.savefig('{}_output_fig.jpg'.format(cls))
    plt.savefig('./result/demo_' + image_name)
    print('Saved to `{}`'.format(os.path.join(os.getcwd(), 'result/demo_' + image_name)))
            

    print ('demo.py result: ', demo_result)

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Tensorflow Faster R-CNN demo')
    parser.add_argument('--net', dest='demo_net', help='Network to use [vgg16 res101]',
                        choices=NETS.keys(), default='res101')
    parser.add_argument('--dataset', dest='dataset', help='Trained dataset [pascal_voc pascal_voc_0712]',
                        choices=DATASETS.keys(), default='pascal_voc_0712')
    args = parser.parse_args()

    return args

if __name__ == '__main__':
    # disable AVX warning
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    cfg.TEST.HAS_RPN = True  # Use RPN for proposals
    args = parse_args()

    # model path
    demonet = args.demo_net
    dataset = args.dataset
    tfmodel = os.path.join('output', demonet, DATASETS[dataset][0], 'default',
                              NETS[demonet][0])


    if not os.path.isfile(tfmodel + '.meta'):
        raise IOError(('{:s} not found.\nDid you download the proper networks from '
                       'our server and place them properly?').format(tfmodel + '.meta'))

    # set config
    tfconfig = tf.ConfigProto(allow_soft_placement=True)
    tfconfig.gpu_options.allow_growth=True

    # init session
    sess = tf.Session(config=tfconfig)
    # load network
    if demonet == 'vgg16':
        net = vgg16()
    elif demonet == 'res101':
        net = resnetv1(num_layers=101)
    else:
        raise NotImplementedError
    net.create_architecture("TEST", 10,
                          tag='default', anchor_scales=[8, 16, 32])
    saver = tf.train.Saver()
    saver.restore(sess, tfmodel)

    print('Loaded network {:s}'.format(tfmodel))
    
    im_names = []
    for file in os.listdir('./data/demo/'):
        im_names.append(file)

    for im_name in im_names:
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print('Demo for data/demo/{}'.format(im_name))
        demo(sess, net, im_name)

    # plt.show()

    # write result to file
    if os.path.isfile('./demo_result'):
        os.system('rm ./demo_result')
    res_file = open('demo_result', 'a')
    for index in demo_result:
        if index[0] == 'diningtable':
            res_file.write('{} {} {} {} {} '.format(index[0], str(index[1]), str(index[2]), str(index[3]), str(index[4])))
        else:    
            res_file.write('{} {} {} '.format(index[0], str(index[1]), str(index[2])))
            
    res_file.close()
