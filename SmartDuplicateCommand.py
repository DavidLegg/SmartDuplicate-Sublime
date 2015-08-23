##
## Author:  David Legg
## Original Author:  Mathias Paumgarten
## Version: 1.2
## Date:    08/23/2015
## 
## Makes a series of simple substitutions when duplicating lines.
## 
## TODO: Allow for the value in the replacements dictionary to take 
## expressions and groups from the matching key.
## 
## v1.2 changes:
## Slight tweak to allow for the use of regexes for keys.
## 
## v1.1 changes:
## Replaced the hard-coded values for softReplace with a dictionary,
## which allows for easier extensibility.
## 


import sublime, sublime_plugin, re

class SmartDuplicateCommand( sublime_plugin.TextCommand ):

    ## Change by David Legg: added dictionary of replacements for easy extensibility.
    ## Note that regular expressions can be used as keys here.
    softReplacements = {
        # The original set of expressions.
        "height"      : "width",
        "width"       : "height",
        "left"        : "right",
        "right"       : "left",
        "top"         : "bottom",
        "bottom"      : "top",

        # Numbers, spelled out, with a few negative lookaheads
        # that prevent matching against ordinals
        "one"         : "two",
        "two"         : "three",
        "three"       : "four",
        "four(?!th)"  : "five",
        "five"        : "six",
        "six(?!th)"   : "seven",
        "seven(?!th)" : "eight",
        "eight(?!h)"  : "nine",
        "nine"        : "ten",

        # Ordinal numbers
        "first"       : "second",
        "second"      : "third",
        "third"       : "fourth",
        "fourth"      : "fifth",
        "fifth"       : "sixth",
        "sixth"       : "seventh",
        "seventh"     : "eighth",
        "eighth"      : "ninth",
        "ninth"       : "tenth"
    }

    def run( self, edit ):
        for region in self.view.sel():

            if region.empty():

                line = self.view.line( region )
                line_contents = self.scan( '\n' + self.view.substr( line ) )

                self.view.insert( edit, line.end(), line_contents )

            else:
                self.view.insert( edit, region.begin(), self.view.substr( region ) )

    def scan( self, string ):

        def hardReplace( match ):
            if ( match.group( 0 ) == ".x" ): return ".y"
            elif ( match.group( 0 ) == ".y" ): return ".x"

        def fillReplace( match ):
            value = match.group( 0 )

            if ( re.match( r"\w+X", value ) ): return value[ 0 : -1 ] + "Y"
            if ( re.match( r"\w+Y", value ) ): return value[ 0 : -1 ] + "X"

        def softReplace( match ):
            value = match.group( 0 )

            if ( value.istitle() ): transform = lambda string: string.title();
            elif ( value.isupper() ): transform = lambda string: string.upper();
            elif ( value.islower() ): transform = lambda string: string.lower();
            else: transform = lambda string: string

            value = value.lower();

            ## Change by David Legg: Replaced if/return block with for loop.
            # if ( value == "height" ): return transform( "width" )
            # elif ( value == "width" ): return transform( "height" )
            # elif ( value == "left" ): return transform( "right" )
            # elif ( value == "right" ): return transform( "left" )
            # elif ( value == "top" ): return transform( "bottom" )
            # elif ( value == "bottom" ): return transform( "top" )

            for key, replacement in self.softReplacements.items():
                ## This works with literal strings as keys, but we can be a little more flexible
                ## at the slight cost of performance (which isn't too important here.)
                # if ( key == value ): return transform( replacement )
                ## This will build exactly the same regex as below, but trying each option singly.
                if ( re.match( r"(?i)" + key, value ) ):
                    return transform( replacement )

        string = re.sub( r"(\.x|\.y)", hardReplace, string )
        ## Change by David Legg: dynamically building expressions from dictionary keys.
        # string = re.sub( r"(?i)(width|height|left|right|top|bottom)", softReplace, string )
        ## Lucky for us, | has the highest precedence, so we don't need to mess around with groups.
        string = re.sub( r"(?i)({0})".format( "|".join(self.softReplacements.keys()) ), softReplace, string )
        string = re.sub( r"(\w+X|\w+Y)", fillReplace, string )

        return string
