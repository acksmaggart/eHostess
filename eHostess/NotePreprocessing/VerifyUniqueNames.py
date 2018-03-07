import glob

def VerifyUniqueNames(directories):
	files = []
	for dir in _cleanDirNames(directories):
		files.extend(glob.glob(dir))
	sortedFilepaths = sorted(files)
	sortedFiles = []
	for path in sortedFilepaths:
		parts = path.split('/')
		sortedFiles.append(parts[-1])	
	print files
	duplicateNames = []	
	previousFile = None
	for filename in sortedFiles:
		if previousFile == None:
			previousFile = filename
			continue
		if filename == previousFile:
			duplicateNames.append(filename)
		previousFile = filename

	return duplicateNames		

def _cleanDirNames(dirList):
	newList = []
	for name in dirList:
		if name[-1] != '*' and name[-1] != '/' and name[-1] != '\\':
			newList.append(name + '/*')
			continue
		if name[-1] == '/':
			newList.append(name + '*')
			continue
		if name[-2:] == '/*':
			newList.append(name)
	return newList
