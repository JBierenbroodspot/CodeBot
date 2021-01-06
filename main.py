import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
from PIL import Image
import requests

class Cbot():

  def __init__(self, log=True, log_file='log.txt'):
    self.log = log
    self.message = 'Default message!'

  def clog(self, user, content, channel, time):
    if self.log:
      self.write_log(f'{user} wrote \'{content}\' in {channel} at {time}\n')
        
  def enable_logging(self):
    if self.log:
      _string = 'Logging is already enabled!'
    else:
      self.log = True
      _string = 'Logging is now enabled!'
      self.write_log('##### Logging is enabled #####\n')
    return _string

  def disable_logging(self):
    if not self.log:
      _string = 'logging is already disabled!' 
    else:
      self.log = False
      _string = 'Logging is now disabled!'
      self.write_log('##### Logging disabled #####\n')
    return _string

  def shift_image(self, image_url, shift=20):
    img = Image.open(self.get_image(image_url))
    pixels = img.load()
    for _col in range(img.size[1]):
      for _row in range(img.size[0]):
        _pixel = [x + shift -255 if x > 255 - shift else x + shift for x in list(pixels[_row,_col])]
        pixels[_row,_col] = tuple(_pixel)

    img.save('img_new.png')
    return discord.File('img_new.png', filename='img_new.png')

  def encrypt_message(self, message, key):
    for char in list(chr(message)):
      pass
            

  @staticmethod
  def write_log(message, file='log.txt'):
    with open(file, 'a+') as _file:
      # unicode messes with write()
      _file.write(message.encode('ascii', 'ignore').decode('utf-8'))

  @staticmethod
  def get_image(image_url, file='img.png'):
    with open(file, 'wb+') as _file:
      _file.write(requests.get(image_url).content)
    return file


# ================ Initialize ================ #
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
cbot = Cbot()
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

##@bot.command(name='shoo', help='this brutally murders the bot, do not use')
##async def shoo(ctx):
##  await ctx.send('bye bye')
##  exit()

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
