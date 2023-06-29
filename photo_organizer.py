# Modified project from source Aaron Yu at https://python.plainenglish.io/create-a-photo-organizer-in-1-hour-with-python-9d4b82552f21

import os
import shutil
import time
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import TAGS
from pillow_heif import register_heif_opener

register_heif_opener()

# This is your original photo folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
localPath = BASE_DIR
destinationPath = os.path.join(BASE_DIR, "SortedPhotos")
videos_destination_path = os.path.join(BASE_DIR, "Videos")
_TAGS_r = dict(((v, k) for k, v in TAGS.items()))
totalFiles = 0
processedPhotos = 0
notPhotos = 0


def processPhoto(photoPath):
    global processedPhotos, notPhotos
    try:
        if Path(photoPath).suffix.lower() in ['.jpg', '.png']:
            with open(photoPath, 'rb') as file:
                im = Image.open(file)
                exif_data_PIL = im.getexif()
                im = Image.open(file)
                destinationFolder = datetime.fromtimestamp(
                    os.path.getctime(photoPath)
                ).strftime('%B_%Y')
                if not os.path.isdir(
                    os.path.abspath(os.path.join(destinationPath, destinationFolder))
                ):
                    os.mkdir(
                        os.path.abspath(
                            os.path.join(destinationPath, destinationFolder)
                        )
                    )
                photoName = Path(photoPath).stem
                newPhotoName = os.path.abspath(
                    os.path.join(
                        destinationPath, destinationFolder, photoName + '.' + im.format
                    )
                )
                print(newPhotoName)
                im.close()
                shutil.move(photoPath, newPhotoName)
                processedPhotos += 1
                print(
                    "\r%d photos processed, %d not processed"
                    % (processedPhotos, notPhotos),
                    end='',
                )
                return

        if Path(photoPath).suffix.lower() in ['.mpo', '.aac']:
            return
        with open(photoPath, 'rb') as file:
            im = Image.open(file)
            exif_data_PIL = im.getexif()
            if exif_data_PIL is not None:
                if exif_data_PIL[_TAGS_r["DateTime"]] is not None:
                    fileDate = exif_data_PIL[_TAGS_r["DateTime"]]
                    if fileDate != '' and len(fileDate) > 10:
                        if fileDate != '0000:00:00 00:00:00':
                            destinationFolder = datetime.strptime(
                                fileDate[:10], '%Y:%m:%d'
                            ).strftime('%B_%Y')
                        else:
                            destinationFolder = 'no_date'
                        # if destination folder does not exist, create one
                        if not os.path.isdir(
                            os.path.abspath(
                                os.path.join(destinationPath, destinationFolder)
                            )
                        ):
                            os.mkdir(
                                os.path.abspath(
                                    os.path.join(destinationPath, destinationFolder)
                                )
                            )
                        # new name of the photo
                        photoName = Path(photoPath).stem
                        newPhotoName = os.path.abspath(
                            os.path.join(
                                destinationPath,
                                destinationFolder,
                                photoName + '.' + im.format,
                            )
                        )
                        print(newPhotoName)
                        im.close()
                        shutil.move(photoPath, newPhotoName)
                        processedPhotos += 1
                        print(
                            "\r%d photos processed, %d not processed"
                            % (processedPhotos, notPhotos),
                            end='',
                        )
            else:
                notPhotos += 1
                print(
                    "\r%d photos processed, %d not processed"
                    % (processedPhotos, notPhotos),
                    end='',
                )
    except IOError as err:
        print(err)
        notPhotos += 1
        print(
            "\r%d photos processed, %d not processed" % (processedPhotos, notPhotos),
            end='',
        )
        pass
    except KeyError:
        notPhotos += 1
        pass


def processFolder(folderPath, countOnly):
    global totalFiles
    for file in os.listdir(folderPath):
        # print(file)
        # read all files and folder
        fileNameIn = os.path.abspath(os.path.join(folderPath, file))
        # print(fileNameIn)
        # if this is a folder, read all files inside
        if os.path.isdir(fileNameIn):
            processFolder(fileNameIn, countOnly)
        # if it's file, process it as a photo
        else:
            if countOnly:
                totalFiles += 1
            else:
                processPhoto(fileNameIn)


def main(argv=None):
    tic = time.perf_counter()
    processFolder(localPath, True)
    print("There are total %d files" % totalFiles)
    processFolder(localPath, False)
    print(
        "\nThere are %d photos processed, %d not processed"
        % (processedPhotos, notPhotos)
    )
    toc = time.perf_counter()
    print(f"Time used: {toc - tic:0.4f} seconds")


if __name__ == "__main__":
    main()
