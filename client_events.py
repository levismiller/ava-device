import json

class ClientEvents(object):

    def __init__(self, mqtt):
        self.mqtt = mqtt

    def event(self, evt):
        print(f'event {evt} {type(evt)}')
        if str(evt) == 'alarm::off':
            return self.turn_alarm_off(evt)
        elif str(evt) == 'alarm::snooze':
            return self.snooze_alarm(evt)
        else:
            print(f'evt not found {evt}')

    def turn_alarm_off(self, evt):
        # do things to actually turn the alarm off
        self.mqtt.publish_event(evt, True)
        return self.__build_ws_resp(evt, True)
        
    def snooze_alarm(self, evt):
        # do things to actually snooze the alarm
        self.mqtt.publish_event(evt, True)
        return self.__build_ws_resp(evt, True)

    def __build_ws_resp(self, evt, success):
        return json.dumps({
            "evt": evt,
            "success": success,
        })
