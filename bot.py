import discord
from discord.ext import commands
from discord.ui import View, Button
import random

# -------------------------------
# 봇 설정
# -------------------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# -------------------------------
# 결과 저장용
# -------------------------------
roll_results = {}

# -------------------------------
# 버튼 UI 클래스
# -------------------------------
class DiceRollView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.message = None

    @discord.ui.button(label="🎲 주사위 굴리기", style=discord.ButtonStyle.primary)
    async def roll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user

        if user.id in roll_results:
            await interaction.response.defer()
            return

        roll = random.randint(1, 100)
        roll_results[user.id] = (user.display_name, roll)

        # 높은 수부터 정렬
        sorted_results = sorted(roll_results.values(), key=lambda x: x[1], reverse=True)

        # 등수 파란색 강조 (ANSI 코드 사용)
        result_text = "**🎲 주사위 결과:**\n```ansi\n"
        for idx, (name, value) in enumerate(sorted_results, start=1):
            result_text += f"\x1b[34m{idx:>2}위\x1b[0m {name:<15}{value:>3}\n"
        result_text += "```"

        await self.message.edit(content=result_text, view=self)
        await interaction.response.defer()

# -------------------------------
# 슬래시 커맨드: 주사위 시작
# -------------------------------
@tree.command(name="startroll", description="주사위 굴리기 시작")
async def startroll(interaction: discord.Interaction):
    global roll_results
    roll_results = {}

    if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
        await interaction.response.send_message("봇에게 메시지 권한이 없습니다.", ephemeral=True)
        return

    view = DiceRollView()
    message = await interaction.channel.send("🎲 주사위를 굴려보세요! (한 사람당 1번만)", view=view)
    view.message = message
    await interaction.response.send_message("주사위 버튼이 생성되었습니다!", ephemeral=True)

# -------------------------------
# 슬래시 커맨드: 현재 결과 확인
# -------------------------------
@tree.command(name="showresults", description="현재까지 굴린 주사위 결과 확인")
async def showresults(interaction: discord.Interaction):
    if not roll_results:
        await interaction.response.send_message("아직 굴린 결과가 없습니다.", ephemeral=True)
        return

    sorted_results = sorted(roll_results.values(), key=lambda x: x[1], reverse=True)
    result_text = "**🎲 현재 주사위 결과:**\n```ansi\n"
    for idx, (name, value) in enumerate(sorted_results, start=1):
        result_text += f"\x1b[34m{idx:>2}위\x1b[0m {name:<15}{value:>3}\n"
    result_text += "```"

    await interaction.response.send_message(result_text, ephemeral=True)

# -------------------------------
# 봇 준비 완료 시 슬래시 커맨드 동기화
# -------------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} 봇이 온라인입니다!")

# -------------------------------
# Discord 봇 토큰 실행
# -------------------------------

# 여기에 Discord 봇 토큰 붙여넣기 (반드시 따옴표 안에!)
bot.run(os.environ["DISCORD_TOKEN"])
