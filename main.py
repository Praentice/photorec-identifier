#!/usr/bin/python3
import hashlib
import json
from tqdm import tqdm
import os
from send2trash import send2trash
from datetime import datetime
import argparse
import os
import shutil

VERSION=2.0

# Press the green button in the gutter to run the script.
def safetyMechanism(string1,string2): #Prevent dumb things from happening
    if string1 is string2:
        exit(0)

def getAllFiles(isAllowedToPrint,path):
    file_list = []
    for path, folders, files in tqdm(os.walk(path),disable=isAllowedToPrint):
        for file in files:
            file_list.append(os.path.join(path, file))
    return file_list

def computeAllHashOfFiles(files,isAllowedToPrint):
    database_hashes = {}
    for file in tqdm(files,disable=isAllowedToPrint):
        database_hashes[file] = hashFileWithSHA1(file)
    return database_hashes

def verifySignature(databaseSignaturePhotorec,databaseSignatureFileSystem,isAllowedToPrint):
    knownFileList = []
    for i in tqdm(databaseSignaturePhotorec, disable=isAllowedToPrint):
        signatureToFind = databaseSignaturePhotorec.get(i)
        matchedFileFromPhotorec = ''
        matchedFileFromFilesystem = []
        isKnown = 0
        for k in databaseSignatureFileSystem:
            signatureToCheck = databaseSignatureFileSystem.get(k)
            if (signatureToFind == signatureToCheck):
                matchedFileFromPhotorec = i
                matchedFileFromFilesystem.append(k)
                isKnown = 1
        if isKnown == 1:
                knownFileList.append(matchedFileFromPhotorec)
    return knownFileList

def movingAway(filesToDelete,action,isAllowedToPrint,photorecFolder):
    filesToDelete = list(set(filesToDelete))
    if action == "1": #Move files to trash
        for i in tqdm(filesToDelete):
            send2trash(i)
    elif action == "2": #Delete files
        for i in tqdm(filesToDelete):
            os.remove(i)
    elif action == "3":
        folder = ""
        if photorecFolder[-1] == "/":
            folder = photorecFolder+"trash"
        else:
            folder = photorecFolder+"/trash"
        if not os.path.exists(folder):
            os.mkdir(folder)
        for i in filesToDelete:
            shutil.move(i,folder)



def saveSession(fileName,photoRecDirList,fileSystemDirList,databaseSignaturePhotoRec,databaseSignatureFileSystem,knownFileList,numberOfSteps,action):
    # Sauvegarder le numéro d'étape, la liste des fichers photorec, filesystem, fichiers identifiés, bdd de signature pour photorec et filesystem
    # saveSession(fileName,photoRecDirList,fileSystemDirList,databaseSignaturePhotoRec,databaseSignatureFileSystem,knownFileList,n)
    canIPrintThisMessage(isAllowedToPrint, "Saving current session to {}...".format(fileName))
    with open(fileName, 'w') as f:
        dict = {"photoRecDirList": photoRecDirList, "fileSystemDirList": fileSystemDirList, "databaseSignaturePhotorec": databaseSignaturePhotoRec, "databaseSignatureFileSystem": databaseSignatureFileSystem,"knownFileList": knownFileList,"numberOfSteps": numberOfSteps,"action": action}
        json.dump(dict, f)
    return 0

def canIPrintThisMessage(arg,message):
    if not arg:
        print(message)

def hashFileWithSHA1(file):
    h = hashlib.sha1()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(file, 'rb', buffering=0) as f:
        while n := f.readinto(mv):
            h.update(mv[:n])
    return h.hexdigest()

def getOptions():
    parser = argparse.ArgumentParser(add_help=True, formatter_class=argparse.RawTextHelpFormatter,
                                     description=
    """
    ╔═╗┬ ┬┌─┐┌┬┐┌─┐┬─┐┌─┐┌─┐       ┬┌┬┐┌─┐┌┐┌┌┬┐┬┌─┐┬┌─┐┬─┐
    ╠═╝├─┤│ │ │ │ │├┬┘├┤ │    ───  │ ││├┤ │││ │ │├┤ │├┤ ├┬┘
    ╩  ┴ ┴└─┘ ┴ └─┘┴└─└─┘└─┘       ┴─┴┘└─┘┘└┘ ┴ ┴└  ┴└─┘┴└─
    This CLI tool allows you to keep only deleted files from the disk img by comparing the output of photorec with the current filesystem of the disk image.
    Always make a copy of the disk you want to analyze, do not attempt to launch this tool on the disk itself.
    Launching a session without saving the progress made : ./main.py -p path/to/photorec/output -f path/to/mounted/disk
    Launching a session with saving the progress : ./main.py -p path/to/photorec/output -f path/to/mounted/disk -s your_file.json
    Resuming a previous session : ./main.py -p path/to/photorec/output -f path/to/mounted/disk -r your_file.json
    """,
    epilog=
    """
    Created by Prantice with love <3
    """,
    )
    parser.version = "The current version is {}".format(VERSION)
    parser.add_argument('-p', "--photorec", required=True,
                        help="""Absolute path of the files recovered by photorec software (Mandatory)""", )
    parser.add_argument('-f', "--filesystem", required=True,
                        help="""Absolute path of the mounted disk img filesystem (Mandatory)""", )
    parser.add_argument('-a', "--action", required=True,
                        help="""Choose what to do with the identified file (1 = Move files to trash bin ; 2 = Wipe files from hard drive ; 3 = Move files to a folder named "trash" within photorec folder) (Mandatory)""", )
    parser.add_argument('-q', "--quiet", required=False, action="store_true",
                        help="""Do not print message on the terminal (Optional)""", )
    parser.add_argument('-v', '--version', action='version', help='print the version and exit')
    parser.add_argument('-s', "--savesession", required=False, help="""Save current session to file (Optional)""", )
    parser.add_argument('-r', "--resumesession", required=False,
                        help="""Resume previous session from file (Optionnal)""", )
    args = vars(parser.parse_args())
    return args

if __name__ == '__main__':
    numberOfStep = 0
    args = getOptions()
    start = datetime.now()
    isAllowedToPrint = args['quiet']
    photoRecFolderPath = args['photorec']
    fileSystemFolderPath = args['filesystem']
    action = args['action']
    safetyMechanism(photoRecFolderPath,fileSystemFolderPath)
    knownFileList = []
    photoRecDirList = []
    fileSystemDirList = []
    databaseSignaturePhotorec = {}
    databaseSignatureFileSystem = {}
    if not(args['resumesession']):
        try:
            canIPrintThisMessage(isAllowedToPrint, 'Now, grab a snack and enjoy the strange tale of Photorec-identifier !')
            canIPrintThisMessage(isAllowedToPrint, 'Step 1 : Enumerate all files from photorec folder...')
            numberOfStep+=1
            photoRecDirList = getAllFiles(isAllowedToPrint,photoRecFolderPath)
            canIPrintThisMessage(isAllowedToPrint, 'Step 2 : Enumerate all files from filesystem folder...')
            numberOfStep += 1
            fileSystemDirList = getAllFiles(isAllowedToPrint, fileSystemFolderPath)
            canIPrintThisMessage(isAllowedToPrint, 'Step 3 : Compute all signatures of photorec files folder...')
            numberOfStep += 1
            databaseSignaturePhotorec = computeAllHashOfFiles(photoRecDirList,isAllowedToPrint)
            canIPrintThisMessage(isAllowedToPrint, 'Step 4 : Compute all signatures of filesystem files folder...')
            numberOfStep += 1
            databaseSignatureFileSystem = computeAllHashOfFiles(fileSystemDirList,isAllowedToPrint)
            canIPrintThisMessage(isAllowedToPrint, 'Step 5 : Comparing files from photorec folder to filesystem folder...')
            numberOfStep += 1
            knownFileList = verifySignature(databaseSignaturePhotorec,databaseSignatureFileSystem,isAllowedToPrint)
            canIPrintThisMessage(isAllowedToPrint,'Step 6 : Moving the known files to the trashcan...')
            numberOfStep += 1
            movingAway(knownFileList,action,isAllowedToPrint,photoRecFolderPath)
            stop = datetime.now()-start
            canIPrintThisMessage(isAllowedToPrint, "Script successfully finished in {}".format(stop))
            canIPrintThisMessage(isAllowedToPrint, "{} files were deleted.".format(len(knownFileList)))
        except KeyboardInterrupt:
            if args['savesession']:
                exit(saveSession(args['savesession'], photoRecDirList, fileSystemDirList, databaseSignaturePhotorec, databaseSignatureFileSystem, knownFileList, numberOfStep))
            else:
                canIPrintThisMessage(isAllowedToPrint,"Not saving current session...")
                exit(0)
    else:
        sessionFile = args['resumesession']
        try:
            f = open(sessionFile)
        except FileNotFoundError:
            print("The file {} have not been found.".format(sessionFile))
            exit(1)
        try:
            data = json.load(f)
            knownFileList = data['knownFileList']
            photoRecDirList = data['photoRecDirList']
            fileSystemDirList = data['fileSystemDirList']
            databaseSignaturePhotorec = data['databaseSignaturePhotorec']
            databaseSignatureFileSystem = data['databaseSignatureFileSystem']
            numberOfStep = data['numberOfSteps']
            action = data['action']
            canIPrintThisMessage(isAllowedToPrint,"Resuming session from {}".format(sessionFile))
            if numberOfStep == 1: # Resume process from step 1
                canIPrintThisMessage(isAllowedToPrint, 'Step 1 : Enumerate all files from photorec folder...')
                numberOfStep += 1
                photoRecDirList = getAllFiles(isAllowedToPrint, photoRecFolderPath)
                canIPrintThisMessage(isAllowedToPrint, 'Step 2 : Enumerate all files from filesystem folder...')
                numberOfStep += 1
                fileSystemDirList = getAllFiles(isAllowedToPrint, fileSystemFolderPath)
                canIPrintThisMessage(isAllowedToPrint, 'Step 3 : Compute all signatures of photorec files folder...')
                numberOfStep += 1
                databaseSignaturePhotorec = computeAllHashOfFiles(photoRecDirList, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 4 : Compute all signatures of filesystem files folder...')
                numberOfStep += 1
                databaseSignatureFileSystem = computeAllHashOfFiles(fileSystemDirList, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint,'Step 5 : Comparing files from photorec folder to filesystem folder...')
                numberOfStep += 1
                knownFileList = verifySignature(databaseSignaturePhotorec, databaseSignatureFileSystem,isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 6 : Moving the known files to the trashcan...')
                numberOfStep += 1
                movingAway(knownFileList,action,isAllowedToPrint,photoRecFolderPath)
            elif numberOfStep == 2: # Resume process from step 2
                canIPrintThisMessage(isAllowedToPrint, 'Step 2 : Enumerate all files from filesystem folder...')
                numberOfStep += 1
                fileSystemDirList = getAllFiles(isAllowedToPrint, fileSystemFolderPath)
                canIPrintThisMessage(isAllowedToPrint, 'Step 3 : Compute all signatures of photorec files folder...')
                numberOfStep += 1
                databaseSignaturePhotorec = computeAllHashOfFiles(photoRecDirList, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 4 : Compute all signatures of filesystem files folder...')
                numberOfStep += 1
                databaseSignatureFileSystem = computeAllHashOfFiles(fileSystemDirList, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint,'Step 5 : Comparing files from photorec folder to filesystem folder...')
                numberOfStep += 1
                knownFileList = verifySignature(databaseSignaturePhotorec, databaseSignatureFileSystem,isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 6 : Moving the known files to the trashcan...')
                numberOfStep += 1
                movingAway(knownFileList,action,isAllowedToPrint,photoRecFolderPath)
            elif numberOfStep == 3: # Resume process from step 3
                canIPrintThisMessage(isAllowedToPrint, 'Step 3 : Compute all signatures of photorec files folder...')
                numberOfStep += 1
                databaseSignaturePhotorec = computeAllHashOfFiles(photoRecDirList, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 4 : Compute all signatures of filesystem files folder...')
                numberOfStep += 1
                databaseSignatureFileSystem = computeAllHashOfFiles(fileSystemDirList, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 5 : Comparing files from photorec folder to filesystem folder...')
                numberOfStep += 1
                knownFileList = verifySignature(databaseSignaturePhotorec, databaseSignatureFileSystem,isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 6 : Moving the known files to the trashcan...')
                numberOfStep += 1
                movingAway(knownFileList,action,isAllowedToPrint,photoRecFolderPath)
            elif numberOfStep == 4: # Resume process from step 4
                canIPrintThisMessage(isAllowedToPrint, 'Step 4 : Compute all signatures of filesystem files folder...')
                numberOfStep += 1
                databaseSignatureFileSystem = computeAllHashOfFiles(fileSystemDirList, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 5 : Comparing files from photorec folder to filesystem folder...')
                numberOfStep += 1
                knownFileList = verifySignature(databaseSignaturePhotorec, databaseSignatureFileSystem,isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 6 : Moving the known files to the trashcan...')
                numberOfStep += 1
                movingAway(knownFileList,action,isAllowedToPrint,photoRecFolderPath)
            elif numberOfStep == 5: # Resume process from step 5
                canIPrintThisMessage(isAllowedToPrint,'Step 5 : Comparing files from photorec folder to filesystem folder...')
                numberOfStep += 1
                knownFileList = verifySignature(databaseSignaturePhotorec, databaseSignatureFileSystem, isAllowedToPrint)
                canIPrintThisMessage(isAllowedToPrint, 'Step 6 : Moving the known files to the trashcan...')
                numberOfStep += 1
                movingAway(knownFileList,action,isAllowedToPrint,photoRecFolderPath)
            elif numberOfStep == 6: # Resume process from step 6
                canIPrintThisMessage(isAllowedToPrint, 'Step 6 : Moving the known files to the trashcan...')
                numberOfStep += 1
                movingAway(knownFileList,action,isAllowedToPrint,photoRecFolderPath)
            else:
                exit(0)
            canIPrintThisMessage(isAllowedToPrint, "Script successfully finished")
            canIPrintThisMessage(isAllowedToPrint, "{} files were deleted.".format(len(knownFileList)))
        except KeyboardInterrupt:
            exit(saveSession(args['savesession'], photoRecDirList, fileSystemDirList, databaseSignaturePhotorec, databaseSignatureFileSystem, knownFileList, numberOfStep))







