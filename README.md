# epictitles
A SublimeText plugin to make ASCII art titles, because why not

## What it does
EpicTitles turns any selected text into large ASCII art style text. This	is useful for clearly marking different sections of files, and 
works really well when combined with the minimap for quick and easy navigation of large	files. Supports word wrapping, auto wrapping result
in comment block, margin, replace/insert, multiple selections, lots of options, etc.


## How to use
Simply select any piece of text and press 'Ctrl + Alt + T'!

If you wish to change the default key binding, you can override it by making an entry in your user keybindings file. The command to execute 
on your key binding is 'epictitles'.


## Configuration
You can change the default behaviour of EpicTitles by adding your desired settings into your user settings file. EpicTitles supports the 
following settings:

	epictitle_character_spacing
		type: integer
		default: 1
		Number of extra spaces to insert between each character. Note that the font already has one space built in.

	epictitle_line_spacing 
		type: integer
		default: 0	
		Number of blank lines to insert between lines of asciified text. Note the font may already have some spacing as the line height is
		8 characters, and not all characters take up this whole area, some are lower than others and some may be higher.

	epictitle_space_width
		type: integer
		default: 4			
		Width in real spaces of the asciified space character.

	epictitle_tab_width
		type: integer
		default: 2
		How many spaces tabs should be converted to

	epictitle_use_replace
		type: integer
		default: 1
		0 - The result will be inserted into the file after the selection
		1 - The selection will be replaced with the result

	epictitle_use_comments
		type: integer
		default: 1		
		0 - Don't wrap the result in a comment block
		1 - Wrap the result in a comment block

	epictitle_comment_open
		type: string
		default: "/*"		
		Specifies comment opening tag to prepend to the result. Ingored if epictitle_use_comments is 0.

	epictitle_comment_close
		type: string
		default: "*/"
		Specifies comment closing tag to append to the result. Ingored if epictitle_use_comments is 0.

	epictitle_line_width
		type: integer
		default: 155		
		Maximum number of real characters that will be allowed on one line. 155 seems to fit in the minimap nicely.

	epictitle_margin
		type: integer
		default: 0				
		Width in real spaces of the margin to insert before each line of the result.

	epictitle_word_wrap
		type: integer
		default: 1
		Enables word wrapping to epictitle_line_width when set to 1. Setting to 0 will disable word wrapping. Note that disabling this 
		also disables epictitle_split_words

	epictitle_split_words
		type: integer
		default: 1
		Enables splitting of words that are too long to fit on a line, even	by themselves, when set to 1. Disables splitting of words
		when set to 0. Ignored when epictitle_word_wrap is 0, no words will be split.

