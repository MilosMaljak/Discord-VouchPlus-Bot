#!/usr/bin/env python3


import discord 
import config
import data
import userCommands
import adminCommands

from data import User, Vouch, newEmbed, errorMessage, RED, BLUE, GREEN, YELLOW

PREFIX='+'
intents = discord.Intents.default()
intents.members = True


class DiscordBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allData = data.loadJSON(data.DATABASE_FILENAME)
        self.MasterIDs = allData['Masters']
        self.StaffIDs = allData['Staff']
        self.PremiumIDs = allData['PremiumUsers']
    # ==================================================

    async def on_ready(self):
        """ 
            Called when the discord bot logs in
        """    
        print(f'{self.user.name} successfully logged in!')
        print('---------------------------------\n')

        
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        # Unsubscribe from vouch notifications
        description = reaction.message.embeds[0].description
        if 'Received a' in description and reaction.emoji == '❌':
            noNotifs = data.loadJSON(data.DATABASE_FILENAME)[
                'NoNotificationIDs']
            if user.id not in noNotifs:
                embed = newEmbed(
                    description='Unsubscribed from notifications!')
                embed.set_footer(
                    text='To resubscribe, react with ✅')
                noNotifs.append(user.id)
                data.updateJSON({'NoNotificationIDs': noNotifs})
                msg_1 = await user.send(embed=embed)
                await msg_1.add_reaction('✅')

        # Resubscribe to vouch notifications
        elif 'Unsubscribed' in description and reaction.emoji == '✅':
            noNotifs = data.loadJSON(data.DATABASE_FILENAME)[
                'NoNotificationIDs']
            if user.id in noNotifs:
                #embed = newEmbed(description='Resubscribed to notifications!')
                #embed.set_footer(text='To unsubscribe, react with ❌')
                noNotifs.remove(user.id)
                data.updateJSON({'NoNotificationIDs': noNotifs})
                #msg_2 = await user.send(embed=embed)
                #await msg_2.add_reaction('❌')


    async def on_message(self, message: discord.Message):
        """
            Handles all bot commands
        """
        
        if message.author == self.user:
            return

        isMaster = message.author.id in self.MasterIDs
        isStaff = message.author.id in self.StaffIDs or isMaster
        isPremium = message.author.id in self.PremiumIDs or isStaff
        loweredMsg = message.content.lower()
        words = message.content.split()

    # ==================================================
    
        if loweredMsg.startswith('+vouch') or loweredMsg.startswith('-vouch'):
            if len(message.mentions) == 0 or len(words) < 3:
                await errorMessage('Please follow this format: [+ or -]vouch [@user] [message]',
                                    message.channel)
                return

            if message.author.id == message.mentions[0].id:
                await errorMessage('You cannot vouch for yourself.', message.channel)
                return

            vouchMessage = ' '.join(words[2:])
            isPositive = loweredMsg[0] == '+'
            pendingChannel = self.get_channel(config.PENDING_VOUCHES_CHANNEL_ID)
            await userCommands.vouch(message.author,
                                     message.mentions[0],
                                     vouchMessage,
                                     isPositive,
                                     message.channel,
                                     pendingChannel)

        # ==================================================

        elif (loweredMsg.startswith(f'{PREFIX}approve') and isStaff):
            if len(words) < 2 or not words[1].isdigit():
                await errorMessage(f'Please follow this format: {PREFIX}approve [vouch ID]',
                                   message.channel)
                return

            ids = [int(i) for i in words[1:] if i.isdigit()]
            logChannel = self.get_channel(config.LOGGING_CHANNEL_ID)
            for i in ids:
                await adminCommands.approve(i, message.channel,
                                            logChannel, self.get_user)

        # ==================================================

        elif(loweredMsg.startswith(f'{PREFIX}acceptall') and isStaff):
            if len(message.mentions) == 0:
                user = message.author
            else:
                user = message.mentions[0]
            
            await adminCommands.acceptall(
                targetUser=user,
                channel=message.channel
            )
        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}deny') and isStaff:
            if len(words) < 2 or not words[1].isdigit():
                await errorMessage(f'Please follow this format: {PREFIX}deny [vouch ID]',
                                        message.channel)
                return

            ids = [int(i) for i in words[1:] if i.isdigit()]
            for i in ids:
                await adminCommands.deny(i, message.channel)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}dwc') and isMaster:
            if 'dwc1' in loweredMsg:
                level = 1
            elif 'dwc2' in loweredMsg:
                level = 2
            elif 'dwc3' in loweredMsg:
                level = 3
            else:
                level = 0

            if len(message.mentions) == 0 or (level != 0 and len(words) < 3):
                await errorMessage(f'Please follow this format: {PREFIX}dwc [@user] [reason]',
                                   message.channel)
                return

            reason = ' '.join(words[2:]) if level != 0 else ''
            await adminCommands.dwc(message.mentions[0], level, reason, message.channel)

        # ==================================================
        
        elif loweredMsg.startswith(f'{PREFIX}profile') or loweredMsg.startswith(f'{PREFIX}p'):
            if len(message.mentions) == 0:
                user = message.author
            else:
                user = message.mentions[0]

            await userCommands.profile(
                targetUser=user,
                bcGuild=self.get_guild(900339658427351081),
                channel=message.channel
            )

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}displayvouches'):
            if len(message.mentions) == 0:
                user = message.author
            else:
                user = message.mentions[0]
            
            await userCommands.vouches(
                targetUser = user,
                channel=message.channel
            )

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}scammer') and isMaster:
            if len(message.mentions) == 0:
                await errorMessage(f'Please follow this format: {PREFIX}scammer [@user]',
                                   message.channel)
                return

            await adminCommands.scammer(message.mentions[0], message.channel)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}verify') and isMaster:
            if len(message.mentions) == 0:
                await errorMessage(f'Please follow this format: {PREFIX}verify [@user]',
                                   message.channel)
                return

            await adminCommands.verify(message.mentions[0], message.channel)
        
        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}banner') and isPremium:
            if len(words) < 2:
                await errorMessage(f'Please follow this format: {PREFIX}banner [link to your banner]',
                                   message.channel)
                return

            await adminCommands.banner(message.author, words[1], message.channel)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}rbanner') and isPremium:
            if len(words) > 1:
                await errorMessage(f'Please follow this format: {PREFIX}rbanner',
                                    message.channel)
                return
            await adminCommands.rbanner(message.author, message.channel)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}help'):
            await userCommands.help(PREFIX,
                                    message.channel,
                                    isMaster)
        
        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}about'):
            await userCommands.about(message.channel, self.user.avatar_url)
        
        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}link'):
            if len(words) < 2:
                await errorMessage(
                    f'Please follow this format: {PREFIX}link [https://nulled.to/ link]',
                    message.channel)
                return

            if 'https://nulled.to/' not in words[1]:
                await errorMessage(
                    'Please provide a proper nulled.to link!',
                    message.channel)
                return

            await userCommands.link(message.author, words[1], message.channel)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}admin') and isMaster:
            if len(message.mentions) == 0:
                await errorMessage(f'Please follow this format: {PREFIX}admin [@user]',
                                   message.channel)
                return

            await adminCommands.admin(message.mentions[0], message.channel)
            if message.mentions[0].id in self.MasterIDs:
                self.MasterIDs.remove(message.mentions[0].id)
            else:
                self.MasterIDs.append(message.mentions[0].id)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}staff') and isMaster:
            if len(message.mentions) == 0:
                await errorMessage(f'Please follow this format: {PREFIX}staff [@user]',
                                   message.channel)
                return

            await adminCommands.staff(message.mentions[0], message.channel)
            if message.mentions[0].id in self.StaffIDs:
                self.StaffIDs.remove(message.mentions[0].id)
            else:
                self.StaffIDs.append(message.mentions[0].id)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}premium') and isMaster:
            if len(message.mentions) == 0:
                await errorMessage(f'Please follow this format: {PREFIX}premium [@user]',
                                   message.channel)
                return

            await adminCommands.premium(message.mentions[0], message.channel)
            if message.mentions[0].id in self.PremiumIDs:
                self.PremiumIDs.remove(message.mentions[0].id)
            else:
                self.PremiumIDs.append(message.mentions[0].id)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}blacklist') and isMaster:
            if len(message.mentions) == 0:
                if len(words) >= 2 and not words[1].isdigit():
                    await errorMessage(f'Please follow this format: {PREFIX}blacklist [@user]',
                                       message.channel)
                    return

            if len(message.mentions) != 0:
                id = message.mentions[0].id
            else:
                id = int(words[1])

            await adminCommands.blacklist(id, message.channel)
        
        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}token'):
            await userCommands.token(message.author, message.channel)

        # ==================================================
        
        elif loweredMsg.startswith(f'{PREFIX}redeem'):
            if len(words) <= 1:
                await errorMessage(f'Please follow this format: {PREFIX}redeem [token]',
                                   message.channel)
                return

            await userCommands.redeem(message.author, words[1],
                                      message.channel)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}addvouches'):
            if len(message.mentions) == 0 or len(words) < 3:
                await errorMessage('Please follow this format: +addvouches [@user] [number of vouches]',
                                    message.channel)
                return
            
            await adminCommands.addvouches(message.author, message.mentions[0], message.channel, int(words[2]))

        # ==================================================

        elif (loweredMsg.startswith('+add') or loweredMsg.startswith('-add')) and isMaster:
            if len(message.mentions) == 0 or len(words) < 3:
                await errorMessage(f'Please follow this format: [+ or -]add [@user] [giverID (optional)] [message]',
                                   message.channel)
                return

            # Check if they specify the giver ID
            hasGiverID = False
            giverID = 0
            if words[2].isdigit():
                hasGiverID = True
                giverID = int(words[2])

            vouchMessage = ' '.join(
                words[3:]) if hasGiverID else ' '.join(words[2:])
            isPositive = loweredMsg[0] == '+'
            logChannel = self.get_channel(config.LOG_CHANNEL_ID)
            await adminCommands.add(message.author,
                                    message.mentions[0],
                                    vouchMessage,
                                    isPositive,
                                    message.channel,
                                    logChannel,
                                    giverID)

        # ==================================================

        elif loweredMsg.startswith(f'{PREFIX}remove') and isMaster:
            if len(message.mentions) == 0 or len(words) < 2:
                await errorMessage(f'Please follow this format:\n{PREFIX}remove [@user]\n**or**\n{PREFIX}remove [@user] [vouch ID]',
                                   message.channel)
                return

            vouchNum = -1
            if len(words) >= 3 and words[2].isdigit():
                vouchNum = int(words[2])
                if vouchNum < 0:
                    await errorMessage('Vouch ID cannot be negative!', message.channel)
                    return

            await adminCommands.remove(message.mentions[0], message.channel, vouchNum)


client = DiscordBot(intents=intents)
client.run(config.BOT_TOKEN)