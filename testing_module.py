from unscrew_logging import (MetadataCollector, SkillParameters, SkillOutput,
                             SensorStreams, UnscrewTestRecord, UnscrewLogger)

collector = MetadataCollector()
logger = UnscrewLogger(LogJSON.save_data_with_timestamp,
                       folder="robot_control/robot_unscrew_exp/unscrew_feedback/HDD_T8")

result = collector.collect()
parameters = SkillParameters(
    screw_engage_motor_speed_hz=screw_engage_motor_speed_hz,
    screw_engage_acceleration_hz_s2=screw_engage_acceleration_hz_s2,
    screw_engage_deceleration_hz_s2=screw_engage_deceleration_hz_s2,
    unscrew_motor_speed_hz=unscrew_motor_speed_hz,
    unscrew_acceleration_hz_s2=unscrew_acceleration_hz_s2,
    unscrew_deceleration_hz_s2=unscrew_deceleration_hz_s2,
    screw_engage_indentation_threshold_adc=screw_engage_indentation_threshold_adc,
    screw_engage_torque_threshold_torque_step=screw_engage_torque_threshold_torque_step,
    unscrew_raising_slope_threshold_adc=unscrew_raising_slope_threshold_adc,
    screw_engage_check_time_s=screw_engage_check_time_s,
    unscrew_end_max_time_s=unscrew_end_max_time_s,
    sensor_read_delay_s=sensor_read_delay_s,
    motor_torque_read_delay_s=motor_torque_read_delay_s,
    unscrew_slope_read_delay_s=unscrew_slope_read_delay_s,
    slope_update_delay_s=slope_update_delay_s,
)
output = SkillOutput(
    plot_t_start=_sensor_plot_t_start,
    engage_start_time=screw_engage_start_time, engage_end_time=screw_engage_end_time,
    unscrew_start_time=unscrew_start_time, unscrew_end_time=unscrew_end_time,
    initial_pot=initial_pot, max_engage_torque_Nm=max_engage_torque_Nm,
    max_engage_indentation_mm=max_engage_indentation_mm,
    torque_threshold_reached=torque_threshold_check,
    indentation_threshold_reached=indentation_threshold_check,
    raising_slope_threshold_reached=raising_slope_threshold_check,
    Nm_to_torque_step=Nm_to_torque_step_cov, mm_to_adc_count=mm_to_ADC_count_cov,
)
streams = SensorStreams(
    time_s=list(time_log), motor_torque=list(torque_log), position_sensor=list(pot_log),
    motor_speed=list(motor_speed_log), tcp_speed=list(tcp_speed_log),
    motor_position=list(motor_position_log), raising_slope=list(raising_slope_log),
    joint_torques_Nm=[list(l) for l in (robot_j1_torque_log, robot_j2_torque_log,
                      robot_j3_torque_log, robot_j4_torque_log,
                      robot_j5_torque_log, robot_j6_torque_log)],
)
logger.save(UnscrewTestRecord(result, parameters, output, streams))