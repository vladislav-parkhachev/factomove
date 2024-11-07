import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import SetEnvironmentVariable
from pathlib import Path

from launch_ros.actions import Node
import xacro

def generate_launch_description():

    robotXacroName = 'factomove'

    namePackageDescription = 'factomove_description'

    namePackageSimulations = 'factomove_simulations'

    modelFileRelativePath = 'urdf/factomove.urdf.xacro'

    pathModelFile = os.path.join(get_package_share_directory(namePackageDescription), modelFileRelativePath)

    robotDescription = xacro.process_file(pathModelFile).toxml()

    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py'))
    
    gazeboLaunch = IncludeLaunchDescription(gazebo_rosPackageLaunch, launch_arguments={'gz_args': ['-r -v -v4 empty.sdf'], 'on_exit_shutdown': 'true'}.items())

    spawnModelNodeGazebo = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', robotXacroName,
            '-topic', 'robot_description'
        ],
        output='screen'
    )

    factomove_description_path = os.path.join(get_package_share_directory('factomove_description'))

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

    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description' : robotDescription, 'use_sim_time' : True}]
    )
    
    bridge_params = os.path.join(get_package_share_directory(namePackageSimulations), 'parameters', 'bridge_parameters.yaml')

    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            "/cmd_vel" + "@geometry_msgs/msg/Twist" + "]gz.msgs.Twist",
        ],
        output='screen'
    )

    factomove_description_path = os.path.join(get_package_share_directory('factomove_description'))

    gazebo_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            str(Path(factomove_description_path).parent.resolve())
            ]
    )
    
    launchDescriptionObject = LaunchDescription()

    launchDescriptionObject.add_action(gazebo_resource_path)
    launchDescriptionObject.add_action(gazeboLaunch)
    launchDescriptionObject.add_action(start_gazebo_ros_spawner_cmd)
    # launchDescriptionObject.add_action(spawnModelNodeGazebo)    
    launchDescriptionObject.add_action(nodeRobotStatePublisher)
    launchDescriptionObject.add_action(start_gazebo_ros_bridge_cmd)
    
    return launchDescriptionObject