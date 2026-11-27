from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

# from ..data_logging_module import LogJSON


# ---------------------------------------------------------------- prompting
class ConsolePrompter:

    def boolean(self, prompt: str) -> bool:
        while True:
            answer = input(prompt).strip().lower()
            if answer in ("y", "yes"):
                return True
            if answer in ("n", "no"):
                return False
            print("Invalid input. Please enter 'y' or 'n'.")

    def integer(self, prompt: str) -> int:
        while True:
            try:
                return int(input(prompt).strip())
            except ValueError:
                print("Invalid input. Please enter a valid whole number.")

    def non_empty_string(self, prompt: str) -> str:
        while True:
            value = input(prompt).strip()
            if value: 
                return value
            print("Input cannot be empty.")


# ------------------------------------------------------------------ catalogs
class CodeCatalog:

    def __init__(self, name: str, entries: dict[int, str], prompter: ConsolePrompter):
        self.name = name
        self._entries = entries
        self._prompter = prompter

    def describe(self, code: int) -> str:
        if code in self._entries:
            return self._entries[code]
        return self._prompter.non_empty_string(
            f"{self.name} {code} unknown. Enter description: "
        )

    def ask(self, prompt: str) -> tuple[int, str]:
        code = self._prompter.integer(prompt)
        return code, self.describe(code)


TOOL_CONDITIONS = {
    1: "new tool",
    2: "slight wear on tool",
    3: "high wear on tool",
    4: "slightly bent tool",
    5: "highly bent tool",
}

SCREW_TYPES = {1: "PH0", 2: "PH0", 3: "T6", 4: "T8", 5: "T10", 6: "T15"}

FAILURE_CAUSE = {
    1: "stripped screw head",
    2: "rusted screw",
    3: "missing screw",
    4: "cross-threaded screw",
    5: "screw position offset (non-flat surface)",
    6: "product displacement",
    7: "wrong screwdriver",
    8: "loose bit",
    9: "tangled tool",
    10: "obstructed screw head",
    11: "screw spinning in place",
    12: "previously loosened screw",
    13: "screw position offset (flat surface)",
    14: "high tool wear",
    15: "bent tool",
    99: "others",
}

ANOMALIES = {
    0: "None",
    1: "stripped screw head",
    2: "rusted screw",
    3: "missing screw",
    4: "cross-threaded screw",
    5: "screw position offset (non-flat surface)",
    6: "product displacement",
    7: "wrong screwdriver",
    8: "loose bit",
    9: "tangled tool",
    10: "obstructed screw head",
    11: "screw spinning in place",
    12: "previously loosened screw",
    13: "screw position offset (flat surface)",
    14: "high tool wear",
    15: "bent tool",
    99: "others",
}


# --------------------------------------------------------------- data classes
@dataclass
class UnscrewResult:
    tool_condition: str
    success: bool
    failure_code: int
    failure_reason: str
    anomalies_codes: list[int]
    anomalies_present: list[str]
    screw_type: str

    def to_dict(self) -> dict:
        return {
            "tool_condition": self.tool_condition,
            "success": self.success,
            "failure_code": self.failure_code,
            "anomalies_present_codes": self.anomalies_codes,
            "screw_type": self.screw_type,
        }


@dataclass
class SkillParameters:
    screw_engage_motor_speed_hz: float
    screw_engage_acceleration_hz_s2: float
    screw_engage_deceleration_hz_s2: float
    unscrew_motor_speed_hz: float
    unscrew_acceleration_hz_s2: float
    unscrew_deceleration_hz_s2: float
    screw_engage_indentation_threshold_adc: float
    screw_engage_torque_threshold_torque_step: float
    unscrew_raising_slope_threshold_adc: float
    screw_engage_check_time_s: float
    unscrew_end_max_time_s: float
    sensor_read_delay_s: float
    motor_torque_read_delay_s: float
    unscrew_slope_read_delay_s: float
    slope_update_delay_s: float
    # hardware description: constant, so defaults
    unscrew_motor: str = "Beckhoff AM8131-wJyz Servomotor 1.35 Nm, 1800 rpm"
    unscrew_gearbox: str = "AG2250 PLE60 M01-5"
    position_transmitter: str = "SDAT-MHS-M125-1L-SV-E-0.3-M8"

    def to_dict(self) -> dict:
        # explicit mapping: attribute -> original JSON key (keeps old logs comparable)
        keys = {
            "screw_engage_motor_speed_hz": "raw_screw_engage_motor_speed",
            "screw_engage_acceleration_hz_s2": "raw_screw_engage_acceleration",
            "screw_engage_deceleration_hz_s2": "raw_screw_engage_deceleration",
            "unscrew_motor_speed_hz": "raw_unscrew_motor_speed",
            "unscrew_acceleration_hz_s2": "raw_unscrew_acceleration",
            "unscrew_deceleration_hz_s2": "raw_unscrew_deceleration",
            "screw_engage_indentation_threshold_adc": "raw_screw_engage_indentation_threshold",
            "screw_engage_torque_threshold_torque_step": "raw_screw_engage_torque_threshold",
            "unscrew_raising_slope_threshold_adc": "raw_unscrew_raising_slope_threshold",
            "screw_engage_check_time_s": "screw_engage_check_time_s",
            "unscrew_end_max_time_s": "unscrew_end_max_time_s",
            "sensor_read_delay_s": "sensor_read_delay_s",
            "motor_torque_read_delay_s": "motor_torque_read_delay_s",
            "unscrew_slope_read_delay_s": "unscrew_slope_read_delay_s",
            "slope_update_delay_s": "slope_update_delay_s",
            "unscrew_motor": "Unscrew_Motor",
            "unscrew_gearbox": "Unscrew_Gearbox",
            "position_transmitter": "Position Trasnsmitter",
        }
        return {json_key: getattr(self, attr) for attr, json_key in keys.items()}


@dataclass
class SkillOutput:
    plot_t_start: float
    engage_start_time: Optional[float]
    engage_end_time: Optional[float]
    unscrew_start_time: Optional[float]
    unscrew_end_time: Optional[float]
    initial_pot: Optional[float]
    max_engage_torque_Nm: Optional[float]
    max_engage_indentation_mm: Optional[float]
    torque_threshold_reached: bool
    indentation_threshold_reached: bool
    raising_slope_threshold_reached: bool
    Nm_to_torque_step: float
    mm_to_adc_count: float

    def _rel(self, t: Optional[float]) -> Optional[float]:
        return None if t is None else t - self.plot_t_start

    @staticmethod
    def _scaled(value: Optional[float], factor: float) -> Optional[float]:
        return None if value is None else value * factor

    def to_dict(self) -> dict:
        return {
            "screw_engage_start_time_s": self._rel(self.engage_start_time),
            "screw_engage_end_time_s": self._rel(self.engage_end_time),
            "unscrew_start_time_s": self._rel(self.unscrew_start_time),
            "unscrew_end_time_s": self._rel(self.unscrew_end_time),
            "raw_initial_engage_indentation": self.initial_pot,
            "raw_max_engage_torque": self._scaled(self.max_engage_torque_Nm, self.Nm_to_torque_step),
            "raw_max_engage_indentation": self._scaled(self.max_engage_indentation_mm, self.mm_to_adc_count),
            "torque_threshold_reached": self.torque_threshold_reached,
            "indentation_threshold_reached": self.indentation_threshold_reached,
            "raising_slope_threshold_reached": self.raising_slope_threshold_reached,
        }


@dataclass
class SensorStreams:
    time_s: list[float]
    motor_torque: list[float]
    position_sensor: list[float]
    motor_speed: list[float]
    tcp_speed: list[float]
    motor_position: list[float]
    raising_slope: list[float]
    joint_torques_Nm: list[list[float]] = field(default_factory=list)  # [j1..j6][samples]

    def to_dict(self) -> dict:
        return {
            "unscrew_sensor_stream": {
                "time_s": self.time_s,
                "raw_motor_torque": self.motor_torque,
                "raw_position_sensor_value": self.position_sensor,
                "raw_motor_speed": self.motor_speed,
                "raw_tcp_speed": self.tcp_speed,
                "raw_motor_position": self.motor_position,
            },
            "unscrew_raising_slope_log": {"raw_unscrew_raising_slope": self.raising_slope},
            "robot_joint_torque_log": {
                f"robot_j{i}_torque_Nm": log
                for i, log in enumerate(self.joint_torques_Nm, start=1)
            },
        }


# ------------------------------------------------------------------- collector
class MetadataCollector:

    def __init__(self, prompter: Optional[ConsolePrompter] = None):
        self.prompter = prompter or ConsolePrompter()
        self.tool_conditions = CodeCatalog("Tool condition", TOOL_CONDITIONS, self.prompter)
        self.screw_types = CodeCatalog("Screw type", SCREW_TYPES, self.prompter)
        self.failure_causes = CodeCatalog("Failure code", FAILURE_CAUSE, self.prompter)
        self.anomalies = CodeCatalog("Anomaly code", ANOMALIES, self.prompter)

    def collect(self) -> UnscrewResult:
        success = self.prompter.boolean("Unscrew success (yes/no): ")
        _, tool_condition = self.tool_conditions.ask("tool condition: ")
        _, screw_type = self.screw_types.ask("screw type: ")

        if success:
            failure_code, failure_reason = 0, ""
        else:
            failure_code, failure_reason = self.failure_causes.ask("Failure cause code: ")

        codes, reasons = self._collect_anomalies()
        return UnscrewResult(tool_condition, success, failure_code, failure_reason,
                             codes, reasons, screw_type)

    def _collect_anomalies(self) -> tuple[list[int], list[str]]:
        codes: list[int] = []
        reasons: list[str] = []
        while True:
            raw = input("Anomalies present code (Enter to finish): ").strip()
            if raw == "":
                if codes:
                    return codes, reasons
                print("Enter at least one anomaly code.")
                continue
            try:
                code = int(raw)
            except ValueError:
                print("Invalid input. Please enter a valid whole number.")
                continue
            codes.append(code)
            reasons.append(self.anomalies.describe(code))


# ---------------------------------------------------------------------- record
@dataclass
class UnscrewTestRecord:
    result: UnscrewResult
    parameters: SkillParameters
    output: SkillOutput
    streams: SensorStreams

    def to_dict(self) -> dict:
        return {
            "unscrew_test_result": self.result.to_dict(),
            "unscrew_skill_input_information": self.parameters.to_dict(),
            "unscrew_skill_output_information": self.output.to_dict(),
            **self.streams.to_dict(),
        }


# ---------------------------------------------------------------------- logger
# class UnscrewLogger:
# 
#     def __init__(self, saver: Callable[..., str], folder: str, prefix: str = "HDD_T8"):
#         self._saver = saver
#         self._folder = folder
#         self._prefix = prefix

#     def save(self, record: UnscrewTestRecord) -> str:
#         label = "success" if record.result.success else "failure"
#         return self._saver(
#             record.to_dict(),
#             relative_folder_path=self._folder,
#             file_name_prefix=f"{self._prefix}_{label}_{record.result.failure_code}",
#         )

