MORNING, NOON, AFTERNOON, EVENING = range(4)

class Bed:
    positive = ["You wake up in the morning and remember that you have a lot of interesting things to do today.",
                "It is raining outside and sound of it creates cosy atmosphere. It is nice to lie in bed, but interesting classes start soon!",
                "It's a good idea to spend the hotest hour in bed but you are getting a little bit bored.",
                "It is night already. You close your eyes and fall asleep instantly."]
    negative = ["You wake up and suddenly remember all of your problems. You fill really bad and don't want to move.",
                "It's raining outside, grey clouds cover the sky and it won't end. You don't want to get out of the bed.",
                "A half of the day passed and you haven't done anything good. Maybe you can't accomplish anything at all.",
                "It is time to sleep but thoughts bother you and you feel lonely and sad. You are not able to make yourself fall asleep."]

class Kitchen:
    positive = ["", "You are feeling hungry and (what luck!) you have delicious leftover pizza in your fridge. It is time to leave for the class 'cause you don't want to be late",
                "Instead of classes (that are a little bit boring) you've invited some friends. Good time to play some games",
                "You started reading the book your friend recommended you. It was so interesting, you went on reading well after midnight and finally fell asleep over it."]

    negative = ["", "You don't want to eat at all and you can't even think about eating tasteless cold pizza that is the only food left. The only thing you want is lie down and cry.",
                "You forgot about it, but yesterday you have invited some friends to come over. What a stupid thing to do! They party and laugh and do not notice that you are sad, which makes you really angry. Stupid friends!",
                "It is night already but you are still sitting in the darkness, unable even to move to the bed."]

class School:
    positive = ["", "The first class is on Math. You listen with great interest to beautiful concepts that you proff explains.",
                "Today is semester test. Tasks are quite hard, but after some time you master them all and hand in your paper",
                "You desided to go to all-night party at the University. There is good music and cheerful atmosphere. You are just in the right mood to dance for hours."]
    
    negative = ["", "Boring math class again! You can't concentrate on endless formulae and start thinking of you problems again. How good would it be to return to bed!",
                "Oh, those dreadful tests! The moment you saw the tasks you understood that you are too stupid to solve any of them.",
                "In the evening people leave the building and lights are turned off. You wander in dark and silent halls, alone with your dark thoughts."]

STATES = {
    "Bed": Bed,
    "Kitchen": Kitchen,
    "School": School
}

class Game:
    def __hash__(self):
        return hash((self.positive, self.time, self.state))

    def __init__(self):
        self.positive = False
        self.time = MORNING
        self.state = "Bed"
        self.finished = 0
    
    def get_state(self):
        return STATES[self.state]
    
    def get_description(self):
        room = self.get_state()
        desc = room.positive if self.positive else room.negative
        return "======\n" + desc[self.time] + "\n======"
    
    def start(self):
        return ("To better understand how depression can affect your mood play my little game. "
               "It has the same day of a life presented from two points of view: healthy person and depressed person. "
               "Select point of view for your first try. After, you will play the same game from the other perspective.")
    
    def select_perspective(self, perspective):
        self.positive = perspective == "Healthy"
        return self.get_description()

    def take_move(self, move):
        self.time += 1
        self.state = move
        return self.get_description()
