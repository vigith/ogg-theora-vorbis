import sys
import Image as IM
#sys.path.append("/home/ik/ogg/ogg/build/lib.linux-i686-2.6")
################################################################
from CuOgg import *
from CuTheora import *


class VideoEncode:
	def __init__(self, width, height, videofile):
		self.width = width;
		self.height = height;
		self.ogg_packet = make_ogg_packet()
		self.page   = make_ogg_page()
		self.stream = make_ogg_stream_state()
		self.state  = make_ogg_sync_state()
		self.ret1 = ogg_sync_init(self.state)
		ogg_stream_init(self.stream, 12345)  ## serial number can be anything, 12345	     
		self.th_setupInfo_addr = 0
		self.theoraInfo = make_th_info()
		th_info_init(self.theoraInfo)
		set_th_info(self.theoraInfo, self.width, self.height)
		self.mComment = make_th_comment()
		th_comment_init(self.mComment)
		self.enc=th_encode_alloc(self.theoraInfo)
		## no page is read, so can't use function ogg_page_serialno(ogg_page *)
		self.fd = open(videofile,"wb")
		self.packetNo = 0
		return

	def printTheoraInfo(self):
		print get_th_info(self.theoraInfo)

	def getSize(self):
		w, h = width_height(self.theoraInfo)
		return w, h

	def isPageBOS(self):
		out = ogg_page_bos(self.page)
		if out > 0: out = 1
		elif out < 0:
			print "ERROR PAGE BOS"
		return out

	def isPageEOS(self):
		out = ogg_page_eos(self.page)
		if out > 0: out = 1
		return out

	def pageNo(self):
		no = ogg_page_pageno(self.page)
		return no

	def isHeader(self):
		val = th_packet_isheader(self.ogg_packet)  
		return val

	def isKeyFrame(self):
		val = th_packet_iskeyframe(self.ogg_packet)
		return val

	def flushHeader(self):
		n = 1
		while n > 0:
			n = th_encode_flushheader(self.enc, self.mComment, self.ogg_packet)
			if n > 0:
				nnn = ogg_stream_packetin(self.stream, self.ogg_packet)
		self.savePage()
		return

	def flushStream(self):
		n = ogg_stream_flush(self.stream, self.page)
		self.savePage()
		return

	def savePage(self):
		n = ogg_stream_pageout(self.stream, self.page) ## forms packets to pages
		if n:
			header = page_header(self.page)
			body = page_body(self.page)
			self.fd.write(header)
			self.fd.write(body)
		return

	def addImageFrame(self, img):
		img2 = img.resize([self.width, self.height])
		img3 = img2.convert('RGB')  ## you don't have to do this as image is already RGB
		img4 = img3.tostring()
		n = th_encode_ycbcr_in(self.enc, img4, self.width, self.height)
		n = th_encode_packetout(self.enc, 0, self.ogg_packet)
		n = ogg_stream_packetin(self.stream, self.ogg_packet)
		self.savePage()
		self.packetNo += 1
		print self.packetNo, "\r",
		sys.stdout.flush()
		return n

	def readImage(self, filename = "aaa.jpg"):
		img = IM.open(filename)
		return img

	def addImages(self, filename, no = 1):
		img = self.readImage(filename)
		for i in range(no):
			self.addImageFrame(img)
			
	def close(self):
		self.fd.close()
		return

	def endVideo(self):
		th_encode_free(self.enc)
		return
