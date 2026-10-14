" Deepwick theme for vim-airline. Neovim only: colors come from the Lua palette.
if !has('nvim') || empty(nvim_get_runtime_file('lua/deepwick/palette.lua', v:false))
  echoerr "Deepwick airline theme needs Neovim with the deepwick port on 'runtimepath'"
  finish
endif

let s:c = luaeval('require("deepwick.palette")')

function! s:mode(color, cterm) abort
  let l:a = [s:c.background, a:color, 0, a:cterm, 'bold']
  let l:b = [s:c.foreground, s:c.overlay, 7, 0, '']
  let l:c = [s:c.foreground, s:c.surface, 7, 0, '']
  return airline#themes#generate_color_map(l:a, l:b, l:c)
endfunction

let g:airline#themes#deepwick#palette = {}
let g:airline#themes#deepwick#palette.normal = s:mode(s:c.blue, 4)
let g:airline#themes#deepwick#palette.insert = s:mode(s:c.green, 2)
let g:airline#themes#deepwick#palette.visual = s:mode(s:c.magenta, 5)
let g:airline#themes#deepwick#palette.replace = s:mode(s:c.red, 1)
let g:airline#themes#deepwick#palette.commandline = s:mode(s:c.yellow, 3)

let s:inactive = [s:c.muted, s:c.surface, 8, 0, '']
let g:airline#themes#deepwick#palette.inactive = airline#themes#generate_color_map(s:inactive, s:inactive, s:inactive)

let g:airline#themes#deepwick#palette.normal_modified = {'airline_c': [s:c.yellow, s:c.surface, 3, 0, '']}
let g:airline#themes#deepwick#palette.insert_modified = g:airline#themes#deepwick#palette.normal_modified
let g:airline#themes#deepwick#palette.visual_modified = g:airline#themes#deepwick#palette.normal_modified
let g:airline#themes#deepwick#palette.replace_modified = g:airline#themes#deepwick#palette.normal_modified

let g:airline#themes#deepwick#palette.accents = {'red': [s:c.red, '', 1, '', '']}
