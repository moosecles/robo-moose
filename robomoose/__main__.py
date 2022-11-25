import os
from platform import node
from __init__ import *
import hikari
import lightbulb
import lavaplayer
import asyncio


# This block creates the botApp
bot = lightbulb.BotApp(
    token = TOKEN_ID,  #uses init TOKEN_ID we set
    prefix = '/',      #For now it uses the prefix / but will change this later
    intents = hikari.Intents.ALL,   #Intents means what permission the bot has
    default_enabled_guilds = GUILD_ID, #This just loads our test server fast
)

#Linking the lavalink server
lavalink = lavaplayer.Lavalink(
    host="" #Enter your server's ID Here
    port= #Enter your server's password Here,
    password=#Enter a password here
    user_id=#Enter a user id here
)


"""

THIS IS THE START OF THE MUSIC COMMANDS

"""

# The join command
@bot.command()
@lightbulb.command(name="join", description="join voice channel")
@lightbulb.implements(lightbulb.SlashCommand)
async def join_command(ctx: lightbulb.context.Context):
    states = bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]
    is_bot_in = [state async for state in states.iterator().filter(lambda i: i.user_id == #ENTER YOUR BOTS ID HERE)] 
    print (voice_state)
    if not voice_state:
        await ctx.respond("You are not in a voice channel")
        return
    if not is_bot_in:
        channel_id = voice_state[0].channel_id
        await bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
        await lavalink.wait_for_connection(ctx.guild_id)
        await ctx.respond(f"Joining, <#{channel_id}>!")
        return
    await ctx.respond("I can't join twice!")


# The play command
@bot.command()
@lightbulb.option(name="input", description="...", required=True)
@lightbulb.command(name="play", description="Play some music through the bot!", aliases=["p"])
@lightbulb.implements(lightbulb.SlashCommand)
async def play_command(ctx: lightbulb.context.Context):
    states = bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]
    is_bot_in = [state async for state in states.iterator().filter(lambda i: i.user_id == #ENTER YOUR BOTS ID HERE)]
    query = ctx.options.input # get query from options)
    result = await lavalink.auto_search_tracks(query)  # search for the query
    if not voice_state:
        await ctx.respond("You are not in a voice channel")
        return
    if not is_bot_in:
        channel_id = voice_state[0].channel_id
        await bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
        await lavalink.wait_for_connection(ctx.guild_id)
    if not result:
        await ctx.respond("Nothing is showing up.")
        return
    elif isinstance(result, lavaplayer.TrackLoadFailed):
        await ctx.respond("Track load failed, try again later.\n```{}```".format(result.message))
        return
    elif isinstance(result, lavaplayer.PlayList):
        await lavalink.add_to_queue(GUILD_ID, result.tracks, ctx.author.id)
        await ctx.respond(f"added {len(result.tracks)} tracks to queue")
        return 

    await lavalink.play(GUILD_ID, result[0], ctx.author.id)  # play the first result
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")  # send the embed

#The skip command
@bot.command()
@lightbulb.command(name="skip", description="Skip the music!", aliases=["sk"])
@lightbulb.implements(lightbulb.SlashCommand)
async def skip_command(ctx: lightbulb.context.Context):
    await lavalink.skip(ctx.guild_id)
    await ctx.respond("Skipped the track!")

#The stop command
@bot.command()
@lightbulb.command(name="stop", description="Stop command", aliases=["s"])
@lightbulb.implements(lightbulb.SlashCommand)
async def stop_command(ctx: lightbulb.context.Context):
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("Music is stopped.")

#The pause command
@bot.command()
@lightbulb.command(name="pause", description="Pause command")
@lightbulb.implements(lightbulb.SlashCommand)
async def pause_command(ctx: lightbulb.context.Context):
    await lavalink.pause(ctx.guild_id, True)
    await ctx.respond("Pausing the music...")

#The resume command
@bot.command()
@lightbulb.command(name="resume", description="Resume command")
@lightbulb.implements(lightbulb.SlashCommand)
async def resume_command(ctx: lightbulb.context.Context):
    await lavalink.pause(ctx.guild_id, False)
    await ctx.respond("Resuming the party!")

#The seek command
@bot.command()
@lightbulb.option(name="position", description="Position to seek", required=True)
@lightbulb.command(name="seek", description="Seek command")
@lightbulb.implements(lightbulb.SlashCommand)
async def seek_command(ctx: lightbulb.context.Context):
    position = ctx.options.position
    await lavalink.seek(ctx.guild_id, position)
    await ctx.respond(f"Seeking to... {position}")

#The queue command
@bot.command()
@lightbulb.command(name="queue", description="Queue command")
@lightbulb.implements(lightbulb.SlashCommand)
async def queue_command(ctx: lightbulb.context.Context):
    node = await lavalink.get_guild_node(ctx.guild_id)
    embed = hikari.Embed(
        description="\n".join(
            [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)])
    )
    await ctx.respond(embed=embed)

#The 'now playing' command
@bot.command()
@lightbulb.command(name="np", description="Now playing command")
@lightbulb.implements(lightbulb.SlashCommand)
async def np_command(ctx: lightbulb.context.Context):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("Nothing is playing!")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")

#The shuffle command
@bot.command()
@lightbulb.command(name="shuffle", description="Shuffle command")
@lightbulb.implements(lightbulb.SlashCommand)
async def shuffle_command(ctx: lightbulb.context.Context):
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("Shuffled!")

#The leave command
@bot.command()
@lightbulb.command(name="leave", description="Leave command")
@lightbulb.implements(lightbulb.SlashCommand)
async def leave_command(ctx: lightbulb.context.Context):
    await bot.update_voice_state(ctx.guild_id, None)
    await ctx.respond("I ain't wanna be here anyway.")




"""
THIS IS THE START OF THE LISTENER EVENTS
"""


# Listens for the event (Started Event) this event tells you when the bot has started)
@bot.listen(hikari.StartedEvent)                                           
async def on_started(event:hikari.StartedEvent ) -> None:
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.set_user_id(bot.get_me().id)
    lavalink.connect()

# Registers the command
@bot.command
# Sets the command (name of command, description of command)
@lightbulb.command('ping', 'Checks to see if the bot is up and working')
# Tells discord we are going to be using the slash feature
@lightbulb.implements(lightbulb.SlashCommand)
# Function that takes the message content and then will make RoboMoose reply (aka respond) to said message
async def alive(ctx: lightbulb.MessageContext) -> None:
    await ctx.respond("Pong!")



@bot.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    await lavalink.raw_voice_state_update(event.guild_id, event.state.user_id, event.state.session_id, event.state.channel_id)

@bot.listen(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()
    bot.run()
    