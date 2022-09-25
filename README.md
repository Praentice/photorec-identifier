# Photorec-identifier
This CLI tool allows you to keep only deleted files from the disk img by comparing the output of photorec with the current filesystem of the disk image.
Always make a copy of the disk you want to analyze, do not attempt to launch this tool on the disk itself.

You can delete the files, move them to the bin or in a dedicated folder within the photorec one.
## Install
### Requirements
```commandline
pip install -r requirements.txt
```
### Running the tool
```
./main.py -p path/to/photorec/output -f path/to/mounted/disk -a 1 #Launching a session and moving the files to the bin without saving the progress made
./main.py -p path/to/photorec/output -f path/to/mounted/disk -s your_file.json -a 1 #Launching a session and moving the files while saving the progress 
./main.py -p path/to/photorec/output -f path/to/mounted/disk -r your_file.json -a 1 #Resuming a previous session from file and at the end, move the file to the bin
```
## Documentation
### Mandatory flags
| Flag              |                                                           Description |
|-------------------|----------------------------------------------------------------------|
| -p / --photorec   | Absolute path of the files recovered by photorec software  |
| -f / --filesystem | Absolute path of the mounted disk img filesystem |
| -a / --action     |Choose what to do with the identified file (1 = Move files to trash bin ; 2 = Wipe files from hard drive ; 3 = Move files to a folder named "trash" within photorec folder)|
### Optional flags
| Flag               | Description                          |
|--------------------|--------------------------------------|
| -q / --quiet       | Do not print message on the terminal |
| -v / --version     | Print the version of tool and exit   |
| -s / --savesession | Save current session to file         |
| -r / --resumesession | Resume previous session from file |
## Credits
This tool was created by Prantice and is provided for free under GNU License.


