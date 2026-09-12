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
    "home": "Welcome to the Indigo Bot help menu. Select a category from the dropdown below to view its commands.",
    "points": "View and track player points across two categories: PVM Points and Community Points.",
    "verification": "Submit raid screenshots for human verification and earn PVM points.",
    "admin": "Manage players, items, and data. Requires admin permissions.",
}


def build_home_embed():
    embed = discord.Embed(
        title="Indigo Bot — Commands",
        color=discord.Color.purple(),
    )

    embed.add_field(
        name="↳ Command Categories",
        value=(
            "```\n"
            "Points\n"
            "Verification\n"
            "Admin\n"
            "```"
        ),
        inline=False,
    )
    embed.add_field(
        name="↳ Points Category",
        value=(
            "`/points [user]`\n"
            "↳ View a player's PVM and Community points.\n"
            "`/my_points`\n"
            "↳ Quick view of your own points.\n"
            "`/leaderboard`\n"
            "↳ View top 10 players by total points."
        ),
        inline=False,
    )
    embed.add_field(
        name="↳ Verification Category",
        value=(
            "`/submit_image <image> <players>`\n"
            "↳ Submit a raid screenshot for PVM points.\n"
            "`/pending`\n"
            "↳ View pending submissions (admin).\n"
            "`/verify <id> <main_pts> <part_pts>`\n"
            "↳ Approve a submission and award points (admin).\n"
            "`/deny <id>`\n"
            "↳ Deny a submission (admin)."
        ),
        inline=False,
    )
    embed.add_field(
        name="↳ Admin Category",
        value=(
            "`/add_player <user> <name>`\n"
            "↳ Add a player to the clan roster.\n"
            "`/remove_player <user>`\n"
            "↳ Remove a player from the roster.\n"
            "`/award_community <user> <pts> [reason]`\n"
            "↳ Award community points.\n"
            "`/set_community <user> <pts>`\n"
            "↳ Set a player's community points.\n"
            "`/add_item <name> <value>`\n"
            "↳ Register an item with its point value.\n"
            "`/remove_item <name>`\n"
            "↳ Remove a tracked item.\n"
            "`/items`\n"
            "↳ List all registered items.\n"
            "`/export`\n"
            "↳ Export all data as a spreadsheet.\n"
            "`/sync`\n"
            "↳ Force sync slash commands."
        ),
        inline=False,
    )
    embed.set_footer(text="Indigo Bot • OSRS Clan Points System")
    return embed


def build_category_embed(category: str):
    color = discord.Color.purple()
    label = CATEGORY_LABELS[category]

    if category == "points":
        embed = discord.Embed(
            title=f"{label} — Commands",
            color=color,
        )
        embed.description = "```\n" + CATEGORY_DESCRIPTIONS[category] + "\n```"
        embed.add_field(
            name="`/points [user]`",
            value=(
                "↳ View a player's **PVM Points** and **Community Points**.\n"
                "↳ If no user is specified, shows your own.\n"
                "↳ **Example:** `/points @Nathan`"
            ),
            inline=False,
        )
        embed.add_field(
            name="`/my_points`",
            value=(
                "↳ Quick shortcut to view your own points.\n"
                "↳ **Example:** `/my_points`"
            ),
            inline=False,
        )
        embed.add_field(
            name="`/leaderboard`",
            value=(
                "↳ Shows the top 10 players ranked by combined points.\n"
                "↳ **Example:** `/leaderboard`"
            ),
            inline=False,
        )

    elif category == "verification":
        embed = discord.Embed(
            title=f"{label} — Commands",
            color=color,
        )
        embed.description = "```\n" + CATEGORY_DESCRIPTIONS[category] + "\n```"
        embed.add_field(
            name="`/submit_image <image> <players>`",
            value=(
                "↳ Upload a raid screenshot and tag all participants.\n"
                "↳ Image is checked for duplicates via hash.\n"
                "↳ **Example:** `/submit_image <file> Nathan, Jeff, Chris`"
            ),
            inline=False,
        )
        embed.add_field(
            name="`/pending`",
            value=(
                "↳ View all pending submissions awaiting review.\n"
                "↳ **Admin only.**"
            ),
            inline=False,
        )
        embed.add_field(
            name="`/verify <id> <main_pts> <part_pts>`",
            value=(
                "↳ Approve a submission and assign points.\n"
                "↳ `id` — submission ID from `/pending`.\n"
                "↳ `main_pts` — points for the item receiver.\n"
                "↳ `part_pts` — points for each participant.\n"
                "↳ **Admin only.**\n"
                "↳ **Example:** `/verify 3 500 50`"
            ),
            inline=False,
        )
        embed.add_field(
            name="`/deny <id>`",
            value=(
                "↳ Deny a submission.\n"
                "↳ **Admin only.**\n"
                "↳ **Example:** `/deny 3`"
            ),
            inline=False,
        )

    elif category == "admin":
        embed = discord.Embed(
            title=f"{label} — Commands",
            color=color,
        )
        embed.description = "```\n" + CATEGORY_DESCRIPTIONS[category] + "\n```"
        embed.add_field(
            name="↳ Player Management",
            value=(
                "`/add_player <user> <name>`\n"
                "↳ Add a player to the clan roster.\n"
                "`/remove_player <user>`\n"
                "↳ Remove a player from the roster.\n"
                "`/award_community <user> <pts> [reason]`\n"
                "↳ Award community points to a player.\n"
                "`/set_community <user> <pts>`\n"
                "↳ Set a player's exact community points."
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ Item Management",
            value=(
                "`/add_item <name> <value>`\n"
                "↳ Register an item with its point value.\n"
                "`/remove_item <name>`\n"
                "↳ Remove a tracked item.\n"
                "`/items`\n"
                "↳ List all registered items."
            ),
            inline=False,
        )
        embed.add_field(
            name="↳ Data",
            value=(
                "`/export`\n"
                "↳ Download a spreadsheet of all player data.\n"
                "`/sync`\n"
                "↳ Force sync slash commands."
            ),
            inline=False,
        )

    embed.set_footer(text="Indigo Bot • OSRS Clan Points System")
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