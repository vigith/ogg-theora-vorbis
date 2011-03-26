import sys
import Image as IM
#sys.path.append("/home/ik/ogg/ogg/build/lib.linux-i686-2.6")
################################################################
from PyExOgg import *
from PyExTheora import *


class DecodeTheora:
	def __init__(self, file_name):
		self.file_name = file_name
		self.packet = make_ogg_packet()
		self.page   = make_ogg_page()
		self.stream = make_ogg_stream_state()
		self.state  = make_ogg_sync_state()
		self.th_setupInfo_addr = 0

		self.file = open_file(self.file_name)
		self.ret1 = ogg_sync_init(self.state)

		self.readPage()
		self.slno = ogg_page_serialno(self.page)
		self.ret3 = ogg_stream_init(self.stream, self.slno)
		self.ret4 = ogg_stream_pagein(self.stream, self.page)

		self.theoraInfo = make_th_info()
		th_info_init(self.theoraInfo)
		self.mComment   = make_th_comment()		
		th_comment_init(self.mComment)
		self.setupInfo_addr = 0

	def getSize(self):
		w, h = width_height(self.theoraInfo)
		return w, h

	def readPage(self):
		# read_page/3 of Ogg Lib uses ogg_sync_pageout internally
		# ogg_sync_pageout, takes the data stored in the buffer of the ogg_sync_state struct and inserts them into an ogg_page. 
		self.ret2 = read_page(self.file, self.state, self.page)
		return self.ret2

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

	def readPacket(self):
		self.ret5 = ogg_stream_packetout(self.stream, self.packet)
		while self.ret5 == 0:
			## readPage is from Ogg Lib (indirectly)
			## read_page() returns '0' during normal case
			## and undef when EOF (bytes read == 0)
			if self.readPage() == None:
				print "PAGE END"
				return None
			# ogg_stream_pagein:
			# http://www.xiph.org/ogg/doc/libogg/ogg_stream_pagein.html
			# This function adds a complete page to the bitstream.
			# ret4 == 0 means that the page was successfully submitted to the bitstream.
			self.ret4 = ogg_stream_pagein(self.stream, self.page)
			# ogg_stream_packetout:
			# http://www.xiph.org/ogg/doc/libogg/ogg_stream_packetout.html
			# This function assembles a data packet for output to the codec decoding engine.
			# op contains the next packet from the stream (only if ret5 == 1, for 0 and -1 it is not updated)
			self.ret5 = ogg_stream_packetout(self.stream, self.packet)

		return self.packet

	def isHeader(self):
		val = th_packet_isheader(self.packet)
		# Returns:
		# 1 : The packet is a header packet
		# 0 : The packet is a video data packet. 
		return val

	def isKeyFrame(self):
		val = th_packet_iskeyframe(self.packet)
		return val

	def decodeHeader(self):
		""" calls th_decode_headerin which Decodes the header packets of a Theora stream.
		This (th_decode_headerin) should be called on the initial packets of the stream, in succession, until it returns 0 (0 == VIDEO),
		indicating that all headers have been processed, or an error is encountered.
		This can be used on the first packet of any logical stream to determine if that stream is a Theora stream. 
		"""
		
		ret = ""
		
		# th_decode_headerin(self.theoraInfo, self.mComment, self.setupInfo_addr, self.packet)
		# self.setupInfo_addr:-
		# Returns a pointer to additional, private setup information needed by the decoder.
		# The contents of this pointer must be initialized to NULL on the first call,
		# and the returned value must continue to be passed in on all subsequent calls.
		#
		# setupInfo_addr can be free'd after this using th_decode_free()
		
		while self.isHeader():
			ret, self.setupInfo_addr = th_decode_headerin(self.theoraInfo, 
					self.mComment, self.setupInfo_addr, self.packet)
			# val need not be returned, as readPacket() sets the self.packet
			val = self.readPacket()
			if not val: return None

		# iterate till the first VIDEO is encountered
		while not ret == 'VIDEO':
			ret, self.setupInfo_addr = th_decode_headerin(self.theoraInfo, 
					self.mComment, self.setupInfo_addr, self.packet)
			
			if not ret == 'VIDEO':
				val = self.readPacket()
		return

	def beginVideo(self):
		# th_decode_alloc(self.theoraInfo, self.setupInfo_addr)
		# th_decode_alloc, Allocates a decoder instance.
		# theoraInfo, A th_info struct filled via th_decode_headerin().
		# setupInfo_addr, A th_setup_info handle returned via th_decode_headerin(). 
		self.dec = th_decode_alloc(self.theoraInfo, self.setupInfo_addr)

		# th_setup_free(self.setupInfo_addr)
		# th_setup_free, Releases all storage used for the decoder setup information.
		# setupInfo_addr is returned by th_decode_headerin()
		th_setup_free(self.setupInfo_addr)

		self.gpos = 0
		w, h = self.getSize()

		# creates a python memory 
		# PyMem_New(unsigned char, sizeof(th_ycbcr_buffer))
		self.buff = make_yuv_buffer(w*h*2)  ## ycbcr_buffer

		# th_decode_packetin(self.dec, self.packet, self.gpos)
		# Submits a packet containing encoded video data to the decoder.
		# self.dec, A th_dec_ctx handle.
		# self.packet, An ogg_packet containing encoded video data.
		# self.gpos, Returns the granule position of the decoded packet.
		#            (This is computed incrementally from previously decoded packets.)
		ret, self.gpos = th_decode_packetin(self.dec, self.packet, self.gpos)

		# th_decode_ycbcr_out(self.dec, self.buff)
		# Outputs the next available frame of decoded Y'CbCr data.
		# self.dec, A th_dec_ctx handle.
		# self.buff, A video buffer structure to fill in.
		#            libtheoradec will fill in all the members of this structure, including the pointers to the uncompressed video data.
		#            (It may be freed or overwritten without notification when subsequent frames are decoded.)
		# Returns:
		# 'ok', 'FAULT' or 'UNKNOWN'
		val = th_decode_ycbcr_out(self.dec, self.buff)
		return val 

	def gotoKeyFrame(self):
		while not self.isKeyFrame():
			self.readPacket()
		return

	# the image is in ycbcr format, need to convert it
	def rgbBuffer(self):
		self.rgb = get_rgb_buffer(self.buff)
		return self.rgb

	def readVideo(self):
		val = self.readPacket()
		if val == None: return None
		ret, self.gpos = th_decode_packetin(self.dec, self.packet, self.gpos)
		val = th_decode_ycbcr_out(self.dec, self.buff) ## self.buff will have the ycbcr data
		return val

	def endVideo(self):
		# Frees an allocated decoder instance. 
		th_decode_free(self.dec)
		## ogg_packet_clear(self.packet) (malloc error as expected, freed by codecs)
		return

	def saveImage(self, name = "frame.png"):
		w,h = self.getSize()
		img = IM.fromstring('RGB', [w, h], self.rgb)	
		img.save(name)

if __name__ == '__main__':

	def test1():
		ogg = DecodeTheora("PyExTheora.ogv")
		ogg.decodeHeader()
		ogg.beginVideo()
		i = 0
		while True:
			i += 1
			val = ogg.readVideo()
			print ogg.getSize(), val
			if val == 'ok':
				buff = ogg.rgbBuffer()
				ogg.saveImage("frame%03d.png" % (i))
			## val == None will be set by the ReadPage (if you follow the stack trace)
			elif val == None:
				break
		print get_th_info(ogg.theoraInfo)
		print_th_comment(ogg.mComment)
		ogg.endVideo()

	test1()


