from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    ld = LaunchDescription()

    factomove_description_package = FindPackageShare('factomove_description')
    
    ld.add_action(IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('urdf_launch'), 'launch', 'display.launch.py']),
        launch_arguments={
            'urdf_package': 'factomove_description',
            'urdf_package_path': PathJoinSubstitution(['urdf', 'factomove.urdf.xacro']),
            'rviz_config': PathJoinSubstitution([factomove_description_package, 'config', 'factomove.rviz'])}.items()   
    ))
    
    return ld