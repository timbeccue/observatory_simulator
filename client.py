from cmd import Cmd
import json, time, datetime,yaml
from aws.resources import Resources



class MyPrompt(Cmd):

    r = Resources("sites_config.yml")
    q = r.get_all_sqs()
    d = r.get_all_dyanmodb()
    s = r.get_all_s3()
    all_sites = r.get_all_sites() 
    current_site = all_sites[0] 

    prompt = current_site+':: '
    intro = "\nWelcome to photon ranch! Type ? to list commands"

    def default(self, inp):
        if inp == 'x' or inp == 'q' or inp == 'exit':
            return True 
        print(inp)

    def emptyline(self):
        """
        Hitting enter without input just adds a new line.
        (Used to repeat last command instead)
        """
        pass
    


    def do_set_obs(self, inp):
        lowercase_input = inp.lower()
        if lowercase_input in self.all_sites:
           self.current_site = lowercase_input
           self.prompt = lowercase_input+':: '

    def help_set_obs(self):
        print(f'Current active observatory: {self.current_site}.')
        print(f'Change the current active observatory with "set_obs <3-letter-sitename>".')



    def do_test(self, inp):
        """
        Send n test messages to sqs.
        Messages are commands to goto random valid ra and dec.
        """
        if inp=='': inp=1
        try:
            n = int(inp)
            print(f"\nSending {n} test messages to sqs.")
            self.q[self.current_site].send(n)
            print()
        except:
            print("input must be an integer (number of messages to send)") 
    def help_test(self):
        print("Send test messages to sqs. First argument is number of messages.")
        print("If no argument is provided, default is 1.")
        

    def do_get(self, inp):
        messages = self.q[self.current_site].read_queue()
        for message in messages:
            message = json.loads(message)
            if message['command'] == 'goto':
                self.m.slew_to_eq(message['ra'], message['dec'])
    def help_get(self):
        print('Read messages from sqs.')


    def do_tracking(self, inp):
        input = inp.strip().lower()
        if input == 'on':
            pass
        elif input == 'off':
            pass
        else:
            print("Required argument must be either 'on' or 'off'.")
    def help_tracking(self):
        print("Turn tracking on or off. Requires string arg: 'on'|'off'.")
    

    def do_park(self, inp):
        msg = {
            "device": "mount_1",
            "command": "park",
            "timestamp": int(time.time())
        }
        self.q[self.current_site].send_to_queue(json.dumps(msg))
    def help_park(self):
        print("Parks the telescope.")


    def do_status(self, inp):
        status = {"State": "State"}
        response = self.d[self.current_site].get_item(status)
        secondsold = int(time.time()) - int(response['timestamp'])
        age = str(datetime.timedelta(seconds=secondsold))
        print(json.dumps(response, indent=2))
        print(f"Status is {age} (hh:mm:ss) old.")
    def help_status(self):
        print("Retrieve and print status from dynamodb.")


    def do_print(self, inp):
        print(f"Type: {type(inp)}.")
        print(f"Content: {inp}.")
    def help_print(self):
        print("Prints the argument and its type.")
 

    def do_goto(self, inp):
        """
        Arguments: two args spearated by a space.
        Example: 'ra=23.22 dec=44.64'
        """
        try:
            args = parse(inp)     
            if not ('ra' in args.keys()) and 'dec' in args.keys():
                print("invalid inputs. use form 'ra=x dec=y'")
            msg = {
                "device": "mount_1",
                "ra": args['ra'],
                "dec": args['dec'],
                "command": "goto",
                "timestamp": int(time.time())
            }
            self.q[self.current_site].send_to_queue(json.dumps(msg))
        except:
            print("Error (probably bad input). See sample goto command: ")
            print("'goto ra=1.1 dec=2.2'")
    def help_goto(self):
        print("Send goto command. Expects args: 'ra=<float> dec=<float>'.")


    def do_expose(self, inp):
        print(f"Starting exposure: {inp} seconds.")
        msg = {
            "device": "camera_1",
            "command": "expose",
            "duration": float(inp),
            "timestamp": int(time.time()),
        }
        self.q[self.current_site].send_to_queue(json.dumps(msg))
    def help_expose(self):
        print("Starts an exposure. Provide duration in seconds. Example: 'expose 5.3'.")

    def do_get_url(self, inp):
        status = {"State": "State"}
        response = self.d[self.current_site].get_item(status)
        filename = response['last_image_name']
        if filename != 'empty':
            url = self.s[self.current_site].get_image_url(filename)
            print(f"Last image url: {url}")
        else:
            print("No images available.")
        



def parse(inp):
    """
    Parse input string and return dict.
    Input is split into key=value, with each kv pair separated with spaces.
    """

    # Remove whitespace in front and back. Split into separate strings at spaces.
    arg_list = inp.strip().split()
    arg_dict = {}
    for arg in arg_list:
        kv = arg.split("=")
        arg_dict[kv[0]] = kv[1]
    return arg_dict



 
if __name__ == '__main__':
    MyPrompt().cmdloop()


