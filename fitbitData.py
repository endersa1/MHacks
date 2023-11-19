import fitbit
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import arrow  # Arrow is a really useful date time helper library
import numpy as np

client = fitbit.Fitbit(
    '23RFVG', 
    'ed6085c8a0e2a7cb173e95e1f97ab6c2',
    access_token='eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1JGVkciLCJzdWIiOiJCUURZOFoiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNzAwMzkwMDMzLCJpYXQiOjE3MDAzNjEyMzN9.FgPag1kg5LNTRxXRFI9fnO1eVKcLNvFdUcpz-2OhIIs', 
    refresh_token='409bbdb145e77ef6adc8c31439c7c4133065beffa0e5c6fb8219101cf67fbc56'
)

start_date = arrow.get("2023-01-01")
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
  heartrateUrl = f"{client.API_ENDPOINT}/1/user/-/activities/heart/date/{date_range[0].year}-{date_range[0].month:02}-{date_range[0].day:02}/{date_range[1].year}-{date_range[1].month:02}-{date_range[1].day:02}.json"
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
plt.xlim(pd.to_datetime("2023-01-01"), pd.to_datetime("2023-12-31"))
plt.show()