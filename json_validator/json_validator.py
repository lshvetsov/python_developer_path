import json
import re
import sys
from collections import Counter

class EasyRiderValidator:

    """
    This class validates bus stop data including types, required fields, and time sequences.
    It also provides a report of all bus stops with specifics on errors and stop categorizations.
    """

    def __init__(self):
        self._initialize()

    def reset(self):
        """
        Public method to reset all instance variables to their initial state, useful
        for reinitializing an object without having to create a new one.
        """
        self._initialize()

    def _initialize(self):
        """
        Helper method to initialize or reset the attributes to default values.
        """
        self.bus_lines = dict()
        self.all_stops_by_type = {'S': set(), 'O': set(), 'F': set(), '': set()}
        self.err_count = dict(
            bus_id=0,
            stop_id=0,
            stop_name=0,
            next_stop=0,
            stop_type=0,
            a_time=0
        )
        self.key_type = dict(
            bus_id=int,
            stop_id=int,
            stop_name=str,
            next_stop=int,
            stop_type=str,
            a_time=str
        )
        self.allow_empty = dict(
            bus_id=False,
            stop_id=True,
            stop_name=False,
            next_stop=True,
            stop_type=True,
            a_time=False
        )
        self.value_choice = dict(
            bus_id=None,
            stop_id=None,
            stop_name=None,
            next_stop=None,
            stop_type=['', 'S', 'O', 'F'],
            a_time=None
        )
        self.value_format = dict(
            bus_id=None,
            stop_id=None,
            stop_name=r'^[A-Z][a-z]*(?:\s[A-Z][a-z]*)*\s(?:Road|Avenue|Boulevard|Street)$',
            next_stop=None,
            stop_type=None,
            a_time=r'^([01][0-9]|2[0-3]):([0-5][0-9])$'
        )

    def validate(self, input_json):
        """
        Validate input JSON data against predefined types, formats, and orders of times.
        Accumulate error counts and data categorization as per bus ids and stop types.

        Args:
            input_json (list of dict): A JSON list of dictionaries each holding bus stop information.
        """
        previous_bus_id = None
        previous_time = None
        time_errors = dict()

        for item in input_json:
            if not isinstance(item, dict):
                continue

            self.__apply_rules_per_field(item)

            # populate data structures for printing result
            bus_id = item.get('bus_id')
            stop_type = item.get('stop_type') if item.get('stop_type') in ['S', 'O', 'F', ''] else ''
            time = item.get('a_time')

            self.all_stops_by_type[stop_type].add(item.get('stop_name'))

            if bus_id:
                if bus_id not in self.bus_lines:
                    self.bus_lines[bus_id] = {'S': set(), 'O': set(), 'F': set(), '': set()}
                self.bus_lines[bus_id][stop_type].add(item.get('stop_name'))
                if bus_id not in time_errors:
                    time_errors[bus_id] = (False, time)

            self.__check_time_linearity(bus_id, time, time_errors)

        self.__print_result()

    def __apply_rules_per_field(self, item):
        for k, v in item.items():
            if any([
                not isinstance(v, self.key_type.get(k)),
                not v and not self.allow_empty.get(k),
                self.value_choice.get(k) and v not in self.value_choice.get(k),
                self.value_format.get(k) and not re.match(self.value_format.get(k), v)
            ]):
                self.err_count[k] += 1

    def __check_time_linearity(self, bus_id, time, time_errors):
        previous_exception = time_errors[bus_id][0]
        previous_time = time_errors[bus_id][1]

        if previous_time and time and not self.compare_bus_stop_time(previous_time, time) and not previous_exception:
            self.err_count['a_time'] += 1
            time_errors[bus_id] = (True, time)
        else:
            time_errors[bus_id] = (False, time)

    def __print_result(self):
        """
        Print formatted results from validations including error counts and summarizations.
        """
        print(f'Type and required field validation: {sum(self.err_count.values())} errors')
        for k, v in self.err_count.items():
            print(f'{k}: {v}')

        print(f'\nLines names and number of stops:')
        error_flag = False
        error_message = ""
        for line, stops in self.bus_lines.items():
            number_of_stops = len(set.union(*stops.values()))
            if (not error_flag) & (len(stops['S']) != 1 or len(stops['F']) != 1):
                error_flag = True
                error_message = f"\nThere is no start or end stop for the line: {line}"
            print(f'bus_id: {line} stops: {number_of_stops}')

        if error_flag:
            print(error_message)
            sys.exit(1)

        all_stops = [stop for subset in self.all_stops_by_type.values() for stop in subset]
        starts = self.all_stops_by_type["S"]
        ends = self.all_stops_by_type["F"]
        transfers = [stop for stop, count in Counter(all_stops).items() if count >= 2]
        on_demand = [stop for stop in self.all_stops_by_type["O"] if stop not in transfers and stop not in starts and stop not in ends]

        print(f'\nStart stops: {len(starts)} {sorted(starts)}')
        print(f'Transfer stops: {len(transfers)} {sorted(transfers)}')
        print(f'Finish stops: {len(ends)} {sorted(ends)}')
        print(f'On demand stops: {len(on_demand)} {sorted(on_demand)}')

    @staticmethod
    def compare_bus_stop_time(previous, current):
        """
        Compare two bus stop times to determine if the current time is later than the previous time.

        Args:
            previous (str): The previous time in 'HH:MM' format.
            current (str): The current time in 'HH:MM' format.

        Returns:
            bool: True if the current time is after the previous time, False otherwise.
        """
        p_time = previous.split(':')
        c_time = current.split(':')
        return int(c_time[0]) * 60 + int(c_time[1]) >= int(p_time[0]) * 60 + int(p_time[1])

def main():
    input_json = read_json_from_file("tests/test5_1.json")
    validator = EasyRiderValidator()
    validator.validate(input_json)
    validator.reset()

def read_json_from_file(test_file_name):
    with open(test_file_name) as f:
        return json.load(f)

if __name__ == '__main__':
    main()