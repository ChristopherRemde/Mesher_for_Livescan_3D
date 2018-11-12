from plyfile import PlyData, PlyElement
import numpy

remove_all_vertices_above_sd_sigma_of = 1.5  # In Standard Deviation sigma. E.g. 1 means remove all vertices that are
#  above 68% of all vertex qualites, 2 means remove all above 95% ect. Defaul is 1.5 or 86%

pointcloud_with_outliers = PlyData.read('SOR_testfile.ply')

quality_list_with_statistical_outliers = pointcloud_with_outliers['vertex'].data['quality']


mean = numpy.mean(quality_list_with_statistical_outliers, axis= 0)
print("The mean of the vertex radius is: " + mean.__str__())
sd =  numpy.std(quality_list_with_statistical_outliers, axis= 0)
print ("The Standard Deviation of the vertex radius is: " + sd.__str__())

print("Removing all vertices above sigma of " + remove_all_vertices_above_sd_sigma_of.__str__())


list_of_vertices_without_SO = []


for index, x in enumerate(quality_list_with_statistical_outliers):
    if x < mean + remove_all_vertices_above_sd_sigma_of * sd:
        list_of_vertices_without_SO.append(pointcloud_with_outliers["vertex"][index])

print("Removed " + (len(quality_list_with_statistical_outliers) - len(list_of_vertices_without_SO)).__str__() + " outlier vertices")
print("Creating PLY file now")

vertex = numpy.array(list_of_vertices_without_SO, dtype=[('x', 'f4'), ('y', 'f4'), ('z', 'f4'), ('quality', 'f4'), ('radius', 'f4')])

new_ply_element = PlyElement.describe(vertex, "vertex")

PlyData([new_ply_element]).write("Temp_File_Without_Outliers.ply")
