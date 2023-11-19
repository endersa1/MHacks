import fitbit
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import arrow  # Arrow is a really useful date time helper library
import numpy as np
import streamlit as st

client = fitbit.Fitbit(
    '23RFVG', 
    'ed6085c8a0e2a7cb173e95e1f97ab6c2',
    access_token='eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1JGVkciLCJzdWIiOiJCUURZOFoiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJ3aHIgd3BybyB3bnV0IHdzbGUgd3dlaSB3c29jIHdhY3Qgd3NldCB3bG9jIiwiZXhwIjoxNzAwNDAzMDE4LCJpYXQiOjE3MDAzNzQyMTh9.QRp8IXrFKXn8BrxmqykEzbfCeUo8jICf6jHDl8Q_3N8', 
    refresh_token='13260ddec59ab0af5c02488352d5c94063d5c119d4e82c25dbe6faf66acfcbc3'
)

start_date = arrow.get("2023-08-01")
end_date = arrow.get("2023-12-31")

# Create a series of 100-day date-range tuples between start_date and end_date
date_ranges = []
start_range = start_date
while start_range < end_date:
  if start_range.shift(days=100) < end_date:
    date_ranges.append((start_range, start_range.shift(days=100)))
    start_range = start_range.shift(days=101)
  else:
    date_ranges.append((start_range, end_date))
    start_range = end_date

# Print the result to the console
all_data = []
heart_data = []
for date_range in date_ranges:
  print(f"Requesting data for {date_range[0]} to {date_range[1]}.")
  url = f"{client.API_ENDPOINT}/1.2/user/-/sleep/date/{date_range[0].year}-{date_range[0].month:02}-{date_range[0].day:02}/{date_range[1].year}-{date_range[1].month:02}-{date_range[1].day:02}.json"
  heartrateUrl = f"{client.API_ENDPOINT}/1/user/-/activities/heart/date/{date_range[0].year}-{date_range[0].month:02}-{date_range[0].day:02}/{date_range[1].year}-{date_range[1].month:02}-{date_range[1].day:02}/15min.json"
  range_data = client.make_request(url)
  heartData = client.make_request(heartrateUrl)
  all_data.append(range_data)
  heart_data.append(heartData)
  print(f"Success!")
sleep_summaries = []
print(heart_data)

# Iterate through all data and create a list of dictionaries of results:
for data in all_data:
  for sleep in data["sleep"]:
    # For simplicity, ignoring "naps" and going for only "stage" data
    if sleep["isMainSleep"] and sleep["type"] == "stages":
      sleep_summaries.append(dict(
          date=pd.to_datetime(sleep["dateOfSleep"]).date(),
          duration_hours=sleep["duration"]/1000/60/60,
          total_sleep_minutes=sleep["minutesAsleep"],
          total_time_in_bed=sleep["timeInBed"],
          start_time=sleep["startTime"],
          deep_minutes=sleep["levels"]["summary"].get("deep").get("minutes"),
          light_minutes=sleep["levels"]["summary"].get("light").get("minutes"),
          rem_minutes=sleep["levels"]["summary"].get("rem").get("minutes"),
          wake_minutes=sleep["levels"]["summary"].get("wake").get("minutes"),            
      ))
# Convert new dictionary format to DataFrame
sleep_data = pd.DataFrame(sleep_summaries)
# Sort by date and view first rows
sleep_data.sort_values("date", inplace=True)
sleep_data.reset_index(drop=True, inplace=True)
print(sleep_data.head())
# It's useful for grouping to get the "date" from every timestamp
sleep_data["date"] = pd.to_datetime(sleep_data["date"])
# Also add a boolean column for weekend detection
sleep_data["is_weekend"] = sleep_data["date"].dt.weekday > 4
# Sleep distribution
(sleep_data["total_sleep_minutes"]/60).plot(
    kind="hist", 
    bins=50, 
    alpha=0.8,
    figsize=(12,8)
)
(sleep_data["total_time_in_bed"]/60).plot(
    kind="hist", 
    bins=50, 
    alpha=0.8
)
plt.legend()
# add some nice axis labels:
ax = plt.gca()
ax.set_xticks(range(2,12))
plt.grid("minor", linestyle=":")
plt.xlabel("Hours")
plt.ylabel("Frequency")
plt.title("Sleeping Hours")
plt.show()
#Plot a scatter plot directly from Pandas
sleep_data.plot(
    x="total_time_in_bed", 
    y="total_sleep_minutes", 
    kind="scatter", 
    figsize=(10,10)
)
# Add a perfect 1:1 line for comparison
ax = plt.gca()
ax.set_aspect("equal")
x = np.linspace(*ax.get_xlim())
ax.plot(x,x, linestyle="--")
plt.grid(linestyle=":")
plt.show()
# Sleep makeup - calculate data to plot
plot_data = sleep_data.\
  sort_values("date").\
  set_index("date")\
  [["deep_minutes", "light_minutes", "rem_minutes", "wake_minutes"]]
# Matplotlib doesn't natively support stacked bars, so some messing here:
df = plot_data
fig, ax = plt.subplots(figsize=(30,7), constrained_layout=True)
bottom = 0
for c in df.columns:
  ax.bar(df.index, df[c], bottom=bottom, width=1, label=c)
  bottom+=df[c]
# Set a date axis for the x-axis allows nicer tickmarks.
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax.legend()
plt.xlabel("Date")
plt.ylabel("Minutes")
# Show a subset of data for clarity on the website:
plt.xlim(pd.to_datetime("2023-08-01"), pd.to_datetime("2023-12-31"))
plt.show()

# Heart Rate
heart_summaries = []
for data in heart_data:
  for heart in data["activities-heart"]:
    print(heart)
    # For simplicity, ignoring "naps" and going for only "stage" data
    if "restingHeartRate" in heart["value"] and heart["value"]["restingHeartRate"]:
      heart_summaries.append(dict(
          date=pd.to_datetime(heart["dateTime"]).date(),
          resting_heart_rate=heart["value"]["restingHeartRate"]
      ))
# Convert new dictionary format to DataFrame
heart_data = pd.DataFrame(heart_summaries)
# Sort by date and view first rows
heart_data.sort_values("date", inplace=True)
heart_data.reset_index(drop=True, inplace=True)
print(heart_data.head())
# It's useful for grouping to get the "date" from every timestamp
heart_data["date"] = pd.to_datetime(heart_data["date"])
# Also add a boolean column for weekend detection
heart_data["is_weekend"] = heart_data["date"].dt.weekday > 4
plot_data = heart_data.\
  sort_values("date").\
  set_index("date")\
  [["resting_heart_rate"]]
# Matplotlib doesn't natively support stacked bars, so some messing here:
df = plot_data
fig, ax = plt.subplots(figsize=(30,7), constrained_layout=True)
bottom = 0
for c in df.columns:
  ax.bar(df.index, df[c], bottom=bottom, width=1, label=c)
  bottom+=df[c]
# Set a date axis for the x-axis allows nicer tickmarks.
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
ax.legend()
plt.xlabel("Date")
plt.ylabel("Resting Heart Rate")
# Show a subset of data for clarity on the website:
plt.xlim(pd.to_datetime("2023-08-01"), pd.to_datetime("2023-12-31"))
plt.show()


sameDay = f"{client.API_ENDPOINT}/1/user/-/activities/heart/date/today/today/1min.json"
sameDayData = client.make_request(sameDay)
heart_summaries = []
for heart in sameDayData["activities-heart"]:
  print(heart)
  # For simplicity, ignoring "naps" and going for only "stage" data
  if "restingHeartRate" in heart["value"] and heart["value"]["restingHeartRate"]:
    heart_summaries.append(dict(
        date=pd.to_datetime(heart["dateTime"]).date(),
        resting_heart_rate=heart["value"]["restingHeartRate"]
    ))
# Convert new dictionary format to DataFrame
# heart_data = pd.DataFrame(heart_summaries)
# # Sort by date and view first rows
# heart_data.sort_values("date", inplace=True)
# heart_data.reset_index(drop=True, inplace=True)
# print(heart_data.head())
# # It's useful for grouping to get the "date" from every timestamp
# heart_data["date"] = pd.to_datetime(heart_data["date"])
# # Also add a boolean column for weekend detection
# heart_data["is_weekend"] = heart_data["date"].dt.weekday > 4
# plot_data = heart_data.\
#   sort_values("date").\
#   set_index("date")\
#   [["resting_heart_rate"]]
# # Matplotlib doesn't natively support stacked bars, so some messing here:
# df = plot_data
# fig, ax = plt.subplots(figsize=(30,7), constrained_layout=True)
# bottom = 0
# for c in df.columns:
#   ax.bar(df.index, df[c], bottom=bottom, width=1, label=c)
#   bottom+=df[c]
# # Set a date axis for the x-axis allows nicer tickmarks.
# ax.xaxis.set_major_locator(mdates.MonthLocator())
# ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
# ax.legend()
# plt.xlabel("Date")
# plt.ylabel("Resting Heart Rate")
# # Show a subset of data for clarity on the website:
# plt.xlim(pd.to_datetime("2023-08-01"), pd.to_datetime("2023-12-31"))
# plt.show()

sameDay = f"{client.API_ENDPOINT}/1/user/-/activities/heart/date/2023-11-18/1d/1min.json?timezone=EST"
sameDayData = client.make_request(sameDay)
print(sameDayData["activities-heart-intraday"]["dataset"])
#graph it
heart_summaries = []
for heart in sameDayData["activities-heart-intraday"]["dataset"]:
  print(heart)
  # For simplicity, ignoring "naps" and going for only "stage" data
  if "value" in heart:
    heart_summaries.append(dict(
        time=heart["time"],
        heart_rate=heart["value"]
    ))
# Convert new dictionary format to DataFrame
heart_data = pd.DataFrame(heart_summaries)
# Sort by date and view first rows
heart_data.sort_values("time", inplace=True)
heart_data.reset_index(drop=True, inplace=True)
print(heart_data.head())
#scatter plot
fig, ax = plt.subplots(figsize=(10, 10))
heart_data.plot(
    x="time", 
    y="heart_rate", 
    kind="scatter", 
    ax=ax
)
# make x-axis time values readable
ax = plt.gca()
ax.set_xticks(range(0,1440,60))
ax.set_xticklabels(range(0,24))
plt.xlabel("Time")
plt.grid(linestyle=":")
# plt.show()
st.pyplot(fig)


# devices = f"{client.API_ENDPOINT}/1/user/-/devices.json"
# devicesData = client.make_request(devices)
# print(devicesData)
# deviceID = devicesData[0].get("id")

#create alarm
# alarm = f"{client.API_ENDPOINT}/1/user/-/devices/tracker/{deviceID}/alarms.json"
# time = "01:00"
# enabled = True
# weekDays = "SUNDAY"
# recurring = False
# alarm += f"?time={time}&enabled={enabled}&weekDays={weekDays}&recurring={recurring}"
# alarmData = client.make_request(alarm)
# print(alarmData)