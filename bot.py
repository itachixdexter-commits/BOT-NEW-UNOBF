import discord
from discord import app_commands
import os
import io
from deobfuscator import LuaDeobfuscator

# إعداد البوت باستخدام المتغير البيئي
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.deobf_engine = LuaDeobfuscator()

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

bot = MyBot()

@bot.tree.command(name="deobf", description="Deobfuscate a Lua script using multiple tools")
async def deobf(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer(thinking=True)
    
    if not file.filename.endswith(('.lua', '.luac', '.txt')):
        await interaction.followup.send("الرجاء رفع ملف Lua أو ملف نصي يحتوي على السكربت.")
        return

    try:
        content = await file.read()
        results = bot.deobf_engine.deobfuscate_all(content)
        
        final_output = ""
        for tool, output in results.items():
            final_output += f"\n--- Result from {tool} ---\n{output}\n"
        
        output_file = io.BytesIO(final_output.encode('utf-8'))
        discord_file = discord.File(fp=output_file, filename=f"deobfuscated_{file.filename}")
        
        await interaction.followup.send(content="تم الانتهاء من فك التشفير باستخدام الأدوات المتاحة:", file=discord_file)
        
    except Exception as e:
        await interaction.followup.send(f"حدث خطأ أثناء المعالجة: {str(e)}")

if __name__ == "__main__":
    if not TOKEN:
        print("حدثت مشكله اثناء فك تشفير يرجى المحاوله")
    else:
        bot.run(TOKEN)
