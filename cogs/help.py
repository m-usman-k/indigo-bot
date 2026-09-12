import discord
from discord import app_commands
from discord.ext import commands


CATEGORIES = ["home", "points", "verification", "admin"]
CATEGORY_LABELS = {
    "home": "Home",
    "points": "Points",
    "verification": "Verification",
    "admin": "Admin",
}
CATEGORY_DESCRIPTIONS = {
    "home": "Welcome to Indigo Bot.",
    "points": "View and track player points across two categories: PVM Points and Community Points.",
    "verification": "Submit raid screenshots for human verification and earn PVM points.",
    "admin": "Manage players, items, and data. Requires admin permissions.",
}

POINTS_COMMANDS = [
    ("/points [user]", "↳ View a player's PVM and Community points."),
    ("/my_points", "↳ Quick view of your own points."),
    ("/leaderboard", "↳ View top 10 players by total points."),
]

VERIFICATION_COMMANDS = [
    ("/submit_image <image> @players", "↳ Submit a raid screenshot; mention up to 5 players."),
    ("/pending", "↳ View pending submissions (admin)."),
]

ADMIN_COMMANDS = [
    ("/add_player <user> <name>", "↳ Add a player to the clan roster."),
    ("/remove_player <user>", "↳ Remove a player from the roster."),
    ("/award_community <user> <pts> [reason]", "↳ Award community points to a player."),
    ("/set_community <user> <pts>", "↳ Set a player's exact community points."),
    ("/add_item <name> <value>", "↳ Register an item with its point value."),
    ("/remove_item <name>", "↳ Remove a tracked item."),
    ("/items", "↳ List all registered items."),
    ("/export", "↳ Download a spreadsheet of all player data."),
    ("/setup_channel <channel>", "↳ Choose the channel where submissions get reviewed."),
    ("/sync", "↳ Force sync slash commands."),
]


def build_home_embed():
    embed = discord.Embed(
        title="Indigo Bot",
        description=(
            "A clan management bot for Oldschool RuneScape.\n\n"
            "**Features:**\n"
            "↳ Track PVM Points and Community Points for clan members\n"
            "↳ Submit raid screenshots for human verification\n"
            "↳ Leaderboards, item tracking, and data export\n\n"
            "**Categories:** Points, Verification, Admin\n"
            "Select a category from the dropdown below."
        ),
        color=discord.Color.purple(),
    )
    embed.set_footer(text="Indigo Bot • OSRS Clan Points System")
    return embed


def build_category_embed(category: str):
    if category == "points":
        commands_list = POINTS_COMMANDS
        footer = "Select another category from the dropdown below."
    elif category == "verification":
        commands_list = VERIFICATION_COMMANDS
        footer = "Select another category from the dropdown below."
    else:
        commands_list = ADMIN_COMMANDS
        footer = "Select another category from the dropdown below."

    lines = [f"{name}\n{desc}" for name, desc in commands_list]

    embed = discord.Embed(
        title=f"{CATEGORY_LABELS[category]} — Commands",
        description=CATEGORY_DESCRIPTIONS[category],
        color=discord.Color.purple(),
    )
    embed.add_field(name="Commands", value="\n\n".join(lines), inline=False)
    embed.set_footer(text=footer)
    return embed


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.current = "home"
        self._rebuild_components()

    def _rebuild_components(self):
        self.clear_items()

        options = [
            discord.SelectOption(
                label=CATEGORY_LABELS[cat],
                value=cat,
                description=CATEGORY_DESCRIPTIONS[cat],
                default=(cat == self.current),
            )
            for cat in CATEGORIES
        ]
        select = discord.ui.Select(
            placeholder="Select a category...",
            options=options,
            min_values=1,
            max_values=1,
        )

        async def select_callback(interaction: discord.Interaction):
            self.current = select.values[0]
            await self.update(interaction)

        select.callback = select_callback
        self.add_item(select)

        prev_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="⬅",
            label="Previous",
        )
        prev_btn.callback = self.previous
        self.add_item(prev_btn)

        next_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            emoji="➡",
            label="Next",
        )
        next_btn.callback = self.next
        self.add_item(next_btn)

    async def previous(self, interaction: discord.Interaction):
        idx = CATEGORIES.index(self.current)
        self.current = CATEGORIES[idx - 1]
        await self.update(interaction)

    async def next(self, interaction: discord.Interaction):
        idx = CATEGORIES.index(self.current)
        self.current = CATEGORIES[(idx + 1) % len(CATEGORIES)]
        await self.update(interaction)

    async def update(self, interaction: discord.Interaction):
        self._rebuild_components()
        embed = (
            build_home_embed()
            if self.current == "home"
            else build_category_embed(self.current)
        )
        await interaction.response.edit_message(embed=embed, view=self)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        view = HelpView()
        embed = build_home_embed()
        await interaction.response.send_message(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(Help(bot))