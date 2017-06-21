def cleanDirectoryList(corpusDirectoryList):
    newList = []
    for dirName in corpusDirectoryList:
        if dirName[-1] == '/':
            dirName += '*'
            newList.append(dirName)
            continue
        if dirName[-1] != '*' and dirName[-1] != '/':
            dirName += '/*'
            newList.append(dirName)
            continue
        if dirName[-2:] == '/*':
            newList.append(dirName)

    return newList