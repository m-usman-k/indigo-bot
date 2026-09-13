import os
import discord
from discord.ext import commands

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR = os.path.join(BASE_DIR, "images")


def image(filename: str) -> discord.File:
    return discord.File(os.path.join(IMAGE_DIR, filename))


class IntroView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

        ranks = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Ranks & Points",
            custom_id="intro_ranks",
        )
        ranks.callback = self.ranks_callback
        self.add_item(ranks)

        apply = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Application Process",
            custom_id="intro_apply",
        )
        apply.callback = self.apply_callback
        self.add_item(apply)

        reqs = discord.ui.Button(
            style=discord.ButtonStyle.blurple,
            label="Requirements",
            custom_id="intro_requirements",
        )
        reqs.callback = self.requirements_callback
        self.add_item(reqs)

    def _cog(self, interaction: discord.Interaction):
        return interaction.client.get_cog("Info")

    async def ranks_callback(self, interaction: discord.Interaction):
        cog = self._cog(interaction)
        if cog is not None:
            await cog.ranks_info(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Error",
                    description="The info system is not available right now.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

    async def apply_callback(self, interaction: discord.Interaction):
        cog = self._cog(interaction)
        if cog is not None:
            await cog.apply_info(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Error",
                    description="The info system is not available right now.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )

    async def requirements_callback(self, interaction: discord.Interaction):
        cog = self._cog(interaction)
        if cog is not None:
            await cog.requirements_info(interaction)
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Error",
                    description="The info system is not available right now.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="intro", description="Post the welcome message with the info buttons (admin only)")
    @commands.has_permissions(administrator=True)
    async def intro(self, ctx):
        embed = discord.Embed(
            title="Welcome to Indigo",
            description=(
                "Welcome to Indigo — an Oldschool RuneScape raid & PVM clan.\n\n"
                "We are a 115+ combat clan that grinds raids and PVM together, "
                "tracking **PVM Points** and **Community Points** so members can "
                "progress through the ranks.\n\n"
                "Use the buttons below to learn more:\n"
                "↳ **Ranks & Points** — the rank progression and how points work\n"
                "↳ **Application Process** — how to join Indigo\n"
                "↳ **Requirements** — combat, stats and gear requirements"
            ),
            color=discord.Color.blurple(),
        )
        embed.set_footer(text="Indigo")
        await ctx.send(embed=embed, view=IntroView())

    async def ranks_info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Ranks & Points",
            description=(
                "Here is our rank progression. The bottom of this message shows "
                "our different ranks & what is required to reach them.\n\n"
                "Ranking up requires a combination of **PVM Points** & "
                "**Community Points**.\n\n"
                "**PVM Points** are gained by receiving drops from certain "
                "encounters across the game! The bottom of this message shows the "
                "spreadsheet for all eligible items and their point values.\n\n"
                "**Community Points** are earned by contributing to and "
                "participating in Indigo.\n\n"
                "Current ways to earn Community Points include:\n"
                "↳ Recruit a new member: **+40 points**\n"
                "↳ Small clan events such as masses, maxing parties, BOTW/SOTW, "
                "etc.: **+20 points**\n"
                "↳ Clan coffer donations: **+1 point per 1M gp donated**\n"
                "↳ Discord boosting: **+50 points per boost, per month**\n"
                "↳ Getting a drop while grouping with clan members: **5 points to "
                "everyone that participated**"
            ),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(
            embed=embed,
            files=[image("image1.png"), image("image2.png")],
            ephemeral=True,
        )

    async def apply_info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Application Process",
            description=(
                "To apply to Indigo please open a ticket in "
                "<#1539435366749052968> and post a screenshot of your gear using "
                'the image in **"Requirements"** as a reference to understand what '
                "our minimum gear requirements are."
            ),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def requirements_info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Requirements",
            description=(
                "Indigo is a **115+ combat** raid & PVM clan.\n\n"
                "Here are our stat and gear requirements:\n\n"
                "**Combat Level:** 115+\n"
                "**Attack:** 90+\n"
                "**Strength:** 90+\n"
                "**Defence:** 90+\n"
                "**Ranged:** 90+\n"
                "**Prayer:** 77+ (Rigour & Augury)\n"
                "**Magic:** 94+ (Ice Barrage)\n\n"
                "**A note for ironmen and maybe undergeared mains**\n"
                "If you do not meet this gear requirements just post the best of "
                "what you have anyway when you apply in the ticket. If you meet "
                "every requirement but are short by 1 or 2 pieces we can talk "
                "about it."
            ),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(
            embed=embed,
            files=[image("image3.png")],
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Info(bot))