'Inmarsat data import and cleaning'
from datetime import datetime, timedelta
from collections import namedtuple, defaultdict

InmarsatRecord = namedtuple('InmarsatRecord', 'time channel bto bfo')


class InmarsatLog:
    'Contains Inmarsat data set'

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return (item for item in self.data)

    def bin_data(self, time_step):
        'Creates new list with binned data'
        binned_values = []
        time_hash = defaultdict(lambda: [])
        if time_step == timedelta(seconds=10):
            for item in self.data:
                time_key = item.time.replace(
                    second=5 + 10*(item.time.second // 10),
                    microsecond=0)
                time_hash[time_key].append(item)
        else:
            raise NotImplementedError()
        for time, records in time_hash.items():
            bfos = [item.bfo for item in records]
            bfo = sum(bfos) / len(bfos)
            btos = [item.bto for item in filter(
                lambda record: record.bto is not None, records)]
            bto = None if len(btos) == 0 else sum(btos) / len(btos)
            channels = list(filter(lambda record: record.channel, records))
            channel = max(set(channels), key=channels.count)
            binned_values.append(InmarsatRecord(time, channel, bto, bfo))
        return InmarsatLog(sorted(binned_values, key=lambda item: item.time))

    @classmethod
    def from_csv(cls, folder, file_name):
        'Loads data from Sladen csv file'
        def parse_time(time_string):
            'Parses time string'
            time_format = '%d/%m/%Y %H:%M:%S.%f'
            return datetime.strptime(time_string, time_format)

        def parse_channel(channel_string):
            'Parses channel ID'
            try:
                channel = channel_string.split('-')[3]
            except IndexError:
                channel = channel_string.split('-')[1]
            return channel

        def process_bto(bto_string, message_string, time_string, channel):
            'Applies known tweaks to BTO data'
            adjust_for_messages = ['Subsequent Signalling Unit',
                                   '0x71 - User Data (ISU) - RLS']
            bto_tweaks = {
                '7/03/2014 18:25:27.421': 4600,
                '7/03/2014 18:25:34.461': 5 * 7820,
                '8/03/2014 00:19:29.416': 4600,
                '8/03/2014 00:19:37.443': 4 * 7820,
            }
            bto = float(bto_string)
            if message_string in adjust_for_messages or channel == '36FA':
                bto += 5000
            if time_string in bto_tweaks.keys():
                bto -= bto_tweaks[time_string]
            return bto

        def process_bfo(bfo_string, channel):
            'Removes interchannel bias in BFO data'
            adjust_for_channels = ['36ED', '36E3']
            bfo = float(bfo_string)
            if channel in adjust_for_channels:
                bfo += 4
            return bfo

        data = []
        with open(folder + '/' + file_name, 'rt') as fin:
            next(fin)
            for line in fin:
                items = line.split(',')
                if items[25]:
                    item_time = parse_time(items[0])
                    item_channel = parse_channel(items[3])
                    item_bfo = process_bfo(items[25], item_channel)
                    try:
                        float(items[27])
                        item_bto = process_bto(items[27], items[13], items[0], item_channel)
                    except ValueError:
                        item_bto = None
                    data.append(InmarsatRecord(
                        item_time, item_channel, item_bto, item_bfo))
        return cls(sorted(data, key=lambda item: item.time))
