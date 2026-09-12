import discord
from discord import app_commands
from discord.ext import commands
import database as db

PER_PAGE = 10


class RosterView(discord.ui.View):
    def __init__(self, players: list[dict]):
        super().__init__(timeout=180)
        self.players = players
        self.page = 0
        self.max_page = max((len(players) - 1) // PER_PAGE, 0)
        self._update_buttons()

    def _update_buttons(self):
        self.clear_items()
        prev_btn = discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="⬅", label="Previous")
        prev_btn.callback = self.previous
        prev_btn.disabled = self.page <= 0
        self.add_item(prev_btn)

        page_label = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"Page {self.page + 1}/{self.max_page + 1}",
            disabled=True,
        )
        self.add_item(page_label)

        next_btn = discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="➡", label="Next")
        next_btn.callback = self.next
        next_btn.disabled = self.page >= self.max_page
        self.add_item(next_btn)

    def build_embed(self) -> discord.Embed:
        start = self.page * PER_PAGE
        end = min(start + PER_PAGE, len(self.players))
        page_players = self.players[start:end]

        lines = []
        for i, p in enumerate(page_players, start=start + 1):
            total = p["pvm_points"] + p["community_points"]
            lines.append(
                f"`{i}.` <@{p['user_id']}>\n"
                f"↳ `{total}` pts  `(PVM: {p['pvm_points']} | CMM: {p['community_points']})`"
            )

        embed = discord.Embed(
            title=f"↳ Clan Roster ({len(self.players)} members)",
            description="\n\n".join(lines) if lines else "No members.",
            color=discord.Color.purple(),
        )
        embed.set_footer(text=f"↳ Page {self.page + 1}/{self.max_page + 1} • Indigo Bot")
        return embed

    async def previous(self, interaction: discord.Interaction):
        self.page = max(self.page - 1, 0)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    async def next(self, interaction: discord.Interaction):
        self.page = min(self.page + 1, self.max_page)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.build_embed(), view=self)


class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="points", description="View a player's points in both categories")
    @app_commands.describe(user="The player to check (defaults to yourself)")
    async def points(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        player = db.get_player(target.id)

        if not player:
            embed = discord.Embed(
                title="❌ Player Not Found",
                description=f"{target.mention} is not in the clan roster.\nAn admin must use `/add_player` first.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        total = player["pvm_points"] + player["community_points"]

        embed = discord.Embed(
            title=f"⬦ {player['username']}'s Points",
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="⚔️ PVM Points", value=f"```{player['pvm_points']}```", inline=True)
        embed.add_field(name="🤝 Community Points", value=f"```{player['community_points']}```", inline=True)
        embed.add_field(name="📊 Total", value=f"```{total}```", inline=True)
        embed.set_footer(text="Indigo Bot • OSRS Clan Points System")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="my_points", description="Quick view of your own points")
    async def my_points(self, interaction: discord.Interaction):
        player = db.get_player(interaction.user.id)

        if not player:
            embed = discord.Embed(
                title="❌ Player Not Found",
                description="You are not in the clan roster.\nAn admin must use `/add_player` first.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        total = player["pvm_points"] + player["community_points"]

        embed = discord.Embed(
            title=f"⬦ {player['username']}'s Points",
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.add_field(name="⚔️ PVM Points", value=f"```{player['pvm_points']}```", inline=True)
        embed.add_field(name="🤝 Community Points", value=f"```{player['community_points']}```", inline=True)
        embed.add_field(name="📊 Total", value=f"```{total}```", inline=True)
        embed.set_footer(text="Indigo Bot • OSRS Clan Points System")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="roster", description="View all clan roster members with page navigation")
    async def roster(self, interaction: discord.Interaction):
        players = db.get_all_players()

        if not players:
            embed = discord.Embed(
                title="📋 Clan Roster",
                description="No players in the clan roster yet.",
                color=discord.Color.purple(),
            )
            await interaction.response.send_message(embed=embed)
            return

        view = RosterView(players)
        await interaction.response.send_message(embed=view.build_embed(), view=view)

    @app_commands.command(name="leaderboard", description="View top players by total points")
    async def leaderboard(self, interaction: discord.Interaction):
        players = db.get_all_players()

        if not players:
            embed = discord.Embed(
                title="📋 Leaderboard",
                description="No players in the clan roster yet.",
                color=discord.Color.purple(),
            )
            await interaction.response.send_message(embed=embed)
            return

        top = players[:10]
        medals = ["🥇", "🥈", "🥉"] + ["⬦"] * 7

        lines = []
        for i, p in enumerate(top):
            total = p["pvm_points"] + p["community_points"]
            lines.append(f"{medals[i]} **{p['username']}** — `{total}` pts  `(PVM: {p['pvm_points']} | CMM: {p['community_points']})`)")

        embed = discord.Embed(
            title="📋 Clan Leaderboard — Top 10",
            description="\n".join(lines),
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Indigo Bot • OSRS Clan Points System")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Points(bot))
