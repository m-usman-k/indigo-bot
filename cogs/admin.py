import io
import discord
from discord import app_commands
from discord.ext import commands
import database as db


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="add_player", description="Add a player to the clan roster (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The Discord user to add", name="In-game name")
    async def add_player(self, interaction: discord.Interaction, user: discord.Member, name: str):
        if db.player_exists(user.id):
            embed = discord.Embed(
                title="❌ Already Exists",
                description=f"{user.mention} is already in the clan roster.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        db.add_player(user.id, name)

        embed = discord.Embed(
            title="✅ Player Added",
            description=(
                f"**{name}** has been added to the clan roster.\n"
                f"**Discord:** {user.mention}"
            ),
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove_player", description="Remove a player from the clan roster (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The player to remove")
    async def remove_player(self, interaction: discord.Interaction, user: discord.Member):
        player = db.get_player(user.id)
        if not player:
            embed = discord.Embed(
                title="❌ Not Found",
                description=f"{user.mention} is not in the clan roster.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        db.remove_player(user.id)

        embed = discord.Embed(
            title="✅ Player Removed",
            description=f"**{player['username']}** has been removed from the clan roster.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="award_community", description="Award community points to a player (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        user="The player to award points to",
        points="Number of community points",
        reason="Reason for the award"
    )
    async def award_community(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        points: int,
        reason: str = "No reason provided",
    ):
        player = db.get_player(user.id)
        if not player:
            embed = discord.Embed(
                title="❌ Player Not Found",
                description=f"{user.mention} is not in the clan roster.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        db.add_community_points(user.id, points)
        updated = db.get_player(user.id)

        embed = discord.Embed(
            title="✅ Community Points Awarded",
            description=(
                f"**{player['username']}** received `{points}` community points.\n\n"
                f"**Reason:** {reason}\n"
                f"**Total Community Points:** `{updated['community_points']}`"
            ),
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

        try:
            dm_embed = discord.Embed(
                title="🤝 Community Points Awarded!",
                description=(
                    f"You received **{points}** community points.\n"
                    f"**Reason:** {reason}\n"
                    f"**Total:** {updated['community_points']}"
                ),
                color=discord.Color.green(),
            )
            await user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    @app_commands.command(name="set_community", description="Set a player's community points (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(user="The player", points="New community points value")
    async def set_community(self, interaction: discord.Interaction, user: discord.Member, points: int):
        player = db.get_player(user.id)
        if not player:
            embed = discord.Embed(
                title="❌ Player Not Found",
                description=f"{user.mention} is not in the clan roster.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        old = player["community_points"]
        db.set_community_points(user.id, points)

        embed = discord.Embed(
            title="✅ Community Points Updated",
            description=(
                f"**{player['username']}** community points: "
                f"`{old}` → `{points}`"
            ),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add_item", description="Add an item with its point value (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(name="Item name (e.g. Dragon Warhammer)", value="Point value")
    async def add_item(self, interaction: discord.Interaction, name: str, value: int):
        db.add_item(name, value)

        embed = discord.Embed(
            title="✅ Item Added",
            description=f"**{name}** added with value `{value}` points.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="remove_item", description="Remove an item (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(name="Item name to remove")
    async def remove_item(self, interaction: discord.Interaction, name: str):
        if db.remove_item(name):
            embed = discord.Embed(
                title="✅ Item Removed",
                description=f"**{name}** has been removed.",
                color=discord.Color.green(),
            )
        else:
            embed = discord.Embed(
                title="❌ Item Not Found",
                description=f"No item named **{name}** exists.",
                color=discord.Color.red(),
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="items", description="View all tracked items and their values")
    async def items(self, interaction: discord.Interaction):
        items = db.get_all_items()

        if not items:
            embed = discord.Embed(
                title="📦 Items",
                description="No items have been registered yet.",
                color=discord.Color.purple(),
            )
            await interaction.response.send_message(embed=embed)
            return

        lines = [f"• **{item['name']}** — `{item['value']}` pts" for item in items]

        embed = discord.Embed(
            title="📦 Registered Items",
            description="\n".join(lines),
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Indigo Bot • Use /add_item or /remove_item to manage")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="export", description="Export all player data as a spreadsheet (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def export(self, interaction: discord.Interaction):
        players = db.get_all_players()
        submissions = db.get_all_submissions() if hasattr(db, "get_all_submissions") else []
        items = db.get_all_items()

        if not players and not items:
            embed = discord.Embed(
                title="❌ No Data",
                description="No data in the database to export.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        files = []

        player_lines = ["Username,Discord ID,PVM Points,Community Points,Total Points"]
        for p in players:
            total = p["pvm_points"] + p["community_points"]
            player_lines.append(f"{p['username']},{p['user_id']},{p['pvm_points']},{p['community_points']},{total}")
        if players:
            files.append(
                discord.File(
                    io.BytesIO("\n".join(player_lines).encode()),
                    filename="players.csv",
                )
            )

        if submissions:
            sub_lines = [
                "ID,Submitter ID,Status,Reviewed By,Players,PVM Points,Participant Points,Created At"
            ]
            for s in submissions:
                sub_lines.append(
                    f"{s['id']},{s['user_id']},{s['status']},{s['reviewed_by'] or ''},"
                    f"\"{s['players']}\",{s['pvm_points']},{s['participant_points']},{s['created_at']}"
                )
            files.append(
                discord.File(
                    io.BytesIO("\n".join(sub_lines).encode()),
                    filename="submissions.csv",
                )
            )

        item_lines = ["Name,Value"]
        for i in items:
            item_lines.append(f"{i['name']},{i['value']}")
        if items:
            files.append(
                discord.File(
                    io.BytesIO("\n".join(item_lines).encode()),
                    filename="items.csv",
                )
            )

        try:
            dm = await interaction.user.create_dm()
            dm_embed = discord.Embed(
                title="✅ Database Export",
                description=(
                    f"Here is the full database export.\n"
                    f"**Players:** `{len(players)}`\n"
                    f"**Submissions:** `{len(submissions)}`\n"
                    f"**Items:** `{len(items)}`"
                ),
                color=discord.Color.green(),
            )
            dm_embed.set_footer(text="Indigo Bot • OSRS Clan Points System")
            await dm.send(embed=dm_embed, files=files)

            embed = discord.Embed(
                title="✅ Data Exported",
                description=f"Sent **{len(players)}** players, **{len(submissions)}** submissions, and **{len(items)}** items to your DMs.",
                color=discord.Color.green(),
            )
            embed.set_footer(text="Check your DMs for the spreadsheet files.")
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ DM Failed",
                description="I couldn't send you a DM. Please enable DMs from server members and try again.",
                color=discord.Color.red(),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(name="sync", description="Force sync slash commands (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def sync(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        synced = await self.bot.tree.sync()
        embed = discord.Embed(
            title="✅ Commands Synced",
            description=f"**{len(synced)}** commands synced to Discord.",
            color=discord.Color.green(),
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Admin(bot))
