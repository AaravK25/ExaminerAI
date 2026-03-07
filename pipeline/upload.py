#Handles Image Upload

import shutil
import os

# Source - https://stackoverflow.com/a/49237357
# Posted by FlyingTeller, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-07, License - CC BY-SA 4.0

#Modified StackOverflow code for my needs.
def uploadImg(src_dir: str, imageNames: list):
    dst_dir = "data/raw_images"
    for imageName in imageNames:
        shutil.copy(os.path.join(src_dir, imageName), dst_dir)
    
    return "Upload Function Successful", dst_dir, imageNames
