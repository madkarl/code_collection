#!/usr/bin/python3
# coding:utf-8

import sys, os


def get_base_dir():
    '''
    获取当前脚本所在目录
    :return: 目录绝对路径
    '''
    print(sys.argv[0])
    path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return path


if __name__ == "__main__":
    path = get_base_dir()
    print(path)

