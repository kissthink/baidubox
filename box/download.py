#!/usr/bin/env python2
# coding:utf-8

import os
import sys
import urllib
import urllib2
import threading

class DownloadThread(threading.Thread):
    def __init__(self,quene):
        threading.Thread.__init__(self)
        self.queue = quene

    def run(self):
        while True:
            if not self.queue.empty():
                item = self.queue.get()
                download(item['url'], item['params'], item['dest'])
            else:
                break

def download(url, params, destination, blocksize=8192):
    """
    把百度音乐从服务器上下载到本地
    支持断点续传
    简单的文件下载进度
    """
    if params:
        params = urllib.urlencode(params)
        url = '%s?%s' % (url, params)

    print "Downloading to %s" %(destination)

    resume = os.path.exists(destination)
    with open(destination, "ab") as fh:
        if resume:
            print "Resuming download"
            fh.seek(0, 2)
            curpos = fh.tell()
            header =  {'Range':'bytes={0}-'.format(curpos)}
            request = urllib2.Request(url, headers=header)

            try:
                wh = urllib2.urlopen(request)
            except urllib2.HTTPError, inst:
                if inst.code == 416:
                    print "Download already completed"
                    return

            try:
                size = int(wh.info().getheaders("Content-Length")[0]) + curpos
            except IndexError:
                size = 999999999
            cur = curpos
            if size == cur:
                print "Download already completed"
                return
        else:
            wh = urllib2.urlopen(url)
            try:
                size = int(wh.info().getheaders("Content-Length")[0])
            except IndexError:
                size = 999999999
            cur = 0

        content = wh.read(blocksize)
        while content:
            cur += len(content)
            fh.write(content)
            content = wh.read(blocksize)
            sys.stdout.write("Progress: {0:8}% \t {1}k of {2}k \r".format(round((float(cur)/size)*100.0,2), cur/1024.0, size/1024.0))
            sys.stdout.flush()
