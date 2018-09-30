import time

def format_time(timestamp: int):
    if timestamp is None:
        return ''
    else:
        return time.strftime('%b %d, %Y %H:%M:%S %Z', time.localtime(timestamp))