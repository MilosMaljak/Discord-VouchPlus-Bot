import data
import discord

from data import User, newEmbed, errorMessage, RED, BLUE, GREEN, YELLOW, ORANGE

async def vouch(user: discord.User,
                targetUser: discord.User,
                message: str,
                isPositive: bool,
                curChannel: discord.TextChannel,
                pendingVouchesChannel: discord.TextChannel):

    """
        Leaves a vouch for a user
    """
    u = User(user.id)
    if user.id in u.allData['Blacklist']:
        return

    # Save to pending vouches
    d = data.loadJSON(data.DATABASE_FILENAME)
    vouchNum: int = d['VouchCount'] + 1
    vouch = {
        'ID': vouchNum,
        'Giver': user.id,
        'Receiver': targetUser.id,
        'IsPositive': isPositive,
        'Message': message,
    }
    pendingVouches: list = d['PendingVouches']
    pendingVouches.append(vouch)
    data.updateJSON({
        'PendingVouches': pendingVouches,
        'VouchCount': vouchNum,
    })

    # Send embeds to the user
    embed = newEmbed(description='Vouch is pending.', color=data.YELLOW)
    embed2 = newEmbed(
        description='Thank you for vouching using our bot, please remember when vouching for someone to state the deal when vouching for someone', color=data.GREEN)
    await curChannel.send(embed=embed)
    await curChannel.send(embed=embed2)

    # Send embed to pending channel
    embed = newEmbed(description='', title=f'Vouch ID: {vouchNum}')
    embed.add_field(name='Type', value=(
        'Pos' if isPositive else 'Neg'), inline=False)
    embed.add_field(name='Receiver', value=targetUser.name, inline=False)
    embed.add_field(name='Giver', value=user.name, inline=False)
    embed.add_field(name='Comment', value=message, inline=False)
    embed.set_footer(
        text=f'+approve {vouchNum} | +deny {vouchNum} in order to assign this vouch')
    await pendingVouchesChannel.send(embed=embed)

# ==================================================

async def profile(targetUser: discord.User, bcGuild: discord.Guild,
                  channel: discord.TextChannel):
    '''
        If a user is mentioned, it will display their profiles
        details. If a user isn't mentioned, then the author's
        profile is displayed.
    '''
    u = User(targetUser.id)

    # Decide a proper color
    if u.isScammer or u.dwc == 3:
        color = RED
    elif u.dwc == 2:
        color = ORANGE
    elif u.negVouchCount > u.posVouchCount or u.dwc == 1:
        color = YELLOW
    else:
        color = GREEN

    # Add relevant information
    embed = newEmbed(description='', title='', color=color)
    embed.add_field(name='__Vouch Information:__',
                    value=f'**Positive:** {u.posVouchCount}\n**Negative:** {u.negVouchCount}\n\n**Total:** {len(u.vouches)}')

    # Added Nulled link and verification
    nulledLink = f'[Click Here]({u.link})' if u.link else 'Set this!'
    # verification = ''
    # if u.link:
    verification = '❌' if not u.verified else '✅'
    verification = f'**Verification:**{verification}\n'

    dwcMsg = u.dwcReason + '\n' if u.dwc > 0 else ''
    dwcTitle = '' if u.dwc == 0 else f'**DWC {u.dwc}:** '

    # Add tags and comments
    embed.add_field(
        name='__Tags:__', value=f'**Scammer:** {u.isScammer}\n{dwcTitle}{dwcMsg}{verification}**Nulled Link:** {nulledLink}')

    if u.vouches:
        comments = []
        prevLength = 0
        # Combine all the vouch messages into a list
        for i, x in list(enumerate(u.vouches))[::-1]:
            comment = f'{i+1}) ' + x.message
            # We have to make sure the string total is less than
            # 1024 characters otherwise discord wont send it
            #if len(comment) + prevLength <= 1024:
            #prevLength += len(comment)
            if i < 5:
                comments.append(comment)
            #else:
                #break
        # Combine the comments into new lines
        if comments:
            comments = '\n'.join(comments)
            if len(comments) > 1024:
                comments = comments[:1024]
            embed.add_field(name='__Last 5 Comments:__', value=comments, inline=False)

    # Gather possible roles
    badges = []
    owner_role = discord.utils.get(bcGuild.roles, name='Founder')
    staff_role = discord.utils.get(bcGuild.roles, name='V+ Staff')
    developer_role = discord.utils.get(bcGuild.roles, name='Developer')
    trusted_role = discord.utils.get(bcGuild.roles, name='Trusted')
    supporter_role = discord.utils.get(bcGuild.roles, name='Supporters')
    premium_user_role = discord.utils.get(bcGuild.roles, name='Premium')
    tenP_vouches_role = discord.utils.get(bcGuild.roles, name='10+ vouches')
    twentyP_vouches_role = discord.utils.get(bcGuild.roles, name='20+ vouches')
    thirtyP_vouches_role = discord.utils.get(bcGuild.roles, name='30+ vouches')
    fourtyP_vouches_role = discord.utils.get(bcGuild.roles, name='40+ vouches')
    fiftyP_vouches_role = discord.utils.get(bcGuild.roles, name='50+ vouches')
    sixtyP_vouches_role = discord.utils.get(bcGuild.roles, name='60+ vouches')
    seventyP_vouches_role = discord.utils.get(bcGuild.roles, name='70+ vouches')
    eightyP_vouches_role = discord.utils.get(bcGuild.roles, name='80+ vouches')
    ninetyP_vouches_role = discord.utils.get(bcGuild.roles, name='90+ vouches')
    hundredP_vouches_role = discord.utils.get(bcGuild.roles, name='100+ vouches')
    hundredfiftyP_vouches_role = discord.utils.get(bcGuild.roles, name='150+ vouches')
    twohundredP_vouches_role = discord.utils.get(bcGuild.roles, name='200+ vouches')
    threehundredP_vouches_role = discord.utils.get(bcGuild.roles, name='300+ vouches')
    fourhundredP_vouches_role = discord.utils.get(bcGuild.roles, name='400+ vouches')
    fivehundredP_vouches_role = discord.utils.get(bcGuild.roles, name='500+ vouches')

                   
    for member in bcGuild.members:
        if member == targetUser:
            if owner_role in member.roles:
                badges.append(':crown: **Owner**')

            if staff_role in member.roles:
                badges.append(':shield: **Staff**')

            if developer_role in member.roles:
                badges.append(':hammer_and_wrench: **Developer**')

            if trusted_role in member.roles:
                badges.append(':white_check_mark: **Trusted**')
            
            if supporter_role in member.roles:
                badges.append(':orange_heart: **Supporter**')
            
            if premium_user_role in member.roles:
                badges.append('<:PremiumBadge:900351270890639370> **Premium User**')

            if tenP_vouches_role in member.roles:
                badges.append('<:10pVouches:900351167085834280> **10+ vouches**')
            
            if twentyP_vouches_role in member.roles:
                badges.append('<:20pVouches:900351175948386326> **20+ vouches**')
            
            if thirtyP_vouches_role in member.roles:
                badges.append('<:30pVouches:900351183644921916> **30+ vouches**')
            
            if fourtyP_vouches_role in member.roles:
                badges.append('<:40pVouches:900351190452277280> **40+ vouches**')
            
            if fiftyP_vouches_role in member.roles:
                badges.append('<:50pVouches:900351196575969310> **50+ vouches**')
            
            if sixtyP_vouches_role in member.roles:
                badges.append('<:60pVouches:900351203299442698> **60+ vouches**')
            
            if seventyP_vouches_role in member.roles:
                badges.append('<:70pVouches:900351209091792917> **70+ vouches**')
            
            if eightyP_vouches_role in member.roles:
                badges.append('<:80pVouches:900351215517450311> **80+ vouches**')
            
            if ninetyP_vouches_role in member.roles:
                badges.append('<:90pVouches:900351221569843221> **90+ vouches**')
            
            if hundredP_vouches_role in member.roles:
                badges.append('<:100pVouches:900351228603695144> **100+ vouches**')
            
            if hundredfiftyP_vouches_role in member.roles:
                badges.append('<:150pVouches:900351234257616897> **150+ vouches**')
            
            if twohundredP_vouches_role in member.roles:
                badges.append('<:200pVouches:900351241241128990> **200+ vouches**')
            
            if threehundredP_vouches_role in member.roles:
                badges.append('<:300pVouches:900351249348706324> **300+ vouches**')
            
            if fourhundredP_vouches_role in member.roles:
                badges.append('<:400pVouches:900351249348706324> **400+ vouches**')
            
            if fivehundredP_vouches_role in member.roles:
                badges.append('<:500pVouches:900351262665613342> **500+ vouches**')


    formattedBadges = '\n'.join(badges)
    if len(badges) == 0:
        formattedBadges = 'No badges given.'
    if u.isScammer:
        authorName = f'💀{str(targetUser)} 💀'
    elif u.dwc:
        authorName = f'⚠️{str(targetUser)} ⚠️'
    else:
        authorName = f'{str(targetUser)}\'s Profile'

    embed.set_image(url=u.profileBanner)
    embed.add_field(name='__Badges:__', value=formattedBadges, inline=False)
    embed.set_author(name=authorName, icon_url=targetUser.avatar_url)
    embed.set_thumbnail(url=targetUser.avatar_url)
    embed.set_footer(text='Endorsed by BCN')

    await channel.send(embed=embed)

# ==================================================

async def token(user: discord.User, channel: discord.TextChannel):
    u = User(user.id)
    embed = newEmbed(description=f'Your token: {u.token}')
    await user.send(embed=embed)
    embed = newEmbed(description='Token was DM\'d to you.')
    await channel.send(embed=embed)

# ==================================================

async def redeem(user: discord.User, token: str,
                 channel: discord.TextChannel):
    '''
        Redeems a token and transfers all vouches
        to the new account
    '''
    u = User(user.id)
    success = u.redeemToken(token)
    if success:
        embed = newEmbed(description='Retrieved all vouches!',
                         title='Token Redeemed', color=GREEN)
    else:
        embed = newEmbed(description='Could not find token!',
                         title='Error', color=RED)

    await channel.send(embed=embed)

# ==================================================

async def help(prefix: str, channel: discord.TextChannel, isMaster: bool = False, isStaff: bool = False):
    '''
        Displays all the commands that the user can use
    '''
    embed = discord.Embed(title='Vouch Pro Commands',
                          color=(GREEN if isMaster else BLUE))

    embed.add_field(name=f'[+ or -]vouch [@user] [message]',
                    value='Leave a positive or negative vouch for the user.',
                    inline=False)
    embed.add_field(name=f'{prefix}token',
                    value='View your current token.',
                    inline=False)
    embed.add_field(name=f'{prefix}redeem [token]',
                    value='Transfers all the vouches from another account to the current one.',
                    inline=False)
    embed.add_field(name=f'{prefix}link [nulled.to link]',
                    value='Link your Nulled profile.',
                    inline=False)
    embed.add_field(name=f'{prefix}p **OR** {prefix}profile [@user]',
                    value='See a user\'s profile. (If user is not provided, shows the senders profile).',
                    inline=False)
    embed.add_field(name=f'{prefix}about',
                    value='Displays info about Vouch Plus',
                    inline=False)
    embed.add_field(name=f'{prefix}displayvouches',
                    value='Displays last 20 vouches that user has received',
                    inline=False)                                   
    embed.add_field(name=f'{prefix}banner [link to your banner]',
                    value='Sets the banner onto your profile (Only available to **Premium** users).',
                    inline=False)
    embed.add_field(name=f'{prefix}rbanner',
                    value='Removes the banner from your profile (Only available to **Premium** users).',
                    inline=False)
    if isMaster:
        embed.add_field(name=f'{prefix}deny [vouch ID]',
                        value='Denies a vouch.',
                        inline=False)
        embed.add_field(name=f'{prefix}approve [vouch ID]',
                        value='Approves a vouch',
                        inline=False)
        embed.add_field(name=f'{prefix}addvouches [@user] [amount of the vouches]',
                        value='Adds the desired amount of the vouches to the given user',
                        inline=False)
        embed.add_field(name=f'{prefix}acceptall [@user]',
                        value='Accepts all the pending vouches of the given user',
                        inline=False)
        embed.add_field(name=f'{prefix}admin [@user]',
                        value='Toggles admin privelges for the user.',
                        inline=False)
        embed.add_field(name=f'{prefix}dwc[1 or 2 or 3] [@user] [reason]',
                        value='Adds the DWC tag for the user.',
                        inline=False)
        embed.add_field(name=f'{prefix}dwc [@user]',
                        value='Removes the DWC tag for the user.',
                        inline=False)
        embed.add_field(name=f'{prefix}scammer [@user]',
                        value='Toggles the Scammer tag for the user',
                        inline=False)
        embed.add_field(name=f'[+ or -]add [@user] [giverID (optional)] [message]',
                        value='Leave a positive or negative vouch for the user.',
                        inline=False)
        embed.add_field(name=f'{prefix}blacklist [@user]',
                        value='Blacklists a user from vouching.',
                        inline=False)
        embed.add_field(name=f'{prefix}remove [@user] [vouch ID]',
                        value='Removes a vouch from a user.',
                        inline=False)
        
    await channel.send(embed=embed)

# ==================================================

async def about(channel: discord.TextChannel, avatarUrl):
    embed = newEmbed(description='', title='About Vouch Plus')

    embed.add_field(name='What is it?', value=f'**Vouch Plus is a bot created to end the corruption on discord marketplaces.** We have teamed up with some of the leading people in discord trading business and as a result we created Vouch Plus to once and for all put a STOP sign to the scamming business that has been going for too long, especially here on discord platform.')
    embed.add_field(name='How do I add it?',
                    value='**Below is the invite URL:\n**https://discord.com/api/oauth2/authorize?client_id=782642754643558430&permissions=346176&scope=bot')
    embed.set_image(
        url='https://cdn.discordapp.com/attachments/801154096869408818/801154330886668329/VouchPlus.png')
    embed.set_author(name='Vouch Plus', icon_url=avatarUrl)
    embed.set_footer(text='Endorsed by BCN')

    await channel.send(embed=embed)

# ==================================================

async def link(user: discord.User, link: str, channel: discord.TextChannel):
    '''
        Links a Nulled.to account to the profile
    '''
    u = User(user.id)
    u.setLink(link)
    embed = newEmbed(description='Successfully set profile link!', color=GREEN)
    await channel.send(embed=embed)

# ==================================================

async def vouches(targetUser: discord.User, channel: discord.TextChannel):
    """
        Displays the list of all the vouches that user has obtained
    """
    u = User(targetUser.id)

    # Decide a proper color
    if u.isScammer or u.dwc == 3:
        color = RED
    elif u.dwc == 2:
        color = ORANGE
    elif u.negVouchCount > u.posVouchCount or u.dwc == 1:
        color = YELLOW
    elif not (u.vouches):
        color = RED
    else:
        color = GREEN
    
    embed = newEmbed(description='', title='', color=color)

    if u.vouches:
        comments = []
        prevLength = 0
        # Combine all the vouch messages into a list
        for i, x in list(enumerate(u.vouches))[::-1]:
            comment = f'{i+1}) ' + x.message
            if i < 10:
            # We have to make sure the string total is less than
            # 1024 characters otherwise discord wont send it
                if len(comment) + prevLength <= 1024:
                    prevLength += len(comment)
                    comments.append(comment)
                else:
                    break
        # Combine the comments into new lines
        if comments:
            comments = '\n\n'.join(comments)
            if len(comments) > 1024:
                comments = comments[:1024]
            embed.add_field(name='__Last 10 Comments:__', value=comments, inline=False)
        
    if u.isScammer:
        authorName = f'💀{str(targetUser)} 💀'
    elif u.dwc:
        authorName = f'⚠️{str(targetUser)} ⚠️'
    else:
        authorName = f'{str(targetUser)}\'s Vouches'
    if not (u.vouches):
        embed.add_field(name='ERROR', value='User has no current vouches available', inline=False)
    embed.set_image(url=u.profileBanner)
    embed.set_author(name=authorName, icon_url=targetUser.avatar_url)
    embed.set_thumbnail(url=targetUser.avatar_url)
    embed.set_footer(text='Endorsed by BCN')

    await channel.send(embed=embed)
