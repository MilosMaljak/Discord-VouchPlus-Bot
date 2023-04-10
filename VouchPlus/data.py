import json
import discord
import string
import random

DATABASE_FILENAME = 'database.json'

RED = 0xEF233C
BLUE = 0x00A6ED
GREEN = 0x3EC300
YELLOW = 0xFFB400
ORANGE = 0xFF7106


def loadJSON(filename: str) -> dict:
    with open(DATABASE_FILENAME, 'r') as f:
        return json.load(f)

def saveJSON(data: dict):
    with open(DATABASE_FILENAME, 'w') as f:
        json.dump(data, f, indent=4)
    return True

def updateJSON(data: dict):
    try:
        d = loadJSON(DATABASE_FILENAME)
    except FileNotFoundError:
        d = {}
    d.update(data)
    saveJSON(d)

# ==================================================

def newEmbed(description: str,
             color: hex = BLUE,
             title: str = 'Vouch Plus') -> discord.Embed:
    """
    Creates a new embed object
    """
    return discord.Embed(
        title = title,
        color = color,
        description = description,
    )

# ==================================================

async def errorMessage(message: str, channel: discord.TextChannel):
    '''
        Sends an error message to a channel
    '''
    embed = newEmbed(message, color=RED, title='Error')
    await channel.send(embed=embed)

# ==================================================

def generateToken() -> str:
    return ''.join(random.choices(string.hexdigits, k=16)).upper()

# ==================================================

class Vouch:
    def __init__(self, vouchData: dict):
        self.vouchID = vouchData.get('ID', -1)
        self.message = vouchData.get('Message', '')
        self.giverID = vouchData.get('Giver', 0)
        self.receiverID = vouchData.get('Receiver', 0)
        self.isPositive = vouchData.get('IsPositive', True)

    def toDict(self) -> dict:
        '''
            Represents the Vouch object as a dictionary
        '''
        return {
            'ID': self.vouchID,
            'Message': self.message,
            'Giver': self.giverID,
            'Receiver': self.receiverID,
            'IsPositive': self.isPositive,
        }

# ==================================================

class User:
    def __init__(self, userID: int, userData: dict = None):
        self.userID = int(userID)
        self.allData = loadJSON(DATABASE_FILENAME)
        self.users = self.allData['Users']

        for i in self.users:
            if userID == i['ID']:
                userData = i
                self.isNewUser = False
                break
        else:
            self.isNewUser = True
            userData = {}

        self.isMaster = userID in self.allData['Masters']
        self.vouches = [Vouch(i) for i in userData.get('Vouches', [])]
        self.ignoreNotifications = userID in self.allData['NoNotificationIDs']
        self.link = userData.get('Link', '')
        self.dwc = userData.get('DWC', 0)
        if self.dwc is False or self.dwc is True:
            self.dwc = 0
        self.dwcReason = userData.get('DWC Reason', '')
        self.isScammer = userData.get('Scammer', False)
        self.token = userData.get('Token', generateToken())
        self.verified = userData.get('Verified', False)
        self.profileBanner = userData.get('Banner', '')
        self.posVouchCount = len([i for i in self.vouches if i.isPositive])
        self.negVouchCount = len(self.vouches) - self.posVouchCount

        if self.isNewUser:
            self.save()
    
    def addVouch(self, vouch: Vouch):
        """ 
            Adds a vouch to the user
        """
        self.vouches.append(vouch)
        self.save()
    
    # ==================================================

    def setScammer(self, scammer: bool):
        '''
            Sets the user as a scammer or not
        '''
        self.isScammer = scammer
        self.save()
    
    # ==================================================

    def redeemToken(self, token: str) -> bool:
        '''
            Transfers all previous vouches to the 
            current profile
        '''
        for i, x in enumerate(self.users):
            if x['Token'] == token:
                self.vouches.extend([Vouch(i) for i in x.get('Vouches')])
                break
            
        else:
            return False

        self.save()    
        return True

    # ==================================================

    def setDWC(self, dwc: int, reason: str):
        '''
            Sets the Deal With Caution flag on the user
        '''
        self.dwc = dwc
        self.dwcReason = reason
        self.save()
    
    # ==================================================

    def setVerified(self, verified: bool):
        '''
            Updates the verification of the user
        '''
        self.verified = verified
        self.save()
    
    # ==================================================

    def setLink(self, link: str):
        '''
            Updates the link of the user
        '''
        self.link = link
        self.save()
    
    # ==================================================

    def setBanner(self, banner: str):
        """
            Sets the banner onto the user's profile 
        """
        self.profileBanner = banner
        self.save()
    
    # ==================================================

    def removeBanner(self):
        """
            Removes the banner from the user's profile
        """
        self.profileBanner=''
        self.save()
    
    # ==================================================

    def removeVouch(self, vouchID: int) -> bool:
        '''
            Removes a vouch from the user and database
        '''
        for i, x in enumerate(self.vouches):
            if x.vouchID == vouchID:
                del self.vouches[i]
                break
        else:
            return False

        self.save()
        return True
    
    # ==================================================

    def formatVouches(self) -> string:
        '''
            Lists the vouches in an organized string
        '''
        vouches = ''
        prevLength = 0
        # Combine all the vouch messages into a list
        for i in self.vouches[::-1]:
            rate = 'Pos' if i.isPositive else 'Neg'
            s = f'**ID** {i.vouchID} **{rate}** | {i.message}\n'
            # We have to make sure the string total is less than
            # 2048 characters otherwise discord wont send it
            if len(vouches) + prevLength <= 2048:
                prevLength += len(s)
                vouches += s
            else:
                break

        return vouches.strip()
    
    # ==================================================

    def save(self):
        """
            Saves the current user info into the database
        """
        d = {
            'ID': self.userID,
            'Token': self.token,
            'Vouches': [i.toDict() for i in self.vouches],
            'Link': self.link,
            'DWC': self.dwc,
            'DWC Reason': self.dwcReason,
            'Scammer': self.isScammer,
            'Verified': self.verified,
            'Banner' : self.profileBanner,
            'PositiveVouches': len([i for i in self.vouches if i.isPositive]),
            'NegativeVouches': len(self.vouches) - self.posVouchCount,
        }

        for i, x in enumerate(self.users):
            if x['ID'] == self.userID:
                self.users[i] = d
                break
        else:
            self.users.append(d)
        updateJSON({'Users': self.users})    
