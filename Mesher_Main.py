import os
from plyfile import PlyData, PlyElement
import numpy
import sys
import json
import xml.etree.ElementTree as ET

working_dir = os.getcwd()

# Settings
path_to_meshlab_dir = "C:\Program Files\VCG\MeshLab\\"
path_to_liveScan3D_files: str = "C:\\Users\\ChrisSSD\\Desktop\\Bachelor\\LiveScan3D_Takes\\Rainer_APose\\"
path_to_mesher_script_template: str = working_dir + "\\mesher.mlx"
path_to_individual_mesher_template: str = working_dir + "\\meshing_individual_frame.mlx"
path_to_individual_vertex_reomver = working_dir + "\\remove_vertices_above_individual_frame.mlx"
path_to_SOR_script: str = working_dir + "\\SOR.mlx"
path_to_output: str = working_dir + "\\output\\"

startUp_files = [path_to_meshlab_dir + "meshlabserver.exe", path_to_mesher_script_template, path_to_SOR_script]
startUp_paths = [path_to_output, path_to_liveScan3D_files]

# Global variables

ball_point_radius = 0
poisson_disk_vertices = 0
useSSPR = True


def check_dir_make_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def check_path_and_file_integrity(list_of_files_to_check, list_of_paths_to_check):

    if list_of_files_to_check.__len__() != 0:
        for file in list_of_files_to_check:
            file_exists = os.path.isfile(file)
            if not file_exists:
                print("Couldn't find file: " + file)
                return False

    if list_of_paths_to_check.__len__() != 0:
        for path_dir in list_of_paths_to_check:
            dir_exists = os.path.isdir(path_dir)
            if not dir_exists:
                print("Couldn't find directory: ")
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

    return temp_list_of_files


def get_number_of_depth_sensors_used(list_of_all_files):

    path_to_camPose_file = path_to_liveScan3D_files + "CamPose.txt"

    if os.path.isfile(path_to_camPose_file):

        try:
            camPose_json = open(path_to_camPose_file).read()

            camPose_deserialized = json.loads(camPose_json)

        except:

            sys.exit("Error in JSON File format! Did you modify the File manually? Check for syntax errors! ")

        return sum(len(v) for v in camPose_deserialized.values())

    else:
        sys.exit("camPose File not found, aborting!")


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


def write_custom_mlx_file_template(number_of_cameras):

    mlx_doc = ET.parse('mesher_template.mlx')  # Get the mlx template
    root = mlx_doc.getroot()

    mlx_change_current_layer = root[0]
    mlx_compute_normals_for_point_sets = root[1]
    mlx_flatten_visible_layer = root[2]
    mlx_poisson_disk_sampling = root[3]
    mlx_delete_current_mesh = root[4]
    mlx_ball_pivoting = root[5]
    mlx_sspr = root[6]
    mlx_estimate_radius = root[7]
    mlx_per_vertex_quality = root[8]
    mlx_select_by_vertex_quality = root[9]
    mlx_delete_selected_vertices = root[10]

    childlist = []   # Delete all contents in root to get a clean template
    for child in root:
        childlist.append(child)
    for child in childlist:
        root.remove(child)

    for cameras in range(number_of_cameras):   # Start the document by adding all the normal calculations for each cam

        root.append(mlx_change_current_layer)
        root.append(mlx_compute_normals_for_point_sets)

    root.append(mlx_flatten_visible_layer)  # After normal calculations, flatten all layers to one
    root.append(mlx_poisson_disk_sampling)
    root.append(mlx_delete_current_mesh)
    if useSSPR:
        root.append(mlx_sspr)
        root.append(mlx_delete_current_mesh)
        root.append(mlx_estimate_radius)
        root.append(mlx_per_vertex_quality)
    else:
        root.append(mlx_ball_pivoting)

    mlx_doc.write("meshing_custom_template.mlx")


def write_custom_mlx_file_for_each_frame(camera_positions, number_of_cameras):
    mlx_custom_doc = ET.parse('meshing_custom_template.mlx')  # Get the mlx template
    root = mlx_custom_doc.getroot()

    child_counter = 0
    for cameras in range(number_of_cameras):  # Start the document by adding all the normal calculations for each cam

        root[child_counter][0].set("value", str(cameras))
        root[child_counter + 1][3].set("x", str(camera_positions["camPoses"][cameras]["x"]))
        root[child_counter + 1][3].set("y", str(camera_positions["camPoses"][cameras]["y"]))
        root[child_counter + 1][3].set("z", str(camera_positions["camPoses"][cameras]["z"]))

        if cameras != (number_of_cameras - 1):  # Only increment the childcounter if there are more values to set in the loop
            child_counter += 2

    root[child_counter + 2].set("value", str(poisson_disk_vertices))
    root[child_counter + 4].set("value", str(ball_point_radius))

    mlx_custom_doc.write("meshing_individual_frame.mlx")


def write_custom_mlx_file_for_vertex_removal(remove_vertices_above):

    mlx_custom_doc = ET.parse("custom_vertex_removal_template.mlx")
    root = mlx_custom_doc.getroot()
    root[0][0].set("value", str(remove_vertices_above))

    mlx_custom_doc.write("remove_vertices_above_individual_frame.mlx")



def meshlabserver_cmd_promt_creator_single_file(frame_name, input_path, script_path, output_path, prefix_string, output_format, output_flags):
    input_cmd: str = " -i "
    output_cmd: str = " -o "
    script_cmd: str = " -s "
    if script_path == "":
        script_cmd = ""


    meshlabserver_input_cmds = input_cmd + input_path + frame_name

    file_number = s = ''.join(x for x in frame_name if x.isdigit())
    output_file_name = file_number + output_format

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
    if script_path == "":
        script_cmd = ""
    meshlabserver_input_cmds = ""

    for frames in list_of_files:
        meshlabserver_input_cmds = meshlabserver_input_cmds + input_cmd + input_path + frames

    file_number = s = ''.join(x for x in list_of_files[0] if x.isdigit())
    output_file_name = file_number + output_format

    cmd_promt = path_to_meshlab_dir + "meshlabserver" + meshlabserver_input_cmds + output_cmd + output_path + prefix_string + \
                output_file_name + output_flags + script_cmd + script_path
    file_output_path = output_path + prefix_string + output_file_name
    print("Created Command: " + cmd_promt)
    cmd_promt_and_output_path = (cmd_promt, file_output_path)
    return cmd_promt_and_output_path


def meshlabserver_supervisor(cmd_to_call, file_output_path):
    from subprocess import call
    print("Calling Meshlabserver with command: " + cmd_to_call)
    call(cmd_to_call)
    print("MeshlabServer finished operation")
    file_exists = os.path.isfile(file_output_path)
    if file_exists:
        print("File successfully created! Moving on to the next file")
    else:
        print("MeshlabServer crashed during meshing! Retrying....")
        meshlabserver_supervisor(cmd_to_call, file_output_path)


def statistical_outlier_removal(input_file, output_file):
    remove_all_vertices_above_sd_sigma_of = 1.5  # In Standard Deviation sigma. E.g. 1 means remove all vertices that
    # are above 68% of all vertex qualities, 2 means remove all above 95% ect. Default is 1.5 or 86%

    file_exists = os.path.isfile(input_file)
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


    vertex = numpy.array(list_of_vertices_without_SO, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('quality', 'f4')])

    new_ply_element = PlyElement.describe(vertex, "vertex")

    PlyData([new_ply_element]).write(output_file)

    global poisson_disk_vertices
    global ball_point_radius
    poisson_disk_vertices = len(list_of_vertices_without_SO) / 2
    ball_point_radius = mean + remove_all_vertices_above_sd_sigma_of * sd

    return True

def get_quality_standard_deviation(input_file):
    get_standard_deviation_of = 1.5  # In Standard Deviation sigma. E.g. 1 means remove all vertices that
    # are above 68% of all vertex qualities, 2 means remove all above 95% ect. Default is 1.5 or 86%

    file_exists = os.path.isfile(input_file)
    if not file_exists:
        return 0

    pointcloud_with_outliers = PlyData.read(input_file)

    quality_list_with_statistical_outliers = pointcloud_with_outliers['vertex'].data['quality']

    mean = numpy.mean(quality_list_with_statistical_outliers, axis=0)
    print("The mean of the vertex radius is: " + mean.__str__())
    sd = numpy.std(quality_list_with_statistical_outliers, axis=0)
    print("The Standard Deviation of the vertex radius is: " + sd.__str__())

    return mean + get_standard_deviation_of * sd



def userInterface ():
    print("Mesher for LiveScan3D by ChrisR")
    print("Starting Setup...")
    ml_valid = False
    global path_to_meshlab_dir
    ml_path = path_to_meshlab_dir[:]
    while ml_valid == False:
        if check_path_and_file_integrity([], [ml_path]):
            ml_valid = True
        else:
            print("Couldn't find Meshlab!")
            ml_path = input("Please enter your Meshlab Path: ")

    path_to_meshlab_dir = ml_path

    ip_path = ""
    ip_valid = False
    while ip_valid == False:
        if check_path_and_file_integrity([], [ip_path]):
            ip_valid = True
        else:
            print("Couldn't find Meshlab!")
            ip_path = input("Please enter the Path to the Meshlab .PLY Files: ")

    global path_to_liveScan3D_files
    path_to_liveScan3D_files = ml_path

    yn = input("Do you want to use Poisson Reconstruction? (y/n): ")

    if yn == "y":
        global useSSPR
        useSSPR = True
    elif yn == "n":
        useSSPR = False
    else:
        print("Invalid input!")
        sys.exit("Invalid Input!")


def main_loop():

    check_dir_make_dir(path_to_output)
    # Check if paths and files are valid
    if not check_path_and_file_integrity(startUp_files, startUp_paths):
        sys.exit("Startup files and paths are not vallid!")

    # Set all static variables
    list_of_files_to_process = get_list_of_liveScan3D_files()
    number_of_depth_sensors = get_number_of_depth_sensors_used(list_of_files_to_process)
    cam_pose_data = get_camera_positions_dic_from_file()

    # Create a custom mlx file for meshing, depending on how many cameras there are in the scene
    write_custom_mlx_file_template(number_of_depth_sensors)

    # Calculate how much frames need to be processed
    frames_to_process = len(list_of_files_to_process) / number_of_depth_sensors
    #frames_to_process = 5
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
        write_custom_mlx_file_for_each_frame(cam_pose_data, number_of_depth_sensors)

        # Meshing
        if not useSSPR:
            cmd_for_meshlabserver_with_output_path = meshlabserver_cmd_promt_creator_multiple_files(coherent_frames,
                                                                                                    tempdir, path_to_individual_mesher_template,
                                                                                                    path_to_output, "meshed", ".obj", "")
            meshlabserver_supervisor(cmd_for_meshlabserver_with_output_path[0], cmd_for_meshlabserver_with_output_path[1])

        else:

            cmd_for_meshlabserver_with_output_path = meshlabserver_cmd_promt_creator_multiple_files(coherent_frames, tempdir,
                                                                                                    path_to_individual_mesher_template,
                                                                                                    tempdir, "SSPR_with_SO", ".ply"," -m vq")
            meshlabserver_supervisor(cmd_for_meshlabserver_with_output_path[0], cmd_for_meshlabserver_with_output_path[1])
            temp_filenumber = list_of_files_to_process[current_frame_to_process].split(".")
            remove_vertices_above_quality_of = get_quality_standard_deviation(cmd_for_meshlabserver_with_output_path[1])
            write_custom_mlx_file_for_vertex_removal(remove_vertices_above_quality_of)
            cmd_for_meshlabserver_with_output_path = meshlabserver_cmd_promt_creator_single_file("SSPR_with_SO" + temp_filenumber[0] + ".ply",
                                                                                                 tempdir, path_to_individual_vertex_reomver, path_to_output, "meshed", ".obj", "")
            meshlabserver_supervisor(cmd_for_meshlabserver_with_output_path[0], cmd_for_meshlabserver_with_output_path[1])

        current_frame_to_process += number_of_depth_sensors

        # Delete temp files

        temp_files_to_delete = []
        for file in os.listdir(tempdir):
            temp_files_to_delete.append(tempdir + file)

        cleanup_files(temp_files_to_delete, [])

    print("No more frames to process! Processed " + (current_frame_to_process / number_of_depth_sensors).__str__() + " frames. Program will perform cleanup & exit shortly")
    cleanup_files([], [tempdir])


main_loop()
