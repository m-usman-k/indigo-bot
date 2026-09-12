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


def build_home_embed():
    embed = discord.Embed(
        title="↳ Indigo Bot — Commands",
        description=(
            "Welcome to the **Indigo Bot** help menu.\n"
            "Use the dropdown below to browse command categories."
        ),
        color=discord.Color.purple(),
    )
    embed.add_field(
        name="↳ Points",
        value=(
            "```\n"
            "/points [user]\n"
            "/my_points\n"
            "/leaderboard\n"
            "```"
        ),
        inline=False,
    )
    embed.add_field(
        name="↳ Verification",
        value=(
            "```\n"
            "/submit_image <image> <players>\n"
            "/pending\n"
            "/verify <id> <main_pts> <part_pts>\n"
            "/deny <id>\n"
            "```"
        ),
        inline=False,
    )
    embed.add_field(
        name="↳ Admin",
        value=(
            "```\n"
            "/add_player <user> <name>\n"
            "/remove_player <user>\n"
            "/award_community <user> <points> [reason]\n"
            "/set_community <user> <points>\n"
            "/add_item <name> <value>\n"
            "/remove_item <name>\n"
            "/items\n"
            "/export\n"
            "/sync\n"
            "```"
        ),
        inline=False,
    )
    embed.set_footer(text="Indigo Bot • OSRS Clan Points System")
    return embed


def build_category_embed(category: str):
    if category == "points":
        embed = discord.Embed(
            title="↳ Points Commands",
            description="View and track player points across two categories.",
            color=discord.Color.purple(),
        )
        embed.add_field(
            name="↳ /points [user]",
            value=(
                "```\n"
                "View a player's PVM Points and Community Points.\n"
                "If no user is specified, shows your own.\n\n"
                "Example:\n"
                "/points @Nathan\n"
                "```"
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ /my_points",
            value=(
                "```\n"
                "Quick shortcut to view your own points.\n\n"
                "Example:\n"
                "/my_points\n"
                "```"
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ /leaderboard",
            value=(
                "```\n"
                "Shows the top 10 players ranked by combined points.\n\n"
                "Example:\n"
                "/leaderboard\n"
                "```"
            ),
            inline=False,
        )

    elif category == "verification":
        embed = discord.Embed(
            title="↳ Verification Commands",
            description="Submit raid screenshots for point verification.",
            color=discord.Color.purple(),
        )
        embed.add_field(
            name="↳ /submit_image <image> <players>",
            value=(
                "```\n"
                "Upload a raid screenshot and tag all participants.\n"
                "Image is checked for duplicates via hash.\n\n"
                "Example:\n"
                "/submit_image <screenshot> Nathan, Jeff, Chris, Mike\n"
                "```"
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ /pending",
            value=(
                "```\n"
                "View all pending submissions awaiting review.\n"
                "Admin only.\n\n"
                "Example:\n"
                "/pending\n"
                "```"
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ /verify <id> <main_pts> <part_pts>",
            value=(
                "```\n"
                "Approve a submission and assign points.\n"
                "  id          — Submission ID from /pending\n"
                "  main_pts    — Points for the item receiver\n"
                "  part_pts    — Points for each participant\n\n"
                "Example:\n"
                "/verify 3 500 50\n"
                "```"
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ /deny <id>",
            value=(
                "```\n"
                "Deny a submission.\n\n"
                "Example:\n"
                "/deny 3\n"
                "```"
            ),
            inline=False,
        )

    elif category == "admin":
        embed = discord.Embed(
            title="↳ Admin Commands",
            description="Manage players, items, and data. Requires admin permissions.",
            color=discord.Color.purple(),
        )
        embed.add_field(
            name="↳ Player Management",
            value=(
                "```\n"
                "/add_player <user> <name>\n"
                "/remove_player <user>\n"
                "/award_community <user> <points> [reason]\n"
                "/set_community <user> <points>\n"
                "```"
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ Item Management",
            value=(
                "```\n"
                "/add_item <name> <value>\n"
                "/remove_item <name>\n"
                "/items\n"
                "```"
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ Data",
            value=(
                "```\n"
                "/export\n"
                "/sync\n"
                "```"
            ),
            inline=False,
        )

    return embed


def build_nav_embeds(current: str):
    idx = CATEGORIES.index(current)
    prev_cat = CATEGORIES[idx - 1] if idx > 0 else CATEGORIES[-1]
    next_cat = CATEGORIES[idx + 1] if idx < len(CATEGORIES) - 1 else CATEGORIES[0]

    prev_embed = discord.Embed(
        title=f"⬅ ↳ {CATEGORY_LABELS[prev_cat]}",
        description=f"Select dropdown to view **{CATEGORY_LABELS[prev_cat]}** commands.",
        color=discord.Color.purple(),
    )

    next_embed = discord.Embed(
        title=f"↳ {CATEGORY_LABELS[next_cat]} ➡",
        description=f"Select dropdown to view **{CATEGORY_LABELS[next_cat]}** commands.",
        color=discord.Color.purple(),
    )

    return prev_embed, next_embed


class HelpView(discord.ui.View):
    def __init__(self, current: str = "home"):
        super().__init__(timeout=120)
        self.current = current
        self._add_items()

    def _add_items(self):
        self.clear_items()

        options = [
            discord.SelectOption(
                label=CATEGORY_LABELS[cat],
                value=cat,
                description=f"View {CATEGORY_LABELS[cat]} commands",
                default=(cat == self.current),
            )
            for cat in CATEGORIES
        ]
        self.add_item(HelpSelect(options=options))

        idx = CATEGORIES.index(self.current)
        prev_cat = CATEGORIES[idx - 1] if idx > 0 else CATEGORIES[-1]
        next_cat = CATEGORIES[idx + 1] if idx < len(CATEGORIES) - 1 else CATEGORIES[0]

        prev_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"⬅ {CATEGORY_LABELS[prev_cat]}",
        )
        prev_btn.callback = self.prev_callback
        self.add_item(prev_btn)

        next_btn = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"{CATEGORY_LABELS[next_cat]} ➡",
        )
        next_btn.callback = self.next_callback
        self.add_item(next_btn)

    async def prev_callback(self, interaction: discord.Interaction):
        idx = CATEGORIES.index(self.current)
        self.current = CATEGORIES[idx - 1] if idx > 0 else CATEGORIES[-1]
        await self.refresh(interaction)

    async def next_callback(self, interaction: discord.Interaction):
        idx = CATEGORIES.index(self.current)
        self.current = CATEGORIES[idx + 1] if idx < len(CATEGORIES) - 1 else CATEGORIES[0]
        await self.refresh(interaction)

    async def refresh(self, interaction: discord.Interaction):
        self._add_items()

        if self.current == "home":
            main_embed = build_home_embed()
        else:
            main_embed = build_category_embed(self.current)

        prev_embed, next_embed = build_nav_embeds(self.current)

        await interaction.response.edit_message(
            embeds=[main_embed, prev_embed, next_embed],
            view=self,
        )


class HelpSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(
            placeholder="Browse categories...",
            options=options,
            custom_id="help_category_select",
        )

    async def callback(self, interaction: discord.Interaction):
        view: HelpView = self.view
        view.current = self.values[0]
        await view.refresh(interaction)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        view = HelpView(current="home")
        main_embed = build_home_embed()
        prev_embed, next_embed = build_nav_embeds("home")

        await interaction.response.send_message(
            embeds=[main_embed, prev_embed, next_embed],
            view=view,
        )


async def setup(bot):
    await bot.add_cog(Help(bot))
