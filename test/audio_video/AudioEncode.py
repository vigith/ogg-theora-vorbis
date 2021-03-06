from PyExOgg import *
from PyExVorbis import *

import wave
import random

class AudioEncode:
	def __init__(self, fd):
		self.noChannels = 2
		self.width      = 2
		self.frameRate  = 44100

		self.vi = make_vorbis_info()      # struct that stores all the static vorbis bitstream
		self.vc = make_vorbis_comment()   # struct that stores all the user comments 
		self.vd = make_vorbis_dsp_state() # central working state for the packet->PCM decoder
		self.vb = make_vorbis_block()     # local working space for packet->PCM decode

		self.header      = make_ogg_packet()
		self.header_comm = make_ogg_packet()
		self.header_code = make_ogg_packet()
		self.audio_pkt   = make_ogg_packet()

		self.to   = make_ogg_stream_state()
		self.page = make_ogg_page()
		self.fout = fd


	def flushFrames(self):
		vorbis_analysis_wrote(self.vd,0)
		while (vorbis_analysis_blockout(self.vd, self.vb) == 1):
			vorbis_analysis(self.vb,self.audio_pkt)
          		ogg_stream_packetin(self.to,self.audio_pkt)
		self.savePage()


	def addAudioFrame(self, vals):
		vorbis_encode_int_values(self.vd, self.vb, vals, len(vals), self.noChannels)
		while (vorbis_analysis_blockout(self.vd, self.vb) == 1):
			vorbis_analysis(self.vb,self.audio_pkt)
          		ogg_stream_packetin(self.to,self.audio_pkt)
		self.savePage()
		return 1


	def start(self):
		quality = 1.0 # values between -0.1 to 1.0
		r1 = vorbis_info_init(self.vi)
		r2 = vorbis_encode_init_vbr(self.vi, self.noChannels, self.frameRate, quality)
		r3 = vorbis_encode_setup_init(self.vi)

		r4 = vorbis_comment_init(self.vc)
		r5 = vorbis_analysis_init(self.vd,self.vi)
		r6 = vorbis_block_init(self.vd,self.vb)

		r7 = vorbis_analysis_headerout(self.vd, 
				self.vc, 
				self.header, 
				self.header_comm, 
				self.header_code)

		#print r1, r2, r3, '--', r4, r5, r6, '--', r7

		rnd = int(random.random()*10000)
		ogg_stream_init(self.to,rnd)

		r1 = ogg_stream_packetin(self.to, self.header)
		r2 = ogg_stream_packetin(self.to, self.header_comm)
		r3 = ogg_stream_packetin(self.to, self.header_code)

		self.savePage()

	def clear(self):
		vorbis_block_clear(self.vb)
		vorbis_dsp_clear(self.vd)
		vorbis_comment_clear(self.vc)
		vorbis_info_clear(self.vi)
		return

        def savePage(self):
                n = ogg_stream_pageout(self.to, self.page)
                if n:
                        header = page_header(self.page)
                        body = page_body(self.page)
                        self.fout.write(header)
                        self.fout.write(body)
                return


            
