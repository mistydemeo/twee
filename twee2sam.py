#!/usr/bin/env python

import sys, os, getopt, glob
scriptPath = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path.append(os.sep.join([scriptPath, 'tw', 'lib']))
sys.path.append(os.sep.join([scriptPath, 'lib']))
from tiddlywiki import TiddlyWiki
from twparser import TwParser


def usage():
	print 'usage: twee [-a author] [-t target] [-m mergefile] [-r rss] source1 [source2..]'


def main (argv):

	# defaults

	author = 'twee'
	target = 'jonah'
	merge = rss_output = ''
	plugins = []

	# read command line switches

	try:
		opts, args = getopt.getopt(argv, 'a:m:p:r:t:', ['author=', 'merge=', 'plugins=', 'rss=', 'target='])
	except getopt.GetoptError:
		usage()
		sys.exit(2)

	for opt, arg in opts:
		if (opt in ('-a', '--author')):
			author = arg
		elif (opt in ('-m', '--merge')):
			merge = arg
		elif (opt in ('-p', '--plugins')):
			plugins = arg.split(',')
		elif (opt in ('-r', '--rss')):
			rss_output = arg
		elif (opt in ('-t', '--target')):
			target = arg

	# construct a TW object

	tw = TiddlyWiki(author)

	# read in a file to be merged

	if merge != '':
		file = open(merge)
		tw.addHtml(file.read())
		file.close()

	# read source files

	sources = []

	for arg in args:
		for file in glob.glob(arg):
			sources.append(file)

	if len(sources) == 0:
		print 'twee: no source files specified\n'
		sys.exit(2)

	for source in sources:
		file = open(source)
		tw.addTwee(file.read())
		file.close()

	# generate RSS if requested

	if rss_output != '':
		rss_file = open(rss_output, 'w')
		tw.toRss().write_xml(rss_file)
		rss_file.close()

	# output the target header

#	if (target != 'none') and (target != 'plugin'):
#		file = open(scriptPath + os.sep + 'targets' + os.sep + target \
#								+ os.sep + 'header.html')
#		print(file.read())
#		file.close()

	# the tiddlers

	twp = TwParser(tw)


	#
	# Number the passages
	#

	passage_indexes = {}

	def process_passage_index(passage):
		global next_seq

		if not passage.title in passage_indexes:
			passage_indexes[passage.title] = process_passage_index.next_seq
			process_passage_index.next_seq += 1

	process_passage_index.next_seq = 0

	# 'Start' _must_ be the first script
	process_passage_index(twp.passages['Start'])
	for passage in twp.passages.values():
		process_passage_index(passage)

	print passage_indexes


	#
	# Generate SAM scripts
	#

	for passage in twp.passages.values():
		print "*** ", passage.title

		def out_string(msg):
			print '"{0}"'.format(msg)

		links = []
		for cmd in passage.commands:
			if cmd.kind == 'text':
				out_string(cmd.text)
			elif cmd.kind == 'link':
				links.append(cmd)
				out_string(cmd.actual_label())
			elif cmd.kind == 'list':
				for lcmd in cmd.children:
					if lcmd.kind == 'link':
						links.append(lcmd)

		print '!'

		if links:
			out_string('\n'.join([link.actual_label() for link in links]))
			print '?A.'

			nlink = 0
			for link in links:
				print 'A:{0}=[{1}j]'.format(nlink, passage_indexes[link.target])
				nlink += 1






#	print tw.toHtml()

	# plugins

#	for plugin in plugins:
#		file = open(scriptPath + os.sep + 'targets' + os.sep + target \
#								+ os.sep + 'plugins' + os.sep + plugin + os.sep + 'compiled.html')
#		print(file.read())
#		file.close()

	# and close it up

#	print '</div></html>'


if __name__ == '__main__':
	main(sys.argv[1:])

