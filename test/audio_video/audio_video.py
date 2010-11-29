from VideoEncode import *
from AudioEncode import *

# how to execute ?
# $ python audio_video.py
#
# This file uses AudioEncode and VideoEncode
# to create the combined binary file

class WaveData:
	def __init__(self, wave_file):
		self.fd         = wave.open(wave_file)
		self.noChannels = self.fd.getnchannels() # 2 for sterio
		self.width      = self.fd.getsampwidth() # 2 bytes
		self.frameRate  = self.fd.getframerate() # 44100
		self.noFrames   = self.fd.getnframes()   # total number of frames
		self.paramList  = self.fd.getparams() 
				# (2, 2, 44100, 2752, 'NONE', 'not compressed')
		self.video_fps  = 25
		self.frame_size = self.frameRate/self.video_fps

	def eof(self):
		if self.noFrames == self.fd.tell(): return 1
		return 0

	def getFrame(self):
		no = self.frame_size
		pos = self.fd.tell()
		if pos + no > self.noFrames:
			no = self.noFrames - pos
		frames = self.fd.readframes(no)
		vals = wave_frames_to_int(frames, no, self.noChannels)
		#print "\t\t===", self.fd.tell(), len(vals),self.fd.tell()+882
		if self.frame_size == 1764:
			return vals
		elif self.frame_size == 882:
			pos = self.fd.tell()
			if no == self.frame_size:
				framen = self.fd.readframes(1)
				valn = wave_frames_to_int(framen, 1, self.noChannels)
				self.fd.setpos(pos)
				valn = valn[0]
			else:
				valn = [0L]*self.noChannels
			return self.insertOne(vals, valn)
		else:
			print "ERROR getFrame"
			return None
			
	def appendNoSound(self):
		vals = self.getFrame()
		#print "AN sound", self.fd.tell(), len(vals), self.frame_size
		if len(vals) == 1764:
			return vals
		elif len(vals) < 1764:
			no = 1764 - len(vals)
			return vals + [[0L]*self.noChannels]*no
			self.eof = 1
		else:
			print "ERROR appendsound"
			return None


	def insertOne(self, vals, valn):
		out = []
		n = len(vals) -1
		for i in range(n):
			out.append(vals[i])
			data = []
			for j in range(self.noChannels):
				m = (vals[i][j] + vals[i+1][j])/2
				data.append(m)
			out.append(data)
		out.append(vals[-1])
		data = []
		for j in range(self.noChannels):
			m = (vals[-1][j] + valn[j])/2
			data.append(m)
		out.append(data)
		return out
		
	def getAudioFrameData(self):
		if self.eof(): return None
		vals = self.appendNoSound()
		return vals
            

class AudioVideo:
	def __init__(self, width, height, output_file):
		self.video = VideoEncode(width, height, output_file)
		self.video.flushHeader()
		self.audio = AudioEncode(self.video.fd)
		self.audio.start()
		return
	
	def addAudioImages(self, img_file, wav_file):
		img = self.video.readImage(img_file)
		wav = WaveData(wav_file)
		no = 0
		while 1:
			val = wav.getAudioFrameData()
			if val == None: break
			self.video.addImageFrame(img)
			self.audio.addAudioFrame(val)
			no += 1
		print "%-5d frames added with audio" % (no)
		return

	def addNoAudioImages(self, img_file, no):
		img = self.video.readImage(img_file)
		for i in range(no):
			val = [[0L,0L]]*(44100/25)
			self.video.addImageFrame(img)
			self.audio.addAudioFrame(val)
		print "%-5d frames added" % (no)
		return no

	def close(self):
		self.video.close()
	


if __name__ == '__main__':
		
	def test():
		av = AudioVideo(320, 240, 'PyExAudioVideoTest.ogv')
		av.addNoAudioImages("aaa.jpg",100)
		av.addAudioImages("bbb.jpg","a.wav")
		av.addAudioImages("ccc.jpg","wind.wav")
		av.close()
		
	test()
