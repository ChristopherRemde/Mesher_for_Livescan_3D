import xml.etree.ElementTree as ET

tree = ET.parse('SOR.mlx')
root = tree.getroot()

print(root.tag)




