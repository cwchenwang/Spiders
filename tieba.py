#-*- coding:utf-8 -*-
import urllib
import urllib2
import re

class Tool:
	removeImg = re.compile('<img.*?>| {7}|')
	removeAddr = re.compile('<a.*?>|</a>')
	replaceLine = re.compile('<tr>|<div>|</div>|</p>')
	replaceTD = re.compile('<td>')
	replacePara = re.compile('<p.*?>')
	replaceBR = re.compile('<br><br>|<br>')
	removeExtraTag = re.compile('<.*?>')

	def replace(self, x):
		x = re.sub(self.removeImg, "", x)
		x = re.sub(self.removeAddr, "", x)
		x = re.sub(self.replaceLine, "\n", x)
		x = re.sub(self.replaceTD, "\t", x)
		x = re.sub(self.replacePara, "\n  ", x)
		x = re.sub(self.replaceBR, "\n", x)
		x = re.sub(self.removeExtraTag, "", x)
		return x.strip()

class BDTB:
	def __init__(self, baseUrl, seeLZ, floorTag):
		self.baseURL = baseUrl
		self.seeLZ = '?see_lz=' + str(seeLZ)
		self.tool = Tool()
		self.file = None
		self.floor = 1
		self.defaultTitle = u"百度贴吧"
		self.floorTag = floorTag
	def getPage(self, pageNum):
		try:
			url = self.baseURL + self.seeLZ + '&pn=' + str(pageNum)
			request = urllib2.Request(url)
			response = urllib2.urlopen(request)
			#print response.read()
			return response.read().decode('utf-8')
		except urllib2.URLError, e:
			if hasattr(e, "reason"):
				print u"连接百度贴吧失败，错误原因", e.reason
				return None

	def getTitle(self, page):
		page = self.getPage(1)
		pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>', re.S)
		#re.S点任意匹配(\n)
		result = re.search(pattern, page)
		print result
		if result:
			#print result.group(1).strip()
			return result.group(1).strip()
		else:
			return None

	def getPageNum(self, page):
		pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>', re.S)
		result = re.search(pattern, page)
		if result:
			return result.group(1).strip()
		else:
			return None

	def getContent(self, page):
		pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
		items = re.findall(pattern, page)
		contents = []
		for item in items:
		# 	print item
			# print floor,u"楼-------------------\n"
			# print self.tool.replace(item)
			# floor += 1
			content = '\n' + self.tool.replace(item) + '\n'
			print content
			contents.append(content.encode('utf-8'))
		return contents

	def setFileTitle(self, title):
		if title is not None:
			self.file = open(title+".txt", "w+")
		else:
			self.file = open(self.defaultTitle+".txt", "w+")

	def writeData(self, contents):
		for item in contents:
			if self.floorTag == '1':
				floorLine = "\n" + str(self.floor) + u"--------------\n"
				self.file.write(floorLine)
			self.file.write(item)
			self.floor += 1

	def start(self):
		indexPage = self.getPage(1)
		pageNum = self.getPageNum(indexPage)
		title = self.getTitle(indexPage)
		self.setFileTitle(title)
		if pageNum == None:
			print "URL失效"
			return

		try:
			print "该帖子共有" + str(pageNum) + "页"
			for i in range(1, int(pageNum)+1):
				print "正在写入第" + str(i) + "页数据"
				page = self.getPage(i)
				contents = self.getContent(page)
				self.writeData(contents)

		except IOError, e:
			print "写入异常， 原因" + e.message
		finally:
			print "写入任务完成"


print u"请输入帖子代号"
baseURL = 'http://tieba.baidu.com/p/'+str(raw_input(u'http://tieba.baidu.com/p/'))
seeLZ = raw_input("是否只获取楼主发言，是1否0\n")
floorTag = raw_input('是否写入楼层信息，是1否0\n')
bdtb = BDTB(baseURL, seeLZ, floorTag)
bdtb.start()