"""All message templates and lists used by the bot."""

import discord

# --- Bot Status ---

games = [
    (discord.ActivityType.listening, "Geekspeak Radio"),
    (discord.ActivityType.watching, "My inbox for new messages"),
    (discord.ActivityType.watching, "Watu wa Gaming on YouTube"),
    (discord.ActivityType.streaming, "https://www.youtube.com/@watuwagaming"),
]

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

gn_callouts = [
    "didn't you say goodnight like {mins} minutes ago? \U0001f928",
    "bro said gn {mins} minutes ago and is STILL HERE \U0001f480",
    "goodnight means LEAVE {user} \U0001f6aa",
    "\"gn\" is not a suggestion to yourself apparently \U0001f914",
    "the gn was a lie. {mins} minutes and counting.",
    "we all saw you say goodnight {mins} min ago {user}. explain yourself.",
]

# --- Hype Detector ---

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

# --- Typing Callout ---

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
