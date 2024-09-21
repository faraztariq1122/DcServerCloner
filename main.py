import discord
from discord.ext import commands


TOKEN = 'Your_Discord_Token'

# Intents setup
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.members = True


bot = commands.Bot(command_prefix="!", self_bot=True, intents=intents)


@bot.event
async def on_ready():
    print("DarkCloner is running")
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

async def clear_server(target_guild):
    """Delete all channels, categories, and roles in the target server."""
    # Delete all roles except @everyone
    for role in target_guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
                print(f"Deleted role: {role.name}")
            except discord.Forbidden:
                print(f"Permission denied to delete role: {role.name}")
            except discord.NotFound:
                print(f"Role not found: {role.name}")
            except Exception as e:
                print(f"Failed to delete role: {role.name} | Error: {e}")


    for category in target_guild.categories:
        try:
            for channel in category.channels:
                try:
                    await channel.delete()
                    print(f"Deleted channel: {channel.name}")
                except discord.NotFound:
                    print(f"Channel not found: {channel.name}")
                except Exception as e:
                    print(f"Failed to delete channel: {channel.name} | Error: {e}")
            try:
                await category.delete()
                print(f"Deleted category: {category.name}")
            except discord.NotFound:
                print(f"Category not found: {category.name}")
            except Exception as e:
                print(f"Failed to delete category: {category.name} | Error: {e}")
        except Exception as e:
            print(f"Failed to process category: {category.name} | Error: {e}")

    for channel in target_guild.channels:
        try:
            await channel.delete()
            print(f"Deleted channel: {channel.name}")
        except discord.NotFound:
            print(f"Channel not found: {channel.name}")
        except Exception as e:
            print(f"Failed to delete channel: {channel.name} | Error: {e}")

async def clone_server_name(source_guild, target_guild):
    """Clone the server name from the source to the target guild."""
    try:
        await target_guild.edit(name=source_guild.name)
        print(f"Server name changed to: {source_guild.name}")
    except Exception as e:
        print(f"Failed to change server name | Error: {e}")

async def copy_roles(source_guild, target_guild):
    """Clone roles from the source to the target guild."""
    roles = sorted(source_guild.roles, key=lambda r: r.position, reverse=True)  

    for role in roles:
        if role.name != "@everyone":
            try:
                await target_guild.create_role(
                    name=role.name,
                    color=role.color,
                    hoist=role.hoist,
                    mentionable=role.mentionable,
                    permissions=role.permissions
                )
                print(f"Created role: {role.name}")
            except discord.Forbidden:
                print(f"Permission denied to create role: {role.name}")
            except Exception as e:
                print(f"Failed to create role: {role.name} | Error: {e}")

async def copy_server_structure(source_guild_id, target_guild_id):
    """Copy categories, channels, roles, and server name from one server to another."""
    source_guild = bot.get_guild(source_guild_id)
    target_guild = bot.get_guild(target_guild_id)

    if not source_guild:
        print(f"Source guild with ID {source_guild_id} not found.")
        return
    if not target_guild:
        print(f"Target guild with ID {target_guild_id} not found.")
        return


    await clear_server(target_guild)


    await clone_server_name(source_guild, target_guild)


    await copy_roles(source_guild, target_guild)


    for category in source_guild.categories:
        new_category = await target_guild.create_category(name=category.name)
        print(f"Created category: {new_category.name}")

        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                await new_category.create_text_channel(name=channel.name, topic=channel.topic)
                print(f"Created text channel: {channel.name}")
            elif isinstance(channel, discord.VoiceChannel):
                await new_category.create_voice_channel(name=channel.name)
                print(f"Created voice channel: {channel.name}")


    for channel in source_guild.channels:
        if channel.category is None:
            if isinstance(channel, discord.TextChannel):
                await target_guild.create_text_channel(name=channel.name, topic=channel.topic)
                print(f"Created text channel: {channel.name}")
            elif isinstance(channel, discord.VoiceChannel):
                await target_guild.create_voice_channel(name=channel.name)
                print(f"Created voice channel: {channel.name}")

@bot.command()
async def clone(ctx, source_guild_id: int, target_guild_id: int):
    """Command to start cloning server structure."""
    await copy_server_structure(source_guild_id, target_guild_id)
    await ctx.send("Server structure cloning complete.")


bot.run(TOKEN, bot=False)
