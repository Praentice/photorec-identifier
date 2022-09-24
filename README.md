# Photorec-identifier
This CLI tool allows you to keep only deleted files from the disk img by comparing the output of photorec with the current filesystem of the disk image.
Always make a copy of the disk you want to analyze, do not attempt to launch this tool on the disk itself.
## Install
### Requirements
```commandline
pip install -r requirements.txt
```
### Running the tool
```
./main.py -p path/to/photorec/output -f path/to/mounted/disk #Launching a session without saving the progress made
./main.py -p path/to/photorec/output -f path/to/mounted/disk -s your_file.json #Launching a session with saving the progress 
./main.py -p path/to/photorec/output -f path/to/mounted/disk -r your_file.json Resuming a previous session from file 
```
## Documentation
## Credits
This tool was created by Prantice and is provided for free.


