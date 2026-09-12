import discord
from discord import app_commands
from discord.ext import commands
import database as db

MAX_PLAYERS = 10
COMMUNITY_BONUS = 5


class PointsModal(discord.ui.Modal, title="Assign Points"):
    main_points_input = discord.ui.TextInput(
        label="Points for the main player",
        placeholder="e.g. 500",
    )
    participant_points_input = discord.ui.TextInput(
        label="Points for each participant",
        placeholder="e.g. 50",
    )

    def __init__(self, submission_id: int):
        super().__init__(timeout=None)
        self.submission_id = submission_id

    async def on_submit(self, interaction: discord.Interaction):
        try:
            main_pts = int(self.main_points_input.value)
            part_pts = int(self.participant_points_input.value)
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Points",
                description="Points must be whole numbers.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if main_pts < 0 or part_pts < 0:
            embed = discord.Embed(
                title="❌ Invalid Points",
                description="Points cannot be negative.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        cog = interaction.client.get_cog("Verification")
        if cog is None:
            embed = discord.Embed(
                title="❌ Error",
                description="The verification system is not available right now.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await cog.accept_submission(interaction, self.submission_id, main_pts, part_pts)

    async def on_error(self, interaction: discord.Interaction, error):
        embed = discord.Embed(
            title="❌ Error",
            description="Something went wrong while processing your input.",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SubmissionView(discord.ui.View):
    def __init__(self, submission_id: int):
        super().__init__(timeout=None)
        self.submission_id = submission_id

        accept = discord.ui.Button(
            style=discord.ButtonStyle.green,
            label="Accept",
            emoji="✅",
            custom_id=f"sub_accept_{submission_id}",
        )
        accept.callback = self.accept_callback
        self.add_item(accept)

        deny = discord.ui.Button(
            style=discord.ButtonStyle.red,
            label="Deny",
            emoji="❌",
            custom_id=f"sub_deny_{submission_id}",
        )
        deny.callback = self.deny_callback
        self.add_item(deny)

    def _cog(self, interaction: discord.Interaction):
        return interaction.client.get_cog("Verification")

    async def accept_callback(self, interaction: discord.Interaction):
        sub = db.get_submission(self.submission_id)
        if sub is None or sub["status"] != "pending":
            embed = discord.Embed(
                title="❌ Already Reviewed",
                description="This submission has already been handled.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        modal = PointsModal(self.submission_id)
        await interaction.response.send_modal(modal)

    async def deny_callback(self, interaction: discord.Interaction):
        cog = self._cog(interaction)
        if cog is None:
            embed = discord.Embed(
                title="❌ Error",
                description="The verification system is not available right now.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await cog.deny_submission(interaction, self.submission_id)


def _review_embed(sub: dict, guild: discord.Guild, status: str = "pending"):
    if status == "pending":
        color = discord.Color.orange()
        title = f"📬 New Submission — #{sub['id']}"
        footer = "Waiting for review"
        description = None
    elif status == "verified":
        color = discord.Color.green()
        title = f"✅ Verified — #{sub['id']}"
        footer = "Accepted by " + (f"<@{sub['reviewed_by']}>" if sub["reviewed_by"] else "admin")
        description = (
            f"**Main player:** `{sub['pvm_points']}` PVM + `{COMMUNITY_BONUS}` Community points\n"
            f"**Each participant:** `{sub['participant_points']}` PVM + `{COMMUNITY_BONUS}` Community points"
        )
    else:
        color = discord.Color.red()
        title = f"❌ Denied — #{sub['id']}"
        footer = "Denied by " + (f"<@{sub['reviewed_by']}>" if sub["reviewed_by"] else "admin")
        description = None

    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_image(url=sub["image_url"])

    submitter = guild.get_member(sub["user_id"])
    embed.add_field(
        name="Submitted by",
        value=submitter.mention if submitter else f"<@{sub['user_id']}>",
        inline=True,
    )

    participant_ids = [int(x) for x in (sub["participant_ids"] or "").split(",") if x]
    mentions = " ".join(f"<@{pid}>" for pid in participant_ids) or "None"
    embed.add_field(name="Participants", value=mentions, inline=False)

    embed.set_footer(text=footer)
    return embed


class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="submit_image", description="Submit a raid screenshot for PVM points")
    @app_commands.describe(
        image="The raid screenshot",
        player1="Member 1 (up to 10 total)",
        player2="Member 2 (up to 10 total)",
        player3="Member 3 (up to 10 total)",
        player4="Member 4 (up to 10 total)",
        player5="Member 5 (up to 10 total)",
        player6="Member 6 (up to 10 total)",
        player7="Member 7 (up to 10 total)",
        player8="Member 8 (up to 10 total)",
        player9="Member 9 (up to 10 total)",
        player10="Member 10 (up to 10 total)",
    )
    async def submit_image(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        player1: discord.Member = None,
        player2: discord.Member = None,
        player3: discord.Member = None,
        player4: discord.Member = None,
        player5: discord.Member = None,
        player6: discord.Member = None,
        player7: discord.Member = None,
        player8: discord.Member = None,
        player9: discord.Member = None,
        player10: discord.Member = None,
    ):
        channel_id = db.get_submissions_channel(interaction.guild.id)
        if channel_id is None:
            embed = discord.Embed(
                title="❌ Review Channel Not Setup",
                description=(
                    "The review channel has not been setup yet.\n"
                    "An admin must run `/setup_channel <channel>` first so submissions have somewhere to go."
                ),
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        submitter = interaction.user
        submitter_name = submitter.display_name or submitter.name
        if db.get_player(submitter.id) is None:
            embed = discord.Embed(
                title="❌ Not in Clan Roster",
                description=(
                    "You are not on the clan roster yet.\n"
                    "Ask an admin to run `/add_player` so you can submit and earn points."
                ),
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        supplied = [player1, player2, player3, player4, player5,
                    player6, player7, player8, player9, player10]

        mentioned_members = []
        seen = set()
        for m in supplied:
            if m is None or m.id in seen or m.id == submitter.id:
                continue
            seen.add(m.id)
            mentioned_members.append(m)

        if len(mentioned_members) < 1:
            embed = discord.Embed(
                title="❌ No Players Mentioned",
                description=(
                    "Select at least 1 other player in the fight.\n"
                    f"Max **{MAX_PLAYERS}** other players allowed."
                ),
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if len(mentioned_members) > MAX_PLAYERS:
            embed = discord.Embed(
                title="❌ Too Many Players",
                description=f"Max **{MAX_PLAYERS}** other players allowed.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        player_list = [submitter_name] + [m.display_name or m.name for m in mentioned_members]
        participant_ids = [m.id for m in mentioned_members]

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

        channel = interaction.guild.get_channel(channel_id)
        if channel is None:
            embed = discord.Embed(
                title="❌ Review Channel Missing",
                description="The configured review channel no longer exists. Admins must run `/setup_channel` again.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        sub_id = db.create_submission(
            user_id=submitter.id,
            image_url=image.url,
            image_hash=image_hash,
            players=", ".join(player_list),
            participant_ids=participant_ids,
            channel_id=channel_id,
        )

        view = SubmissionView(sub_id)
        embed = _review_embed(
            {
                "id": sub_id,
                "user_id": submitter.id,
                "image_url": image.url,
                "participant_ids": ",".join(str(i) for i in participant_ids),
                "status": "pending",
                "reviewed_by": None,
                "pvm_points": 0,
                "participant_points": 0,
            },
            interaction.guild,
        )
        msg = await channel.send(embed=embed, view=view)

        conn = db.get_connection()
        conn.execute("UPDATE submissions SET review_message_id = ? WHERE id = ?", (msg.id, sub_id))
        conn.commit()
        conn.close()

        description = (
            f"**Submission ID:** `{sub_id}`\n"
            f"**Players:** {', '.join(f'`{p}`' for p in player_list)}\n\n"
            f"Sent to {channel.mention} for review."
        )

        embed = discord.Embed(
            title="✅ Submission Sent",
            description=description,
            color=discord.Color.green(),
        )
        embed.set_image(url=image.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="setup_channel", description="Set the channel where submissions get reviewed (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(channel="The channel for submission reviews")
    async def setup_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        db.set_submissions_channel(interaction.guild.id, channel.id)
        embed = discord.Embed(
            title="✅ Review Channel Set",
            description=f"Submissions will now be sent to {channel.mention}.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
            status = s["status"]
            lines.append(
                f"**#{s['id']}** — {s['players']}\n"
                f"└ Submitted by <@{s['user_id']}> • status: `{status}`"
            )

        embed = discord.Embed(
            title="📬 Pending Submissions",
            description="\n\n".join(lines),
            color=discord.Color.orange(),
        )
        embed.set_footer(text="Review them in the submissions channel.")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="verify", description="Manually approve a submission and assign points (admin only)")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        submission_id="The submission ID",
        main_points="Points for the main player",
        participant_points="Points for each participant",
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        submission_id: int,
        main_points: int,
        participant_points: int,
    ):
        sub = db.get_submission(submission_id)
        if sub is None or sub["status"] != "pending":
            embed = discord.Embed(
                title="❌ Not Pending",
                description=f"No pending submission with ID `{submission_id}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await self.accept_submission(interaction, submission_id, main_points, participant_points)

    async def accept_submission(
        self,
        interaction: discord.Interaction,
        sub_id: int,
        main_points: int,
        participant_points: int,
    ):
        sub = db.get_submission(sub_id)
        if sub is None:
            embed = discord.Embed(
                title="❌ Submission Not Found",
                description=f"No submission found with ID `{sub_id}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if sub["status"] != "pending":
            embed = discord.Embed(
                title="❌ Already Reviewed",
                description=f"Submission `{sub_id}` has already been `{sub['status']}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        submitter_id = sub["user_id"]
        participant_ids = [int(x) for x in (sub["participant_ids"] or "").split(",") if x]

        awarded = []
        missing = []

        if db.get_player(submitter_id) is not None:
            db.add_pvm_points(submitter_id, main_points)
            db.add_community_points(submitter_id, COMMUNITY_BONUS)
            awarded.append((submitter_id, main_points, COMMUNITY_BONUS, "main"))
        else:
            missing.append(submitter_id)

        for pid in participant_ids:
            if pid != submitter_id:
                if db.get_player(pid) is not None:
                    db.add_pvm_points(pid, participant_points)
                    db.add_community_points(pid, COMMUNITY_BONUS)
                    awarded.append((pid, participant_points, COMMUNITY_BONUS, "participant"))
                else:
                    missing.append(pid)

        db.update_submission_status(sub_id, "verified", interaction.user.id)
        conn = db.get_connection()
        conn.execute(
            "UPDATE submissions SET pvm_points = ?, participant_points = ? WHERE id = ?",
            (main_points, participant_points, sub_id),
        )
        conn.commit()
        conn.close()

        confirmed_lines = [f"**#{sub_id} verified.**\n"]
        for pid, pts, cmm, role in awarded:
            confirmed_lines.append(
                f"**{role}** (<@{pid}>) received **`{pts}`** PVM + **`{cmm}`** Community points."
            )
        if missing:
            confirmed_lines.append(
                "\n⚠️ **Not in roster, no points given:** "
                + ", ".join(f"<@{pid}>" for pid in missing)
                + "\nAdd them with `/add_player` first."
            )

        confirm_embed = discord.Embed(
            title="✅ Submission Verified",
            description="\n".join(confirmed_lines),
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=confirm_embed, ephemeral=True)

        await self._edit_review_message(interaction, sub, "verified")
        await self._notify_accepted(sub, main_points, participant_points)

    async def deny_submission(self, interaction: discord.Interaction, sub_id: int):
        sub = db.get_submission(sub_id)
        if sub is None:
            embed = discord.Embed(
                title="❌ Submission Not Found",
                description=f"No submission found with ID `{sub_id}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if sub["status"] != "pending":
            embed = discord.Embed(
                title="❌ Already Reviewed",
                description=f"Submission `{sub_id}` has already been `{sub['status']}`.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        db.update_submission_status(sub_id, "denied", interaction.user.id)

        embed = discord.Embed(
            title="✅ Submission Denied",
            description=f"Submission `#{sub_id}` has been denied.",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        await self._edit_review_message(interaction, sub, "denied")
        await self._notify_denied(sub)

    async def _edit_review_message(self, interaction: discord.Interaction, sub: dict, status: str):
        channel = interaction.guild.get_channel(sub["channel_id"]) if sub["channel_id"] else None
        if channel is None:
            return
        try:
            msg = await channel.fetch_message(sub["review_message_id"])
            embed = _review_embed(sub, interaction.guild, status)
            await msg.edit(embed=embed, view=None)
        except discord.NotFound:
            pass
        except discord.Forbidden:
            pass

    async def _notify_accepted(self, sub: dict, main_points: int, participant_points: int):
        try:
            submitter = await self.bot.fetch_user(sub["user_id"])
            embed = discord.Embed(
                title="🎉 Submission Accepted!",
                description=(
                    f"Your submission `#{sub['id']}` was accepted.\n"
                    f"You received **`{main_points}`** PVM + **`{COMMUNITY_BONUS}`** Community points."
                ),
                color=discord.Color.green(),
            )
            await submitter.send(embed=embed)
        except discord.Forbidden:
            pass

        participant_ids = [int(x) for x in (sub["participant_ids"] or "").split(",") if x]
        for pid in participant_ids:
            if pid == sub["user_id"]:
                continue
            try:
                user = await self.bot.fetch_user(pid)
                embed = discord.Embed(
                    title="🎉 Submission Accepted!",
                    description=(
                        f"Your clan submission `#{sub['id']}` was accepted.\n"
                        f"You received **`{participant_points}`** PVM + **`{COMMUNITY_BONUS}`** Community points."
                    ),
                    color=discord.Color.green(),
                )
                await user.send(embed=embed)
            except discord.Forbidden:
                pass

    async def _notify_denied(self, sub: dict):
        try:
            submitter = await self.bot.fetch_user(sub["user_id"])
            embed = discord.Embed(
                title="❌ Submission Denied",
                description=f"Your submission `#{sub['id']}` was denied by an admin.",
                color=discord.Color.red(),
            )
            await submitter.send(embed=embed)
        except discord.Forbidden:
            pass


async def setup(bot):
    await bot.add_cog(Verification(bot))