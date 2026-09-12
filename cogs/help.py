import discord
from discord import app_commands
from discord.ext import commands


CATEGORIES = ["home", "points", "submitting", "reviewing", "admin", "export"]
CATEGORY_LABELS = {
    "home": "Home",
    "points": "Points",
    "submitting": "Submit a Raid",
    "reviewing": "Review Submissions",
    "admin": "Admin Commands",
    "export": "Database Export",
}
CATEGORY_DESCRIPTIONS = {
    "home": "Everything you need to know about Indigo Bot.",
    "points": "How points work and the commands to check them.",
    "submitting": "Step-by-step guide to submitting a raid for points.",
    "reviewing": "How admins review and approve submissions.",
    "admin": "Every admin command explained.",
    "export": "How to download the whole database as spreadsheets.",
}


def build_home_embed():
    embed = discord.Embed(
        title="Indigo Bot",
        description=(
            "A clan management bot for **Oldschool RuneScape**.\n\n"
            "**What can it do?**\n"
            "↳ Track **PVM Points** and **Community Points** for clan members\n"
            "↳ Accept raid screenshots and award points to everyone in the fight\n"
            "↳ Prevent duplicate screenshots with image hashing\n"
            "↳ Leaderboards, item tracking, and database export\n\n"
            "**Browse the guides:**\n"
            "↳ **Points** — how points work\n"
            "↳ **Submit a Raid** — how to get points from fights\n"
            "↳ **Review Submissions** — the admin review flow\n"
            "↳ **Admin Commands** — full admin reference\n"
            "↳ **Database Export** — get your data as spreadsheets\n\n"
            "Select a category from the dropdown below."
        ),
        color=discord.Color.purple(),
    )
    embed.set_footer(text="Indigo Bot • OSRS Clan Points System")
    return embed


def build_category_embed(category: str):
    color = discord.Color.purple()
    label = CATEGORY_LABELS[category]

    if category == "points":
        embed = discord.Embed(
            title=f"{label} — Commands",
            description=CATEGORY_DESCRIPTIONS[category],
            color=color,
        )
        embed.add_field(
            name="How points work",
            value=(
                "**PVM Points**\n"
                "↳ Earned from raid submissions that get verified by an admin.\n"
                "↳ The player with the drop earns the **main points**.\n"
                "↳ Everyone else in the fight earns the **participant points**.\n\n"
                "**Community Points**\n"
                "↳ Every raid gets an extra **`5` community points per player**.\n"
                "↳ Admins can also award them manually for events, contributions, etc."
            ),
            inline=False,
        )
        embed.add_field(
            name="Commands",
            value=(
                "/points [user]\n"
                "↳ View a player's PVM and Community points.\n"
                "/my_points\n"
                "↳ Quick view of your own points.\n"
                "/leaderboard\n"
                "↳ View top 10 players by total points.\n"
                "/roster\n"
                "↳ Browse the whole clan roster with page navigation."
            ),
            inline=False,
        )

    elif category == "submitting":
        embed = discord.Embed(
            title=f"{label} — Commands",
            description=CATEGORY_DESCRIPTIONS[category],
            color=color,
        )
        embed.add_field(
            name="Step 1 — Setup",
            value=(
                "An admin must run:\n"
                "↳ `/setup_channel <channel>` — choose where submissions get reviewed.\n\n"
                "Without this, submissions cannot be sent."
            ),
            inline=False,
        )
        embed.add_field(
            name="Step 2 — Submit your raid",
            value=(
                "Run the command and pick each player in the `player` options:\n"
                "↳ `/submit_image <image> player1:@Nathan player2:@Jeff player3:@Chris`\n\n"
                "↳ Up to **10 players** can be selected (plus yourself = 11 total).\n"
                "↳ You must be on the clan roster to submit (ask an admin to add you).\n"
                "↳ Your screenshot hash is checked so the same image can't be submitted twice."
            ),
            inline=False,
        )
        embed.add_field(
            name="Step 3 — What happens next",
            value=(
                "↳ Your submission is posted to the review channel as an embed.\n"
                "↳ An admin presses **Accept** or **Deny**.\n"
                "↳ If accepted, you and every participant get their PVM points."
            ),
            inline=False,
        )

    elif category == "reviewing":
        embed = discord.Embed(
            title=f"{label} — Commands",
            description=CATEGORY_DESCRIPTIONS[category],
            color=color,
        )
        embed.add_field(
            name="Step 1 — Set the review channel",
            value=(
                "↳ `/setup_channel <channel>` — choose where submissions appear.\n"
                "↳ **Admin only.**"
            ),
            inline=False,
        )
        embed.add_field(
            name="Step 2 — Review a submission",
            value=(
                "Submissions appear as embeds with the screenshot and the players mentioned.\n\n"
                "↳ **✅ Accept** — a modal opens asking:\n"
                "   ↳ points for the **main player** (the drop owner)\n"
                "   ↳ points for **each participant**\n"
                "↳ The main player gets their points + **`5` community**.\n"
                "↳ Each participant gets their points + **`5` community**.\n"
                "↳ **❌ Deny** — the submission is marked denied."
            ),
            inline=False,
        )
        embed.add_field(
            name="Step 3 — Notifications",
            value=(
                "↳ **Accepted** — every player gets a DM with their points.\n"
                "↳ **Denied** — the submitter gets a DM.\n"
                "↳ The review embed is updated to show the final status.\n\n"
                "⚠️ Players must be on the roster to receive points. "
                "If someone isn't, add them with `/add_player` after accepting."
            ),
            inline=False,
        )
        embed.add_field(
            name="Manual commands",
            value=(
                "/pending\n"
                "↳ View all pending submissions.\n"
                "/verify <id> <main_pts> <part_pts>\n"
                "↳ Manually approve a submission and award points.\n"
                "/deny <id>\n"
                "↳ Manually deny a submission."
            ),
            inline=False,
        )

    elif category == "admin":
        embed = discord.Embed(
            title=f"{label} — Commands",
            description=CATEGORY_DESCRIPTIONS[category],
            color=color,
        )
        embed.add_field(
            name="Player roster",
            value=(
                "/add_player <user> <name>\n"
                "↳ Add a player to the clan roster.\n"
                "/remove_player <user>\n"
                "↳ Remove a player from the roster."
            ),
            inline=False,
        )
        embed.add_field(
            name="Community points",
            value=(
                "/award_community <user> <pts> [reason]\n"
                "↳ Award community points to a player.\n"
                "/set_community <user> <pts>\n"
                "↳ Set a player's exact community points."
            ),
            inline=False,
        )
        embed.add_field(
            name="Items",
            value=(
                "/add_item <name> <value>\n"
                "↳ Register an item with its point value.\n"
                "/remove_item <name>\n"
                "↳ Remove a tracked item.\n"
                "/items\n"
                "↳ List all registered items."
            ),
            inline=False,
        )
        embed.add_field(
            name="Setup & maintenance",
            value=(
                "/setup_channel <channel>\n"
                "↳ Choose the review channel for submissions.\n"
                "/sync\n"
                "↳ Force refresh the bot's slash commands.\n"
                "/export\n"
                "↳ DM yourself the whole database."
            ),
            inline=False,
        )

    elif category == "export":
        embed = discord.Embed(
            title=f"{label} — Commands",
            description=CATEGORY_DESCRIPTIONS[category],
            color=color,
        )
        embed.add_field(
            name="How to export",
            value=(
                "Run:\n"
                "↳ `/export` (admin) — the bot DMs you the spreadsheet files.\n\n"
                "↳ Enable DMs from server members or the export will fail."
            ),
            inline=False,
        )
        embed.add_field(
            name="What you get",
            value=(
                "**players.csv** — username, Discord ID, PVM points, community points, total\n"
                "↳ One row per player on the roster.\n\n"
                "**submissions.csv** — every submission with its status and awarded points\n"
                "↳ Includes who submitted and who reviewed it.\n\n"
                "**items.csv** — every registered item and its point value."
            ),
            inline=False,
        )

    embed.set_footer(text="Select another category from the dropdown below.")
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