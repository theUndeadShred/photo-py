import io
from hashlib import new
from pathlib import Path
from datetime import datetime
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from datetime import datetime
from PIL import Image
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import exifread
import pyheif

# Constants
EXIF_DATETIME_TAG = 36867
COUNTER = 0

imageFileList = [
    '.jpg',
    '.JPG',
    '.jpeg',
    '.JPEG',
    '.HEIC'
]

# Get the directories to use.
folderDialog = Tk()
folderDialog.withdraw()  # Hide useless extra window.

messagebox.showinfo(title="Photo Sort", message="Select a folder to sort.")
unsortedDir = filedialog.askdirectory(title="Select directory to sort")
our_files = Path(unsortedDir)
messagebox.showinfo(title="Photo Sort", message="Now select a destination folder.")
destinationDir = filedialog.askdirectory(title="Where should the sorted files go?")

for file in our_files.iterdir():
    originalFilePath = Path(file)

    if file.is_file() and file.stem != ".DS_Store":
        fileTakenDate = None
        if file.suffix == ".mp4" or file.suffix == ".mov":
            stringPath = str(originalFilePath)
            parser = createParser(stringPath)
            try:
                metadata = extractMetadata(parser)
            except:
                print("Video Metadata Extraction error.")

            if metadata is not None:
                text = metadata.exportPlaintext()
            
            print("Video processing - " + file.stem)

            video_date = metadata.get('creation_date')
            if video_date:
                print(video_date)
                fileTakenDate = datetime.strptime(str(video_date), "%Y-%m-%d %H:%M:%S")
                print(f'formatted video date: {fileTakenDate}')

        elif file.suffix in imageFileList:
            print("Image processing - " + file.stem)

            try:
                if file.suffix == ".HEIC":
                    print("Reading .HEIC file")
                    heif_file = pyheif.read_heif(originalFilePath)
                    for metadata in heif_file.metadata or []:
                        if metadata['type']=='Exif':
                            fstream = io.BytesIO(metadata['data'][6:])
                            exifData = exifread.process_file(fstream)
                            print(str(exifData["EXIF DateTimeOriginal"]))
                            fileTakenDate = datetime.strptime(str(exifData["EXIF DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
                            print(f'.HEIC date_taken = {file.stem} {str(fileTakenDate)}')

                        else:
                            print(file.stem + " - No date_taken found.")
                else:
                    currentImage = Image.open(originalFilePath)
                    exifData = currentImage._getexif()
                    
                    if (exifData != None) and (EXIF_DATETIME_TAG in exifData): # If the file does have "date taken" data embedded in the file.
                        fileTakenDate = datetime.strptime(exifData[EXIF_DATETIME_TAG], "%Y:%m:%d %H:%M:%S")
                        print(f'{file.stem} {str(fileTakenDate)}')
            
                    else:
                        print(file.stem + " - No date_taken found.")
            except:
                print(f'Image Metadata Extraction error: {file.stem}')

        # Calculate the month and create a new path with it
        if fileTakenDate is not None:
            month = datetime.strftime(fileTakenDate, "%B")
            year = datetime.strftime(fileTakenDate, "%Y")
            
            currentPath = Path(destinationDir)

            new_path = currentPath.joinpath(f'{year}')
            full_new_path = new_path.joinpath(month)

            if not new_path.exists():
                new_path.mkdir()

            if not full_new_path.exists():
                full_new_path.mkdir()

            # Create a new path in the new directory
            extension = file.suffix
            file_name_formatted = f'{file.stem}{extension}'
            new_file_path = full_new_path.joinpath(file_name_formatted)

            # Move the file
            file.replace(new_file_path)
            COUNTER += 1

messagebox.showinfo(title="Photo Sort", message=f'Process Completed. {str(COUNTER)} files sorted. I love you!')
