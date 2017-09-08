'''
                                      ########                     ########                                  
                                      ##        #####   #   ####      ##     #  #####  #       ######        
                                      ##        #    #  #  #    #     ##     #    #    #       #             
                                      ######    #    #  #  #          ##     #    #    #       #####         
                                      ##        #####   #  #          ##     #    #    #       #             
                                      ##        #       #  #    #     ##     #    #    #       #             
                                      ########  #       #   ####      ##     #    #    ######  ######        
                                                                                                             
   ######                                                    ########                               ########                                      
  ##    ##  #    #  #####   #       #  #    #  ######           ##     ######  #    #  #####        ##     ##  #       #    #   ####   #  #    #  
  ##        #    #  #    #  #       #  ##  ##  #                ##     #        #  #     #          ##     ##  #       #    #  #    #  #  ##   #  
   ######   #    #  #####   #       #  # ## #  #####            ##     #####     ##      #          ########   #       #    #  #       #  # #  #  
        ##  #    #  #    #  #       #  #    #  #                ##     #         ##      #          ##         #       #    #  #  ###  #  #  # #  
  ##    ##  #    #  #    #  #       #  #    #  #                ##     #        #  #     #          ##         #       #    #  #    #  #  #   ##  
   ######    ####   #####   ######  #  #    #  ######           ##     ######  #    #    #          ##         ######   ####    ####   #  #    #

Version: 1 20/3/2012

Copyright (c) 2013, Silas Normanton (silas.normanton@gmail.com)
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

import sublime, sublime_plugin

# implements the 'epictitle' command
class epictitleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        # if the user has set any of our settings, load them in
        self.loadConfig()

        lineEnding = '\n'

        # interate over each selected region of the view, skipping empty ones
        for s in self.view.sel():
            if s.empty():
                continue
            else:
                asciified = self.asciifyString(self.view.substr(s))     # asciify the selected text
                output = ''    # clear output buffer

                # if comment wrapping is enabled, add the opening comment
                if self.useComments == 1:
                    output += (self.openingComment + lineEnding)

                # append all the lines, row by row to the output buffer
                linesOutput = ''
                fullMargin = (self.margin * ' ')
                for line in asciified:
                    for row in line:
                        linesOutput += (fullMargin + row + lineEnding)

                # strip trailing whitespace from the output
                output += linesOutput.rstrip()

                # if comment wrapping is enabled, add the closing comment
                if self.useComments == 1:
                    output += (lineEnding + self.closingComment)

                # put the asciified text into the view, either using replace or insert
                if self.useReplace == 1:
                    self.view.replace(edit, s, output)
                else:
                    self.view.insert(edit, s.end(), (lineEnding + output))

    def loadConfig(self):
        # load any user config settings, or use defaults
        settings = self.view.settings()
        self.fontCharSpacing = settings.get('epictitle_character_spacing', 1)
        self.fontLineSpacing = settings.get('epictitle_line_spacing', 0)
        self.fontSpaceWidth = settings.get('epictitle_space_width', 4)
        self.useReplace = settings.get('epictitle_use_replace', 1)
        self.useComments = settings.get('epictitle_use_comments', 1)
        self.openingComment = settings.get('epictitle_comment_open', '/*')
        self.closingComment = settings.get('epictitle_comment_close', '*/')
        self.lineWidth = settings.get('epictitle_line_width', 155)
        self.margin = settings.get('epictitle_margin', 2)
        self.wordwrap = settings.get('epictitle_word_wrap', 1)
        self.splitwords = settings.get('epictitle_split_words', 1)
        self.tabWidth = settings.get('epictitle_tab_width', 2)

        self.lineHeight = self.getLineHeight() + self.fontLineSpacing  # grab the line height from the font, plus lineSpacing
        self.spaceWidth = self.getCharWidth(' ')                       # grab the width of the space character from the font

    def getCharWidth(self, pChar):
        widthMax = 0
        charIdx = ord(pChar)        # grab the index into the font array this char resides at

        # make sure the font has this character
        if len(self.font) <= charIdx:
            return 0

        # scan each line in the char to find the longest
        for l in self.font[charIdx]:
            lineLen = len(l)
            if lineLen > widthMax:
                widthMax = lineLen

        return widthMax

    def getCharHeight(self, pChar):
        charHeight = 0
        charIdx = ord(pChar)        # grab the index into the font array this char resides at

        # make sure the font has this character
        if len(self.font) <= charIdx:
            return 0

        # count the number of lines this char has
        for l in self.font[charIdx]:
            charHeight += 1

        return charHeight

    def getLineHeight(self):
        heightMax = 0

        # compare the heights of each character in the font, finding the height of the highest one
        for i, c in enumerate(self.font):
            charHeight = self.getCharHeight(chr(i))   # grab the height of this char

            # if this char is higher than the current highest, store its height
            if charHeight > heightMax:
                heightMax = charHeight

        return heightMax

    def getWordWidth(self, pWord):
        wordWidth = 0

        # add up the widths of each character in the word
        for c in pWord:
            wordWidth += self.getCharWidth(c) + self.fontCharSpacing

        return wordWidth

    def newLine(self):
        self.curLine = []
        self.curLineWidth = 0 

        # initialise each of the lines to a blank string
        for i in range(0, self.lineHeight):
            self.curLine.append('')

    def asciifyWord(self, pWord):
        wordWidth = self.getWordWidth(pWord)     # grab the width of the whole word, including spacing (not a trailing space)

        # if there is already something on the line
        if self.curLineWidth > 0:
            # if this word is too long to fit on the current line, or a space won't even fit on the line, word wrap and start a new line, otherwise insert a space
            if self.wordwrap == 1 and ((self.curLineWidth + self.fontSpaceWidth) >= self.lineWidth or (self.curLineWidth + wordWidth + self.fontSpaceWidth) >= self.lineWidth):
                self.lines.append(self.curLine)
                self.newLine()
            #else:
            #    for i,l in enumerate(self.curLine):
            #        self.curLine[i] += (self.fontSpaceWidth * ' ')

        # iterate over each character of the current word, appending it to the current line
        for c in pWord:
            charIdx = ord(c)                 # grab the index into the font array this char resides at
            charWidth = self.getCharWidth(c) # grab the width of the character from the font

            # if the font doesn't have this character, skip it
            if charWidth == 0:
                continue

            # if this word is too long for one line and needs to be split, start a new line, making sure to take into account line spacing
            if self.wordwrap == 1 and self.splitwords == 1 and (self.curLineWidth + charWidth + self.fontCharSpacing) >= self.lineWidth:
                self.lines.append(self.curLine)
                self.newLine()

            # append this char to the current line, spacing it where necessary
            for i in range(0, self.lineHeight):
                charHeight = self.getCharHeight(c)   # grab the height of this char from the font

                # append this char to the line, but if this char doesn't have a line for this i, insert a blank line, make sure to take into account spacing
                if i >= charHeight:
                    self.curLine[i] += ((charWidth + self.fontCharSpacing) * ' ')
                else:
                    self.curLine[i] += (self.font[charIdx][i] + ((self.fontCharSpacing + (charWidth - len(self.font[charIdx][i]))) * ' '))

            # increase the current lines width counter by the width of this char plus spacing
            self.curLineWidth += (charWidth + self.fontCharSpacing)

    def asciifyString(self, pString):
        # initialise the first line
        self.lines = []
        self.newLine()
        word = ''

        # preprocess tabs into spaces
        processedStr = ''
        for c in pString:
            if ord(c) == 9:
                processedStr += (self.tabWidth * ' ')
            else:
                processedStr += c

        # split the string into words, then iterate over each one
        for c in processedStr:
            charIdx = ord(c)     # grab the ascii code of the character

            if charIdx == 10:    # newline
                if len(word) > 0:
                    self.asciifyWord(word)
                    word = ''    # clear the word
                self.lines.append(self.curLine)
                self.newLine()
            elif charIdx == 13:  # carriage return
                continue;
            elif charIdx == 32:  # space
                self.asciifyWord(word + c)
                word = ''    # clear the word
            elif charIdx > 32 and charIdx < 128:      # normal ascii character
                word += c

        # append the last word to the lines list, taking into account line spacing
        self.asciifyWord(word)
        self.lines.append(self.curLine)

        return self.lines

    # working vars
    curLine = ''
    curLineWidth = 0
    lines = []

    # config vars
    lineWidth = 155        # number of chars that seem to be visible in the minimap, wrap once the longest string in the current line is >= lineWidth
    useReplace = 1         # replace the selections or insert asciified text after selections, 1 = replace, 0 = insert
    useComments = 1        # wrap the asciified text in a comment block, 1 = yes, 0 = no
    openingComment = '/*'  # the start comment syntax for your language
    closingComment = '*/'  # th end comment syntax for your language
    margin = 0             # number of real spaces to insert before each line
    wordwrap = 1           # enable/disable word wrapping to line width
    splitwords = 1         # enable/disable splitting words that are too long to fit on one line over multiple lines
    tabWidth = 2           # number of spaces to replace tabs with

    # font definition follows
    fontCharSpacing = 1    # number of spaces to add between characters, some space may already be included in the font characters themselves
    fontLineSpacing = 0    # number of blank lines to insert between rows of text, some space may already be included in the font characters themselves
    fontSpaceWidth = 4     # number of real spaces an asciified space should be
    font = [
        [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], [''], 
        [
            '     ',
            '     ',
            '     ',
            '     ',
            '     ',
            '     ',
            '     ',
            '     ',
        ],
        [
            '### ',
            '### ',
            '### ',
            ' #  ',
            '    ',
            '### ',
            '### ',
            '    ',
        ],
        [
            '### ### ',
            '### ### ',
            ' #   #  ',
            '        ',
            '        ',
            '        ',
            '        ',
            '        ',
        ],
        [
            '  # #   ',
            '  # #   ',
            '####### ',
            '  # #   ',
            '####### ',
            '  # #   ',
            '  # #   ',
            '        ',
        ],
        [
            ' #####  ',
            '#  #  # ',
            '#  #    ',
            ' #####  ',
            '   #  # ',
            '#  #  # ',
            ' #####  ',
            '        ',
            
        ],
        [
            '###   # ',
            '# #  #  ',
            '### #   ',
            '   #    ',
            '  # ### ',
            ' #  # # ',
            '#   ### ',
            '        ',
        ],
        [ 
            '  ##    ',
            ' #  #   ',
            '  ##    ',
            ' ###    ',
            '#   # # ',
            '#    #  ',
            ' ###  # ',
            '        ',
        ],
        [ 
            '### ',
            '### ',
            ' #  ',
            '#   ',
            '    ',
            '    ',
            '    ',
            '    ',
        ],
        [ 
            '  ## ',
            ' #   ',
            '#    ',
            '#    ',
            '#    ',
            ' #   ',
            '  ## ',
            '     ',
        ],
        [ 
            '##   ',
            '  #  ',
            '   # ',
            '   # ',
            '   # ',
            '  #  ',
            '##   ',
            '     ',
        ],
        [  
            '        ',
            ' #   #  ',
            '  # #   ',
            '####### ',
            '  # #   ',
            ' #   #  ',
            '        ',
            '        ',
        ],
        [ 
            '      ',
            '  #   ',
            '  #   ',
            '##### ',
            '  #   ',
            '  #   ',
            '      ',
            '      ',
        ],
        [ 
            '    ',
            '    ',
            '    ',
            '    ',
            '### ',
            '### ',
            ' #  ',
            '#   ',
        ],
        [ 
            '      ',
            '      ',
            '      ',
            '##### ',
            '      ',
            '      ',
            '      ',
            '      ',
        ],
        [ 
            '    ',
            '    ',
            '    ',
            '    ',
            '### ',
            '### ',
            '### ',
            '    ',
        ],
        [ 
            '      # ',
            '     #  ',
            '    #   ',
            '   #    ',
            '  #     ',
            ' #      ',
            '#       ',
            '        ',
        ],
        [ 
            '  ###   ',
            ' #   #  ',
            '#     # ',
            '#     # ',
            '#     # ',
            ' #   #  ',
            '  ###   ',
            '        ',
        ],
        [ 
            '  #   ',
            ' ##   ',
            '# #   ',
            '  #   ',
            '  #   ',
            '  #   ',
            '##### ',
            '      ',
        ],
        [ 
            ' #####  ',
            '#     # ',
            '      # ',
            ' #####  ',
            '#       ',
            '#       ',
            '####### ',
            '        ',
        ],
        [ 
            ' #####  ',
            '#     # ',
            '      # ',
            ' #####  ',
            '      # ',
            '#     # ',
            ' #####  ',
            '        ',
        ],
        [ 
            '#       ',
            '#    #  ',
            '#    #  ',
            '#    #  ',
            '####### ',
            '     #  ',
            '     #  ',
            '        ',
        ],
        [ 
            '####### ',
            '#       ',
            '#       ',
            '######  ',
            '      # ',
            '#     # ',
            ' #####  ',
            '        ',
        ],
        [ 
            ' #####  ',
            '#     # ',
            '#       ',
            '######  ',
            '#     # ',
            '#     # ',
            ' #####  ',
            '        ',
        ],
        [ 
            '####### ',
            '#    #  ',
            '    #   ',
            '   #    ',
            '  #     ',
            '  #     ',
            '  #     ',
            '        ',
        ],
        [ 
            ' #####  ',
            '#     # ',
            '#     # ',
            ' #####  ',
            '#     # ',
            '#     # ',
            ' #####  ',
            '        ',
        ],
        [  
            ' #####  ',
            '#     # ',
            '#     # ',
            ' ###### ',
            '      # ',
            '#     # ',
            ' #####  ',
            '        ',
        ],
        [  
            ' #  ',
            '### ',
            ' #  ',
            '    ',
            ' #  ',
            '### ',
            ' #  ',
            '    ',
        ],
        [  
            '    ',
            '### ',
            '### ',
            '    ',
            '### ',
            '### ',
            ' #  ',
            '#   ',
        ],
        [  
            '   # ',
            '  #  ',
            ' #   ',
            '#    ',
            ' #   ',
            '  #  ',
            '   # ',
            '     ',
        ],
        [  
            '      ',
            '      ',
            '##### ',
            '      ',
            '##### ',
            '      ',
            '      ',
            '      ',
        ],
        [  
            '#    ',
            ' #   ',
            '  #  ',
            '   # ',
            '  #  ',
            ' #   ',
            '#    ',
            '     ',
        ],
        [  
            ' #####  ',
            '#     # ',
            '      # ',
            '   ###  ',
            '   #    ',
            '        ',
            '   #    ',
            '        ',
        ],
        [ 
            ' #####  ',
            '#     # ',
            '# ### # ',
            '# ### # ',
            '# ####  ',
            '#       ',
            ' #####  ',
            '        ',
        ],
        [
            '   ###    ',  
            '  ## ##   ',  
            ' ##   ##  ',  
            '##     ## ',  
            '######### ',  
            '##     ## ',  
            '##     ## ', 
        ],
        [
            '########  ',  
            '##     ## ',  
            '##     ## ',  
            '########  ',  
            '##     ## ',  
            '##     ## ',  
            '########  ', 
        ],
        [
            ' ######  ',   
            '##    ## ',   
            '##       ',   
            '##       ',   
            '##       ',   
            '##    ## ',   
            ' ######  ',
        ],
        [
            '########  ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '########  ',
        ],
        [
            '######## ',   
            '##       ',   
            '##       ',   
            '######   ',   
            '##       ',   
            '##       ',   
            '######## ', 
        ],
        [
            '######## ',   
            '##       ',   
            '##       ',   
            '######   ',   
            '##       ',   
            '##       ',   
            '##       ', 
        ],
        [
            ' ######   ',  
            '##    ##  ',  
            '##        ',  
            '##   #### ',  
            '##    ##  ',  
            '##    ##  ',  
            ' ######   ', 
        ],
        [
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '######### ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ', 
        ],
        [
            '#### ',       
            ' ##  ',       
            ' ##  ',       
            ' ##  ',       
            ' ##  ',       
            ' ##  ',       
            '#### ',     
        ],
        [
            '      ## ',   
            '      ## ',   
            '      ## ',   
            '      ## ',   
            '##    ## ',   
            '##    ## ',   
            ' ######  ',
        ],
        [
            '##    ## ',   
            '##   ##  ',   
            '##  ##   ',   
            '#####    ',   
            '##  ##   ',   
            '##   ##  ',   
            '##    ## ', 
        ],
        [
            '##       ',         
            '##       ',  
            '##       ',  
            '##       ', 
            '##       ',
            '##       ',   
            '######## ', 
        ],
        [
            '##     ## ',  
            '###   ### ',  
            '#### #### ',  
            '## ### ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ', 
        ],
        [
            '##    ## ',   
            '###   ## ',   
            '####  ## ',   
            '## ## ## ',   
            '##  #### ',   
            '##   ### ',   
            '##    ## ', 
        ],
        [
            ' #######  ',   
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            ' #######  ',
        ],
        [
            '########  ',  
            '##     ## ',  
            '##     ## ',  
            '########  ',  
            '##        ',  
            '##        ',  
            '##        ', 
        ],
        [
            ' #######  ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##  ## ## ',  
            '##    ##  ',  
            ' ##### ## ', 
        ],
        [
            '########  ',  
            '##     ## ',  
            '##     ## ',  
            '########  ',  
            '##   ##   ',  
            '##    ##  ',  
            '##     ## ', 
        ],
        [
            ' ######  ',   
            '##    ## ',   
            '##       ',   
            ' ######  ',   
            '      ## ',   
            '##    ## ',   
            ' ######  ', 
        ],
        [
            '######## ',   
            '   ##    ',   
            '   ##    ',   
            '   ##    ',   
            '   ##    ',   
            '   ##    ',   
            '   ##    ', 
        ],
        [
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            ' #######  ',  
        ],
        [
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            '##     ## ',  
            ' ##   ##  ',  
            '  ## ##   ',  
            '   ###    ', 
        ],
        [
            '##      ## ', 
            '##  ##  ## ', 
            '##  ##  ## ', 
            '##  ##  ## ', 
            '##  ##  ## ', 
            '##  ##  ## ', 
            ' ###  ###  ',
        ],
        [
            '##     ## ',  
            ' ##   ##  ',  
            '  ## ##   ',  
            '   ###    ',  
            '  ## ##   ',  
            ' ##   ##  ',  
            '##     ## ',
        ],
        [
            '##    ## ', 
            ' ##  ##  ',  
            '  ####   ',  
            '   ##    ',  
            '   ##    ',  
            '   ##    ',  
            '   ##    ',
        ],
        [
            '######## ',   
            '     ##  ',   
            '    ##   ',   
            '   ##    ',   
            '  ##     ',   
            ' ##      ',   
            '######## ', 
        ],
        [
            '##### ',
            '#     ',
            '#     ',
            '#     ',
            '#     ',
            '#     ',
            '##### ',
            '      ',
        ],
        [
            '#       ',
            ' #      ',
            '  #     ',
            '   #    ',
            '    #   ',
            '     #  ',
            '      # ',
            '        ',
        ],
        [
            '##### ',
            '    # ',
            '    # ',
            '    # ',
            '    # ',
            '    # ',
            '##### ',
            '      ',
        ],
        [
            '  #   ',
            ' # #  ',
            '#   # ',
            '      ',
            '      ',
            '      ',
            '      ',
            '      ',
        ],
        [
            '        ',
            '        ',
            '        ',
            '        ',
            '        ',
            '        ',
            '####### ',
            '        ',
        ],
        [
            '### ',
            '### ',
            ' #  ',
            '  # ',
            '    ',
            '    ',
            '    ',
            '    ',
        ],
        [
            '       ',
            '  ##   ',
            ' #  #  ',
            '#    # ',
            '###### ',
            '#    # ',
            '#    # ',
            '       ',
        ],
        [
            '       ',
            '#####  ',
            '#    # ',
            '#####  ',
            '#    # ',
            '#    # ',
            '#####  ',
            '       ',
        ],
        [
            '       ',
            ' ####  ',
            '#    # ',
            '#      ',
            '#      ',
            '#    # ',
            ' ####  ',
            '       ',
        ],
        [
            '       ',
            '#####  ',
            '#    # ',
            '#    # ',
            '#    # ',
            '#    # ',
            '#####  ',
            '       ',
        ],
        [
            '       ',
            '###### ',
            '#      ',
            '#####  ',
            '#      ',
            '#      ',
            '###### ',
            '       ',
        ],
        [
            '       ',
            '###### ',
            '#      ',
            '#####  ',
            '#      ',
            '#      ',
            '#      ',
            '       ',
        ],
        [
            '       ',
            ' ####  ',
            '#    # ',
            '#      ',
            '#  ### ',
            '#    # ',
            ' ####  ',
            '       ',
        ],
        [
            '       ',
            '#    # ',
            '#    # ',
            '###### ',
            '#    # ',
            '#    # ',
            '#    # ',
            '       ',
        ],
        [
            '  ',
            '# ',
            '# ',
            '# ',
            '# ',
            '# ',
            '# ',
            '  ',
        ],
        [
            '       ',
            '     # ',
            '     # ',
            '     # ',
            '     # ',
            '#    # ',
            ' ####  ',
            '       ',
        ],
        [
            '       ',
            '#    # ',
            '#   #  ',
            '####   ',
            '#  #   ',
            '#   #  ',
            '#    # ',
            '       ',
        ],
        [
            '       ',
            '#      ',
            '#      ',
            '#      ',
            '#      ',
            '#      ',
            '###### ',
            '       ',
        ],
        [
            '       ',
            '#    # ',
            '##  ## ',
            '# ## # ',
            '#    # ',
            '#    # ',
            '#    # ',
            '       ',
        ],
        [
            '       ',
            '#    # ',
            '##   # ',
            '# #  # ',
            '#  # # ',
            '#   ## ',
            '#    # ',
            '       ',
        ],
        [
            '       ',
            ' ####  ',
            '#    # ',
            '#    # ',
            '#    # ',
            '#    # ',
            ' ####  ',
            '       ',
        ],
        [
            '       ',
            '#####  ',
            '#    # ',
            '#    # ',
            '#####  ',
            '#      ',
            '#      ',
            '       ',
        ],
        [
            '       ',
            ' ####  ',
            '#    # ',
            '#    # ',
            '#  # # ',
            '#   #  ',
            ' ### # ',
            '       ',
        ],
        [
            '       ',
            '#####  ',
            '#    # ',
            '#    # ',
            '#####  ',
            '#   #  ',
            '#    # ',
            '       ',
        ],
        [
            '       ',
            ' ####  ',
            '#      ',
            ' ####  ',
            '     # ',
            '#    # ',
            ' ####  ',
            '       ',
        ],
        [
            '      ',
            '##### ',
            '  #   ',
            '  #   ',
            '  #   ',
            '  #   ',
            '  #   ',
            '      ',
        ],
        [
            '       ',
            '#    # ',
            '#    # ',
            '#    # ',
            '#    # ',
            '#    # ',
            ' ####  ',
            '       ',
        ],
        [
            '       ',
            '#    # ',
            '#    # ',
            '#    # ',
            '#    # ',
            ' #  #  ',
            '  ##   ',
            '       ',
        ],
        [
            '       ',
            '#    # ',
            '#    # ',
            '#    # ',
            '# ## # ',
            '##  ## ',
            '#    # ',
            '       ',
        ],
        [
            '       ',
            '#    # ',
            ' #  #  ',
            '  ##   ',
            '  ##   ',
            ' #  #  ',
            '#    # ',
            '       ',
        ],
        [
            '      ',
            '#   # ',
            ' # #  ',
            '  #   ',
            '  #   ',
            '  #   ',
            '  #   ',
            '      ',
        ],
        [
            '       ',
            '###### ',
            '    #  ',
            '   #   ',
            '  #    ',
            ' #     ',
            '###### ',
            '       ',
        ],
        [
            '##### ', 
            '#     ', 
            '#     ', 
            '#     ', 
            '#     ', 
            '#     ', 
            '##### ', 
            '      ', 
        ],
        [
            '# ', 
            '# ', 
            '# ', 
            '  ', 
            '# ', 
            '# ', 
            '# ', 
            '  ', 
        ],
        [
            '##### ', 
            '    # ', 
            '    # ', 
            '    # ', 
            '    # ', 
            '    # ', 
            '##### ', 
            '      ', 
        ],
        [
            ' ##     ', 
            '#  #  # ', 
            '    ##  ', 
            '        ', 
            '        ', 
            '        ', 
            '        ', 
            '        ', 
        ],
        [[]]
    ]