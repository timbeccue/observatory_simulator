from cmd import Cmd
import json
import sqs, mount_device
 
class MyPrompt(Cmd):
    prompt = ':: '
    intro = "\nWelcome to photon ranch! Type ? to list commands"

    q = sqs.Queuer()
    m = mount_device.Mount()


    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)
        print(inp)

    def emptyline(self):
        pass
 
    def do_exit(self, inp):
        print("Safely shutting down. Goodbye")
        return True
    def help_exit(self):
        print('exit the application. Shorthand: x q Ctrl-D.')
 
    def do_send(self, inp):
        if inp=='': inp=1
        n = int(inp)
        if type(n) is int:
            print("\nSending test messages to sqs.")
            self.q.send(n)
            print()
        else:
            print("input must be an integer (number of messages to send)") 
    def help_send(self):
        print("Send test messages to sqs. First argument is number of messages.")
        print("If no argument is provided, default is 1.")

    def do_get(self, inp):
        messages = self.q.read_queue()
        for message in messages:
            message = json.loads(message)
            if message['command'] == 'goto':
                self.m.slew_to_eq(message['ra'], message['dec'])
    def help_get(self):
        print('Read messages from sqs.')

    def do_tracking(self, inp):
        input = inp.strip().lower()
        if input == 'on':
            print("tracking is on")
        elif input == 'off':
            print("tracking is off")
        else:
            print("Required argument must be either 'on' or 'off'.")
    def help_tracking(self):
        print("Turn tracking on or off. Requires string arg: 'on'|'off'.")
    
    def do_park(self, inp):
        print("Parking telescope.")
        self.m.park()
    def help_park(self):
        print("Parks the telescope.")

    def do_status(self, inp):
        self.m.get_mount_status()
    def help_status(self):
        print("Retrieve and print status from mount device.")
 
    do_EOF = do_exit
    help_EOF = help_exit
 
if __name__ == '__main__':
    MyPrompt().cmdloop()