import redis
import json
import requests
import randfacts
import pyjokes
import threading
import os
from dotenv import load_dotenv
import sys

load_dotenv()

class Chatbot:
    def __init__(self, host='redis', port=6379):
        try:
            self.client = redis.StrictRedis(host=host, port=port, decode_responses=True)
            self.client.ping()  # Test connection
            self.pubsub = self.client.pubsub()
        except redis.ConnectionError:
            print("Error: Could not connect to Redis. Make sure Redis is running.")
            sys.exit(1)
    
    def introduce(self):
        # Provide an introduction and list of commands
        intro = """
        Hello! My Name is C-bot! I am your friendly neighborhood chatbot!
        Following are the commands I can use:
        !identify: allows you to identify youself
        !help: list of commands
        !weather: I will provide a weather report for your area
        !fact: I can give you a random fun fact!
        !joke: I will tell you a funny joke!
        !whoami: I will give you back your user information!
        !join <channel name>: This will let you join a channel of your choice
        !send: this will start a prompt for you to send a message to a channel of your choice
        !leave: this will start a prompt for which channel you would like to leave
        !quit: This will shut down the the chat bot.
        """
        print(intro)
    
    #Identitfy command that allos the user to ID themselves 
    def identify(self, name, age, sex, location):
        #user key is the name of the user. 
        user_key = f"user:{name}"
        #setting the hash of the user in the redis database
        self.client.hset(user_key, mapping={
            "name": name,
            "age": age,
            "sex": sex,
            "location": location
        })
        
        #I am making ther username of each user just be their name. 
        self.username = name
        
        
    def list_users(self):
        # Fetch all keys that follow the 'user:*' pattern
        user_keys = self.client.keys('user:*')
        
        # list of user names
        user_names = []

        # finding the names over all of users
        for user_key in user_keys:
            user_data = self.client.hget(user_key, "name")
            if user_data:
                user_names.append(user_data.decode('utf-8'))  # Decoding process

        return user_names
       
    #!help command, showing the list of all usable commands
    def helpers(self):
        response = """
        I am here to help! 
        Here are the commands I support:
        !identify: allows you to identify youself
        !help: list of commands
        !weather: I will provide a weather report for your area
        !fact: I can give you a random fun fact!
        !joke: I will tell you a funny joke!
        !whoami: I will return a list of active users for you to get information on
        !join <channel name>: This will let you join a channel of your choice
        !send: this will start a prompt for you to send a message to a channel of your choice
        !leave: this will start a prompt for which channel you would like to leave
        !quit: This will shut down the the chatbot
        """
        print(response)
        
     #gets the information of a selected user and prints it out in a good format  
    def whoami(self, user):
        user_key = f"user:{user}"
        #getting the info of the hash then decoding each piece into its own variable
        info = self.client.hgetall(user_key)
        name = info[b'name'].decode('utf-8')
        sex = info[b'sex'].decode('utf-8')
        age = info[b'age'].decode('utf-8')
        city = info[b'location'].decode('utf-8')
        #printing the variable in a clean format
        response = f"""
        Name: {name}
        Age: {age}
        Sex: {sex}
        City: {city}
        """
        print(response)
        
        #helper function to get the location of a user for the get weather function
    def get_location(self, user):
        user_key = f"user:{user}"
        info = self.client.hgetall(user_key)
        location = info[b'location'].decode('utf-8')
        return location

    #api function to show the weather for the given city of the user. I wanted to used this versus storing dummy data since
    #this would provide a more engaging experience. 
    
    def get_weather(self, location):
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            return "Error: Weather API key not configured."
        base_url = "http://api.openweathermap.org/data/2.5/weather"

        params = {
            'q': location,  
            'appid': api_key,  
            'units': 'imperial' 
        }
  
        response = requests.get(base_url, params=params)


        if response.status_code == 200:
            data = response.json()

            city = data['name']
            temp = data['main']['temp']
            description = data['weather'][0]['description']

            return f"The current weather in {city} is {temp:.0f}°F with {description}."
        else:

            return f"Error: Unable to get weather for {location}."
        
        #!fact command using the randfacts library the command will return a random fact for the user. The facts are stored in a list in the db
    def rand_fact(self):
        fact = randfacts.get_fact()
        #stores the facts in the db as a list
        self.client.rpush('facts', fact)
        return fact
        
        #!joke using the pyjokes library I get to see a random joke a fun addition to the bot, the jokes are also stored in a list of jokes in the db
    def rand_joke(self):
        joke = pyjokes.get_joke()
        #stores the joke in the database as a list
        self.client.rpush('jokes', joke)
        return joke
                          
        #!join function to join the channel This will take the current user and join them to listen to a channel. I found this threading library that allowed me to have the user join the channel and listen while still being able to engage with functions that I implemented. 
    def join_channel(self, channel):
        #this subscribes the user to the channel
        self.pubsub.subscribe(channel)
        print(f"{self.username} has joined the channel: {channel}")
        
        #I have this function to get all the previous messages that had been sent to channel before the user joined
        self.get_prev_messages(channel)
        #This is the threading libary that I found. It takes the listen to channel function that starts a thread of that function running so the user can still receive messages while being able to use other commands from the main thread. The threading also allows for the user to listen to multiple channels at once.
        threading.Thread(target=self.listen_to_channel_messages, args=(channel,), daemon=True).start()
        
        
        #!leave this will have the user leave the chanel
    def leave_channel(self, channel):
        self.pubsub.unsubscribe(channel)
        print(f"You have left the channel: {channel}")

        #!send this will have the user send a message to the chosen channel from the interactions function
    def send_message_to_channel(self, channel, message):
        
        message_obj = {
            #this channel piece allows for me to show which channel the message comes from for the user
            "channel": channel,
            "from": self.username,
            "message": message
        }
        
        #publishes the message to the chosen channel
        self.client.publish(channel, json.dumps(message_obj))
        
        #this is what will help store the messages for the message history when a user joins
        history_key = f"channel_history:{channel}"
        #I am storing the messages in a list. Using the Rpush function so the most recent message is on the right. 
        self.client.rpush(history_key, json.dumps(message_obj))
        print(f"Message sent to {channel}: {message}")
        
        #This function gets all of the messages in a list
    def get_prev_messages(self, channel):
        #this takes the channel name from the channel a user says they want to join
        prev_key = f"channel_history:{channel}"
        
        #this will bring the list of all of the messages
        message_history = self.client.lrange(prev_key, 0, -1)  # Get all messages in the list
        
        # I have this loop so that if there are no messages in the message history it will let the user know. Otherwise it will print all of the previous messages and who they were from
        if message_history:
            print(f"Previous messages in {channel}:")
            for message in message_history:
                msg_data = json.loads(message)
                print(f"{msg_data['from']}: {msg_data['message']}")
        else:
            print(f"No previous messages in {channel}.")
        
        #This is the functio nthat gets used in my threading. So when a user has joined a channel they will constantly be listening for new messages so when a message comes in the user will receive it. 
    def listen_to_channel_messages(self, channel):
        while True:
            inc_message = self.pubsub.get_message()  # Get the next available message
            if inc_message and inc_message['type'] == 'message':
                msg_data = json.loads(inc_message['data'])
                #gives us the message and the channel it is from
                print(f"\nMessage in {msg_data['channel']} from {msg_data['from']}: {msg_data['message']}")
       
    # this is the main interaction loop of the whole bot. Once it is started the user will be given a list of options to choose from that the bot is able to use
    def interaction(self,name): 
        while True:
            print("\nPlease select an option:")
            print("!join")
            print("!leave")
            print("!send")
            print("!identify")
            print("!whoami")
            print("!joke")
            print("!fact")
            print("!weather")
            print("!help")
            print("!quit")
            
            
            #this gets our user input
            user_input = input("You: ").strip()
            
            #since all of the commands start with '!' I have this here so if they accidentally do not have a '!' the bot will let thm know. 
            if user_input.startswith("!"):
                #chaning it to commabd to make the logic here be a bit easier
                command = user_input
                # this is the logic behind all of the commands that will do the function for all of the commands
                #This will do the help command
                if command == "!help":
                    self.helpers()
                    
                #This returns the weather for the current user
                elif command == "!weather":
                    location = self.get_location(name)
                    print(self.get_weather(location))
                    
                    #this will give a fact to the user
                elif command == "!fact":
                    print(self.rand_fact())
                    
                    #this will tell a joke to the user
                elif command == "!joke":
                    print(self.rand_joke())
                    
                    #after initialization this will allow the user to identify themselves again. I do not have it a updating or replacing them in the DB so there would be 2 records of the same name 
                elif command == "!identify":
                    print("Please Identity yourself with your name, age, sex and city you are located in")

                    identity = input("You: ").strip().lower()
                    try:
                        name, age, sex, location = identity.split(", ")
                        self.identify(name, age, sex, location)
                        print(f"Hello {name}, you have been saved into the system!")
                    except ValueError:
                        print("Please provide your details in the format: !identify <name>, <age>, <sex>, <location>")
                        
                    #This will provide a list of the current users in the db. From there you are able to select the user you want to get information about
                elif command == "!whoami":
                    print(self.list_users())
                    name = input("Who would you like to get info about?: ").strip().lower()
                    self.whoami(name)
                    
                    #allows the user to join/listen to a channel
                elif command == "!join":
                    channel = input("What channel would you like to join?: ").strip()
                    self.join_channel(channel)
                    
                    #a user can send a message to a chosen channel
                elif command == "!send":
                    chan = input("What channel would you like to send a message to?: ")
                    mess = input("What would you like to say?: ").strip()
                    self.send_message_to_channel(chan, mess)
                    
                    #Allows the user to decide what channel they would like to leave
                elif command == "!leave":
                    channel = input("What channel would you like to leave?: ").strip()
                    self.leave_channel(channel)  
                    
                    #quits the chatbot
                elif command == "!quit":
                    print("Goodbye!")
                    break
                    
                    #I have this incase the user mistypes one of the commands but starts it with a '!'
                else:
                    print("Unknown command. Type !help to see available commands.")
                    
            #this helps deal with any issues of commands that do not start with '!'
            else:
                print("Commands must start with '!'.")
        


#this will run the chatbot. 
def main():
    
    #I intialize the class with bot, so now all function callas need to be with the bot.<function> format
    bot = Chatbot()
    
    #this will introduce the chatbot with the list of commands and the bot name. Right after introduction, I force the user into an identification process so they can already exist in the DB before any other commands
    bot.introduce()
    
    print("Please Identity yourself with your name, age, sex, and city you are located in")
    
    #I get the input and lower/strip it to make it a bit easer
    identity = input("You: ").strip().lower()
    
    #this ensures the information is inputted in the correct format and will let the user know if it is successful otherwise it will tell the user that the information is not inputted correctly and break out of the main function
    try:
        name, age, sex, location = identity.split(", ")
        bot.identify(name, age, sex, location)
        print(f"Hello {name}, you have been saved into the system!")
    except ValueError:
        print("Please provide your details in the format: !identify <name>, <age>, <sex>, <location>")
        
        
        #this starts how the user interacts with the bot. 
    bot.interaction(name)


if __name__ == "__main__":
    main()



        
        