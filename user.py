from cmd import Cmd
import json, time, datetime,yaml
import sqs, dynamodb, mount_device



def init_resources(configfile):

    all_queues = {} 
    all_dynamodb = {} 

    with open(configfile, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            sites = config['Sites'].keys() 

            for site in sites:
                d = make_dynamodb(site)
                q = make_queues(site)

                all_dynamodb[site] = d
                all_queues[site] = q

            resources = {
                "all_dynamodb": all_dynamodb,
                "all_queues": all_queues,
                "all_sites": list(sites)
                }
            return resources

        except yaml.YAMLError as exc:
            print(exc)

def make_queues(sitename):
    fromAWS = sitename + '_from_aws_pythonbits.fifo'
    toAWS = sitename + '_to_aws_pythonbits.fifo'
    return sqs.Queuer(fromAWS, toAWS)

def make_dynamodb(sitename):
    tablename = sitename + "_state_pythonbits"
    return dynamodb.DynamoDB(tablename) 



class MyPrompt(Cmd):

    resources = init_resources("sites_config.yml")
    q = resources['all_queues']
    d = resources['all_dynamodb']

    all_sites = resources['all_sites']
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
        
    def do_a(self, inp):
        try:
            n = 3 
            print(f"\nSending {n} test messages to sqs A.")
            self.q['wmd'].send(n)
            print()
        except:
            print("failed A") 

    def do_b(self, inp):
        try:
            n = 3 
            print(f"\nSending {n} test messages to sqs B.")
            self.q['saf'].send(n)
            print()
        except:
            print("failed B") 



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
        print(response)
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


