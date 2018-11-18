import os
from plyfile import PlyData, PlyElement
import numpy
import sys
import json


path_to_meshlab_dir: str = "C:\Program Files\VCG\MeshLab\\"
path_to_liveScan3D_files: str = "C:\\Users\\futur\Desktop\BachelorCR\TestSet_Kinect_Recording\\"
path_to_mesher_script: str = "C:\\Users\\futur\Desktop\BachelorCR\KinectToMesh\mesher.mlx"
path_to_SOR_script: str = "C:\\Users\\futur\Desktop\BachelorCR\KinectToMesh\SOR.mlx"
path_to_output: str = "C:\\Users\\futur\Desktop\BachelorCR\KinectToMesh\Mesher\Mesher_for_Livescan_3D\\output\\"

startUp_files = [path_to_meshlab_dir + "meshlabserver.exe", path_to_mesher_script, path_to_SOR_script]
startUp_paths = [path_to_output, path_to_liveScan3D_files]

ball_point_radius = 0
poisson_disk_vertices = 0


def check_path_and_file_integrity(list_of_files_to_check, list_of_paths_to_check):

    if list_of_files_to_check.__len__() != 0:
        for file in list_of_files_to_check:
            file_exists = os.path.isfile(file)
            print(file_exists)
            if not file_exists:
                return False

    if list_of_paths_to_check.__len__() != 0:
        for path_dir in list_of_paths_to_check:
            dir_exists = os.path.isdir(path_dir)
            if not dir_exists:
                return False
        return True


def cleanup_files(list_of_files_to_delete, list_of_paths_to_delete):

    if list_of_files_to_delete.__len__() != 0:
        for file in list_of_files_to_delete:
            if os.path.isfile(file): os.remove(file)

    if list_of_paths_to_delete.__len__() != 0:
        for path in list_of_paths_to_delete:
            if os.path.isdir(path):
                from shutil import rmtree
                rmtree(path)


def get_list_of_liveScan3D_files():
    temp_list_of_files = []
    for file in os.listdir(path_to_liveScan3D_files):
        if file.endswith(".ply"):
            temp_list_of_files.append(file)

    if temp_list_of_files.__len__() == 0:
        sys.exit("No LiveScanFiles found, aborting program!")

    print("LiveScan3D input files: " + temp_list_of_files.__str__())
    return temp_list_of_files


def get_number_of_depth_sensors_used(list_of_all_files):
    previous_depth_sensor_number = 0
    for frames in list_of_all_files:
        frame_string: str = frames
        print(frame_string)
        number_of_current_depth_sensor = int(frame_string[5])
        if number_of_current_depth_sensor + 1 > previous_depth_sensor_number:
            previous_depth_sensor_number = number_of_current_depth_sensor +1
        else:
            print("Found: " + previous_depth_sensor_number.__str__() + " depth sensors")
            if previous_depth_sensor_number == 0:
                sys.exit("Couldn't compute number of depth sensors")
            return previous_depth_sensor_number

def get_camera_positions_dic_from_file():

    path_to_camPose_file = path_to_liveScan3D_files + "CamPose.txt"

    if os.path.isfile(path_to_camPose_file):

        try:
            camPose_json = open(path_to_camPose_file).read()

            camPose_deserialized = json.loads(camPose_json)

            return camPose_deserialized
        except:
            sys.exit("Error while deserializing camPose File. Have you edited the camPose File manually? Check for "
                     "JSON Format errors! Aborting...")


    else:
        sys.exit("camPose File not found, aborting!")




def meshlabserver_cmd_promt_creator_single_file(frame_name, input_path, script_path, output_path, prefix_string, output_format, output_flags):
    input_cmd: str = " -i "
    output_cmd: str = " -o "
    script_cmd: str = " -s "

    meshlabserver_input_cmds = input_cmd + input_path + frame_name

    temp_filenametouple = frame_name.split(".")  # Generate output filename with current output format
    output_file_name = temp_filenametouple[0] + output_format

    cmd_promt = path_to_meshlab_dir + "meshlabserver" + meshlabserver_input_cmds + output_cmd + output_path + prefix_string + \
                output_file_name + output_flags + script_cmd + script_path
    file_output_path = output_path + prefix_string + output_file_name
    print("Final command given to meshlabserver: " + cmd_promt)
    cmd_promt_and_output_path = (cmd_promt, file_output_path)
    return cmd_promt_and_output_path

def meshlabserver_cmd_promt_creator_multiple_files(list_of_files, input_path, script_path, output_path, prefix_string, output_format, output_flags):
    input_cmd: str = " -i "
    output_cmd: str = " -o "
    script_cmd: str = " -s "
    meshlabserver_input_cmds = ""

    for frames in list_of_files:
        meshlabserver_input_cmds = meshlabserver_input_cmds + input_cmd + input_path + frames

    file_number = s = ''.join(x for x in list_of_files[0] if x.isdigit())
    output_file_name = file_number + output_format

    cmd_promt = path_to_meshlab_dir + "meshlabserver" + meshlabserver_input_cmds + output_cmd + output_path + prefix_string + \
                output_file_name + output_flags + script_cmd + script_path
    file_output_path = output_path + prefix_string + output_file_name
    print("Final command given to meshlabserver: " + cmd_promt)
    cmd_promt_and_output_path = (cmd_promt, file_output_path)
    return cmd_promt_and_output_path


def meshlabserver_supervisor(cmd_to_call, file_output_path):
    from subprocess import call
    call(cmd_to_call)
    print("MeshlabServer finished operation")
    file_exists = os.path.isfile(file_output_path)
    if file_exists:
        print("File successfully created! Moving on to the next file")
    else:
        print("MeshlabServer crashed during meshing! Retrying....")
        meshlabserver_supervisor(cmd_to_call, file_output_path)


def check_dir_make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def statistical_outlier_removal(input_file, output_file):
    remove_all_vertices_above_sd_sigma_of = 1.5  # In Standard Deviation sigma. E.g. 1 means remove all vertices that
    # are above 68% of all vertex qualities, 2 means remove all above 95% ect. Default is 1.5 or 86%

    file_exists = os.path.isfile(input_file)
    print(file_exists)
    if not file_exists:
        return False

    pointcloud_with_outliers = PlyData.read(input_file)

    quality_list_with_statistical_outliers = pointcloud_with_outliers['vertex'].data['quality']

    mean = numpy.mean(quality_list_with_statistical_outliers, axis=0)
    print("The mean of the vertex radius is: " + mean.__str__())
    sd = numpy.std(quality_list_with_statistical_outliers, axis=0)
    print("The Standard Deviation of the vertex radius is: " + sd.__str__())

    print("Removing all vertices above sigma of " + remove_all_vertices_above_sd_sigma_of.__str__())

    list_of_vertices_without_SO = []

    for index, x in enumerate(quality_list_with_statistical_outliers):
        if x < mean + remove_all_vertices_above_sd_sigma_of * sd:
            list_of_vertices_without_SO.append(pointcloud_with_outliers["vertex"][index])

    print("Removed " + (len(quality_list_with_statistical_outliers) - len(
        list_of_vertices_without_SO)).__str__() + " outlier vertices")

    print("Creating PLY file now")

    vertex = numpy.array(list_of_vertices_without_SO,
                         dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('quality', 'f4')])

    new_ply_element = PlyElement.describe(vertex, "vertex")

    PlyData([new_ply_element]).write(output_file)

    poisson_disk_vertices = len(list_of_vertices_without_SO) / 2
    ball_point_radius = mean + remove_all_vertices_above_sd_sigma_of * sd

    print(poisson_disk_vertices)
    print(ball_point_radius)

    return True


def main_loop():

    # Check if paths and files are valid

    if not check_path_and_file_integrity(startUp_files, startUp_paths):
        sys.exit("Startup files and paths are not vallid!")

    # Set all static variables
    list_of_files_to_process = get_list_of_liveScan3D_files()
    number_of_depth_sensors = get_number_of_depth_sensors_used(list_of_files_to_process)
    camPoseData = get_camera_positions_dic_from_file()

    # Calculate how much frames need to be processed

    frames_to_process = len(list_of_files_to_process) / number_of_depth_sensors
    frames_to_process = 5
    print("Found " + frames_to_process.__str__() + " frames to process")
    print("Processing started")
    current_frame_to_process = 0  # Dont change!

    # Create a temp directory
    tempdir = path_to_liveScan3D_files + "temp\\"
    check_dir_make_dir(tempdir)

    for frame in range(frames_to_process.__int__()):

        coherent_frames = []

        # Statistic Outlier Removal
        for index, kinect in enumerate(range(number_of_depth_sensors)):
            cmd_for_meshlabserver_with_output_path = meshlabserver_cmd_promt_creator_single_file(list_of_files_to_process[current_frame_to_process + index],
                                                                                                 path_to_liveScan3D_files,
                                                                                                 path_to_SOR_script,
                                                                                                 tempdir, "temp_with_SO_", ".ply",
                                                                                                 " -m vq")
            meshlabserver_supervisor(cmd_for_meshlabserver_with_output_path[0], cmd_for_meshlabserver_with_output_path[1])
            temp_filenumber = list_of_files_to_process[current_frame_to_process + index].split(".")
            SOR_created = statistical_outlier_removal(cmd_for_meshlabserver_with_output_path[1], tempdir + "temp_SOR_removed_" + temp_filenumber[0] + ".ply")
            if SOR_created:
                coherent_frames.append(("temp_SOR_removed_" + temp_filenumber[0] + ".ply"))
            else:
                print("WARNING! Statistical Outlier Removal could not be performed due to missing input file!")

        # Meshing
        cmd_for_meshlabserver_with_output_path = meshlabserver_cmd_promt_creator_multiple_files(coherent_frames,
                                                                                             tempdir, path_to_mesher_script,
                                                                                             path_to_output,
                                                                                             "meshed", ".obj", "")
        meshlabserver_supervisor(cmd_for_meshlabserver_with_output_path[0], cmd_for_meshlabserver_with_output_path[1])
        current_frame_to_process += number_of_depth_sensors
    print("No more frames to process! Processed " + current_frame_to_process.__str__() + " frames. Program will perform cleanup & exit shortly")
    cleanup_files([], [tempdir])


main_loop()
