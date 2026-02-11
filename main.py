import asyncio
import os
import random
from collections import deque
from datetime import datetime, timedelta

import discord
import pytz
from dotenv import load_dotenv
from discord.ext import commands, tasks

load_dotenv()


intents = discord.Intents.all()

client = commands.Bot(command_prefix="$", intents=intents)

# --- Bot Status ---

games = [
    (discord.ActivityType.listening, "Geekspeak Radio"),
    (discord.ActivityType.watching, "My inbox for new messages"),
    (discord.ActivityType.watching, "Watu wa Gaming on YouTube"),
    (discord.ActivityType.streaming, "https://www.youtube.com/@watuwagaming"),
]
gamesTimer = 60 * 10  # 10 minutes

GREETINGS_CHANNEL_ID = 628278524905521179
GENERAL_CHANNEL_ID = 750702727566327869
GAMERS_ARENA_CHANNEL_ID = 1355493926492180632
EAT = pytz.timezone("Africa/Nairobi")  # GMT+3

morning_greetings = [
    "Wassup gamers! It's a good day to game on, so yea have fun and keep it civil \U0001f3ae",
    "Rise and grind gamers! Hope y'all ready to have a good one today \U0001f4aa\U0001f3fe",
    "Good morning WWG fam! Time to level up, stay cool and game on \U0001f579\ufe0f",
    "Yo gamers! Another day another W, let's get it and keep the vibes right \U0001f525",
    "Morning legends! Grab your controllers and let's make today count \U0001f3c6",
    "What's good gamers! New day new adventures, remember to have fun out there \u270c\U0001f3fe",
    "Ayoo WWG! The sun is up and so are we, let's game and keep it \U0001f4af",
    "Hey hey gamers! It's a beautiful day to catch some dubs, stay positive \U0001f60e",
    "Good morning everyone! Whether you're grinding or chilling, enjoy your day gamers \U0001f305",
    "Wassup fam! Another day in the gaming world, keep it fun and keep it civil \U0001f3af",
]

# --- Troll Config ---

TROLL_EXCLUDED_CHANNELS = {
    787194174549393428,
    716572818262720572,
    812233686958342145,
    740807136703021157,
    1352324423591399505,
    628278524905521179,   # greetings
    1136556546168471602,
    745494439455227955,
    1238490815580471327,
    1131832842402410618,
    1092088239600451584,  # modmail
    1092088977030393977,
    1238489063485603840,
    729602427157872752,
    1095785282575548466,
    668549913730088970,
    1355492254869098736,
    1026342989053829170,
    1026343418374397956,
    808056824024268807,
    1245077589752680550,
    1353367229453828118,
    799116876721684542,
    628279095490379777,
    1072396997232951376,
    1463410054223892543,
    658572685273726997,
    1124720930665545918,
    726444462057717770,
    819785075599474688,
    1062661844680052806,
    899175840930205748,
    846404140711149598,
    802584507412250674,
}

message_cache = deque(maxlen=50)

cursed_emojis = [
    ["\U0001f480", "\U0001f525", "\U0001f62d"],
    ["\U0001f921", "\U0001f446"],
    ["\U0001f610", "\U0001f4f8"],
    ["\U0001faf5", "\U0001f639"],
    ["\U0001f480", "\U0001f480", "\U0001f480"],
    ["\U0001f441\ufe0f", "\U0001f444", "\U0001f441\ufe0f"],
    ["\U0001f6b6", "\U0001faa4"],
    ["\U0001f4c9"],
    ["\U0001faa6"],
]

funny_nicknames = [
    # Roasts
    "Carried Every Match", "Hardstuck Bronze", "Free Kill", "Skill Issue",
    "Permanent Bot Lobby", "0 and 15 Enthusiast", "Aim Assist Dependent",
    "Uninstall Speedrunner", "Backpack (Gets Carried)", "The Weakest Link",
    "Emotional Damage", "Walking L", "Average Rage Quitter",
    "Clutch Allergic", "Peak Mediocrity", "Boosted Animal",
    # Absurd
    "14 Raccoons in a Trenchcoat", "Microwave Enthusiast", "Certified Spoon",
    "Sentient WiFi Router", "Professional Grass Toucher", "5 Rats in a Gaming Chair",
    "Fridge Raider", "Divorced Dad Energy", "Aggressive Pedestrian",
    "Tax Evading Penguin", "Legally a Sandwich", "Emotional Support NPC",
    "Unpaid Intern", "Haunted USB Stick", "That One Guy's Cousin",
    "Powered by Audacity", "Room Temperature IQ", "Main Character (Delusional)",
]

jumpscare_messages = [
    "you up?",
    "I saw what you typed in the other server \U0001f440",
    "we need to talk.",
    "don't turn around.",
    "I'm in your walls.",
    "nice search history.",
    "you forgot to mute.",
    "caught in 4k \U0001f4f8",
    "your mic was on the whole time.",
    "I know what you did last game.",
]

fake_typing_messages = [
    None, None, None,  # sends nothing (the real troll)
    "nvm", "...", "wait what", "lol",
]

take_judgements = ["L take", "W take", "mid take", "room temperature take", "freezing cold take"]

wrong_channel_messages = [
    "oops wrong channel",
    "wait this isn't DMs",
    "pretend you didn't see that",
    "ignore this",
    "that wasn't meant for here",
]

fake_mod_reasons = [
    "being too good at gaming",
    "excessive drip",
    "having a suspicious number of wins",
    "being too quiet (sus)",
    "existing without permission",
    "breathing too loud in voice chat",
    "having an opinion",
    "winning too many arguments",
    "using default skins unironically",
    "not touching grass since 2019",
]

drama_templates = [
    "I can't believe {a} said that about {b} in the other server...",
    "Nah {a} really just called {b} a bot lobby player behind their back \U0001f480",
    "So we're just gonna ignore what {a} said about {b}'s gameplay? ok.",
    "{a} told me they could 1v1 {b} blindfolded. Just putting that out there.",
    "Sources say {a} has been talking crazy about {b}. I'm just the messenger.",
    "BREAKING: {a} does NOT think {b} is good at gaming. The beef is real.",
]

conspiracy_templates = [
    "I'm convinced {user} is actually 3 accounts controlled by one person.",
    "Has anyone noticed {user} has never been seen online at the same time as the server owner? Coincidence?",
    "I have evidence that {user} is actually an AI. I will not be elaborating.",
    "{user} has been suspiciously quiet lately... what are they planning?",
    "Theory: {user} doesn't actually play games. They just watch YouTube and pretend.",
    "I ran the numbers and {user}'s win rate is statistically impossible. Just saying.",
]

afk_check_messages = [
    "you still alive?",
    "hello?? earth to {user}",
    "bro has been online for 3 hours and said nothing",
    "I know you're reading this {user}",
    "don't leave me on read {user}",
]

random_polls = [
    ("Would you rather have lag forever or only play one game for life?", ["Lag forever", "One game"]),
    ("Who carries harder?", ["Me", "Also me"]),
    ("Is water wet?", ["Yes", "No", "Banned topic"]),
    ("Would you rather fight 100 duck-sized horses or 1 horse-sized duck?", ["100 small horses", "1 big duck"]),
    ("Best excuse for losing?", ["Lag", "My controller", "I wasn't trying", "Hacker"]),
    ("Is gaming a sport?", ["Yes and I'm an athlete", "No and I don't care"]),
    ("Would you rather have aimbot but everyone knows, or be average forever?", ["Famous cheater", "Forever mid"]),
]

misquotes = [
    ("\u201cBe the change you wish to see in the world.\u201d", "\u2014 Ninja"),
    ("\u201cIn the middle of difficulty lies opportunity.\u201d", "\u2014 xQc"),
    ("\u201cThe only thing we have to fear is fear itself.\u201d", "\u2014 some guy who went 0-15"),
    ("\u201cTo be or not to be, that is the question.\u201d", "\u2014 DrDisrespect"),
    ("\u201cI think, therefore I am.\u201d", "\u2014 a Minecraft villager"),
    ("\u201cThat's one small step for man, one giant leap for mankind.\u201d", "\u2014 the first person to touch grass"),
    ("\u201cStay hungry, stay foolish.\u201d", "\u2014 every ranked teammate ever"),
    ("\u201cFloat like a butterfly, sting like a bee.\u201d", "\u2014 someone who mains Jigglypuff"),
    ("\u201cYou miss 100% of the shots you don't take.\u201d", "\u2014 Stormtroopers"),
]

fake_announcements = [
    "\U0001f4e2 **ATTENTION:** The server is shutting down permanently effective immediately.",
    "\U0001f4e2 **NEW RULE:** All messages must now be in rhyme form.",
    "\U0001f4e2 **ANNOUNCEMENT:** We are switching to a Roblox-only server.",
    "\U0001f4e2 **BREAKING:** All roles have been reset. Everyone starts from scratch.",
    "\U0001f4e2 **UPDATE:** The server is now a book club. Gaming talk is banned.",
    "\U0001f4e2 **NOTICE:** Voice chat now requires a formal dress code.",
]

# --- Hype Man ---

hype_messages = [
    "Shoutout to {user} for being absolutely goated. No reason, just felt like it.",
    "Can we get some respect for {user}? Certified legend, no debate.",
    "Just wanna say {user} is carrying this server's vibes right now \U0001f451",
    "Random appreciation post for {user}. You're valid.",
    "Everyone stop what you're doing and acknowledge {user}'s greatness.",
    "{user} walked in and the server got better. That's just facts.",
    "If this server had an MVP award it would go to {user}. Today at least.",
    "Honestly {user} doesn't get enough credit around here.",
]

# --- Dead Chat Reviver ---

hot_takes = [
    "Hot take: mobile gamers are real gamers. Fight me.",
    "Unpopular opinion: the worst game you love is better than the best game you've never played.",
    "Serious question: what game would you delete from existence if you could?",
    "Be honest: what's your most embarrassing gaming moment?",
    "If you could only play one game for the rest of your life, what is it and why?",
    "What's the most overrated game of all time? Wrong answers only.",
    "Controversial: which game has the worst fanbase?",
    "What game made you rage quit so hard you almost broke something?",
    "Real talk: what's a game everyone loves that you just can't get into?",
    "Drop your most controversial gaming opinion. No judgement (there will be judgement).",
    "What's a game you're embarrassed to admit you've never played?",
    "If you had to 1v1 anyone in this server, who are you picking and in what game?",
]

# --- Late Night Mode (midnight-5am EAT) ---

late_night_messages = [
    "Do you think fish know they're wet?",
    "What if we're all just NPCs in someone else's game?",
    "Are you gaming because you enjoy it or because the void is too loud?",
    "It's late. Why are you here instead of sleeping? Actually same.",
    "3am gaming hits different and I can't explain why.",
    "Name a game that genuinely changed your life. I'll wait.",
    "What if respawning is real and we just don't remember?",
    "At this hour nothing matters except the next game. And that's beautiful.",
    "Bro it is so late. Go to sleep. Or don't. I'm a bot not a doctor.",
    "The real endgame boss is your sleep schedule.",
    "Existential question: do you play games or do games play you?",
    "Everyone online right now is either built different or broken. No in between.",
]

# --- GN Police ---

gn_phrases = ["gn", "goodnight", "good night", "nighty night", "night night", "gnight", "g'night"]
gn_watchlist = {}  # {user_id: datetime}

gn_callouts = [
    "didn't you say goodnight like {mins} minutes ago? \U0001f928",
    "bro said gn {mins} minutes ago and is STILL HERE \U0001f480",
    "goodnight means LEAVE {user} \U0001f6aa",
    "\"gn\" is not a suggestion to yourself apparently \U0001f914",
    "the gn was a lie. {mins} minutes and counting.",
    "we all saw you say goodnight {mins} min ago {user}. explain yourself.",
]

# --- Hype Detector ---

recent_message_times = deque(maxlen=200)
hype_cooldown_until = None

hype_detector_messages = [
    "chat is ALIVE right now \U0001f525\U0001f525\U0001f525",
    "why is everyone talking at once I love it",
    "this chat is MOVING",
    "the energy in here rn is unmatched",
    "ok chat is popping off, I see you \U0001f440",
    "everyone woke up and chose to be active today huh",
]

# --- Welcome Hazing ---

fake_rules = [
    "You must greet everyone individually by name every time you enter a channel.",
    "No gaming talk on Tuesdays. We call it Thoughtful Tuesday.",
    "You must win your first game within 24 hours or face consequences.",
    "All messages must be at least 3 sentences long. One-word replies are punishable.",
    "You are required to compliment the bot daily. Failure to comply is noted.",
    "New members must share their most embarrassing gaming clip within 48 hours.",
    "You cannot use emojis for the first week. Earn them.",
    "Every new member must write a 2-paragraph essay on why gaming is a sport.",
]

welcome_messages = [
    "Welcome {user}! Your official server name is **{nick}**.\n\n\u26a0\ufe0f **Important:** Please note Rule #{num}: *{rule}*",
    "Look who just joined... {user}. From now on you will be known as **{nick}**.\n\n\U0001f4cb Don't forget Rule #{num}: *{rule}*",
    "Everyone say hi to {user}! We've assigned you the name **{nick}** for... reasons.\n\n\U0001f6a8 Rule #{num}: *{rule}*",
    "Oh great, another one. Welcome {user}, aka **{nick}**.\n\nPlease review Rule #{num}: *{rule}*. It's very real and very enforced.",
]

# --- Game Detection ---

game_notify_cooldown = {}  # {game_name: datetime}

# --- Typing Callout ---

typing_tracker = {}  # {(channel_id, user_id): datetime}

typing_callout_messages = [
    "{user} you writing a thesis over there?",
    "{user} bro just hit send already",
    "{user} typing for so long I aged a year",
    "whatever {user} is typing better be worth the wait",
    "{user} is writing the next great novel in this channel apparently",
    "someone check on {user} they've been typing for ages",
]

# --- Essay Detector ---

essay_responses = [
    "bro wrote a whole essay",
    "TL;DR anyone?",
    "this man really typed a paragraph \U0001f480",
    "I'm not reading all that. Happy for you tho. Or sorry that happened.",
    "somebody summarize this for me",
    "that's crazy bro but I ain't reading all that",
]

# --- K Energy ---

k_responses = [
    "\U0001f494",
    "the disrespect...",
    "just 'k'? really? REALLY?",
    "and they say words can't hurt",
    "emotional damage in two letters",
    "bro put zero effort into that response \U0001f62d",
]

# --- Friday Hype ---

friday_messages = [
    "IT'S FRIDAY GAMERS \U0001f3ae\U0001f525 THE GRIND STOPS FOR NO ONE",
    "FRIDAY = GAMING NIGHT. No excuses. Everyone online.",
    "Happy Friday WWG! Time to game until our eyes burn \U0001f579\ufe0f",
    "It's Friday and I'm feeling DANGEROUS. Chat better be active today.",
    "TGIF! Who's running games tonight? \U0001f3c6",
    "Friday vibes only. If you're not gaming tonight what are you even doing?",
]


# --- Morning Greeting ---

async def wait_until_morning():
    """Calculate seconds to wait until a random morning time (6am-11am GMT+3)."""
    now = datetime.now(EAT)
    random_hour = random.randint(6, 10)
    random_minute = random.randint(0, 59)
    target = now.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


@tasks.loop(hours=24)
async def morning_greeting():
    channel = client.get_channel(GREETINGS_CHANNEL_ID)
    if channel:
        greeting = random.choice(morning_greetings)
        await channel.send(greeting)


@morning_greeting.before_loop
async def before_morning_greeting():
    await client.wait_until_ready()
    wait_seconds = await wait_until_morning()
    await asyncio.sleep(wait_seconds)


# --- Helper Functions ---

def get_troll_channels(guild):
    """Get text channels that aren't excluded from trolling."""
    return [c for c in guild.text_channels if c.id not in TROLL_EXCLUDED_CHANNELS]


def get_online_members(guild):
    """Get non-bot online members."""
    return [m for m in guild.members if not m.bot and m.status != discord.Status.offline]


def is_late_night():
    """Check if it's between midnight and 5am EAT."""
    hour = datetime.now(EAT).hour
    return hour < 5


# --- Background Troll Functions ---

async def jumpscare_ping(guild):
    """Randomly ping someone with something unhinged."""
    members = get_online_members(guild)
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not members or not channel:
        return
    victim = random.choice(members)
    msg = random.choice(jumpscare_messages)
    await channel.send(f"{victim.mention} {msg}")


async def this_you(guild):
    """Repost a cached message with 'this you?'"""
    if not message_cache:
        return
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    author_id, content, _ = random.choice(message_cache)
    member = guild.get_member(author_id)
    if not member:
        return
    await channel.send(f"{member.mention} this you?\n> {content}")


async def rename_roulette(guild):
    """Give a random online member a funny nickname for 10 minutes."""
    members = get_online_members(guild)
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not members or not channel:
        return
    victim = random.choice(members)
    nickname = random.choice(funny_nicknames)
    try:
        old_nick = victim.nick
        await victim.edit(nick=nickname)
        await channel.send(
            f"\U0001f3b0 **RENAME ROULETTE** \U0001f3b0\n{victim.mention} is now **{nickname}** for the next 10 minutes!"
        )
        await asyncio.sleep(600)
        await victim.edit(nick=old_nick)
    except discord.Forbidden:
        pass


async def vibe_check(guild):
    """Post a vibe check -- a random reactor gets a funny nickname."""
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    msg = await channel.send("**VIBE CHECK** \U0001faf5\nReact to this... if you dare.")
    await msg.add_reaction("\u2705")

    await asyncio.sleep(60)

    msg = await channel.fetch_message(msg.id)
    reactors = []
    for reaction in msg.reactions:
        async for user in reaction.users():
            if user != client.user and isinstance(user, discord.Member):
                reactors.append(user)

    if not reactors:
        await channel.send("Nobody reacted... cowards. \U0001f414")
        return

    victim = random.choice(reactors)
    nickname = random.choice(funny_nicknames)
    try:
        old_nick = victim.nick
        await victim.edit(nick=nickname)
        await channel.send(f"{victim.mention} fell for it! Enjoy being **{nickname}** for 10 minutes \U0001f62d")
        await asyncio.sleep(600)
        await victim.edit(nick=old_nick)
    except discord.Forbidden:
        pass


async def wrong_channel(guild):
    """Post 'oops wrong channel' then delete it after a minute."""
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    msg = await channel.send(random.choice(wrong_channel_messages))
    await asyncio.sleep(60)
    try:
        await msg.delete()
    except discord.NotFound:
        pass


async def fake_mod_action(guild):
    """Post a fake warning for a random member."""
    members = get_online_members(guild)
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not members or not channel:
        return
    victim = random.choice(members)
    reason = random.choice(fake_mod_reasons)
    await channel.send(f"\u26a0\ufe0f **WARNING:** {victim.mention} has been warned for **{reason}**.")


async def server_drama(guild):
    """Create fake beef between two random members."""
    members = get_online_members(guild)
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if len(members) < 2 or not channel:
        return
    a, b = random.sample(members, 2)
    template = random.choice(drama_templates)
    await channel.send(template.format(a=a.mention, b=b.mention))


async def afk_check(guild):
    """Ping an online member asking if they're alive."""
    members = get_online_members(guild)
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not members or not channel:
        return
    victim = random.choice(members)
    msg = random.choice(afk_check_messages).format(user=victim.mention)
    await channel.send(msg)


async def random_poll(guild):
    """Post an absurd poll."""
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    question, options = random.choice(random_polls)
    number_emojis = ["1\ufe0f\u20e3", "2\ufe0f\u20e3", "3\ufe0f\u20e3", "4\ufe0f\u20e3"]
    text = f"\U0001f4ca **POLL:** {question}\n"
    for i, option in enumerate(options):
        text += f"{number_emojis[i]} {option}\n"
    msg = await channel.send(text)
    for i in range(len(options)):
        await msg.add_reaction(number_emojis[i])


async def motivational_misquote(guild):
    """Post a misattributed inspirational quote."""
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    quote, attribution = random.choice(misquotes)
    await channel.send(f"\U0001f4a1 **Inspirational Quote of the Day**\n\n*{quote}*\n{attribution}")


async def fake_announcement(guild):
    """Post something dramatic, edit it to 'jk' after a minute."""
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    msg = await channel.send(random.choice(fake_announcements))
    await asyncio.sleep(60)
    try:
        await msg.edit(content=f"{msg.content}\n\n*jk lol*")
    except discord.NotFound:
        pass


async def conspiracy_theory(guild):
    """Post an unhinged theory about a random member."""
    members = get_online_members(guild)
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not members or not channel:
        return
    victim = random.choice(members)
    theory = random.choice(conspiracy_templates).format(user=victim.mention)
    await channel.send(f"\U0001f9f5 **THREAD:** {theory}")


async def hype_man(guild):
    """Randomly shout out a member for no reason."""
    members = get_online_members(guild)
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not members or not channel:
        return
    victim = random.choice(members)
    msg = random.choice(hype_messages).format(user=victim.mention)
    await channel.send(msg)


async def friday_hype(guild):
    """Post a Friday hype message (only fires on Fridays)."""
    if datetime.now(EAT).weekday() != 4:
        return
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    await channel.send(random.choice(friday_messages))


# --- Background Loops ---

BACKGROUND_TROLLS = [
    jumpscare_ping,
    this_you,
    rename_roulette,
    vibe_check,
    wrong_channel,
    fake_mod_action,
    server_drama,
    afk_check,
    random_poll,
    motivational_misquote,
    fake_announcement,
    conspiracy_theory,
    hype_man,
    friday_hype,
]


@tasks.loop()
async def troll_loop():
    """Periodic troll events -- runs at random intervals."""
    if not client.guilds:
        return
    guild = client.guilds[0]

    troll = random.choice(BACKGROUND_TROLLS)
    await troll(guild)

    # Weekend/Friday: more frequent (30min-2hr), otherwise 1-4hr
    day = datetime.now(EAT).weekday()
    if day in (4, 5, 6):
        wait_hours = random.uniform(0.5, 2)
    else:
        wait_hours = random.uniform(1, 4)
    await asyncio.sleep(wait_hours * 3600)


@troll_loop.before_loop
async def before_troll_loop():
    await client.wait_until_ready()
    # Random initial delay so the bot doesn't troll immediately on startup
    await asyncio.sleep(random.randint(300, 1800))


last_message_time = None


@tasks.loop(minutes=30)
async def dead_chat_loop():
    """Revive dead chat if nobody has talked for 2+ hours."""
    global last_message_time
    if not client.guilds or last_message_time is None:
        return
    guild = client.guilds[0]
    now = datetime.now(EAT)
    silence = (now - last_message_time).total_seconds()
    if silence < 7200:  # 2 hours
        return
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    if is_late_night():
        msg = random.choice(late_night_messages)
    else:
        msg = random.choice(hot_takes)
    await channel.send(msg)
    last_message_time = now  # Reset so it doesn't spam


@dead_chat_loop.before_loop
async def before_dead_chat_loop():
    await client.wait_until_ready()


# --- Bot Events ---

@tasks.loop(seconds=gamesTimer)
async def rotate_status():
    """Rotate bot's activity status."""
    # 30% chance to show "Playing with [member]" if anyone is online
    if client.guilds and random.random() < 0.30:
        members = get_online_members(client.guilds[0])
        if members:
            member = random.choice(members)
            await client.change_presence(
                activity=discord.Game(name=f"with {member.display_name}")
            )
            return

    randomGame = random.choice(games)
    if randomGame[0] == discord.ActivityType.streaming:
        await client.change_presence(
            activity=discord.Streaming(
                name="Watu wa Gaming", url=randomGame[1]
            )
        )
    else:
        await client.change_presence(
            activity=discord.Activity(
                type=randomGame[0],
                name=randomGame[1],
            )
        )


@rotate_status.before_loop
async def before_rotate_status():
    await client.wait_until_ready()


@client.event
async def on_ready():
    print("Bot's Ready")
    if not morning_greeting.is_running():
        morning_greeting.start()
    if not troll_loop.is_running():
        troll_loop.start()
    if not dead_chat_loop.is_running():
        dead_chat_loop.start()
    if not rotate_status.is_running():
        rotate_status.start()


@client.event
async def on_member_join(member):
    """Welcome hazing -- give new members a ridiculous nickname and a fake rule."""
    if member.bot:
        return
    if random.random() > 0.20:
        return
    channel = client.get_channel(GENERAL_CHANNEL_ID)
    if not channel:
        return
    nickname = random.choice(funny_nicknames)
    rule = random.choice(fake_rules)
    rule_num = random.randint(47, 200)

    try:
        await member.edit(nick=nickname)
    except discord.Forbidden:
        nickname = None

    template = random.choice(welcome_messages)
    await channel.send(template.format(user=member.mention, nick=nickname or member.display_name, num=rule_num, rule=rule))

    # Revert nickname after random 1 hour to 1 week
    if nickname:
        wait_hours = random.uniform(1, 168)  # 1 hour to 7 days
        await asyncio.sleep(wait_hours * 3600)
        try:
            await member.edit(nick=None)
        except discord.Forbidden:
            return

        if wait_hours < 6:
            early_messages = [
                f"fine {member.mention}, you can have your name back. I was feeling generous today.",
                f"{member.mention} got lucky. I was gonna keep that name for WAY longer.",
                f"giving {member.mention} their name back early because I'm in a good mood. Don't get used to it.",
                f"{member.mention} you're free. That was just a taste of what I can do.",
                f"releasing {member.mention} from nickname jail early. Good behavior I guess.",
            ]
            await channel.send(random.choice(early_messages))
        elif wait_hours > 120:
            late_messages = [
                f"{member.mention} I almost forgot about you. Here's your name back... you earned it.",
                f"oh right {member.mention} exists. My bad. Name restored I guess.",
                f"after careful consideration (I forgot), {member.mention} can have their name back.",
                f"{member.mention} served their full sentence. Welcome back to society.",
                f"finally freeing {member.mention}. That nickname was growing on me though.",
                f"{member.mention} has been released from nickname prison. It's been real.",
            ]
            await channel.send(random.choice(late_messages))
        else:
            normal_messages = [
                f"{member.mention} alright your time is up. Name's back. You're welcome.",
                f"restoring {member.mention}'s identity. Try not to get caught again.",
                f"{member.mention} you survived. Name restored. Don't let it happen again.",
                f"giving {member.mention} their name back. It was fun while it lasted.",
            ]
            await channel.send(random.choice(normal_messages))


@client.event
async def on_presence_update(before, after):
    """Detect when someone starts playing a game others are already on."""
    if after.bot:
        return

    before_games = {a.name for a in before.activities if a.type == discord.ActivityType.playing and a.name}
    after_games = {a.name for a in after.activities if a.type == discord.ActivityType.playing and a.name}
    new_games = after_games - before_games

    if not new_games:
        return

    now = datetime.now(EAT)
    for game_name in new_games:
        # Cooldown: only notify once per game per hour
        if game_name in game_notify_cooldown:
            if (now - game_notify_cooldown[game_name]).total_seconds() < 3600:
                continue

        # Find others playing the same game
        players = []
        for m in after.guild.members:
            if m == after or m.bot:
                continue
            for a in m.activities:
                if a.type == discord.ActivityType.playing and a.name == game_name:
                    players.append(m)
                    break

        if len(players) >= 2 and random.random() < 0.10:
            msg = (
                f"\U0001f440 {after.mention} just hopped on **{game_name}** \u2014 "
                f"{', '.join(m.mention for m in players[:5])} "
                f"{'are' if len(players) > 1 else 'is'} already on it. Link up?"
            )
            for ch_id in (GENERAL_CHANNEL_ID, GAMERS_ARENA_CHANNEL_ID):
                ch = client.get_channel(ch_id)
                if ch:
                    await ch.send(msg)
            game_notify_cooldown[game_name] = now


@client.event
async def on_typing(channel, user, when):
    """Typing callout -- if someone types for 25+ seconds, call them out."""
    if user.bot:
        return
    if not hasattr(channel, "guild") or channel.guild is None:
        return
    if channel.id in TROLL_EXCLUDED_CHANNELS:
        return

    key = (channel.id, user.id)
    now = datetime.now(EAT)

    if key not in typing_tracker:
        typing_tracker[key] = now
    else:
        elapsed = (now - typing_tracker[key]).total_seconds()
        if elapsed >= 25 and random.random() < 0.30:
            msg = random.choice(typing_callout_messages).format(user=user.mention)
            await channel.send(msg)
            del typing_tracker[key]
        elif elapsed > 60:
            # Stale entry, clear it
            del typing_tracker[key]


@client.event
async def on_reaction_add(reaction, user):
    """Reaction chain -- if 3+ people react the same emoji, bot piles on."""
    if user.bot:
        return
    # Count non-bot users with this reaction
    non_bot_count = 0
    bot_already = False
    async for reactor in reaction.users():
        if reactor.id == client.user.id:
            bot_already = True
        elif not reactor.bot:
            non_bot_count += 1

    if non_bot_count >= 3 and not bot_already:
        try:
            await reaction.message.add_reaction(reaction.emoji)
        except discord.HTTPException:
            pass


@client.event
async def on_message(message):
    global last_message_time, hype_cooldown_until

    if message.author == client.user:
        return

    # --- DM Modmail: Forward user DMs to staff channel as an embed ---
    if isinstance(message.channel, discord.DMChannel):
        modmail_channel = client.get_channel(1092088239600451584)
        if not modmail_channel:
            return
        embed = discord.Embed(
            description=message.content or "*No text*",
            color=discord.Color.blue(),
            timestamp=message.created_at,
        )
        embed.set_author(
            name=str(message.author),
            icon_url=message.author.display_avatar.url,
        )
        embed.set_footer(text=f"User ID: {message.author.id}")

        await modmail_channel.send(embed=embed)

        if message.attachments:
            for file in message.attachments:
                await modmail_channel.send(file.url)

        await message.channel.send(
            f"Hey you \U0001f44b\U0001f3fe, {message.author.mention} The Staff will get back to you when they get to see your message"
        )
        return

    # --- Staff reply: Reply to an embed in the modmail channel to DM the user ---
    if message.channel.id == 1092088239600451584 and message.reference:
        try:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
        except discord.NotFound:
            return

        if not ref_msg.embeds:
            return
        footer_text = ref_msg.embeds[0].footer.text or ""
        if not footer_text.startswith("User ID: "):
            return

        user_id = int(footer_text.replace("User ID: ", ""))
        target_user = client.get_user(user_id) or await client.fetch_user(user_id)

        try:
            if message.content:
                await target_user.send(message.content)
            if message.attachments:
                for file in message.attachments:
                    await target_user.send(file.url)
            await message.add_reaction("\u2705")
        except discord.Forbidden:
            await message.channel.send("Could not DM that user \u2014 they may have DMs disabled.")
        return

    # --- Track activity for dead chat reviver ---
    if message.guild and message.channel.id not in TROLL_EXCLUDED_CHANNELS:
        last_message_time = datetime.now(EAT)

    try:
        # --- GN Police: check if sender previously said goodnight ---
        if message.guild and message.author.id in gn_watchlist:
            said_gn_at = gn_watchlist[message.author.id]
            mins = int((datetime.now(EAT) - said_gn_at).total_seconds() / 60)
            # Only call out if it's been 20 min to 3 hours since they said gn
            if 20 <= mins <= 180:
                callout = random.choice(gn_callouts).format(user=message.author.mention, mins=mins)
                await message.channel.send(callout)
                del gn_watchlist[message.author.id]
            elif mins > 180:
                # Too long ago, clear it
                del gn_watchlist[message.author.id]

        # --- GN Police: detect goodnight messages ---
        if message.guild and message.content:
            lower = message.content.lower().strip()
            if any(lower == phrase or lower.startswith(phrase + " ") or lower.endswith(" " + phrase) for phrase in gn_phrases):
                gn_watchlist[message.author.id] = datetime.now(EAT)

        # --- Keyword Triggers (only one fires per message) ---
        keyword_triggered = False

        # --- Rage Detector ---
        if not keyword_triggered and message.guild and message.content and message.channel.id not in TROLL_EXCLUDED_CHANNELS:
            content = message.content
            # Detect rage: mostly caps (70%+) and at least 10 chars, or 3+ exclamation marks
            is_caps_rage = len(content) >= 10 and sum(1 for c in content if c.isupper()) / max(len(content.replace(" ", "")), 1) > 0.70
            is_exclaim_rage = content.count("!") >= 3
            if (is_caps_rage or is_exclaim_rage) and random.random() < 0.35:
                rage_responses = [
                    "bro breathe. it's just a game.",
                    "I can feel the anger through the screen \U0001f480",
                    "somebody get this person some water",
                    "controller status: in danger",
                    "the caps lock is doing a lot of heavy lifting rn",
                    "deep breaths. in through the nose. out through the mouth.",
                    "this is a certified rage moment",
                    "I think {user} needs a break \U0001f62d",
                    "calm down before you break something",
                    "bro is HEATED. someone check on them.",
                ]
                resp = random.choice(rage_responses).format(user=message.author.mention)
                await message.reply(resp, mention_author=False)
                keyword_triggered = True

        # --- Excuse Generator ---
        if not keyword_triggered and message.guild and message.content and message.channel.id not in TROLL_EXCLUDED_CHANNELS:
            lower = message.content.lower()
            loss_phrases = ["i lost", "we lost", "took an l", "got destroyed", "got clapped", "got wrecked", "got bodied", "lost the game"]
            if any(phrase in lower for phrase in loss_phrases) and random.random() < 0.40:
                excuse_responses = [
                    "nah it was definitely lag",
                    "your controller was broken obviously",
                    "the sun was in your eyes. through the ceiling. it happens.",
                    "you were just warming up. the real game starts next round.",
                    "I blame the matchmaking tbh",
                    "the other team was clearly cheating. I ran the numbers.",
                    "your teammate sold you. not your fault.",
                    "that game doesn't count. I'm deleting it from the records.",
                    "you weren't even trying. we all know that.",
                    "it was rigged from the start honestly",
                ]
                await message.reply(random.choice(excuse_responses), mention_author=False)
                keyword_triggered = True

        # --- Cap Alarm ---
        if not keyword_triggered and message.guild and message.content and message.channel.id not in TROLL_EXCLUDED_CHANNELS:
            lower = message.content.lower()
            cap_phrases = ["i swear", "no cap", "trust me", "on my life", "on god", "deadass", "fr fr", "i promise", "not lying"]
            if any(phrase in lower for phrase in cap_phrases) and random.random() < 0.35:
                cap_responses = [
                    "\U0001f9e2\U0001f9e2\U0001f9e2",
                    "cap detected \U0001f6a8",
                    "the cap alarm is going off rn",
                    "idk bro that sounds like cap to me",
                    "my cap detector is going CRAZY right now",
                    "source: trust me bro",
                    "interesting... the lie detector determined that was cap",
                    "you said 'trust me' so now I trust you less",
                    "cap levels are off the charts \U0001f4c8",
                ]
                await message.reply(random.choice(cap_responses), mention_author=False)
                keyword_triggered = True

        # --- Flex Police ---
        if not keyword_triggered and message.guild and message.content and message.channel.id not in TROLL_EXCLUDED_CHANNELS:
            lower = message.content.lower()
            flex_phrases = ["i'm the best", "im the best", "easy win", "easy dub", "too easy", "i carried", "they can't beat me", "i'm goated", "im goated", "undefeated", "no one can", "i don't lose", "i dont lose"]
            if any(phrase in lower for phrase in flex_phrases) and random.random() < 0.40:
                flex_responses = [
                    "calm down it's not that serious \U0001f612",
                    "bro is flexing in a Discord server \U0001f480",
                    "someone humble this person please",
                    "screenshot this for when they lose next game",
                    "the ego on this one...",
                    "and then you woke up",
                    "bold words for someone in trolling distance",
                    "saved this message for later. you know, for when you lose.",
                    "ok champ. we'll see about that.",
                    "this is going on the wall of shame if you lose tonight",
                ]
                await message.reply(random.choice(flex_responses), mention_author=False)
                keyword_triggered = True

        # --- Lag Defender ---
        if not keyword_triggered and message.guild and message.content and message.channel.id not in TROLL_EXCLUDED_CHANNELS:
            lower = message.content.lower()
            if "lag" in lower.split() and random.random() < 0.40:
                lag_responses = [
                    "IT WAS DEFINITELY LAG. I believe you.",
                    "100% lag. No way that was a skill issue. Absolutely not.",
                    "I checked the servers and yeah it was lagging. Trust me.",
                    "lag is undefeated honestly",
                    "they need to fix these servers fr fr",
                    "I SAW the lag. You would've won if it wasn't for the lag.",
                    "the lag was crazy just now ngl",
                    "lag diff. nothing else to say.",
                    "bro was about to go crazy but the lag said no \U0001f480",
                ]
                await message.reply(random.choice(lag_responses), mention_author=False)
                keyword_triggered = True

        # --- Hype Detector ---
        if message.guild and message.channel.id not in TROLL_EXCLUDED_CHANNELS:
            now = datetime.now(EAT)
            recent_message_times.append(now)
            recent_count = sum(1 for t in recent_message_times if (now - t).total_seconds() < 60)
            if recent_count >= 15 and (hype_cooldown_until is None or now > hype_cooldown_until):
                await message.channel.send(random.choice(hype_detector_messages))
                hype_cooldown_until = now + timedelta(minutes=30)

        # --- Troll checks (only in non-excluded guild channels) ---
        if message.guild and message.channel.id not in TROLL_EXCLUDED_CHANNELS:

            # Silently cache messages for "this you?" feature
            if message.content and len(message.content) > 10 and random.random() < 0.10:
                message_cache.append((message.author.id, message.content, message.channel.id))

            # Essay detector (long messages, 30% chance)
            if message.content and len(message.content) > 500 and random.random() < 0.30:
                await message.reply(random.choice(essay_responses), mention_author=False)

            # K energy (short dismissive messages, 30% chance)
            elif message.content and message.content.strip().lower() in ("k", "ok", "okay", "kk"):
                if random.random() < 0.30:
                    await message.reply(random.choice(k_responses), mention_author=False)

            else:
                # Standard trolls -- 5% base, 8% on Friday/weekends
                day = datetime.now(EAT).weekday()
                troll_chance = 0.08 if day in (4, 5, 6) else 0.05

                if random.random() < troll_chance:
                    troll_type = random.randint(1, 13)

                    if troll_type == 1:
                        await message.add_reaction("\U0001f1f1")  # Random L

                    elif troll_type == 2:
                        await message.add_reaction("\U0001f480")  # Skull react

                    elif troll_type == 3:
                        combo = random.choice(cursed_emojis)  # Emoji roulette
                        for emoji in combo:
                            await message.add_reaction(emoji)

                    elif troll_type == 4:
                        # Slow clap
                        clap_emojis = ["\U0001f44f", "\U0001f44f\U0001f3fb", "\U0001f44f\U0001f3fc", "\U0001f44f\U0001f3fd", "\U0001f44f\U0001f3fe", "\U0001f44f\U0001f3ff"]
                        count = random.randint(3, 5)
                        for emoji in clap_emojis[:count]:
                            await message.add_reaction(emoji)
                            await asyncio.sleep(2)

                    elif troll_type == 5:
                        # Fake typing
                        async with message.channel.typing():
                            await asyncio.sleep(random.randint(3, 8))
                        reply = random.choice(fake_typing_messages)
                        if reply:
                            await message.channel.send(reply)

                    elif troll_type == 6:
                        await message.reply("?", mention_author=False)

                    elif troll_type == 7:
                        await message.reply("nobody asked", mention_author=False)

                    elif troll_type == 8:
                        await message.add_reaction("\U0001f9e2")  # Cap

                    elif troll_type == 9:
                        await message.add_reaction("\U0001f4ee")  # Sus

                    elif troll_type == 10:
                        await message.add_reaction("\U0001f44e")  # Disagree

                    elif troll_type == 11:
                        await message.add_reaction("\U0001f440")  # Read receipt

                    elif troll_type == 12:
                        # Countdown -- 3, 2, 1... nothing
                        for emoji in ["3\ufe0f\u20e3", "2\ufe0f\u20e3", "1\ufe0f\u20e3"]:
                            await message.add_reaction(emoji)
                            await asyncio.sleep(2)

                    elif troll_type == 13:
                        await message.reply(random.choice(take_judgements), mention_author=False)  # L/W take

            # Late night bonus trolls (extra 3% chance midnight-5am)
            if is_late_night() and random.random() < 0.03:
                await message.channel.send(random.choice(late_night_messages))

    except Exception:
        pass  # Never let troll errors break command processing

    await client.process_commands(message)


client.run(os.getenv("TOKEN"))
