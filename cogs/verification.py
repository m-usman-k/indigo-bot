import discord
from discord import app_commands
from discord.ext import commands
import database as db


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="submit_image", description="Submit a raid screenshot for PVM points")
    @app_commands.describe(
        image="The raid screenshot",
        players="Comma-separated list of all participants (e.g. Nathan, Jeff, Chris)"
    )
    async def submit_image(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        players: str,
    ):
        player = db.get_player(interaction.user.id)
        if not player:
            embed = discord.Embed(
                title="❌ Not in Clan",
                description="You are not in the clan roster. An admin must `/add_player` you first.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        image_bytes = await image.read()
        image_hash = db.compute_image_hash(image_bytes)

        if db.image_already_submitted(image_hash):
            embed = discord.Embed(
                title="❌ Duplicate Image",
                description="This image has already been submitted and cannot be used again.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        player_list = [p.strip() for p in players.split(",") if p.strip()]
        if len(player_list) < 2:
            embed = discord.Embed(
                title="❌ Invalid Player List",
                description="Please provide at least 2 players (including yourself).",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        sub_id = db.create_submission(
            user_id=interaction.user.id,
            image_url=image.url,
            image_hash=image_hash,
            players=", ".join(player_list),
        )

        embed = discord.Embed(
            title="✅ Submission Created",
            description=(
                f"**Submission ID:** `{sub_id}`\n"
                f"**Submitted by:** {interaction.user.mention}\n"
                f"**Players:** {', '.join(f'`{p}`' for p in player_list)}\n\n"
                "An admin will review and assign points shortly."
            ),
            color=discord.Color.green(),
        )
        embed.set_image(url=image.url)
        embed.set_footer(text="Indigo Bot • OSRS Clan Points System")

        await interaction.response.send_message(embed=embed)

        admin_channel = discord.utils.get(interaction.guild.text_channels, name="admin-reviews")
        if admin_channel:
            review_embed = discord.Embed(
                title=f"📬 New Submission — ID `{sub_id}`",
                description=(
                    f"**Submitted by:** {interaction.user.mention}\n"
                    f"**Players:** {', '.join(f'`{p}`' for p in player_list)}\n\n"
                    "Use `/verify` or `/deny` to review."
                ),
                color=discord.Color.orange(),
            )
            review_embed.set_image(url=image.url)
            review_embed.set_footer(text=f"Submission ID: {sub_id}")
            await admin_channel.send(embed=review_embed)

    @app_commands.command(name="pending", description="View all pending submissions (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    async def pending(self, interaction: discord.Interaction):
        subs = db.get_pending_submissions()

        if not subs:
            embed = discord.Embed(
                title="📬 Pending Submissions",
                description="No pending submissions to review.",
                color=discord.Color.green(),
            )
            await interaction.response.send_message(embed=embed)
            return

        lines = []
        for s in subs[:15]:
            lines.append(
                f"**ID `{s['id']}`** — {s['players']}\n"
                f"└ Submitted by <@{s['user_id']}> • <t:{int(s['created_at']) if s['created_at'] else 0}:R>"
            )

        embed = discord.Embed(
            title="📬 Pending Submissions",
            description="\n\n".join(lines),
            color=discord.Color.orange(),
        )
        embed.set_footer(text="Use /verify <id> <main_pts> <part_pts> or /deny <id>")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="verify", description="Approve a submission and assign points (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        submission_id="The submission ID from /pending",
        main_points="Points for the item receiver",
        participant_points="Points for each participant"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        submission_id: int,
        main_points: int,
        participant_points: int,
    ):
        sub = db.get_submission(submission_id)
        if not sub:
            embed = discord.Embed(
                title="❌ Submission Not Found",
                description=f"No submission found with ID `{submission_id}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if sub["status"] != "pending":
            embed = discord.Embed(
                title="❌ Already Reviewed",
                description=f"Submission `{submission_id}` has already been `{sub['status']}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        submitter_id = sub["user_id"]
        player_list = [p.strip() for p in sub["players"].split(",")]

        submitter = db.get_player(submitter_id)
        if not submitter:
            db.add_player(submitter_id, f"User_{submitter_id}")
            submitter = db.get_player(submitter_id)

        db.add_pvm_points(submitter_id, main_points)

        participants_notified = []
        for p_name in player_list:
            if p_name.lower() == submitter["username"].lower():
                continue
            for pid in self._find_player_id(p_name):
                db.add_pvm_points(pid, participant_points)
                participants_notified.append((p_name, pid))

        db.update_submission_status(submission_id, "verified", interaction.user.id)

        embed = discord.Embed(
            title="✅ Submission Verified",
            description=(
                f"**Submission ID:** `{submission_id}`\n"
                f"**Reviewed by:** {interaction.user.mention}\n\n"
                f"**{submitter['username']}** received `{main_points}` PVM points\n"
            ),
            color=discord.Color.green(),
        )

        if participants_notified:
            for name, pid in participants_notified:
                embed.description += f"**{name}** received `{participant_points}` PVM points\n"

        embed.set_footer(text="Indigo Bot • OSRS Clan Points System")
        await interaction.response.send_message(embed=embed)

        try:
            submitter_user = await self.bot.fetch_user(submitter_id)
            dm_embed = discord.Embed(
                title="🎉 PVM Points Awarded!",
                description=(
                    f"You received **{main_points}** PVM points from submission `{submission_id}`.\n"
                    f"**Other participants:** {participant_points} pts each"
                ),
                color=discord.Color.green(),
            )
            await submitter_user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    @app_commands.command(name="deny", description="Deny a submission (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(submission_id="The submission ID to deny")
    async def deny(self, interaction: discord.Interaction, submission_id: int):
        sub = db.get_submission(submission_id)
        if not sub:
            embed = discord.Embed(
                title="❌ Submission Not Found",
                description=f"No submission found with ID `{submission_id}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if sub["status"] != "pending":
            embed = discord.Embed(
                title="❌ Already Reviewed",
                description=f"Submission `{submission_id}` has already been `{sub['status']}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        db.update_submission_status(submission_id, "denied", interaction.user.id)

        embed = discord.Embed(
            title="❌ Submission Denied",
            description=(
                f"**Submission ID:** `{submission_id}`\n"
                f"**Denied by:** {interaction.user.mention}"
            ),
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)

        try:
            submitter_user = await self.bot.fetch_user(sub["user_id"])
            dm_embed = discord.Embed(
                title="❌ Submission Denied",
                description=f"Your submission `{submission_id}` has been denied by an admin.",
                color=discord.Color.red(),
            )
            await submitter_user.send(embed=dm_embed)
        except discord.Forbidden:
            pass

    def _find_player_id(self, name: str) -> list[int]:
        conn = db.get_connection()
        c = conn.cursor()
        c.execute(
            "SELECT user_id FROM players WHERE LOWER(username) = LOWER(?)",
            (name,),
        )
        rows = c.fetchall()
        conn.close()
        return [r["user_id"] for r in rows]


async def setup(bot):
    await bot.add_cog(Verification(bot))
