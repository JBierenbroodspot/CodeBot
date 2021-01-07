from logging import log
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
from PIL import Image
import requests

class Bot:
  """
  A discord bot.
  
  It logs messages by default and its default log path is 'log.txt'
  
  Optional attributes:
    log: Check wether logging is enabled
    log_file: Log output file
  """
  def __init__(self, log: bool=True, log_file: str='log.txt'):
    self._log = log
    self._log_file = log_file

  def clog(self, 
           user: discord.member.Member, 
           content: str, channel: discord.channel.TextChannel, 
           time: discord.channel.TextChannel
           ) -> None:
    """
    Logs message, returns None
    
    Parameters:
      user: User who wrote the message
      content: Body of the message
      channel: Channel the message has been sent in
      time: The time at which the message has been sent
    """
    _message = f'{user} wrote \'{content}\' in {channel} at {time}\n'
    if self._log:
      with open(self._log_file, 'a+') as file:
        # Format message into utf-8 as unicode does not show properly in file
        file.write(_message.encode('ascii', 'ignore').decode('utf-8'))
    return None
        
  def enable_logging(self) -> str:
    """Toggles logging on, return string with log status"""
    if self._log:
      _string = 'Logging is already enabled!'
    else:
      self._log = True
      _string = 'Logging is now enabled!'
      self.write_log('##### Logging is enabled #####\n')
    return _string

  def disable_logging(self) -> str:
    """Toggles logging off, return string with log status"""
    if not self._log:
      _string = 'logging is already disabled!' 
    else:
      self._log = False
      _string = 'Logging is now disabled!'
      self.write_log('##### Logging disabled #####\n')
    return _string

  def shift_image(self, image_url: str, shift: int=20) -> discord.File:
    """
    Shifts the value of every pixel in image by set amount
    
    Parameters:
      image_url: URL leading to image
      
    Optional parameters:
      shift: Amount every pizel in image should be changed by. Should be value bteween -255 and 255
    """
    img = Image.open(self.get_image(image_url))
    pixels = img.load()
    for _col in range(img.size[1]):
      for _row in range(img.size[0]):
        _pixel = [x + shift -255 if x > 255 - shift else x + shift for x in list(pixels[_row,_col])]
        pixels[_row,_col] = tuple(_pixel)
    img.save('img_new.png')
    return discord.File('img_new.png', filename='img_new.png')

  @staticmethod
  def get_image(image_url: str, file: str='img.png') -> str:
    """Downloads image to set file, returns string"""
    with open(file, 'wb+') as _file:
      _file.write(requests.get(image_url).content)
    return file


# ================ Initialize ================ #
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
cbot = Bot()
bot = commands.Bot(command_prefix='>')

# ================ Bot commands ================ #
@bot.command(name='test', help='tests the bot')
async def test(ctx):
  print('>test')
  await ctx.send('oke')

@bot.command(name='log', help='disables/enables logging')
async def log(ctx, onoff: str):
  if onoff == 'on':
    await ctx.send(cbot.enable_logging())
  elif onoff == 'off':
    await ctx.send(cbot.disable_logging())

@bot.command(name='enhance', help='\'enhances\' image in attachment', pass_context=True)
async def enhance(ctx, shift: int):
  if shift != None:
    _file = cbot.shift_image(ctx.message.attachments[0].url, shift)
  else:
    _file = cbot.shift_image(ctx.message.attachments[0].url)
  await ctx.send('here you go!', file=_file)

# ================ Bot events ================ #
@bot.event
async def on_ready():
  print("ready")

@bot.event
async def on_member_join(member):
  _channel = bot.get_channel(630702417155194881)
  await _channel.send("welcome {}".format(member.name))

@bot.event
async def on_message(message):
  # Do not make general on_message returns as bot listens to self
  print(f'{message.author}, {message.content}, {message.channel}')
  cbot.clog(message.author, message.content, message.channel, message.created_at)

  # Prevents on_mesage conflict with commands  
  await bot.process_commands(message)


bot.run(TOKEN)
