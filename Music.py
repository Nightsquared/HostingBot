import lyricsgenius as lg
genius = lg.Genius('f73ErIT7085pKZu-KZ8BYiJtcG7D_uKsv9SrU-0nlyhIrE52tjSPtdtW_DIrteo2')
genius.verbose = False # Turn off status messages
genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
import random

difficulty = .5
linelength = .5

async def MusicRespond(messagearray, message):
    global difficulty, linelength, genius
    def create_line_puzzle(lyrics):
        sl = lyrics.split('\n')
        sorted_list = sorted(sl, key=len)
        options = sorted_list[-int(len(sorted_list)*linelength):]#choose from the longest 35% of lines
        line = random.choice(options)
        sline = line.split()
        eject = random.sample([i for i in range(len(sline))], int(len(sline)*difficulty))
        ns = '`'
        for i in range(len(sline)):
            #print(i)
            if i in eject:
                ns += '---- '
            else:
                ns += sline[i] + ' '
        ns = ns[:-1]
        ns += '`'
        return ns
    
    if messagearray[1].lower() == 'difficulty':
        try:
            difficulty = float(messagearray[2])
        except:
            pass
    
    if messagearray[1].lower() == 'phraselength':
        try:
            linelength = float(messagearray[2])
        except:
            pass
          
    if messagearray[1].lower() == 'trivia':
        lyrics = ''
        if messagearray[2].lower() == 'artist':
            try:
                songnum = int(messagearray[3])
                s = ''
                for i in messagearray[4:]:
                    s += i + ' '
                s = s[:-1]
            except:
                songnum = random.randint(1, 20)
                s = ''
                for i in messagearray[3:]:
                    s += i + ' '
                s = s[:-1]
            try:
                artist_id = genius.find_artist_id(s)#this function doesn't exist on it's own, so you need to modify the genius class to have this as its own function. You can find the function in search_song
                song = genius.artist_songs(artist_id, sort='popularity', per_page = 1, page = songnum)
                if song == None:
                    await message.channel.send('Couldn\'t find the song. Try entering a lower number (less than 20 if no number was entered)')
                print(song['songs'][0]['title'])    
                fullsong = genius.search_song(song['songs'][0]['title'], song_id = song['songs'][0]['id'])
                #print(fullsong)
                lyrics = fullsong.lyrics
                if lyrics == None:
                    await message.channel.send('The song didn\'t have any lyrics.')
                    return
            except:
                await message.channel.send('Something went wrong.')
                return
        if messagearray[2].lower() == 'song':
            title = messagearray[3]
            try:
                artist = messagearray[4]
            except:
                artist = None
            try:  
                if artist == None:
                    fullsong = genius.search_song(title)
                else:
                    fullsong = genius.search_song(title = title, artist = artist)
                if fullsong == None:
                    await message.channel.send('Couldn\'t find the song.')
                    return
                lyrics = fullsong.lyrics
                if lyrics == None:
                    await message.channel.send('The song didn\'t have any lyrics.')
                    return
            except:
                await message.channel.send('Something went wrong.')
                return
        await message.channel.send(create_line_puzzle(lyrics))
        return