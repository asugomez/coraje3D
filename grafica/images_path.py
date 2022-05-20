
"""Convenience functionality to access images files"""

import os.path

def getImagesPath(filename):
    """Convenience function to access assets files regardless from where you run the example script."""

    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    parentFolderPath = os.path.dirname(thisFolderPath)
    assetsDirectory = os.path.join(parentFolderPath, "images")
    requestedPath = os.path.join(assetsDirectory, filename)
    return requestedPath