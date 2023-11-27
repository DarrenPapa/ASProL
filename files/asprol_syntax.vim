" asprol.vim

syntax enable
setlocal iskeyword+=_-

" Define ASProL keywords
syntax keyword asprolKeyword add inc dec sub mul div fdiv set setr igt ilt ieq ine jiz jnz jmp
syntax keyword asprolKeyword sizeof_str new_string put_string str-eq str-ne into_int str-copy
syntax keyword asprolKeyword new_vector append_vector pop_vector subroutine return gosub
syntax keyword asprolKeyword put put_value ipt load_mem save_mem register_mode memory_mode
syntax keyword asprolKeyword pointer allocate malloc auto_malloc free_malloc free forget
syntax keyword asprolKeyword purge_memory purge_all hlt

" Highlight numbers
syntax match asprolNumber /\v\d+(\.\d+)?/

" Highlight pointers and memory addresses
syntax match asprolPointer /\v[%&]\w+/

" Highlight strings
syntax match asprolString /\v"([^"])*"/

" Highlight comments
syntax match asprolComment /;;.*/

" Define ASProL default highlighting
highlight default link asprolKeyword Keyword
highlight default link asprolNumber Number
highlight default link asprolPointer Special
highlight default link asprolString String
highlight default link asprolComment Comment
