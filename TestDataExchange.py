import sys
sys.path.insert(0, 'C:\EnergyPlusV22-1-0')
from pyenergyplus.api import EnergyPlusAPI

one_time_overwrite_weather = True
one_time_get_overwriten_weather = True
outdoor_temp_sensor = 0
outdoor_dry_bulb_actuator = 0


def overwrite_weather(state):
    global one_time_overwrite_weather, outdoor_dry_bulb_actuator
    sys.stdout.flush()
    if one_time_overwrite_weather:
        if api.exchange.api_data_fully_ready(state):
            # val = api.exchange.list_available_api_data_csv()
            # with open('/tmp/data.csv', 'w') as f:
            #     f.write(val.decode(encoding='utf-8'))
            outdoor_dry_bulb_actuator = api.exchange.get_actuator_handle(
                state, "Weather Data", "Site Outdoor Air Drybulb Temperature", "Environment"
            )
            if outdoor_temp_sensor == -1 or outdoor_dry_bulb_actuator == -1:
                sys.exit(1)
            one_time_overwrite_weather = False
    api.exchange.set_actuator_value(state, outdoor_dry_bulb_actuator, 35)
    sim_time = api.exchange.current_sim_time(state)
    print("Current sim time is: %f" % sim_time)

def get_overwriten_weather(state):
    global outdoor_temp_sensor, one_time_get_overwriten_weather
    if one_time_get_overwriten_weather:
        outdoor_temp_sensor = api.exchange.get_variable_handle(
            state, u"SITE OUTDOOR AIR DRYBULB TEMPERATURE", u"ENVIRONMENT"
        )
        one_time_get_overwriten_weather = False
    oa_temp = api.exchange.get_variable_value(state, outdoor_temp_sensor)
    print("Actuated outdoor temp value is: %s" % oa_temp)


api = EnergyPlusAPI()
state = api.state_manager.new_state()
api.runtime.callback_begin_zone_timestep_before_set_current_weather(state, overwrite_weather)
api.runtime.callback_end_system_timestep_after_hvac_reporting(state, get_overwriten_weather)
api.exchange.request_variable(state, "SITE OUTDOOR AIR DRYBULB TEMPERATURE", "ENVIRONMENT")
api.exchange.request_variable(state, "SITE OUTDOOR AIR DEWPOINT TEMPERATURE", "ENVIRONMENT")
# trim off this python script name when calling the run_energyplus function so you end up with just
# the E+ args, like: -d /output/dir -D /path/to/input.idf
import os
output_path = 'ep_outputs'
weather_file_path = 'USA_IL_Chicago-OHare.Intl.AP.725300_TMY3.epw'
idfFilePath = '5ZoneAirCooled.idf'
sys_args = '-d', output_path, '-w', weather_file_path, idfFilePath
api.runtime.run_energyplus(state, sys_args)
