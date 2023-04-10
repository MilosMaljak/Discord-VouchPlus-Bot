import data
import discord

from data import User, Vouch, newEmbed, errorMessage, RED, BLUE, GREEN, YELLOW

async def approve(vouchID: int, channel: discord.TextChannel,
                  logChannel: discord.TextChannel, getUser):
    '''
        Approves a vouch
    '''
    # Load the pending vouches
    allData = data.loadJSON(data.DATABASE_FILENAME)
    pendingVouches = allData['PendingVouches']

    # Check if the vouch exists, then delete it
    for i, x in enumerate(pendingVouches):
        if x['ID'] == vouchID:
            # vouch = x
            vouch = data.Vouch(x)
            del pendingVouches[i]
            break
    else:
        await errorMessage(f'Could not find vouch with ID: {vouchID}', channel)
        return

    u = data.User(vouch.receiverID, allData)
    u.addVouch(vouch)
    receiverUser: discord.User = getUser(vouch.receiverID)
    giverUser: discord.User = getUser(vouch.giverID)

    # Message the user when their vouch is approved
    # and only if they haven't opted out of notifications
    if not u.ignoreNotifications:
        isPositive = vouch.isPositive
        vouchType = 'positive' if isPositive else 'negative'
        msg = f'Received a {vouchType} vouch!'

        embed = newEmbed(description=msg, color=(GREEN if isPositive else RED))
        embed.set_footer(
            text='React with ❌ to stop receiving vouch notifications')
        msg_1 = await receiverUser.send(embed=embed)
        await msg_1.add_reaction('❌')
        
    # Save the vouch and send embed
    data.updateJSON({'PendingVouches': pendingVouches})

    embed = newEmbed(description=f'Approved vouch #{vouchID}!', color=data.GREEN)
    await channel.send(embed=embed)

    # Send embed to log channel
    embed = newEmbed(description='', title=f'Vouch ID: {vouchID}')
    embed.add_field(name='Type', value=(
        'Pos' if isPositive else 'Neg'), inline=False)
    embed.add_field(name='Receiver', value=receiverUser.name, inline=False)
    embed.add_field(name='Giver', value=giverUser.name, inline=False)
    embed.add_field(name='Comment', value=vouch.message, inline=False)
    embed.set_footer(
        text='Approved Vouch')
    await logChannel.send(embed=embed)

# ==================================================

async def acceptall(targetUser: discord.User, channel: discord.TextChannel):
    """
        Approves all vouches for a targeted user
    """
    allData = data.loadJSON(data.DATABASE_FILENAME)
    pendingVouches = allData['PendingVouches']
    u = User(targetUser.id)

    for i, x in reversed(list(enumerate(pendingVouches))):
        if targetUser.id == x['Receiver']:
            vouch = data.Vouch(x)
            u.addVouch(vouch)
            del pendingVouches[i]

        else:
            await errorMessage('User has no pending vouches at the moment', channel)
            return

    # Save the vouch and send embed     
    data.updateJSON({'PendingVouches': pendingVouches})
    
    embed = newEmbed(description=f'Approved all vouches for {targetUser}!', color=data.GREEN)
    await channel.send(embed=embed)
    
# ==================================================

async def addvouches(
              user: discord.User,
              targetUser: discord.User,
              channel: discord.TextChannel,
              vouch_count: int,
              isPositive: bool=True,
              giverID: int = 0,
              message: str = "Test Vouch"):
    '''
        Adds desired amount of vouches to the user
    '''
    u = User(user.id)

    # Create a new vouch
    d = data.loadJSON(data.DATABASE_FILENAME)
    vouchCount = data.loadJSON(data.DATABASE_FILENAME)['VouchCount']
    for i in range (1, vouch_count+1): 
        vouchNum: int = d['VouchCount'] + 1
        vouch = {
            'ID': vouchNum,
            'Giver': user.id if giverID == 0 else giverID,
            'Receiver': targetUser.id,
            'IsPositive': isPositive,
            'Message': message,
        }
        d['VouchCount'] += 1
        data.updateJSON({'VouchCount': d['VouchCount']})
        vouch = Vouch(vouch)
        u.addVouch(vouch)

    embed = newEmbed(description=f'__{vouch_count}__ vouches have been successfully added to `{targetUser}`', color=data.GREEN)
    await channel.send(embed=embed)

# ==================================================

async def deny(vouchID: int, channel: discord.TextChannel):
    """  
        Denies a vouch
    """
    vouchCount = data.loadJSON(data.DATABASE_FILENAME)['VouchCount']
    pendingVouches = data.loadJSON(data.DATABASE_FILENAME)['PendingVouches']
    # Check if it exists, then delete it
    for i, x in enumerate(pendingVouches):
        if x['ID'] == vouchID:
            del pendingVouches[i]
            break
    else:
        await errorMessage(f'Could not find vouch with ID: {vouchID}', channel)
        return

    data.updateJSON({'PendingVouches': pendingVouches})
    data.updateJSON({'VouchCount': vouchCount - 1})
    embed = newEmbed(description=f'Deleted vouch #{vouchID}!', color=data.GREEN)
    await channel.send(embed=embed)

# ==================================================

async def dwc(targetUser: discord.User,
              level: int,
              reason: str,
              channel: discord.TextChannel):
    '''
        Toggles Deal With Caution role to mentioned user
    '''
    u = User(targetUser.id)
    u.setDWC(level, reason)

    if level != 0:
        embed = newEmbed(
            description=f'Added DWC{level} to {targetUser.mention}!',
            color=GREEN)
    else:
        embed = newEmbed(
            description=f'Removed DWC for {targetUser.mention}!',
            color=GREEN)

    await channel.send(embed=embed)

# ==================================================

async def scammer(targetUser: discord.User, channel: discord.TextChannel):
    '''
        Toggles Scammer role to mentioned user
    '''
    u = User(targetUser.id)
    u.setScammer(not u.isScammer)

    if u.isScammer:
        embed = newEmbed(
            description=f'Added Scammer to {targetUser.mention}!',
            color=GREEN)
    else:
        embed = newEmbed(
            description=f'Removed Scammer for {targetUser.mention}!',
            color=GREEN)

    await channel.send(embed=embed)

# ==================================================

async def verify(targetUser: discord.User, channel: discord.TextChannel):
    '''
        Toggles Verification for mentioned user
    '''
    u = User(targetUser.id)
    u.setVerified(not u.verified)

    if u.verified:
        embed = newEmbed(
            description=f'Verified {targetUser.mention}!', color=GREEN)
    else:
        embed = newEmbed(
            description=f'Unverified {targetUser.mention}!', color=GREEN)

    await channel.send(embed=embed)

# ==================================================

async def banner(user: discord.User, banner: str, channel: discord.TextChannel):
    """
        Sets the banner onto the user's profile
    """
    u = User(user.id)
    u.setBanner(banner)

    if u.setBanner:
        embed = newEmbed(
            description=f'Successfully set the banner!', color=GREEN)
    else:
        embed = newEmbed(
            description=f'Hmmm something when wrong, please try again.', color=RED)
    await channel.send(embed=embed)

# ==================================================

async def rbanner(user: discord.User, channel: discord.TextChannel):
    """
        Removes the banner from the user's profile
    """
    u = User(user.id)
    u.removeBanner()
    
    embed = newEmbed(
        description=f'Successfully removed the banner!', color=GREEN)
    await channel.send(embed=embed)

# ==================================================

async def admin(targetUser: discord.User, channel: discord.TextChannel):
    '''
        Toggles Master privileges to mentioned user
    '''
    masters = data.loadJSON(data.DATABASE_FILENAME)['Masters']
    if targetUser.id in masters:
        masters.remove(targetUser.id)
        embed = newEmbed(description='Removed admin!', color=GREEN)
    else:
        masters.append(targetUser.id)
        embed = newEmbed(description='Added admin!', color=GREEN)

    data.updateJSON({'Masters': masters})
    await channel.send(embed=embed)

# ==================================================

async def staff(targetUser: discord.User, channel: discord.TextChannel):
    '''
        Toggles staff privileges to mentioned user
    '''
    masters = data.loadJSON(data.DATABASE_FILENAME)['Staff']
    if targetUser.id in masters:
        masters.remove(targetUser.id)
        embed = newEmbed(description='Removed staff!', color=GREEN)
    else:
        masters.append(targetUser.id)
        embed = newEmbed(description='Added staff!', color=GREEN)

    data.updateJSON({'Staff': masters})
    await channel.send(embed=embed)

# ==================================================

async def premium(targetUser: discord.User, channel: discord.TextChannel):
    '''
        Toggles premium privileges to mentioned user
    '''
    premiums = data.loadJSON(data.DATABASE_FILENAME)['PremiumUsers']
    if targetUser.id in premiums:
        premiums.remove(targetUser.id)
        embed = newEmbed(description='Removed premium', color=GREEN)
    else:
        premiums.append(targetUser.id)
        embed = newEmbed(description='Added premium!', color=GREEN)

    data.updateJSON({'PremiumUsers': premiums})
    await channel.send(embed=embed)

# ==================================================

async def blacklist(targetUserID: int, channel: discord.TextChannel):
    '''
        Toggles the blacklist for the mentioned
        user from vouching other people
    '''
    blacklist: list = data.loadJSON(data.DATABASE_FILENAME)['Blacklist']
    if targetUserID in blacklist:
        blacklist.remove(targetUserID)
        embed = newEmbed(
            description='Removed user from blacklist!', color=GREEN)
    else:
        blacklist.append(targetUserID)
        embed = newEmbed(
            description=f'Added to blacklist!',
            color=GREEN)

    data.updateJSON({'Blacklist': blacklist})
    await channel.send(embed=embed)

# ==================================================

async def add(user: discord.User,
              targetUser: discord.User,
              message: str,
              isPositive: bool,
              curChannel: discord.TextChannel,
              logChannel: discord.TextChannel,
              giverID: int = 0):
    '''
        Leaves a vouch for a user
    '''
    u = User(user.id)

    # Create a new vouch
    d = data.loadJSON(data.DATABASE_FILENAME)
    vouchNum: int = d['VouchCount'] + 1
    vouch = {
        'ID': vouchNum,
        'Giver': user.id if giverID == 0 else giverID,
        'Receiver': targetUser.id,
        'IsPositive': isPositive,
        'Message': message,
    }
    vouch = Vouch(vouch)
    u.addVouch(vouch)

    # Message the user when their vouch is approved
    # and only if they haven't opted out of notifications
    if not u.ignoreNotifications:
        vouchType = 'positive' if isPositive else 'negative'
        msg = f'Received a {vouchType} vouch!'

        embed = newEmbed(description=msg, color=(GREEN if isPositive else RED))
        embed.set_footer(
            text='React with ❌ to stop receiving vouch notifications')
        msg_1 = await targetUser.send(embed=embed)
        await msg_1.add_reaction('❌')

    # Send confirmation message
    embed = newEmbed(
        description=f'Added vouch to {targetUser.mention}', color=GREEN)
    await curChannel.send(embed=embed)

    # Send embed to log channel
    embed = newEmbed(description='', title=f'Vouch ID: {vouchNum}')
    embed.add_field(name='Type', value=(
        'Pos' if isPositive else 'Neg'), inline=False)
    embed.add_field(name='Receiver', value=targetUser.name, inline=False)
    embed.add_field(name='Giver', value=user.name, inline=False)
    embed.add_field(name='Comment', value=message, inline=False)
    embed.set_footer(
        text='Added Vouch')
    await logChannel.send(embed=embed)

# ==================================================

async def remove(targetUser: discord.User,
                 channel: discord.TextChannel,
                 vouchID: int = -1):
    '''
        Lists vouches for a person and
        deletes a specific vouch
    '''
    u = User(targetUser.id)

    # If a vouch ID wasn't passed in, then list them out
    if vouchID == -1:
        vouches = u.formatVouches()
        if len(vouches) == 0:
            vouches = 'No vouches to show!'
        embed = newEmbed(description=vouches, color=BLUE)
        await channel.send(embed=embed)
        return

    success = u.removeVouch(vouchID)

    if success:
        description = 'Successfully removed vouch from profile.'
    else:
        description = f'Vouch #{vouchID} does not exist for this profile.'

    embed = newEmbed(
        description=description, color=(GREEN if success else RED))
    await channel.send(embed=embed)