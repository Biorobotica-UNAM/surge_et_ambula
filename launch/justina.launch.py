#!/usr/bin/env python3
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import AnyLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    # === Generic arguments ===
    namespace = DeclareLaunchArgument(
        'namespace',
        default_value='hardware/robotino',
        description='Top-level namespace for the hardware and navigation stack'
    )

    use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use /clock if true'
    )

    use_nav = DeclareLaunchArgument(
        'use_nav',
        default_value='true',
        description='Launch navigation stack'
    )

    # === Hardware launch (hardware_tools/hardware.launch.xml) ===
    hardware_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('hardware_tools'),
                'launch',
                'hardware.launch.xml'
            )
        ),
        launch_arguments={
            'namespace':   LaunchConfiguration('namespace'),
            # Si tu hardware.launch.xml tiene más args (use_sim_time, etc.),
            # también los puedes pasar aquí:
            # 'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items()
    )

    # === Navigation launch (navigation_tools/navigation.launch.xml) ===
    navigation_launch = IncludeLaunchDescription(
        AnyLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('navigation_tools'),
                'launch',
                'navigation.launch.xml'
            )
        ),
        launch_arguments={
            'namespace':   LaunchConfiguration('namespace'),
            'use_sim_time': LaunchConfiguration('use_sim_time'),
        }.items(),
        condition=IfCondition(LaunchConfiguration('use_nav'))
    )

    # === RViz2 launch ===
    rviz_config = os.path.join(
        get_package_share_directory('surge_et_ambula'),
        'rviz',
        'justina.rviz'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )

    return LaunchDescription([
        namespace,
        use_sim_time,
        use_nav,
        hardware_launch,
        navigation_launch,
        rviz_node
    ])
