# Brewblox_to_brewfather

Read sensor data from Brewblox API and send to Brewfather using the Custom Stream integration.

## Disclaimer

This tool is a quick hack to get data from Brewblox into Brewfather. It was made for my personal experimentation and is by no means complete. Feel free to use and modify as needed. A Brewblox service plugin would be more robust solution.

## Configuration

All parameters can be set in the included YAML file. Rename example **brewblox_to_brewfather.example.yml** to **brewblox_to_brewfather.yml**.

I run the script from crontab every 15 minutes. To run in background set interval to at least 900 seconds.

Adjust other settings as needed
