import urllib, urllib2, cookielib, csv, zipfile, os, shutil, sys
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

csv_path = raw_input('Module list (default "modules_list.csv") : ') or 'modules_list.csv'

k = 0
update_dir = 'tmp'
while (os.path.exists(update_dir)):
	update_dir = 'tmp' + str(k)
	k = k+1
	if (k == 10):
		print 'Too much "tmp" directories'
		sys.exit()
os.mkdir(update_dir)
os.mkdir(update_dir + '\\modules')
os.mkdir(update_dir + '\\themes')

print '--'*20
with open(csv_path, 'rb') as csvfile:
	list = csv.reader(csvfile, delimiter=',')
	i = 0
	already_done = 0
	count_update = 0
	drupal_to_update = ''
	for row in list:
		if (i!=0):
			if (row[0] != ''):
				if (row[0] != 'drupal' or already_done == 0):
				
		
					
					proxy = urllib2.ProxyHandler({'https': 'https://proxy.ign.fr:3128'})
					opener = urllib2.build_opener(proxy)
					urllib2.install_opener(opener)
					req = urllib2.Request(row[2])
					sock = urllib2.urlopen(req)
					
					htmlSource = sock.read()
					sock.close()
					fichier = open(update_dir + "\\htmlSource.txt","w")
					fichier.write(htmlSource)
					fichierr = open(update_dir + "\\htmlSource.txt","r")
					filtrat = ''.join(fichierr.readlines()).rstrip('\n\r').split('<h3>Downloads</h3>')[1]
					version_mod = filtrat.split('</a>')[0]
					version_mod = version_mod.split('<a')[1]
					version_mod = version_mod.split('>')[1]
					down_link = filtrat.split('</a>')[2]
					down_link = down_link.split('href="')[1]
					down_link = down_link.split('">')[0]
					if (version_mod != row[1]):
						print 'Module "'+row[0]+'" to update : '+row[1]+' --> '+version_mod
						print down_link
						url = down_link
						
						proxy = urllib2.ProxyHandler({'http': 'http://proxy.ign.fr:3128'})
						opener = urllib2.build_opener(proxy)
						urllib2.install_opener(opener)
						file_name = url.split('/')[-1]
						u = urllib2.urlopen(url)
						if (row[3] == 'Theme'):
							f = open(update_dir+'\\themes\\'+file_name, 'wb')
						else:
							f = open(update_dir+'\\modules\\'+file_name, 'wb')
						meta = u.info()
						file_size = int(meta.getheaders("Content-Length")[0])
						print "Downloading: %s Bytes: %s" % (file_name, file_size)
						
						file_size_dl = 0
						block_sz = 8192
						while True:
							buffer = u.read(block_sz)
							if not buffer:
								break

							file_size_dl += len(buffer)
							f.write(buffer)
							status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
							status = status + chr(8)*(len(status)+1)
							print status,
						f.close()
						print'--'*20
						if (row[0] != 'drupal'):
							count_update = count_update + 1
						else:
							count_update = count_update + 1
							drupal_to_update = ' including the drupal core'
					else:
						print 'Module "'+row[0]+'" already up to date (version '+version_mod+')'
						print'--'*20
						
				if (row[0] == 'drupal'):
					already_done = 1
		i = i+1


fichier.close()
fichierr.close()
if os.path.exists("up_to_date_DRUPAL_CORE"):
	shutil.rmtree("up_to_date_DRUPAL_CORE")
if os.path.exists("up_to_date_modules"):
	shutil.rmtree("up_to_date_modules")
if (count_update > 0):
	print 'Unzip downloaded packages...'
	print'--'*20
dirs = os.listdir(update_dir + '\\modules')
for file in dirs:
	if zipfile.is_zipfile(update_dir + '\\modules\\' + file):
		fh = open(update_dir + '\\modules\\' + file, 'rb')
		z = zipfile.ZipFile(fh)
			
		if not "drupal-" in file:
			outpath = 'up_to_date_modules'
		else:
			outpath = 'up_to_date_DRUPAL_CORE'
			
		for name in z.namelist():
			z.extract(name, outpath)
		fh.close()
		os.remove(update_dir + '\\modules\\' + file)

dirs = os.listdir(update_dir + '\\themes')
for file in dirs:
	if zipfile.is_zipfile(update_dir + '\\themes\\' + file):
		fh = open(update_dir + '\\themes\\' + file, 'rb')
		z = zipfile.ZipFile(fh)
			
		outpath = 'up_to_date_themes'
			
		for name in z.namelist():
			z.extract(name, outpath)
		fh.close()
		os.remove(update_dir + '\\themes\\' + file)

if os.path.exists(os.path.realpath(__file__)+'\\..\\up_to_date_DRUPAL_CORE'):
	drupal_dir = os.listdir(os.path.realpath(__file__)+'\\..\\up_to_date_DRUPAL_CORE')
	for file in drupal_dir:
		shutil.rmtree(os.path.realpath(__file__)+'\\..\\up_to_date_DRUPAL_CORE\\'+file+'\\sites')

shutil.rmtree(update_dir)
plur = ''
if (count_update > 1):
	plur = 's'
if (count_update > 0):
	print str(count_update) + ' module%s' %(plur) + drupal_to_update + ' have to be updated.'
else:
	print 'Everything is up to date.'