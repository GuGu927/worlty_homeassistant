"""Constants for the Worlty integration."""

from __future__ import annotations

from enum import Enum
import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorDeviceClass
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.switch import SwitchDeviceClass
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
    PERCENTAGE,
    POWER_VOLT_AMPERE_REACTIVE,
    Platform,
    UnitOfApparentPower,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfVolume,
    UnitOfVolumeFlowRate,
)

DOMAIN = "worlty"
MANUFACTURER = "Worlty"

LOGGER = logging.getLogger(__package__)


class WorltyBaseType(Enum):
    """Worlty entity type."""

    BINARY_SENSOR = 1
    SENSOR = 2
    LIGHT = 3
    SWITCH = 4
    EVENT = 5
    FAN = 6
    INPUT = 7
    CLIMATE = 8
    COVER = 9


def map_worlty_state(lang, state) -> Any:
    """Map for worlty sub id."""
    return {
        "en": {
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "auto": "Auto",
            "weak": "Weak",
            "boost": "Boost",
            "eco": "Eco",
            "arrive": "Arrive",
            "call": "Call",
            "detect": "Detect",
            "down": "Down",
            "idle": "idle",
            "left": "Left",
            "move": "Move",
            "open": "Open",
            "right": "Right",
            "ring": "Ring",
            "up": "Up",
            "wait": "Wait",
        },
        "ko": {
            "high": "강",
            "medium": "중",
            "low": "약",
            "auto": "자동",
            "weak": "최저",
            "boost": "최고",
            "eco": "절전",
            "arrive": "도착",
            "call": "통화",
            "detect": "감지",
            "down": "아래쪽",
            "idle": "대기",
            "left": "왼쪽",
            "move": "이동",
            "open": "열기",
            "right": "오른쪽",
            "ring": "벨소리",
            "up": "위쪽",
            "wait": "기다림",
        },
    }.get(lang, {}).get(state, state)


def map_worlty_sub(lang, sub_id) -> str:
    """Map for worlty sub id."""
    return {
        "en": {
            "ctrl_mode": "Controller Mode",
            "ctrl_speed": "Controller Speed",
            "target_speed": "Worlty Speed",
            "blr-err": "Boiler Error",
            "front": "Front of Door",
            "event": "Event",
            "cook": "GasValve",
            "bell": "Bell",
            "direction": "Elevator Direction",
            "floor": "Elevator Floor",
            "location": "Location",
            "apt-0": "APT Gate",
            "apt-1": "APT Gate(book)",
            "home-0": "Home Gate",
            "home-1": "Home Gate(book)",
        },
        "ko": {
            "ctrl_mode": "리모컨모드",
            "ctrl_speed": "리모컨속도",
            "target_speed": "월티속도",
            "blr-err": "보일러에러",
            "front": "현관앞",
            "event": "이벤트",
            "cook": "가스밸브",
            "bell": "초인종",
            "direction": "엘리베이터 방향",
            "floor": "엘리베이터 층",
            "location": "위치",
            "apt-0": "공동현관",
            "apt-1": "공동현관(예약)",
            "home-0": "세대현관",
            "home-1": "세대현관(예약)",
        },
    }.get(lang, {}).get(sub_id, sub_id)


def map_worlty_to_platform(worlty_type, worlty_class) -> str:
    """Map for Worlty type to Platform."""
    mapping = {
        WorltyBaseType.BINARY_SENSOR.value: Platform.BINARY_SENSOR.value,
        WorltyBaseType.CLIMATE.value: Platform.CLIMATE.value,
        WorltyBaseType.COVER.value: Platform.COVER.value,
        WorltyBaseType.EVENT.value: Platform.SENSOR.value,
        WorltyBaseType.FAN.value: Platform.FAN.value,
        WorltyBaseType.LIGHT.value: Platform.LIGHT.value,
        WorltyBaseType.SENSOR.value: Platform.SENSOR.value,
        WorltyBaseType.SWITCH.value: Platform.SWITCH.value,
    }
    ha_type = mapping.get(worlty_type)
    if worlty_type == WorltyBaseType.CLIMATE.value and worlty_class == 1:
        ha_type = Platform.WATER_HEATER.value
    return ha_type


def get_worlty_description(worlty_device_type: int, worlty_device_class: int) -> tuple:
    """Map for Worlty name to entity name."""
    # key, device_class, icon, unit_of_measurement
    unknown = (None, None, None, None)
    descriptions = {
        WorltyBaseType.BINARY_SENSOR.value: {
            0: ("binary_sensor", None, None, None),
            1: (
                BinarySensorDeviceClass.BATTERY.value,
                BinarySensorDeviceClass.BATTERY,
                None,
                None,
            ),
            2: (
                BinarySensorDeviceClass.BATTERY_CHARGING.value,
                BinarySensorDeviceClass.BATTERY_CHARGING,
                None,
                None,
            ),
            3: (
                BinarySensorDeviceClass.CO.value,
                BinarySensorDeviceClass.CO,
                None,
                None,
            ),
            4: (
                BinarySensorDeviceClass.COLD.value,
                BinarySensorDeviceClass.COLD,
                None,
                None,
            ),
            5: (
                BinarySensorDeviceClass.CONNECTIVITY.value,
                BinarySensorDeviceClass.CONNECTIVITY,
                None,
                None,
            ),
            6: (
                BinarySensorDeviceClass.DOOR.value,
                BinarySensorDeviceClass.DOOR,
                None,
                None,
            ),
            7: (
                "error",
                BinarySensorDeviceClass.PROBLEM,
                None,
                None,
            ),
            8: (
                "filter",
                BinarySensorDeviceClass.PROBLEM,
                None,
                None,
            ),
            9: (
                "fire",
                BinarySensorDeviceClass.SAFETY,
                None,
                None,
            ),
            10: (
                BinarySensorDeviceClass.GARAGE_DOOR.value,
                BinarySensorDeviceClass.GARAGE_DOOR,
                None,
                None,
            ),
            11: (
                BinarySensorDeviceClass.GAS.value,
                BinarySensorDeviceClass.GAS,
                None,
                None,
            ),
            12: (
                BinarySensorDeviceClass.HEAT.value,
                BinarySensorDeviceClass.HEAT,
                None,
                None,
            ),
            13: (
                BinarySensorDeviceClass.LIGHT.value,
                BinarySensorDeviceClass.LIGHT,
                None,
                None,
            ),
            14: (
                BinarySensorDeviceClass.LOCK.value,
                BinarySensorDeviceClass.LOCK,
                None,
                None,
            ),
            15: (
                BinarySensorDeviceClass.MOISTURE.value,
                BinarySensorDeviceClass.MOISTURE,
                None,
                None,
            ),
            16: (
                BinarySensorDeviceClass.MOTION.value,
                BinarySensorDeviceClass.MOTION,
                None,
                None,
            ),
            17: (
                BinarySensorDeviceClass.MOVING.value,
                BinarySensorDeviceClass.MOVING,
                None,
                None,
            ),
            18: (
                BinarySensorDeviceClass.OCCUPANCY.value,
                BinarySensorDeviceClass.OCCUPANCY,
                None,
                None,
            ),
            19: (
                BinarySensorDeviceClass.OPENING.value,
                BinarySensorDeviceClass.OPENING,
                None,
                None,
            ),
            20: (
                BinarySensorDeviceClass.PLUG.value,
                BinarySensorDeviceClass.PLUG,
                None,
                None,
            ),
            21: (
                BinarySensorDeviceClass.POWER.value,
                BinarySensorDeviceClass.POWER,
                None,
                None,
            ),
            22: (
                BinarySensorDeviceClass.PRESENCE.value,
                BinarySensorDeviceClass.PRESENCE,
                None,
                None,
            ),
            23: (
                BinarySensorDeviceClass.PROBLEM.value,
                BinarySensorDeviceClass.PROBLEM,
                None,
                None,
            ),
            24: (
                BinarySensorDeviceClass.RUNNING.value,
                BinarySensorDeviceClass.RUNNING,
                None,
                None,
            ),
            25: (
                BinarySensorDeviceClass.SAFETY.value,
                BinarySensorDeviceClass.SAFETY,
                None,
                None,
            ),
            26: (
                BinarySensorDeviceClass.SMOKE.value,
                BinarySensorDeviceClass.SMOKE,
                None,
                None,
            ),
            27: (
                BinarySensorDeviceClass.SOUND.value,
                BinarySensorDeviceClass.SOUND,
                None,
                None,
            ),
            28: (
                BinarySensorDeviceClass.TAMPER.value,
                BinarySensorDeviceClass.TAMPER,
                None,
                None,
            ),
            29: (
                BinarySensorDeviceClass.UPDATE.value,
                BinarySensorDeviceClass.UPDATE,
                None,
                None,
            ),
            30: (
                BinarySensorDeviceClass.VIBRATION.value,
                BinarySensorDeviceClass.VIBRATION,
                None,
                None,
            ),
            31: (
                BinarySensorDeviceClass.WINDOW.value,
                BinarySensorDeviceClass.WINDOW,
                None,
                None,
            ),
            32: (
                "guard",
                BinarySensorDeviceClass.SAFETY,
                None,
                None,
            ),
        },
        WorltyBaseType.CLIMATE.value: {
            1: ("boiler", None, None, None),
            2: ("ac", None, None, None),
        },
        WorltyBaseType.EVENT.value: {
            0: ("event", None, None, None),
            1: ("event_uss", None, None, None),
        },
        WorltyBaseType.FAN.value: {
            0: ("fan", None, None, None),
            1: ("sysclein", None, None, None),
            2: ("airone", None, None, None),
        },
        WorltyBaseType.LIGHT.value: {
            0: ("light", None, None, None),
            1: ("dimming", None, None, None),
        },
        WorltyBaseType.SENSOR.value: {
            0: ("sensor", None, None, None),
            1: (
                SensorDeviceClass.APPARENT_POWER.value,
                SensorDeviceClass.APPARENT_POWER,
                None,
                UnitOfApparentPower.VOLT_AMPERE,
            ),
            2: (
                SensorDeviceClass.AQI.value,
                SensorDeviceClass.AQI,
                None,
                None,
            ),
            3: (
                SensorDeviceClass.ATMOSPHERIC_PRESSURE.value,
                SensorDeviceClass.ATMOSPHERIC_PRESSURE,
                None,
                UnitOfPressure.HPA,
            ),
            4: (
                SensorDeviceClass.BATTERY.value,
                SensorDeviceClass.BATTERY,
                None,
                PERCENTAGE,
            ),
            5: (
                SensorDeviceClass.CO2.value,
                SensorDeviceClass.CO2,
                None,
                CONCENTRATION_PARTS_PER_MILLION,
            ),
            6: (
                SensorDeviceClass.CO.value,
                SensorDeviceClass.CO,
                None,
                CONCENTRATION_PARTS_PER_MILLION,
            ),
            7: (
                SensorDeviceClass.CURRENT.value,
                SensorDeviceClass.CURRENT,
                None,
                None,
            ),
            8: (
                SensorDeviceClass.DATA_RATE.value,
                SensorDeviceClass.DATA_RATE,
                None,
                None,
            ),
            9: (
                SensorDeviceClass.DATA_SIZE.value,
                SensorDeviceClass.DATA_SIZE,
                None,
                None,
            ),
            10: (
                SensorDeviceClass.DATE.value,
                SensorDeviceClass.DATE,
                None,
                None,
            ),
            11: (
                SensorDeviceClass.DISTANCE.value,
                SensorDeviceClass.DISTANCE,
                None,
                None,
            ),
            12: (
                SensorDeviceClass.DURATION.value,
                SensorDeviceClass.DURATION,
                None,
                None,
            ),
            13: (
                SensorDeviceClass.ENERGY.value,
                SensorDeviceClass.ENERGY,
                None,
                UnitOfEnergy.KILO_WATT_HOUR,
            ),
            14: (
                SensorDeviceClass.ENUM.value,
                SensorDeviceClass.ENUM,
                None,
                None,
            ),
            15: (
                "floor",
                None,
                "mdi:elevator",
                None,
            ),
            16: (
                SensorDeviceClass.FREQUENCY.value,
                SensorDeviceClass.FREQUENCY,
                None,
                None,
            ),
            17: (
                SensorDeviceClass.GAS.value,
                SensorDeviceClass.GAS,
                None,
                UnitOfVolume.CUBIC_METERS,
            ),
            18: (
                "heat",
                SensorDeviceClass.VOLUME_FLOW_RATE,
                None,
                UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
            ),
            19: (
                "hotwater",
                SensorDeviceClass.VOLUME_FLOW_RATE,
                None,
                UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
            ),
            20: (
                SensorDeviceClass.HUMIDITY.value,
                SensorDeviceClass.HUMIDITY,
                None,
                PERCENTAGE,
            ),
            21: (
                SensorDeviceClass.ILLUMINANCE.value,
                SensorDeviceClass.ILLUMINANCE,
                None,
                LIGHT_LUX,
            ),
            22: (
                SensorDeviceClass.IRRADIANCE.value,
                SensorDeviceClass.IRRADIANCE,
                None,
                None,
            ),
            23: (
                SensorDeviceClass.MOISTURE.value,
                SensorDeviceClass.MOISTURE,
                None,
                PERCENTAGE,
            ),
            24: (
                SensorDeviceClass.MONETARY.value,
                SensorDeviceClass.MONETARY,
                None,
                None,
            ),
            25: (
                SensorDeviceClass.NITROGEN_DIOXIDE.value,
                SensorDeviceClass.NITROGEN_DIOXIDE,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            26: (
                SensorDeviceClass.NITROGEN_MONOXIDE.value,
                SensorDeviceClass.NITROGEN_MONOXIDE,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            27: (
                SensorDeviceClass.NITROUS_OXIDE.value,
                SensorDeviceClass.NITROUS_OXIDE,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            28: (
                SensorDeviceClass.OZONE.value,
                SensorDeviceClass.OZONE,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            29: (
                "percentage",
                None,
                "mdi:percent",
                PERCENTAGE,
            ),
            30: (
                SensorDeviceClass.PM1.value,
                SensorDeviceClass.PM1,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            31: (
                SensorDeviceClass.PM10.value,
                SensorDeviceClass.PM10,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            32: (
                SensorDeviceClass.PM25.value,
                SensorDeviceClass.PM25,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            33: (
                SensorDeviceClass.POWER_FACTOR.value,
                SensorDeviceClass.POWER_FACTOR,
                None,
                PERCENTAGE,
            ),
            34: (
                SensorDeviceClass.POWER.value,
                SensorDeviceClass.POWER,
                None,
                UnitOfPower.WATT,
            ),
            35: (
                SensorDeviceClass.PRECIPITATION.value,
                SensorDeviceClass.PRECIPITATION,
                None,
                UnitOfPrecipitationDepth.MILLIMETERS,
            ),
            36: (
                SensorDeviceClass.PRECIPITATION_INTENSITY.value,
                SensorDeviceClass.PRECIPITATION_INTENSITY,
                None,
                None,
            ),
            37: (
                SensorDeviceClass.PRESSURE.value,
                SensorDeviceClass.PRESSURE,
                None,
                UnitOfPressure.HPA,
            ),
            38: (
                SensorDeviceClass.REACTIVE_POWER.value,
                SensorDeviceClass.REACTIVE_POWER,
                None,
                POWER_VOLT_AMPERE_REACTIVE,
            ),
            39: (
                SensorDeviceClass.SIGNAL_STRENGTH.value,
                SensorDeviceClass.SIGNAL_STRENGTH,
                None,
                None,
            ),
            40: (
                SensorDeviceClass.SOUND_PRESSURE.value,
                SensorDeviceClass.SOUND_PRESSURE,
                None,
                None,
            ),
            41: (
                SensorDeviceClass.SPEED.value,
                SensorDeviceClass.SPEED,
                None,
                None,
            ),
            42: (
                "string",
                None,
                "mdi:format-text",
                None,
            ),
            43: (
                SensorDeviceClass.SULPHUR_DIOXIDE.value,
                SensorDeviceClass.SULPHUR_DIOXIDE,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            44: (
                SensorDeviceClass.TEMPERATURE.value,
                SensorDeviceClass.TEMPERATURE,
                None,
                UnitOfTemperature.CELSIUS,
            ),
            45: (
                SensorDeviceClass.TIMESTAMP.value,
                SensorDeviceClass.TIMESTAMP,
                None,
                None,
            ),
            46: (
                SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS.value,
                SensorDeviceClass.VOLATILE_ORGANIC_COMPOUNDS,
                None,
                CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
            ),
            47: (
                SensorDeviceClass.VOLTAGE.value,
                SensorDeviceClass.VOLTAGE,
                None,
                UnitOfElectricPotential.VOLT,
            ),
            48: (
                SensorDeviceClass.VOLUME.value,
                SensorDeviceClass.VOLUME,
                None,
                None,
            ),
            49: (
                SensorDeviceClass.WATER.value,
                SensorDeviceClass.VOLUME_FLOW_RATE,
                None,
                UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
            ),
            50: (
                "weather",
                None,
                None,
                None,
            ),
            51: (
                SensorDeviceClass.WEIGHT.value,
                SensorDeviceClass.WEIGHT,
                None,
                None,
            ),
            52: (
                SensorDeviceClass.WIND_SPEED.value,
                SensorDeviceClass.WIND_SPEED,
                None,
                UnitOfSpeed.METERS_PER_SECOND,
            ),
            53: (
                "multisensor",
                None,
                None,
                None,
            ),
        },
        WorltyBaseType.SWITCH.value: {
            0: (
                SwitchDeviceClass.SWITCH.value,
                SwitchDeviceClass.SWITCH,
                None,
                None,
            ),
            1: (
                SwitchDeviceClass.OUTLET.value,
                SwitchDeviceClass.OUTLET,
                None,
                None,
            ),
            2: (
                "valve",
                SwitchDeviceClass.SWITCH,
                "mdi:pipe-valve",
                None,
            ),
            3: (
                "open",
                SwitchDeviceClass.SWITCH,
                "mdi:lock-open",
                None,
            ),
            4: (
                "lock",
                SwitchDeviceClass.SWITCH,
                "mdi:lock",
                None,
            ),
            5: (
                "cook",
                SwitchDeviceClass.SWITCH,
                "mdi:chef-hat",
                None,
            ),
            6: (
                "elevator",
                SwitchDeviceClass.SWITCH,
                "mdi:elevator",
                None,
            ),
            7: (
                "interphone",
                SwitchDeviceClass.SWITCH,
                "mdi:phone",
                None,
            ),
        },
    }.get(worlty_device_type, {})
    return descriptions.get(worlty_device_class, unknown)
