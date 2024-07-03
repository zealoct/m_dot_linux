" ======================================================================================
" File         : v.vim
" Author       : jc han
" Last Change  : 11/01/2011 | 19:26:16 PM | Saturday,May
" Description  : hjc's favor color scheme 
" ======================================================================================

" /////////////////////////////////////////////////////////////////////////////
"  prepare 
" /////////////////////////////////////////////////////////////////////////////

" Set 'background' back to the default.  The value can't always be estimated
" and is then guessed.
hi clear Normal
set background=light

" Remove all existing highlighting and set the defaults.
hi clear

" Load the syntax highlighting defaults, if it's enabled.
if exists("syntax_on")
  syntax reset
endif

let colors_name = "v_dark"

" /////////////////////////////////////////////////////////////////////////////
"  Color Define 
" /////////////////////////////////////////////////////////////////////////////

" set font in vimrc instead of here.
" hi Normal       font=Lucida_Console:h9:cANSI

hi SpecialKey   term=bold ctermfg=2 guifg=Blue
hi NonText      term=bold ctermfg=7 gui=bold guifg=Blue
hi Directory    term=bold ctermfg=1 guifg=Blue
hi ErrorMsg     term=standout ctermfg=7 ctermbg=4 guifg=White guibg=Red
hi IncSearch    term=reverse cterm=reverse gui=reverse
hi Search       term=reverse ctermfg=7 ctermbg=3 guifg=NONE guibg=Blue
hi MoreMsg      term=bold ctermfg=2 gui=bold guifg=SeaGreen
hi ModeMsg      term=bold cterm=bold gui=bold
hi LineNr       term=underline ctermfg=3 gui=none guifg=Brown
hi Question     term=standout ctermfg=2 gui=bold guifg=SeaGreen
hi StatusLine   term=bold,none cterm=bold,none ctermfg=6 ctermbg=7 gui=bold,reverse
hi StatusLineNC term=bold,none cterm=none ctermbg=7 gui=reverse
hi VertSplit    term=none cterm=none ctermbg=7 gui=reverse
hi Title        term=bold ctermfg=5 gui=bold guifg=Magenta
hi Visual       term=none cterm=none guibg=LightGray
hi VisualNOS    term=bold,underline cterm=bold,underline gui=bold,underline
hi WarningMsg   term=standout ctermfg=4 guifg=Red
hi WildMenu     term=standout ctermfg=7 ctermbg=14 guifg=6 guibg=Yellow
hi Folded       term=standout ctermfg=1 ctermbg=7 guifg=DarkBlue guibg=LightGrey
hi FoldColumn   term=standout ctermfg=1 ctermbg=7 guifg=DarkBlue guibg=Grey
hi DiffAdd      cterm=none ctermbg=LightGreen gui=none guibg=LightGreen
hi DiffChange   term=bold cterm=none ctermbg=LightCyan gui=none guibg=LightCyan
hi DiffDelete   term=bold cterm=bold ctermfg=Red ctermbg=LightRed gui=bold guifg=Red guibg=LightRed
hi DiffText     term=reverse cterm=underline ctermbg=LightCyan gui=none guibg=Violet
hi SignColumn   term=standout ctermfg=1 ctermbg=7 guifg=DarkBlue guibg=Grey
hi SpellBad     term=reverse ctermbg=12 gui=undercurl guisp=Red
hi SpellCap     term=reverse ctermbg=9 gui=undercurl guisp=Blue
hi SpellRare    term=reverse ctermbg=13 gui=undercurl guisp=Magenta
hi SpellLocal   term=underline ctermbg=11 gui=undercurl guisp=DarkCyan
hi Pmenu        guibg=LightGray
hi PmenuSel     ctermbg=DarkBlue ctermfg=White guibg=DarkBlue guifg=White
hi PmenuSbar    ctermbg=DarkGray guibg=DarkGray
hi PmenuThumb   ctermbg=Black guibg=Black
hi TabLine      term=underline cterm=underline ctermfg=0 ctermbg=7 gui=underline guibg=LightGrey
hi TabLineSel   term=bold cterm=bold gui=bold
hi TabLineFill  term=reverse cterm=reverse gui=reverse
hi CursorColumn term=reverse cterm=none ctermbg=LightCyan gui=none guibg=#bfffff
hi CursorLine   term=reverse cterm=none ctermfg=7 ctermbg=1 gui=none guibg=#bfffff 
hi Cursor       guifg=bg guibg=fg
hi lCursor      guifg=bg guibg=fg
hi MatchParen   term=reverse ctermbg=6 guibg=Cyan
hi Comment      term=bold cterm=bold ctermfg=0 guifg=Orange
hi Constant     term=underline cterm=bold ctermfg=1
hi Special      term=bold cterm=bold ctermfg=0 guifg=SlateBlue
hi Identifier   term=underline ctermfg=3 guifg=DarkCyan
hi Statement    term=bold ctermfg=3 guifg=Blue
hi PreProc      term=underline ctermfg=5 guifg=Purple
hi Type         term=underline cterm=bold ctermfg=1 guifg=Blue
hi Underlined   term=underline cterm=underline ctermfg=11 gui=underline guifg=SlateBlue
hi Ignore       ctermfg=15 guifg=bg
hi Error        term=reverse ctermfg=15 ctermbg=12 guifg=White guibg=Red
hi Todo         cterm=bold ctermfg=4 ctermbg=0 guifg=Blue guibg=Yellow

" vim: sw=2
