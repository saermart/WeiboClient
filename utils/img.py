#!/usr/bin/python
# coding:utf-8


import codecs
import os
import time

import cv2


def read_video_cover(video_path, frame_poi=1):
    """
    读取上传视频的封面
    :param video_path: 视频路径
    :param frame_poi: 要截取的视频的第几帧
    """
    cover_path = f'{int(time.time() * 1000)}.png'
    vidcap = cv2.VideoCapture(video_path)
    # 获取帧数
    frame_count = vidcap.get(7)
    frame_poi = 1 if frame_poi > frame_count else frame_poi
    # 指定帧
    vidcap.set(cv2.CAP_PROP_POS_FRAMES, frame_poi)
    success, image = vidcap.read()
    status = cv2.imwrite(cover_path, image)
    vidcap.release()
    if status:
        with codecs.open(cover_path, 'rb') as f:
            cover = f.read()
        os.remove(cover_path)
        return cover
