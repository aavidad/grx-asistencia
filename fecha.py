from datetime import datetime, timedelta

def convert_ad_timestamp(timestamp):
	epoch_start = datetime(year=1601, month=1,day=1)
	seconds_since_epoch = timestamp/10**7
	return epoch_start + timedelta(seconds=seconds_since_epoch)

fecha=convert_ad_timestamp(131000290120505595)
print fecha

