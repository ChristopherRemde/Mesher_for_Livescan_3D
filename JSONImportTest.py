import os
import sys
import json

path_to_camPose_file = "C:\\Users\\ChrisSSD\\Desktop\\TexturePipeLineTest\\CamPose.txt"
if os.path.isfile(path_to_camPose_file):


    try:
        camPose_json = open(path_to_camPose_file).read()

        camPose_deserialized = json.loads(camPose_json)

        print(camPose_deserialized["camPositions"][0]["x"])
    except:
            sys.exit("Error while deserializing camPose File. Have you edited the camPose File manually? Check for "
            "JSON Format errors! Aborting...")


else:
    sys.exit("camPose File not found, aborting!")




