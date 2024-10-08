import os
import xacro
from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.actions import SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    ld = LaunchDescription()

    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'))

    gazeboLaunch = IncludeLaunchDescription(gazebo_rosPackageLaunch, 
                    launch_arguments={'gz_args': ['-r -v -v4 empty.sdf'], 'on_exit_shutdown': 'true'}.items())
    
    factomove_description_path = os.path.join(get_package_share_directory('factomove_description'))

    gazebo_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            str(Path(factomove_description_path).parent.resolve())
            ]
        )

    xacro_file = os.path.join(factomove_description_path, 'urdf', 'factomove.urdf.xacro')

    doc = xacro.process_file(xacro_file, mappings={'use_sim' : 'true'})

    robot_desc = doc.toprettyxml(indent='  ')

    params = {'robot_description': robot_desc}

    start_gazebo_ros_spawner_cmd = Node(
    package='ros_gz_sim',
    executable='create',
    arguments=[
        '-name', 'factomove',
        '-string', robot_desc,
        '-x', '0.0',
        '-y', '0.0',
        '-z', '0.01'
    ],
    output='screen',
)

    ld.add_action(gazebo_resource_path)
    ld.add_action(gazeboLaunch)
    ld.add_action(start_gazebo_ros_spawner_cmd)
    
    return ld