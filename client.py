from cmd import Cmd
import json, time, datetime
from aws.init_resources import Resources



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
        print("Send commands to the current site. Takes one arg: number of messages.")
        print("Example: 'test 5' will send 5 commands. 'test' with no arg == 'test 1'.")
        print("Commands will slew the mount to random coordinates.")
        print("This is useful to quickly send lots of messages to test high use handling.")
        

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
        
    def do_unpark(self, inp):
        msg = {
            "device": "mount_1",
            "command": "unpark",
            "timestamp": int(time.time())
        }
        self.q[self.current_site].send_to_queue(json.dumps(msg))
        
        
    def do_allstop(self, inp):
        msg = {
            "device": "mount_1",
            "command": "all_stop",
            "timestamp": int(time.time())
        }
        self.q[self.current_site].send_to_queue(json.dumps(msg))
        
    def help_park(self):
        print("Parks the telescope. Tracking turned off")

    def help_unpark(self):
        print("unParks the telescope. Tracking stays off")

    def help_allstop(self):
        print("Stops all motion.   Tracking stays off")
        
    def do_status(self, inp):
        status = {"State": "State"}
        response = self.d[self.current_site].get_item(status)
        secondsold = int(time.time()) - int(response['timestamp'])
        age = str(datetime.timedelta(seconds=secondsold))
        print(json.dumps(response, indent=2))
        print(f"Status is {age} (hh:mm:ss) old.")
        
    def help_status(self):
        print("Retrieve and print status from dynamodb.")


    def do_goto(self, inp):
        """
        Arguments: Three args separated by a space.
        Example: 'ra=23.22 dec=44.64 sys="J2000.0"'
        """
        try:
            args = parse(inp)
            print('args:  ', args)
            if not ('ra' in args.keys()) and 'dec' in args.keys():
                print("invalid inputs. use form 'ra=x dec=y'")
            msg = {
                "device": "mount_1",
                "ra": float(args['ra']),
                "dec": float(args['dec']),
                'rdsys': args['rdsys'],
                "command": "goto",
                "timestamp": int(time.time())
            }
            self.q[self.current_site].send_to_queue(json.dumps(msg))
        except:
            print("Error (probably bad input). See sample goto command: ")
            print("'goto ra=1.1 dec=2.2 rdsys='J2000.0''")
            
    def do_goto_azalt(self, inp):
        """
        Arguments: Two args separated by a space.
        Example: 'ra=23.22 dec=44.64 '
        """
        try:
            args = parse(inp)     
            if not ('az' in args.keys()) and 'alt' in args.keys():
                print("invalid inputs. use form 'az=x alt=y'")
            msg = {
                "device": "mount_1",
                "az": float(args['az']),       #Does a sngle argument make sense? Also  Zen or airmass
                "alt": float(args['alt']),
                "command": "goto_azalt",
                "timestamp": int(time.time())
            }
            self.q[self.current_site].send_to_queue(json.dumps(msg))
        except:
            print("Error (probably bad input). See sample goto_azalt command: ")
            print("'goto az=30.0 alt=2.2'")
            
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
        filename = response['cam1_last_image_name']
        if filename != 'empty':
            url = self.s[self.current_site].get_image_url(filename)
            print(f"Last image url: {url}")
        else:
            print("No images available.")
    def help_get_url(self):
        print('Gets a url pointing to the latest image taken at the current '\
              'active observatory. The image is a jpg stored at s3.')
        



def parse(inp):
    """
    Parse input string and return dict.
    Input is split into key=value, with each kv pair separated with spaces.
    """

    # Remove whitespace in front and back. Split into separate strings at spaces.
    print(inp)
    arg_list = inp.strip().split()
    arg_dict = {}
    for arg in arg_list:
        kv = arg.split("=")
        arg_dict[kv[0]] = kv[1]
    return arg_dict



 
if __name__ == '__main__':
    MyPrompt().cmdloop()


