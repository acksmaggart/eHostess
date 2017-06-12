import NotePreprocessing.VerifyUniqueNames as verifyUnique

duplicates = verifyUnique.VerifyUniqueNames(['./testDir/', './testDir2/'])

if duplicates:
	print("Duplicates:")
	for name in duplicates:
		print name
else:
	print ("No duplicates.")
