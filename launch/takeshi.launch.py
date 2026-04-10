#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    GroupAction,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.conditions import IfCondition
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # =====================
    #   Launch arguments
    # =====================
    use_sim_time = LaunchConfiguration('use_sim_time')

    namespace_supervisor   = LaunchConfiguration('namespace_supervisor')
    namespace_executor     = LaunchConfiguration('namespace_executor')
    namespace_planning     = LaunchConfiguration('namespace_planning')
    namespace_navigation   = LaunchConfiguration('namespace_navigation')
    namespace_manipulation = LaunchConfiguration('namespace_manipulation')
    namespace_hardware     = LaunchConfiguration('namespace_hardware')
    namespace_hri          = LaunchConfiguration('namespace_hri')
    namespace_vision       = LaunchConfiguration('namespace_vision')
    namespace_tasks        = LaunchConfiguration('namespace_tasks')

    use_nav = LaunchConfiguration('use_nav')
    use_takeshi = LaunchConfiguration('use_takeshi')

    # Delays entre etapas
    delay_nav    = LaunchConfiguration('delay_nav')
    delay_hri    = LaunchConfiguration('delay_hri')
    delay_vision = LaunchConfiguration('delay_vision')
    delay_tasks  = LaunchConfiguration('delay_tasks')
    delay_rviz   = LaunchConfiguration('delay_rviz')

    # =====================
    #   Package shares
    # =====================
    supervisor_pkg  = FindPackageShare('supervisor_manager')
    executor_pkg    = FindPackageShare('executor_tools')
    planning_pkg    = FindPackageShare('planning_tools')
    navigation_pkg  = FindPackageShare('navigation_start')
    hardware_pkg    = FindPackageShare('hardware_tools')
    hri_pkg         = FindPackageShare('hri_tools')
    human_follower_pkg = FindPackageShare('human_follower')
    vision_pkg      = FindPackageShare('vision_tools')
    surge_pkg       = FindPackageShare('surge_et_ambula')

    # =====================
    #   Stage 1: Core/base
    # =====================
    stage_core = GroupAction([
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([supervisor_pkg, 'launch', 'supervisor.launch.xml'])
            ),
            launch_arguments={
                'namespace': namespace_supervisor,
            }.items()
        ),

        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([executor_pkg, 'launch', 'executor.launch.xml'])
            ),
            launch_arguments={
                'namespace': namespace_executor,
            }.items()
        ),

        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([planning_pkg, 'launch', 'planning.launch.xml'])
            ),
            launch_arguments={
                'namespace': namespace_planning,
                'use_sim_time': use_sim_time,
            }.items()
        ),

        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([hardware_pkg, 'launch', 'hardware.launch.xml'])
            ),
            launch_arguments={
                'namespace': namespace_hardware,
                'use_takeshi': use_takeshi,
            }.items()
        ),
    ])

    # =====================
    #   Stage 2: Navigation
    # =====================
    stage_navigation = GroupAction([
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([navigation_pkg, 'launch', 'navigation_takeshi.launch.xml'])
            ),
            condition=IfCondition(use_nav),
            launch_arguments={
                'namespace_nav': namespace_navigation,
                'use_sim_time': use_sim_time,
            }.items()
        ),

        Node(
            package='locations_manager',
            executable='locations_manager_node',
            name='locations_manager_node',
            output='screen'
        ),

        Node(
            package='nav_controller',
            executable='nav_controller_node',
            name='nav_controller_node',
            output='screen'
        ),
    ])

    # =====================
    #   Stage 3: HRI/human
    # =====================
    stage_hri = GroupAction([
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([hri_pkg, 'launch', 'hri.launch.xml'])
            ),
            launch_arguments={
                'namespace': namespace_hri,
                'use_takeshi': use_takeshi,
            }.items()
        ),

        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([hri_pkg, 'launch', 'human_detector.launch.xml'])
            )
        ),

        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([human_follower_pkg, 'launch', 'human_follower.launch.xml'])
            )
        ),
    ])

    # =====================
    #   Stage 4: Vision
    # =====================
    stage_vision = GroupAction([
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([vision_pkg, 'launch', 'vision.launch.xml'])
            ),
            launch_arguments={
                'namespace': namespace_vision,
            }.items()
        ),
    ])

    # =====================
    #   Stage 5: Tasks
    # =====================
    stage_tasks = GroupAction([
        IncludeLaunchDescription(
            AnyLaunchDescriptionSource(
                PathJoinSubstitution([executor_pkg, 'launch', 'tasks.launch.xml'])
            ),
            launch_arguments={
                'namespace': namespace_tasks,
            }.items()
        ),
    ])

    # =====================
    #   Stage 6: RViz
    # =====================
    stage_rviz = GroupAction([
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=[
                '-d',
                PathJoinSubstitution([surge_pkg, 'rviz', 'justina.rviz'])
            ],
            remappings=[
                ('/hardware/base/robot_description', '/robot_description')
            ]
        ),
    ])

    # =====================
    #   LaunchDescription
    # =====================
    return LaunchDescription([
        # Arguments
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        DeclareLaunchArgument('use_takeshi', default_value='true'),

        DeclareLaunchArgument('namespace_supervisor',   default_value='supervisor'),
        DeclareLaunchArgument('namespace_executor',     default_value='executor'),
        DeclareLaunchArgument('namespace_planning',     default_value='planning'),
        DeclareLaunchArgument('namespace_navigation',   default_value='navigation'),
        DeclareLaunchArgument('namespace_manipulation', default_value='manipulation'),
        DeclareLaunchArgument('namespace_hardware',     default_value='hardware'),
        DeclareLaunchArgument('namespace_hri',          default_value='hri'),
        DeclareLaunchArgument('namespace_vision',       default_value='vision'),
        DeclareLaunchArgument('namespace_tasks',        default_value='tasks'),

        DeclareLaunchArgument('use_nav', default_value='true'),

        # Delays ajustables
        DeclareLaunchArgument('delay_nav',    default_value='3.0'),
        DeclareLaunchArgument('delay_hri',    default_value='6.0'),
        DeclareLaunchArgument('delay_vision', default_value='8.0'),
        DeclareLaunchArgument('delay_tasks',  default_value='10.0'),
        DeclareLaunchArgument('delay_rviz',   default_value='12.0'),

        # Etapa 1: inmediata
        stage_core,

        # Etapas siguientes: escalonadas
        TimerAction(
            period=delay_nav,
            actions=[stage_navigation]
        ),

        TimerAction(
            period=delay_hri,
            actions=[stage_hri]
        ),

        TimerAction(
            period=delay_vision,
            actions=[stage_vision]
        ),

        TimerAction(
            period=delay_tasks,
            actions=[stage_tasks]
        ),

        TimerAction(
            period=delay_rviz,
            actions=[stage_rviz]
        ),
    ])