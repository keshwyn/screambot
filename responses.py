#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from string import Template

COMMAND_REGEX = "^<@(|[WU].+?)> (.+)"

# It's a command to @screambot and this is the entire thing.
STANDALONE_COMMANDS = {
  "botsnack": ":cookie:",
  "freak out": "*breathes into a paper bag*",
  "lose it": "I am kind of losing my shit right now?",
  "lose your shit": "I am kind of losing my shit right now?",
  "scream": "AAAARRGGHHHHHHHHHHHHHH",
  "thank you": "Glad to help <3",
  "thanks": "Any time, friend.",
  "hug": ":virtualhug:",
  "flip": "(╯°□°）╯︵ ┻━┻)",
  ":heart:": ":heart:",
  ":poop:": "Seriously.",
  "yo": "Yo.",
  ":yo:": "Yo.",
}

# It's a direct command to @screambot and it starts with this.
# "$what" will be replaced with the thing to scream about.
# TODO: Add "$who" and figure out how to talk to.
STARTER_COMMANDS = {
  "announce that ": ":star: :star: EXCUSE ME HI I HAVE AN ANNOUNCEMENT: $what :star: :star:",
  "freak out about ": "I am LOSING MY SHIT about $what right now.",
  "lose it about ": "AGH what is the deal with $what?",
  "react to ": "EXCUSE ME HI I have opinions about $what",
  "lose your shit about ": "OH SHIT did you know about $what?",
  "hug ": ":virtualhug: for $what",
  "blame ": "Grr, $what strikes again.",
  "flip ": "╯°□°）╯︵ ┻━�",
  "hate ": "I hate $what SO MUCH. Ugh, the worst.", 
  # look, I know this is terrible, but I'm too lazy to handle nice little functions today.
  "scream ": "FUNCTION:UPPERCASE $what",
  "help": "FUNCTION:HELP",
  "what can you ": "FUNCTION:HELP",
}

# Behave exactly as starter commands but aren't in the "what can you do" list.
# Easter eggs, I guess :-)
STARTER_COMMANDS_EE = {
  "you": "I promise to always try.",
  "is ": "I'm just a small bot making my way in the world.",
  "I love you": "It's mutual, I promise you.",
  "<3": "Right back at you <3",
  "why ": "I'm a simple bot. It is not for me to speculate.",
  "good bot": ":heart:",
}

# It's a direct command to @screambot and it contains this text.
CONTAIN_COMMANDS = {
  "botsnack": ":cookie:",
  "code": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :computer:",
  "github": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :computer:",
  "can you even": "I literally can't even.",
  "work": "WERK!",
}

# It's not a command but it contains the word screambot and this text.
CONVERSATION = {
  "botsnack": ":cookie:",
  "code": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR.",
  "github": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR.",
  "thank": "Any time.",
  ":heart:": ":heart_eyes:",
  "love": ":heart_eyes:",
  "good": ":heart_eyes:",
}

def help_message():
  """Returns a user message explaining what this is."""
  commands = set()
  for s in STANDALONE_COMMANDS.keys():
    commands.add(s)
  for s in STARTER_COMMANDS.keys():
    commands.add(s.rstrip(" "))

  return ("Hi, I'm Screambot. I'm running on Tanya's GCE VM. I see all " +
         "traffic on any channel I'm invited to, but I promise I don't log "
         "anything. You can see and modify my code at " +
         "https://github.com/whereistanya/screambot\n" +
         "Commands: " + "; ".join(sorted(commands)))

def create_response(message, bot_id):
  """Return a response to the message if it's about screambot.

  Args:
    message: (str) The entire line that someone typed. Slack sends these to us.
    bot_id: (str) Screambot's userid. It looks like "@U1234566"
  Returns:
    (str) A string to respond with or None.
  """
  # Only trigger on sentences containing "screambot" or @screambot's UID.
  if bot_id.lower() not in message.lower() and "screambot" not in message.lower():
    return

  user = None
  command = None
  # First handle commands starting with a username (@screambot or screambot)
  if message.lower().startswith("screambot "):
    user = "screambot"
    command = message[len("screambot "):]
  else:
    matches = re.search(COMMAND_REGEX, message)
    if matches:
    # Matches things like "@screambot scream a thing" and "@tanya some message"
      user = matches.group(1)  # Who was mentioned, e.g., screambot or tanya
      if user != bot_id: # It was a message for someone else that included the word 'screambot'
        return "You're talking about me <3"
      command = matches.group(2).lower() # Everything past the name: "do a thing".

  if user and command:
    # A complete command like "hug" or "freak out".
    if command in STANDALONE_COMMANDS:
      return STANDALONE_COMMANDS[command]

    # A single emoji, not counting any caught by the STANDALONE_COMMANDS.
    if re.match(":[\w_-]+:", command):
      return command + command + command + "!"

    # A command at the start of the line, like scream or hate. We maintain two
    # dictionaries: the ones we want to show up in the help message and cute
    # surprise extras. We combine them here.
    starts = STARTER_COMMANDS.copy()
    starts.update(STARTER_COMMANDS_EE.copy())

    for text in starts.keys():
      if command.startswith(text.lower()):
        thing = command[len(text):] # Everything but the starter words
        # The template replaces "$what" with the rest of the line.
        string = Template(starts[text]).safe_substitute(what=thing)
        if string.startswith("FUNCTION:UPPERCASE "):
          return string.lstrip("FUNCTION:UPPERCASE ").upper()
        if string.startswith("FUNCTION:HELP"):
          return help_message()
        return string

    # A command that contains a word that wasn't caught by the STARTER_COMMANDS.
    # The template is to replace "$what" with the entire command. 
    for text in CONTAIN_COMMANDS.keys():
      if text in command:
        template = Template(CONTAIN_COMMANDS[text])
        return template.safe_substitute(what=command)

    # A direct command we don't know how to handle.
    return "I don't know how to %s" % command
 
  # Now handle messages that don't start with @screambot/screambot, but use
  # her name somewhere in the sentence.
  for text in CONVERSATION.keys():
    if text in message.lower():
      template = Template(CONVERSATION[text])
      return template.safe_substitute(what=text)

  return "Want me to do something? Start your message with @screambot."

