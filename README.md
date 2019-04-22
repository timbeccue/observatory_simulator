# observatory_simulator

This code is intended to demonstrate a simple working example of communication between a client and an observatory using AWS services (sqs, dynamodb, s3). 

### Observatory features:
- Read from a config file and automatically starts simulated observatory sites for each site in the config. Generates AWS instances for each site. 
- Each site reads from aws sqs work queue at regular intervals, moving commands into its own local work queue to be executed.
- Execute commands in order, interfacing with device classes.
- Device classes store state, which updates after executing a command.
- Sites will regularly compile state from all devices, then update the state in a dynamodb table.
- Camera commands will send a test jpg (with unique filename) to s3, and make it available for client to download.

### Client features:
- Can run with or without an observatory online. 
- Starts interactive session in terminal to send commands. See available commands with `?`.
- Similar to a current working directory, the current active observatory shows which site you are interacting with (note: the site does not need to be online).
- Provides command to see all observatories in the network. You can set the current active obs to any of these with `set_obs <obs-name>`.
- Commands are sent to an sqs queue, which will be processed whenever the observatory is online. 
- Provides method to get status for the current active observatory, and display age of the status. 
- Command to get a link to the last image taken at the current active observatory.


# Commands

Only a few basic device methods have been implemented. Most of the focus is on communication rather than device simulation. Absent entirely is any type of device relationship, configuring devices per site, or specifying which device to control.
- Mount control: `goto ra=x dec=y`, `tracking yes|no`, `park`
- Camera control: `expose <duration in seconds>`

See all available commands with `?`.




# Installation

Clone and cd into the repository. 

Install the python requiremnets into a virtual environment with this command:

(note: requires python 3.6+)

Windows:
`virtualenv venv && .\venv\Scripts\activate && pip install -r requirements.txt`

Mac/Linux:
`virtualenv venv && source venv/bin/activate && pip install -r requirements.txt`

Since the communication between the client/server uses AWS, you must have a valid credentials file connected to an aws account with access to sqs, dynamodb, and s3. See [here](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) for more info.

# Usage

There are two programs to run: client.py and obs.py. They work independently: if client runs without the server, it will send commands to the work queue, but the commands will not be executed until the observatory comes online. Similarly, the observatory can be run by itself and will execute tasks in the work queue. 

To start the observatory, just run obs.py. It will stay running until closing the program with ctrl-c. 

To start the client, run client.py. This will start an interactive session in the terminal where you can type commands. See available commands with `?`, and see documentation for specific commands with `? <command name>`. 
