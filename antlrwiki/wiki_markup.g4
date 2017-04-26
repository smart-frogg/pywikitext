grammar wiki_markup;

wiki_article
    :   elements_markup? EOF
    ;

elements_markup
    :   (tags
    |   link
    |   template
    |   table
    |   url_or_email
    |   assignment
    |   lists
    |   headers
    |   accentuation
    |   ignore_element
    |   AnyText
    |   CommaSymbol
    |   SemicolonSymbol
    |   AmpersandSymbol
    |   DashSymbol
    |   HyphenSymbol
    |   DotSymbol
    |   ApostropheSymbol
    |   ColonSymbol
    |   QuoteSymbol
    |   ForwardSlashSymbol
    |   ExclamationMarkSymbol
    |   DollarSymbol
    |   QuestionSymbol
    |   PlusSymbol
    |   NumSymbol
    |   PercentSymbol
    |   TableDelimitter
    |   BackSlashSymbol)+
    ;

tags
    :   ref | comment | nowiki | code | syntaxhighlight | pre | math | tt | other_tags
    ;

comment
    :   LessThanSymbol ExclamationMarkSymbol HyphenSymbol HyphenSymbol
            text_comment?
        HyphenSymbol HyphenSymbol GreaterThanSymbol
    ;

text_comment
    :   elements_markup
    ;

nowiki
    :   LessThanSymbol ('nowiki' Whitespace?) (ForwardSlashSymbol)? GreaterThanSymbol
            AnyText?
        (LessThanSymbol ForwardSlashSymbol 'nowiki' GreaterThanSymbol)?
    ;

code
    :   LessThanSymbol 'code' GreaterThanSymbol
            AnyText?
        LessThanSymbol ForwardSlashSymbol 'code' GreaterThanSymbol
    ;

syntaxhighlight
    :   LessThanSymbol 'syntaxhighlight' GreaterThanSymbol
            AnyText?
        LessThanSymbol ForwardSlashSymbol 'syntaxhighlight' GreaterThanSymbol
    ;

pre
    :   LessThanSymbol 'pre' GreaterThanSymbol
            .*?
        LessThanSymbol ForwardSlashSymbol 'pre' GreaterThanSymbol
    ;

math
    :   LessThanSymbol 'math' GreaterThanSymbol
            .*?
        LessThanSymbol ForwardSlashSymbol 'math' GreaterThanSymbol
    ;

tt
    :   LessThanSymbol 'tt' GreaterThanSymbol
            .*?
        LessThanSymbol ForwardSlashSymbol 'tt' GreaterThanSymbol
    ;

ref
    :   '<ref' ref_name ForwardSlashSymbol GreaterThanSymbol
    |   '<ref' ref_name? ForwardSlashSymbol? GreaterThanSymbol
            ref_content?
        LessThanSymbol ForwardSlashSymbol 'ref' GreaterThanSymbol
    ;

ref_name
    :   ('name' | 'name ') '=' (BackSlashSymbol | QuoteSymbol)* (AnyText | BackSlashSymbol | DashSymbol | HyphenSymbol | DotSymbol)* QuoteSymbol?
    ;

ref_content
    :   elements_markup
    ;

other_tags
    :   LessThanSymbol AnyText (ForwardSlashSymbol | assignment)? GreaterThanSymbol
            (content_other_tags*
        LessThanSymbol ForwardSlashSymbol AnyText GreaterThanSymbol)?
    ;

content_other_tags
    :   AnyText | ApostropheSymbol | SemicolonSymbol | DashSymbol | HyphenSymbol | BackSlashSymbol
    | CaretSymbol | LessThanSymbol | GreaterThanSymbol | PlusSymbol | AssignmentSymbol
    | ColonSymbol | CommaSymbol | DotSymbol | link | url_or_email | ignore_element | template | assignment
    ;

template
    :   LeftCurlyBrace LeftCurlyBrace
            template_element? (PipeSimbol template_element?)*
        RightCurlyBrace RightCurlyBrace
    ;

template_element
    :   (AnyText | ApostropheSymbol |CommaSymbol| ColonSymbol| ForwardSlashSymbol | PlusSymbol
        | TableDelimitter | 'ref' | SemicolonSymbol
        | HyphenSymbol | SharpSymbol | QuoteSymbol | DashSymbol | BackSlashSymbol | ExclamationMarkSymbol
        | DotSymbol | TildeSymbol | PercentSymbol| template | assignment | ignore_element | tags | link)+
    ;

ignore_element
    :   OpenParenthesisSymbol ignore_content? CloseParenthesisSymbol
    ;

ignore_content
    :   elements_markup
    ;

table
    :  LeftCurlyBrace PipeSimbol .*? PipeSimbol RightCurlyBrace
    |  '{{{!}}' .*? '{{!}}}'
    ;

link
    :   LeftSquareBracketSymbol LeftSquareBracketSymbol
            link_element? (PipeSimbol link_element?)*
        RightSquareBracketSymbol RightSquareBracketSymbol
    ;

link_element
    :   elements_markup
    ;

url_or_email
    :   LeftSquareBracketSymbol content_url_or_email? RightSquareBracketSymbol
    ;

content_url_or_email
    :   (AnyText | SharpSymbol | QuoteSymbol | ColonSymbol | DotSymbol | NumSymbol
    | ForwardSlashSymbol | '='  | PercentSymbol | ExclamationMarkSymbol  | PlusSymbol
    | AmpersandSymbol | AtEmailSymbol | QuestionSymbol | DashSymbol | SemicolonSymbol
    | HyphenSymbol | ApostropheSymbol | CommaSymbol | accentuation | ignore_element | comment)+
    ;

lists
    :   (list_element)+
    ;

list_element
    :   (StarSymbol | SharpSymbol)+ (tags
                                    |   link
                                    |   template
                                    |   table
                                    |   url_or_email
                                    |   assignment
                                    |   headers
                                    |   accentuation
                                    |   ignore_element
                                    |   AnyText
                                    |   CommaSymbol
                                    |   SemicolonSymbol
                                    |   AmpersandSymbol
                                    |   DashSymbol
                                    |   HyphenSymbol
                                    |   DotSymbol
                                    |   ApostropheSymbol
                                    |   ColonSymbol
                                    |   QuoteSymbol
                                    |   ForwardSlashSymbol
                                    |   ExclamationMarkSymbol
                                    |   DollarSymbol
                                    |   QuestionSymbol
                                    |   NumSymbol
                                    |   Digit+ ')')*
    ;

assignment
    :   '=' (tags | template | link | table | accentuation | NumSymbol | BackSlashSymbol | SharpSymbol
                | AnyText | DotSymbol | DollarSymbol | PercentSymbol | QuestionSymbol | PlusSymbol | CommaSymbol | HyphenSymbol | QuoteSymbol | AmpersandSymbol
                | ApostropheSymbol | ForwardSlashSymbol | DashSymbol | ColonSymbol | SemicolonSymbol | 'ref' | 'name')*
    ;

accentuation
    :   logical_accentuation | structural_accentuation
    ;

logical_accentuation
    :   ApostropheSymbol ApostropheSymbol
            text_accentuation?
        ApostropheSymbol ApostropheSymbol
    ;

structural_accentuation
    :   ApostropheSymbol ApostropheSymbol ApostropheSymbol
            text_accentuation?
        ApostropheSymbol ApostropheSymbol ApostropheSymbol
    ;

text_accentuation
    :   elements_markup
    ;

headers
    :   header1
    |   header2
    |   header3
    |   header4
    |   header5
    |   header6
    ;

contend_header
    :   elements_markup
    ;

header1
    : H1 contend_header? H1
    ;

header2
    : H2 contend_header? H2
    ;

header3
    : H3 contend_header? H3
    ;

header4
    : H4 contend_header? H4
    ;

header5
    : H5 contend_header? H5
    ;

header6
    : H6 contend_header? H6
    ;

AnyText
    :   AnySymbol
        (   AnySymbol | Whitespace
        )*
    ;

fragment
AnySymbol
    :   Digit | KirillicLetter | LatinLetter | UnderscoreSymbol
    ;

H1: AssignmentSymbol;
H2: '==';
H3: '===';
H4: '====';
H5: '=====';
H6: '======';

Digit
    : '0'..'9'
    ;

KirillicLetter
    :   'а'..'я'
    |   'А'..'Я'
    |   'ё'
    |   'Ё'
    ;

LatinLetter
    :   'a'..'z'
    |   'A'..'Z'
    ;

AcuteSymbol: '`';

AmpersandSymbol: '&';

ApostropheSymbol: '\'';

AssignmentSymbol: [=];

AtEmailSymbol: '@';

BackSlashSymbol: '\\';

CaretSymbol: '^';

CloseParenthesisSymbol: ')';

ColonSymbol: ':';

CommaSymbol: ',';

DashSymbol: '—' | '–';

DollarSymbol: '$';

DotSymbol: '.';

ExclamationMarkSymbol: '!';

ForwardSlashSymbol: '/';

GreaterThanSymbol: '>';

HyphenSymbol: '-';

LeftCurlyBrace: '{';

LeftSquareBracketSymbol: '[';

LessThanSymbol: '<';

NumSymbol: '№';

OpenParenthesisSymbol: '(';

PercentSymbol: '%';

PipeSimbol: '|';

PlusSymbol: '+';

QuoteSymbol: '"';

QuestionSymbol: '?';

RightCurlyBrace: '}';

RightSquareBracketSymbol: ']';

SemicolonSymbol: ';';

SharpSymbol: '#';

StarSymbol: '*';

TildeSymbol: '~';

UnderscoreSymbol: '_';

TableDelimitter
    :   '{{!}}'
    ;

Whitespace
    :   [ \t] -> skip
    ;
