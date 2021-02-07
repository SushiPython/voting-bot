import pymongo
import discord
from discord.ext import menus, commands
from RandomWordGenerator import RandomWord

bot = commands.Bot(command_prefix='v.')

client = pymongo.MongoClient()


db = client.test
db = client.voting.votes
cands = client.voting.candidates

admins = [614577566228938817, 428560505683050496, 294470646425976843]

bot.remove_command('help')


@bot.command()
async def reset(ctx):
    a = db.count_documents({'id':ctx.author.id})
    if a > 0:
        b = db.find_one({'id':ctx.author.id,'verified': 1})
        db.delete_one({'id': ctx.author.id})
        await ctx.send('> Vote for ' + b['mayor'] + ' has been removed!', delete_after=5.0)
    else:
        await ctx.send("> It doesn't look like you've voted. Do `v.vote [mayor]` to start!", delete_after=5.0)

@bot.command()
async def vote(ctx, mayor):
    await ctx.message.delete()
    print(str(ctx.author.id) + " voted for " + mayor)
    mayorsList = []
    c = cands.find({})
    for d in c:
        mayorsList.append(d['mayor'])
    if mayor not in mayorsList:
        await ctx.send('> That is not a valid candidate.', delete_after=5.0)
    else:
        a = db.count_documents({'id':ctx.author.id,'verified': 1})
        if a > 0:
            b = db.find_one({'id':ctx.author.id,'verified': 1})
            await ctx.send('> You have already voted for ' + b['mayor'] + '. If you would like to change your vote, please run `v.reset`.', delete_after=5.0)
        else:
            rw = RandomWord(max_word_size=5)
            code = rw.generate()
            db.insert_one({
                "mayor": mayor,
                "id": ctx.author.id,
                "verified": 0,
                "code": code,
                "name": ctx.author.name
            })
            await ctx.send(f'> Thanks, {ctx.author.name}. You are almost done. This vote is not yet confirmed until you type `v.confirm {code}`')

@bot.command()
async def confirm(ctx, code):
    await ctx.message.delete()
    a = db.count_documents({'id':ctx.author.id})
    if a > 0:
        b = db.find_one({'id':ctx.author.id})
        if b['verified'] == 0:
            if b['code'] == code:
                db.update_one({'id': ctx.author.id},{'$set': {'verified': 1}},)
                await ctx.send('> Your vote was confirmed! Thanks!', delete_after=5.0)
            else:
                await ctx.send('> Incorrect code. If you lost it, contact `Sushi#5027`.', delete_after=5.0)
        else:
            await ctx.send('> Your vote is already confirmed!', delete_after=5.0)
    else:
        await ctx.send('> You have not voted!', delete_after=5.0)
    
@bot.command()
async def clear(ctx):
    if ctx.author.id in admins:
        db.delete_many({})
        await ctx.send('> Ok, deleted all votes.')
    else:
        await ctx.send('> You are lacking perms or did it wrong.')

@bot.command()
async def candidates(ctx):
    embed=discord.Embed(title="Message Voting", description="Say the candidate name in chat, ex [v.vote Bob]", color=0x0d85fd)
    embed.set_author(name="Skyblock Community Mayor Voting")
    mayorsCount = 0
    for mayor in cands.find({}):
        mayorsCount += 1
        embed.add_field(name="Candidate #"+str(mayorsCount), value=mayor['mayor'], inline=False)
    return await ctx.send(embed=embed)

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="Reaction Voting", description="Get help for the bot", color=0x0d85fd)
    embed.add_field(name="v.vote [mayor]", value="Vote for a candidate", inline=False)
    embed.add_field(name="v.reset", value="Reset your vote", inline=False)
    embed.add_field(name="v.candidates", value="View all the candidates", inline=False)
    embed.add_field(name="v.debug admins", value="[Admin] View the admins", inline=False)
    embed.add_field(name="v.setmayors [a,b,c]", value="[Admin] Set the candidates", inline=False)
    embed.add_field(name="v.clear", value="[Admin] Clear all votes", inline=False)
    embed.add_field(name="v.results", value="[Admin] Get DMd current standings", inline=False)
    embed.add_field(name="v.individual", value="[Admin] Get DMd individual votes", inline=False)
    return await ctx.send(embed=embed)

@bot.command()
async def setmayors(ctx, arg):
    print(arg)
    author = ctx.author.id
    a = arg.split(',')
    if ctx.author.id in admins:
        cands.delete_many({})
        for b in a:
            cands.insert_one({'mayor': b, 'creator': author})
        await ctx.send('> Ok, added.')
    else:
        await ctx.send('> You are lacking perms or did it wrong.')

@bot.command()
async def individual(ctx):
    await ctx.message.delete()
    if ctx.author.id in admins:
        a = db.find({'verified':1})
        votes = []
        for b in a:
            votes.append(b)
        d = ''
        e = 0
        for c in votes:
            e += 1
            d += f'> Vote #{e}\nMayor: {c["mayor"]}\nVoter: {c["name"]}\n\n'
        await ctx.author.send(d)
    else:
        await ctx.send('> You are lacking perms or did it wrong.')

@bot.command()
async def results(ctx):
    await ctx.message.delete()
    if ctx.author.id in admins:
        mayorList = []
        for m in cands.find({}):
            mayorList.append(m['mayor'])
        data = {}
        for mayor in mayorList:
            data[mayor] = {'votes': 0}
        votes = []
        for c in db.find({'verified':1}):
            votes.append(c)
        for a in votes:
            m = a['mayor']
            data[m]['votes'] = data[m]['votes'] + 1
        outputMessage = dict(sorted(data.items(), key = lambda t : t[1]['votes'], reverse=True))
        out = ''
        for b in outputMessage:
            out += f'> {b}: {outputMessage[b]["votes"]} vote(s)\n'
        await ctx.author.send(out)
    else:
        await ctx.send('> You are lacking perms or did it wrong.', delete_after=5.0)

@bot.command()
async def debug(ctx, arg):
    if arg == 'admins':
        await ctx.send(admins)

bot.run()
