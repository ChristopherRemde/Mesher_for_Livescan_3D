import os

path_to_meshlab_dir: str = "C:\Program Files\VCG\MeshLab\meshlabserver"
path_to_liveScan3D_files: str = "C:\\Users\\futur\Desktop\BachelorCR\TestSet_Kinect_Recording\\"
path_to_mlx_script: str = "C:\\Users\\futur\Desktop\BachelorCR\KinectToMesh\Static_Example_MLX_File.mlx"
path_to_output: str = "C:\\Users\\futur\Desktop\BachelorCR\KinectToMesh\Mesher\output\\"
output_format: str = ".obj"


def get_list_of_sorted_liveScan3D_files():
    temp_list_of_files = []
    for file in os.listdir(path_to_liveScan3D_files):
        if file.endswith(".ply"):
            temp_list_of_files.append(file)

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
            return previous_depth_sensor_number


def meshlabserver_cmd_promt_creator(list_of_all_files, frame_to_process, number_of_depth_sensors):
    input_cmd: str = " -i "
    output_cmd: str = " -o "
    script_cmd: str = " -s "
    meshed_string: str = "meshed"
    meshlabserver_input_cmds = ""
    kinect_counter = 0

    for kinect in range(number_of_depth_sensors):
        meshlabserver_input_cmds = meshlabserver_input_cmds + input_cmd + path_to_liveScan3D_files + list_of_all_files[
            frame_to_process + kinect_counter]
        kinect_counter += 1

    temp_filenametouple = list_of_all_files[frame_to_process].split(".")  # Generate output filename with corrent output format
    output_file_name = temp_filenametouple[0] + output_format

    cmd_promt = path_to_meshlab_dir + meshlabserver_input_cmds + output_cmd + path_to_output + meshed_string + \
                output_file_name + script_cmd + path_to_mlx_script
    file_output_path = path_to_output + meshed_string + output_file_name
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


def main_loop():
    list_of_files_to_process = get_list_of_sorted_liveScan3D_files()
    number_of_depth_sensors = get_number_of_depth_sensors_used(list_of_files_to_process)
    frames_to_process = len(list_of_files_to_process) / number_of_depth_sensors
    print("Found " + frames_to_process.__str__() + " frames to process")
    print("Meshing started")
    current_frame_to_process = 0  # Dont change!
    for frame in range(frames_to_process.__int__()):
        cmd_for_meshlabserver_with_output_path = meshlabserver_cmd_promt_creator(list_of_files_to_process, current_frame_to_process, number_of_depth_sensors)
        meshlabserver_supervisor(cmd_for_meshlabserver_with_output_path[0], cmd_for_meshlabserver_with_output_path[1])
        current_frame_to_process += number_of_depth_sensors
    print("No more frames to process! Processed " + current_frame_to_process.__str__() + " frames. Program will exit now")


main_loop()
