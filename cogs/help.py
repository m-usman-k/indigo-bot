import discord
from discord import app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available commands")
    @app_commands.describe(category="Choose a category to view")
    @app_commands.choices(category=[
        app_commands.Choice(name="Points", value="points"),
        app_commands.Choice(name="Verification", value="verification"),
        app_commands.Choice(name="Admin", value="admin"),
        app_commands.Choice(name="All Commands", value="all"),
    ])
    async def help(self, interaction: discord.Interaction, category: str = "all"):
        color = discord.Color.purple()

        if category == "all":
            embed = discord.Embed(
                title="📋 Indigo Bot — Commands",
                description="Use `/help <category>` to view commands in a specific category.",
                color=color,
            )
            embed.add_field(
                name="⬦ Points",
                value=(
                    "`/points [user]` — View your or another player's points\n"
                    "`/my_points` — Quick view of your own points\n"
                    "`/leaderboard` — View top players by total points"
                ),
                inline=False,
            )
            embed.add_field(
                name="⬦ Verification",
                value=(
                    "`/submit_image <image> <players>` — Submit a raid screenshot for PVM points\n"
                    "`/pending` — View pending submissions (admin)\n"
                    "`/verify <id> <main_pts> <part_pts>` — Verify a submission (admin)\n"
                    "`/deny <id>` — Deny a submission (admin)"
                ),
                inline=False,
            )
            embed.add_field(
                name="⬦ Admin",
                value=(
                    "`/add_player <user>` — Add a player to the clan list\n"
                    "`/remove_player <user>` — Remove a player from the clan list\n"
                    "`/award_community <user> <points> [reason]` — Award community points\n"
                    "`/set_community <user> <points>` — Set a player's community points\n"
                    "`/add_item <name> <value>` — Add an item with point value\n"
                    "`/remove_item <name>` — Remove an item\n"
                    "`/items` — View all tracked items\n"
                    "`/export` — Export all data as spreadsheet\n"
                    "`/sync` — Sync slash commands (admin)"
                ),
                inline=False,
            )
            embed.set_footer(text="Indigo Bot • OSRS Clan Points System")

        elif category == "points":
            embed = discord.Embed(
                title="⬦ Points Commands",
                description="View and track player points across two categories.",
                color=color,
            )
            embed.add_field(
                name="`/points [user]`",
                value=(
                    "View a player's **PVM Points** and **Community Points**.\n"
                    "If no user is specified, shows your own points.\n\n"
                    "**Example:**\n"
                    "``/points @Nathan``\n"
                    "Displays Nathan's total points in both categories."
                ),
                inline=False,
            )
            embed.add_field(
                name="`/my_points`",
                value=(
                    "Quick shortcut to view your own points.\n\n"
                    "**Example:**\n"
                    "``/my_points``"
                ),
                inline=False,
            )
            embed.add_field(
                name="`/leaderboard`",
                value=(
                    "Shows the top 10 players ranked by combined points.\n\n"
                    "**Example:**\n"
                    "``/leaderboard``"
                ),
                inline=False,
            )

        elif category == "verification":
            embed = discord.Embed(
                title="⬦ Verification Commands",
                description="Submit raid screenshots for point verification.",
                color=color,
            )
            embed.add_field(
                name="`/submit_image <image> <players>`",
                value=(
                    "Upload a raid screenshot and tag all participants.\n"
                    "The image is checked for duplicates using hash detection.\n\n"
                    "**Example:**\n"
                    "``/submit_image <screenshot> Nathan, Jeff, Chris, Mike, Steve``"
                ),
                inline=False,
            )
            embed.add_field(
                name="`/pending`",
                value=(
                    "View all pending submissions awaiting review (admin only).\n\n"
                    "**Example:**\n"
                    "``/pending``"
                ),
                inline=False,
            )
            embed.add_field(
                name="`/verify <id> <main_pts> <part_pts>`",
                value=(
                    "Approve a submission and assign points.\n"
                    "- `id` — Submission ID from `/pending`\n"
                    "- `main_pts` — Points for the item receiver\n"
                    "- `part_pts` — Points for each participant\n\n"
                    "**Example:**\n"
                    "``/verify 3 500 50``"
                ),
                inline=False,
            )
            embed.add_field(
                name="`/deny <id>`",
                value=(
                    "Deny a submission.\n\n"
                    "**Example:**\n"
                    "``/deny 3``"
                ),
                inline=False,
            )

        elif category == "admin":
            embed = discord.Embed(
                title="⬦ Admin Commands",
                description="Manage players, items, and data. Requires admin permissions.",
                color=color,
            )
            embed.add_field(
                name="⬦ Player Management",
                value=(
                    "`/add_player <user>` — Add a Discord user to the clan roster\n"
                    "`/remove_player <user>` — Remove a player from the roster\n"
                    "`/award_community <user> <points> [reason]` — Award community points\n"
                    "`/set_community <user> <points>` — Set exact community points"
                ),
                inline=False,
            )
            embed.add_field(
                name="⬦ Item Management",
                value=(
                    "`/add_item <name> <value>` — Register an item with its point value\n"
                    "`/remove_item <name>` — Remove a tracked item\n"
                    "`/items` — List all registered items"
                ),
                inline=False,
            )
            embed.add_field(
                name="⬦ Data",
                value=(
                    "`/export` — Download a spreadsheet of all player data\n"
                    "`/sync` — Force sync slash commands"
                ),
                inline=False,
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))
